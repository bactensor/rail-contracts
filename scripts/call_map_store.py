#!/usr/bin/env python3

import sys
import argparse
from common import (
    load_contract_abi,
    get_web3_connection,
    get_account,
    validate_address_format,
    build_and_send_transaction,
    wait_for_receipt
)

def store_value(w3, account, contract_address, key: str, value: str):
    """Store or delete a value in the Map contract.

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

    contract_abi = load_contract_abi("../out/Map.sol/Map.json")
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    try:
        tx_hash = build_and_send_transaction(
            w3,
            contract,
            contract.functions.store(key, value),
            account
        )

        receipt = wait_for_receipt(w3, tx_hash)
        return receipt

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Store or delete a value in the Map contract'
    )
    parser.add_argument(
        'contract_address',
        help='The address of the deployed Map contract'
    )
    parser.add_argument(
        'key',
        help='The key to store the value under'
    )
    parser.add_argument(
        'value',
        help='The value to store. If empty, the key-value pair will be deleted'
    )

    args = parser.parse_args()

    w3 = get_web3_connection()
    account = get_account()

    receipt = store_value(
        w3=w3,
        account=account,
        contract_address=args.contract_address,
        key=args.key,
        value=args.value
    )

    print(f"Successfully {'deleted' if not args.value else 'stored'} value")
    print("Details:")
    print(f"  Account: {account.address}")
    print(f"  Transaction hash: {receipt['transactionHash'].hex()}")
    print(f"  Block number: {receipt['blockNumber']}")
    print(f"  Key: {args.key}")
    if args.value:
        print(f"  Value: {args.value}")

if __name__ == "__main__":
    main()
