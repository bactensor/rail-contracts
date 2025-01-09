import csv
import hashlib
import json
from web3 import Web3
import sys

NUMBER_OF_RECENT_BLOCKS_TO_CHECK = 100
DEPLOYED_CONTRACT_FILE_PATH = '../deployed-contract.json'
OUTPUT_FILE = 'transactions.csv'
BOUNDED_SIGNATURE = 'checkpointBounded(bytes32)'
UNBOUNDED_SIGNATURE = 'checkpointUnbounded(bytes)'
BYTES_TO_SKIP = {
    BOUNDED_SIGNATURE: 10, # Skip function selector (10 characters)
    UNBOUNDED_SIGNATURE: 138 # Skip function selector + encoded length + encoded offset
}


w3 = Web3(Web3.HTTPProvider('https://evm-testnet.dev.opentensor.ai'))


def main(signature):
    assert signature in [BOUNDED_SIGNATURE, UNBOUNDED_SIGNATURE], f"Invalid signature: {signature}"

    address = None
    with open(DEPLOYED_CONTRACT_FILE_PATH, 'r') as file:
        deployed_contract = json.load(file)
        address = deployed_contract['address']

    # Compute the function selector from the signature
    function_selector = Web3.keccak(text=signature)[:4].to_0x_hex()

    with open(OUTPUT_FILE, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['sender', 'argument'])  # Write header

        current_block_num = w3.eth.block_number
        starting_block_num = current_block_num - NUMBER_OF_RECENT_BLOCKS_TO_CHECK
        ending_block_num = current_block_num

        # Iterate through the blocks and transactions
        for block_number in range(starting_block_num, ending_block_num + 1):
            block = w3.eth.get_block(block_number, full_transactions=True)
            for tx in block.transactions:
                if tx['to'] == address and tx['input'].to_0x_hex()[:10] == function_selector:
                    argument = tx['input'].to_0x_hex()[BYTES_TO_SKIP[signature]:]  
                    sender = tx['from']

                    csv_writer.writerow([sender, argument])

    print(f'Results saved to {OUTPUT_FILE}')


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['bounded', 'unbounded']:
        print("Usage: python filter_transactions.py <bounded|unbounded>")
        sys.exit(1)

    signature = BOUNDED_SIGNATURE if sys.argv[1] == "bounded" else UNBOUNDED_SIGNATURE
    main(signature)
