#!/usr/bin/env python3

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Any

import requests
from common import (
    build_and_send_transaction,
    get_account,
    get_web3_connection,
    validate_address_format,
    wait_for_receipt,
)
from eth_account.signers.local import LocalAccount
from pydantic import BaseModel
from web3 import Web3


logger = logging.getLogger(__name__)


ENVIRONMENT_CHOICES = ["preprod", "prod", "staging", "testing", "testnet"]
DEFAULT_GAS_LIMIT = 1000000


class ParamItem(BaseModel):
    value: Any
    effective_from: datetime.datetime | None = None


class Param(BaseModel):
    description: str
    items: list[ParamItem]


class ConfigFetchError(Exception):
    """Custom exception for configuration fetch errors."""
    pass


def build_config_urls(env: str, service: str) -> list[str]:
    base_url = "https://raw.githubusercontent.com/backend-developers-ltd/compute-horde-dynamic-config/master"
    return [
        f"{base_url}/{service}-config-{env}.json",
        f"{base_url}/common-config-{env}.json",
    ]


def load_contract_abi():
    path = Path(__file__).parent.parent / "map_abi.json"
    return json.loads(path.read_bytes())


def store_value(
    w3: Web3, account: LocalAccount, contract_address: str, key: str, value: str
):
    """
    Store or delete a value in the Map contract.

    Args:
        w3: Web3 instance
        account: Account to use for the transaction (must be admin)
        contract_address: Address of the Map contract
        key: The key to store the value under
        value: The value to store. If empty, the key-value pair will be deleted
    Returns:
        receipt
    """
    validate_address_format(contract_address)

    contract_abi = load_contract_abi()
    contract = w3.eth.contract(
        address=w3.to_checksum_address(contract_address), abi=contract_abi
    )

    function_call = contract.functions.store(key, value)
    tx_hash = build_and_send_transaction(
        w3, contract, function_call, account, gas_limit=DEFAULT_GAS_LIMIT
    )

    receipt = wait_for_receipt(w3, tx_hash)
    return receipt


def read_value(w3, contract_address: str, key: str):
    """
    Read a value from the Map contract for a given key.

    Args:
        w3: Web3 instance
        contract_address: Address of the Map contract
        key: The key to look up in the Map contract
    Returns:
        value
    """
    validate_address_format(contract_address)

    abi = load_contract_abi()
    contract = w3.eth.contract(address=contract_address, abi=abi)
    value = contract.functions.value(key).call()
    return value


