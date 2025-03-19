#!/usr/bin/env python3

import sys
from web3 import Web3
from common import (
    load_contract_abi,
    get_web3_connection,
    get_account,
    validate_address_format,
    build_and_send_transaction,
    wait_for_receipt
)


def call_bounded(w3, account, contract_address, data: bytes):
    """Call `bounded` contract call.

    Args:
        w3: Web3 instance
        account: Account to use for the transaction
        contract_address: Address of the contract
        data: data to put on the chain as contract call arguments 
    Returns:
        receipt
    """
    validate_address_format(contract_address)

    contract_abi = load_contract_abi()
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    try:
        tx_hash = build_and_send_transaction(
            w3,
            contract,
            contract.functions.checkpointBounded(data),
            account
        )

        receipt = wait_for_receipt(w3, tx_hash)

        return receipt

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    """Handle command line arguments and execute deposit."""
    # Check command line arguments
    if len(sys.argv) != 3:
        print(
            "Usage: python call_bounded.py <contract_address> "
            "<hex data - max 32 byte string>",
            file=sys.stderr
        )
        print(
            "Example: python call_bounded.py 0x123... 0x45ab",
            file=sys.stderr
        )
        sys.exit(1)

    contract_address = sys.argv[1]
    data = sys.argv[2]
    if data.startswith("0x"):
        data = data[2:]

    w3 = get_web3_connection()
    account = get_account()

    receipt = call_bounded(
        w3=w3,
        account=account,
        contract_address=contract_address,
        data=bytes.fromhex(data.rjust(64, '0'))
    )

    print(f"Successfully stored data on the blockchain")
    print("Details:")
    print(f"  Account: {account.address}")
    print(f"  Transaction hash: {receipt['transactionHash'].hex()}")
    print(f"  Block number: {receipt['blockNumber']}")
    print(f"  Data: {data}")


if __name__ == "__main__":
    main()
