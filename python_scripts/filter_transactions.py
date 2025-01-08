import csv
import hashlib
import json
from web3 import Web3

NUMBER_OF_RECENT_BLOCKS_TO_CHECK = 100
DEPLOYED_CONTRACT_FILE_PATH = '../deployed-contract.json'
OUTPUT_FILE = 'transactions.csv'


w3 = Web3(Web3.HTTPProvider('https://evm-testnet.dev.opentensor.ai'))

address = None
with open(DEPLOYED_CONTRACT_FILE_PATH, 'r') as file:
    deployed_contract = json.load(file)
    address = deployed_contract['address']

# Compute the function selector from the signature
function_selector = Web3.keccak(text='f(bytes)')[:4].to_0x_hex()

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
                # Skip function selector (10 characters) + encoded length (which uses 32 bytes - another 64 characters)
                argument = tx['input'].to_0x_hex()[74:]  
                sender = tx['from']

                csv_writer.writerow([sender, argument])

print(f'Results saved to {OUTPUT_FILE}')
