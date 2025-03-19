import csv
import hashlib
import json
from web3 import Web3
import sys

NUMBER_OF_RECENT_BLOCKS_TO_CHECK = 100
OUTPUT_FILE = 'transactions.csv'
BOUNDED_SIGNATURE = 'checkpointBounded(bytes32)'
UNBOUNDED_SIGNATURE = 'checkpointUnbounded(bytes)'
BYTES_TO_SKIP = {
    BOUNDED_SIGNATURE: 10, # Skip function selector (10 characters)
    UNBOUNDED_SIGNATURE: 138 # Skip function selector + encoded length + encoded offset
}


w3 = Web3(Web3.HTTPProvider('https://evm-testnet.dev.opentensor.ai'))


def main(contract_address, signature):
    assert signature in [BOUNDED_SIGNATURE, UNBOUNDED_SIGNATURE], f"Invalid signature: {signature}"

    # Compute the function selector from the signature
    function_selector = Web3.keccak(text=signature)[:4].to_0x_hex()

    with open(OUTPUT_FILE, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['block', 'sender', 'argument'])  # Write header

        current_block_num = w3.eth.block_number
        starting_block_num = current_block_num - NUMBER_OF_RECENT_BLOCKS_TO_CHECK
        ending_block_num = current_block_num

        # Iterate through the blocks and transactions
        for block_number in range(starting_block_num, ending_block_num + 1):
            block = w3.eth.get_block(block_number, full_transactions=True)
            for tx in block.transactions:
                if tx['to'] == contract_address and tx['input'].to_0x_hex()[:10] == function_selector:
                    argument = tx['input'].to_0x_hex()[BYTES_TO_SKIP[signature]:]  
                    sender = tx['from']

                    csv_writer.writerow([block_number, sender, argument])

    print(f'Results saved to {OUTPUT_FILE}')


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[2] not in ['bounded', 'unbounded']:
        print("Usage: python filter_transactions.py <contract_address> <bounded|unbounded>")
        sys.exit(1)

    contract_address = sys.argv[1]
    
    signature = BOUNDED_SIGNATURE if sys.argv[2] == "bounded" else UNBOUNDED_SIGNATURE
    main(contract_address, signature)
