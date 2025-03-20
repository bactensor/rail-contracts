# Rail Smart Contract  

Rail Smart Contract enables **cheap data storage** on the **Bittensor blockchain**, estimated at **0.03 TAO per MB**.  

## Overview  

- **Deployed by**: A subnet owner  
- **Used by**: Miners & validators  
- **Access**: Data is visible via block explorers or via [`scripts/filter_transactions.py`](scripts/filter_transactions.py).  
- **Wallet requirement**:  
  - Users need an **H160 wallet** (Bittensor EVM-compatible).  
  - The **H160 must be linked to an SS58 hotkey**.  
  - The Bittensor team is working on native linking support, but currently, **knowledge commitments** can be used 
    ([`h160-ss58-bridge/knowledge_commitment.py`](h160_ss58_bridge/knowledge_commitment.py)).
    Check out the [H160-SS58 bridge](#h160-ss58-bridge) section to learn how it works.
  - The H160 must be **funded with TAO** for gas fees.  

## Wallet Setup  

- **Recommended**: [Metamask Setup Guide](https://docs.bittensor.com/evm-tutorials/evm-mainnet-with-metamask-wallet).
- **Alternative (Python)**: Use [`eth-account`](https://pypi.org/project/eth-account/).

### Funding the Wallet  
- Follow **Step 3** in the [Metamask Setup Guide](https://docs.bittensor.com/evm-tutorials/evm-mainnet-with-metamask-wallet).
- You can also use [TAO Transfers bridge](https://bridge.bittensor.com/).
- CLI-based funding method is being researched.  

## EVM Devnet
  
- The repo is **pre-configured for EVM Devnet**:
  ```sh
  RPC_URL=https://evm-testnet.dev.opentestnet.ai
  ```
  RPC_URLs for testnet and mainnet can be found [here](https://docs.bittensor.com/evm-tutorials/subtensor-networks).  

- **Devnet limitation**: Only the **last 256 blocks** are accessible. If `filter_transactions.py` does not return older data, this is expected.  

- **Devnet block explorer**: Check out already deployed [devnet contract](https://evm-testscan.dev.opentensor.ai/address/0xBA1DbF6d0847Fbc46bFE2A0375dB03257fE1D9a0).
  The contract ABI is available in [`deployed-contract.json`](deployed-contract.json)

- **Devnet funds**: You need to have some TAO to deploy and send transactions. You can get devnet TAO from the [faucet](https://evm-testnet.dev.opentensor.ai/faucet).

## Deployment
- Install [Foundry](https://book.getfoundry.sh/).
- Clone this repository.
- Prepare [H160 wallet](#wallet-setup) and fund it (see [EVM devnet](#evm-devnet) faucet info)
- Compile and deploy the contract: export `RPC_URL` and `DEPLOYER_PRIVATE_KEY` and run [`scripts/deploy.sh`](./scripts/deploy.sh):
  ```sh
  export RPC_URL=https://evm-testnet.dev.opentensor.ai
  export PRIVATE_KEY=<your_private_key>

  scripts/deploy.sh
  ```
- Record the deployed contract address - you will be need it later. It can also be found on a block explorer for the network you deployed on.

## Interaction Sample Scripts

| Script                  | Functionality |
|-------------------------|--------------|
| [`call_bounded.py`](./scripts/call_bounded.py)       | Stores up to **32 bytes** of data |
| [`call_unbounded.py`](./scripts/call_unbounded.py)   | Stores **unlimited data** (higher gas cost) |
| [`filter_transactions.py`](./scripts/filter_transactions.py) | Scans on-chain data and outputs **who stored what & when** |


### Storing Data (Bounded)  

```sh
export RPC_URL=https://evm-testnet.dev.opentensor.ai
export PRIVATE_KEY=<your_private_key>

pip install -r requirements.txt
python call_bounded.py <contract address> <data>
```
- `<data>` must be **at most 32 bytes** long.
- Calls the **`checkpointBounded(bytes32)`** function of the smart contract.
- Data will be stored **on-chain** and can be retrieved using [`filter_transactions.py`](#fetching-contract-calls).


### Storing Data (Unbounded)  

```sh
export RPC_URL=https://evm-testnet.dev.opentensor.ai
export PRIVATE_KEY=<your_private_key>

pip install -r requirements.txt
python call_unbounded.py <contract address> <data>
```
- `<data>` can be **any length** (higher gas cost for larger data).
- Calls the **`checkpointUnbounded(bytes)`** function of the smart contract.
- Data will be stored **on-chain** and can be retrieved using [`filter_transactions.py`](#fetching-contract-calls).

### Fetching contract calls
```sh
pip install -r requirements.txt
python filter_transactions.py <contract address> <bounded|unbounded>
```
Where `bounded` tracks calls to `checkpointBounded(bytes32)` and `unbounded` tracks calls to `checkpointUnbounded(bytes)`.
The script searches through the most recent 256 blocks. Adjust it in the script to get results faster.
Script stores results in a file `transactions.csv`.

## H160-SS58 Bridge

The bridge **associates an H160 wallet with an SS58 hotkey** by storing the **connection proof** in the **UID's knowledge commitment**.

### How It Works

**Data Storage in Knowledge Commitment**
  - The **H160 public key** and a **message signed with the H160 private key** are stored inside the knowledge commitment.
  - The **message is the SS58 hotkey**, making the process more mistake-resistant.

**Verification
  - The **H160 public key** (stored in the commitment) can be used to **verify the signature**, proving ownership of the **H160 private key**.
  - The **EVM address** is the **last 20 bytes** of the **Keccak-256 hash** of the public key.

### Sample code
Check out the [sample code](./h160_ss58_bridge/knowledge_commitment.py) demonstrating this process.

