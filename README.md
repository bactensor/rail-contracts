# Install dependencies

You need Node v18.20.3 with npm v10.7.0 to run the scripts.

It's recommended to install them via [nvm (Node Version Manager)](https://github.com/nvm-sh/nvm?tab=readme-ov-file#install--update-script).
After installing `nvm`, do this in the repo root directory:
```
nvm install v18
nvm use 18
npm install
```

# Compiling the contract and interacting with it
To compile the contract and run scripts, you need to provide your own private H160 private key for Bittensor. That's a 40 hex digit string prefixed with `0x`. Put it into the `ethPrivateKey.json` file. You can create an account using [MetaMask](https://docs.bittensor.com/evm-tutorials/evm-testnet-with-metamask-wallet).

You need to have some TAO to deploy and send transactions. You can get testnet TAO from [here.](https://evm-testnet.dev.opentensor.ai/faucet)

To compile the contract:

```npx hardhat compile```

To deploy a contract:

```npx hardhat --network subevm run scripts/deploy.ts```

The contract's address on testnet and ABI are stored in `deployed-contract.json`.

To send a transaction:

```npx hardhat --network subevm run scripts/callF.ts```

To read the value from the contract:

```npx hardhat --network subevm run scripts/readA.ts```

Use [this block explorer](https://evm-testscan.dev.opentensor.ai) to track transactions on-chain.

# Running the Python script for fetching contract calls
```
pip install -r requirements.txt
python3 python_scripts/filter_transactions.py arg_name
```
Where `arg_name` is either `bounded`(tracks calls to `checkpointBounded(bytes32)`) or `unbounded`(tracks calls to `checkpointUnbounded(bytes)`).
