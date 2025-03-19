# Rail Smart Contract  

Rail Smart Contract enables **cheap data storage** on the **Bittensor blockchain**, estimated at **0.03 TAO per MB**.  

## Overview  

- **Deployed by**: A subnet owner  
- **Used by**: Miners & validators  
- **Access**: Data is visible via block explorers or via [`python_scripts/filter_transactions.py`](python_scripts/filter_transactions.py).  
- **Wallet requirement**:  
  - Users need an **H160 wallet** (Bittensor EVM-compatible).  
  - The **H160 must be linked to an SS58 hotkey**.  
  - The Bittensor team is working on native linking support, but currently, **knowledge commitments** can be used 
    ([`h160-ss58-bridge/knowledge_commitment.py`](h160_ss58_bridge/knowledge_commitment.py)).  
  - The H160 must be **funded with TAO** for gas fees.  

## Wallet Setup  

- **Recommended**: [Metamask Setup Guide](https://docs.bittensor.com/evm-tutorials/evm-mainnet-with-metamask-wallet)  
- **Alternative (Python)**: Use [`eth-account`](https://pypi.org/project/eth-account/)

### Funding the Wallet  
- Follow **Step 3** in the [Metamask Setup Guide](https://docs.bittensor.com/evm-tutorials/evm-mainnet-with-metamask-wallet).  
- CLI-based funding method is being researched.  

## EVM Devnet
  
- The repo is **pre-configured for EVM Devnet**:
  ```sh
  RPC_URL=https://evm-testnet.dev.opentestnet.ai
  ```
  RPC_URLs for testnet and mainnet can be found [here](https://docs.bittensor.com/evm-tutorials/subtensor-networks).  

- **Devnet limitation**: Only the **last 256 blocks** are accessible. If `filter_transactions.py` does not return older data, this is expected.  

- **Devnet block explorer**: Checkout already deployed [devnet contract](https://evm-testscan.dev.opentensor.ai/address/0xBA1DbF6d0847Fbc46bFE2A0375dB03257fE1D9a0).
  Its abi can be found in [`deployed-contract.json`](deployed-contract.json)

- **Devnet funds**: You need to have some TAO to deploy and send transactions. You can get devnet TAO from the [faucet](https://evm-testnet.dev.opentensor.ai/faucet).

## Deployment  

- Use [**Hardhat** and **npx**](#hardcat-and-npx-deployment).
- Alternative (non-JS) method is being researched.  

## [Interaction Sample Scripts](./python_scripts/)  

| Script                  | Functionality |
|-------------------------|--------------|
| [`call_bounded.py`](./python_scripts/call_bounded.py)       | Stores up to **32 bytes** of data |
| [`call_unbounded.py`](./python_scripts/call_unbounded.py)   | Stores **unlimited data** (higher gas cost) |
| [`filter_transactions.py`](./python_scripts/filter_transactions.py) | Scans on-chain data and outputs **who stored what & when** |


### Storing Data (Bounded)  

```sh
export RPC_URL=https://evm-testnet.dev.opentensor.ai
export PRIVATE_KEY=<your_private_key>

pip install -r requirements.txt
python3 python_scripts/call_bounded.py <contract address> <data>
```
- `<data>` must be **at most 32 bytes** long.
- Calls the **`checkpointBounded(bytes32)`** function of the smart contract.
- Data will be stored **on-chain** and can be retrieved using [`filter_transactions.py`](#fetching-contract-calls).


### Storing Data (Unbounded)  

```sh
export RPC_URL=https://evm-testnet.dev.opentensor.ai
export PRIVATE_KEY=<your_private_key>

pip install -r requirements.txt
python3 python_scripts/call_unbounded.py <contract address> <data>
```
- `<data>` can be **any length** (higher gas cost for larger data).
- Calls the **`checkpointUnbounded(bytes)`** function of the smart contract.
- Data will be stored **on-chain** and can be retrieved using [`filter_transactions.py`](#fetching-contract-calls).

### Fetching contract calls
```
pip install -r requirements.txt
python3 python_scripts/filter_transactions.py <contract address> <bounded|unbounded>
```
Where `bounded` tracks calls to `checkpointBounded(bytes32)` and `unbounded` tracks calls to `checkpointUnbounded(bytes)`.
The script searches through the most recent 256 blocks. Decrease it in the script to get results faster. 
Script stores results in a file `transactions.csv`.


# Hardcat and npx deployment

## Install dependencies

You need Node v18.20.3 with npm v10.7.0 to run the scripts.

It's recommended to install them via [nvm (Node Version Manager)](https://github.com/nvm-sh/nvm?tab=readme-ov-file#install--update-script).
After installing `nvm`, do this in the repo root directory:
```
nvm install v18
nvm use 18
npm install
```

## Compiling the contract and interacting with it
To compile the contract and run scripts, you need to provide your own private H160 private key for Bittensor. That's a 40 hex digit string prefixed with `0x`. Put it into the `ethPrivateKey.json` file. You can create an account using [MetaMask](https://docs.bittensor.com/evm-tutorials/evm-testnet-with-metamask-wallet).

You need to have some TAO to deploy and send transactions. You can get testnet TAO from [here.](https://evm-testnet.dev.opentensor.ai/faucet)

To compile the contract:

```npx hardhat compile```

To deploy a contract:

```npx hardhat --network subevm run scripts/deploy.ts```

The contract's address on testnet and ABI are stored in `deployed-contract.json`.

To call contract's functions:

```npx hardhat --network subevm run scripts/callBounded.ts```

```npx hardhat --network subevm run scripts/callUnbounded.ts```


Use [this block explorer](https://evm-testscan.dev.opentensor.ai) to track transactions on-chain.

