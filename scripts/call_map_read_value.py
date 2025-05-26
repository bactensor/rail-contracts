#!/usr/bin/env python3

import sys
import argparse
from common import (
    load_contract_abi,
    get_web3_connection,
    validate_address_format
)

def main():
    parser = argparse.ArgumentParser(
        description='Read a value from the Map contract for a given key'
    )
    parser.add_argument(
        'contract_address',
        help='The address of the deployed Map contract'
    )
    parser.add_argument(
        'key',
        help='The key to look up in the Map contract'
    )
    args = parser.parse_args()
    validate_address_format(args.contract_address)

    w3 = get_web3_connection()
    abi = load_contract_abi("../out/Map.sol/Map.json")
    contract = w3.eth.contract(address=args.contract_address, abi=abi)
    try:
        value = contract.functions.value(args.key).call()
        print(value)
    except Exception as e:
        print(f"Error reading value: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