class ConfigSyncer:
    """Handles syncing dynamic configuration from GitHub to Map contract."""

    def __init__(self, w3: Web3, account: LocalAccount, contract_address: str):
        self.w3 = w3
        self.account = account
        self.contract_address = contract_address
        self.stats = {"stored": 0, "skipped": 0, "failed": 0, "unchanged": 0}

    def fetch_config(self, url: str) -> dict:
        """
        Fetch configuration from the given URL.

        Args:
            url: The URL to fetch the configuration from.
        Returns:
            Parsed JSON configuration data.
        """
        try:
            headers = {"User-Agent": "backend-developers-ltd"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ConfigFetchError(f"Failed to fetch config from {url}") from e
        except json.JSONDecodeError as e:
            raise ConfigFetchError(f"Invalid JSON format in config from {url}") from e

    def is_param_effective(self, param_item: ParamItem) -> bool:
        """Check if a parameter item is currently effective."""
        if param_item.effective_from is None:
            return True

        now = datetime.datetime.now(datetime.UTC)
        return param_item.effective_from <= now

    def store_param(self, param_key: str, param_item: ParamItem) -> bool:
        """Store a parameter in the Map contract only if it has changed."""
        new_value = str(param_item.value)
        try:
            # Read the current value from the contract
            current_value = read_value(self.w3, self.contract_address, param_key)

            # Compare current value with new value
            if current_value == new_value:
                logger.debug(f"Config {param_key}={new_value} unchanged, skipping store")
                self.stats["unchanged"] += 1
                return True

            # Value has changed, store the new value
            store_value(
                w3=self.w3,
                account=self.account,
                contract_address=self.contract_address,
                key=param_key,
                value=new_value,
            )

            logger.info(f"Set config {param_key}={param_item.value} (was: {current_value})")

            self.stats["stored"] += 1
            return True

        except Exception as e:
            logger.warning(f"Failed to set config {param_key}={param_item.value}: {e}")
            self.stats["failed"] += 1
            return False

    def sync_config_from_url(self, config_url: str) -> None:
        """Sync configuration from a single URL to the Map contract."""
        logger.info(f"Syncing config from: {config_url}")

        config_data = self.fetch_config(config_url)

        for param_key, raw_param in config_data.items():
            if not param_key.startswith("DYNAMIC_"):
                continue

            try:
                param = Param.model_validate(raw_param)
            except Exception as e:
                logger.warning(f"Invalid param format for {param_key}: {e}")
                self.stats["failed"] += 1
                continue

            for param_item in param.items:
                if not self.is_param_effective(param_item):
                    logger.debug(
                        f"Skipping non-effective config {param_key}={param_item.value}"
                    )
                    self.stats["skipped"] += 1
                    continue

                self.store_param(param_key, param_item)

    def print_stats(self) -> None:
        logger.info(
            f"Sync complete - Stored: {self.stats['stored']}, "
            f"Unchanged: {self.stats['unchanged']}, "
            f"Skipped: {self.stats['skipped']}, Failed: {self.stats['failed']}"
        )


class CLICommands:

    def __init__(self, w3: Web3, contract_address: str):
        self.w3 = w3
        self.contract_address = contract_address

    def set_value(self, key: str, value: str) -> None:
        """
        Set a value in the Map contract.
        """
        account = get_account()
        try:
            receipt = store_value(
                w3=self.w3,
                account=account,
                contract_address=self.contract_address,
                key=key,
                value=value,
            )
        except Exception as e:
            logger.error(f"Failed to set value for key '{key}': {e}")
            sys.exit(1)

        action = "deleted" if not value else "stored"
        logger.info(f"Successfully {action} value for key '{key}'")
        logger.info(
            "Transaction details:\n"
            f"  Account: {account.address}\n"
            f"  Tx Hash: {receipt['transactionHash'].hex()}\n"
            f"  Block:   {receipt['blockNumber']}\n"
            f"  Key:     {key}\n"
            f"  Value:   {value if value else '(deleted)'}"
        )

    def read_value(self, key: str) -> None:
        """
        Read a value from the Map contract.
        """
        try:
            value = read_value(self.w3, self.contract_address, key)
            logger.info(f"Value for key '{key}': {value if value else 'not found'}")
        except Exception as e:
            logger.warning(f"Failed to read value for key '{key}': {e}", exc_info=True)
            sys.exit(1)

    def sync_values(self, service: str, env: str) -> None:
        """
        Sync dynamic configuration from GitHub to the Map contract.
        """
        account = get_account()
        syncer = ConfigSyncer(self.w3, account, self.contract_address)

        try:
            config_urls = build_config_urls(env, service)
            for config_url in config_urls:
                syncer.sync_config_from_url(config_url)
        except Exception as e:
            logger.warning(f"Error syncing config: {e}", exc_info=True)
            sys.exit(1)

        syncer.print_stats()


def build_parser():
    parser = argparse.ArgumentParser(description="Map contract CLI interface")
    parser.add_argument(
        "contract_address", help="The address of the deployed Map contract"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Set command
    set_parser = subparsers.add_parser("set", help="Store a value in the Map contract")
    set_parser.add_argument(
        "--key", required=True, help="The key to store the value under"
    )
    set_parser.add_argument("--value", required=True, help="The value to store")

    # Get command
    get_parser = subparsers.add_parser("get", help="Read a value from the Map contract")
    get_parser.add_argument(
        "--key", required=True, help="The key to look up in the Map contract"
    )

    # Sync command
    sync_parser = subparsers.add_parser(
        "sync", help="Sync dynamic configuration from GitHub to Map contract"
    )
    sync_parser.add_argument(
        "--env", choices=ENVIRONMENT_CHOICES, help="The environment to sync config for"
    )
    sync_parser.add_argument(
        "--service",
        choices=["miner", "validator"],
        required=True,
        help="The service to sync configuration for (miner or validator)",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cli_commands = CLICommands(get_web3_connection(), args.contract_address)

    if args.command == "set":
        return cli_commands.set_value(args.key, args.value)

    elif args.command == "get":
        return cli_commands.read_value(args.key)

    elif args.command == "sync":
        return cli_commands.sync_values(args.service, args.env)


if __name__ == "__main__":
    main()
