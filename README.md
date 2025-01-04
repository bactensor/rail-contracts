# Install dependecies

You need node v18.20.3 with npm v10.7.0 to run the scripts.

It's recommended to install them via [nvm (node version manager)](https://github.com/nvm-sh/nvm?tab=readme-ov-file#install--update-script).
After installing `nvm` do this in repo root directory:
```
nvm install v18
nvm use 18
npm install
```

# Compiling the contract and interacting with it
To compile the contract and run scripts you need to provide your own private H160 private key for bittensor. That's a 40 hex digits string prefixed with `0x`. Put it into `ethPrivateKey.json` file. You can create an account using [MetaMask](https://docs.bittensor.com/evm-tutorials/evm-testnet-with-metamask-wallet)


You need to have some TAO to deploy and send transactions. You can get testnet TAO from [here.](https://evm-testnet.dev.opentensor.ai/faucet)

To compile the contract:

```npx hardhat compile```

To deploy a contract:

```npx hardhat --network subevm run scripts/deploy.ts```

Contract's address on testnet and ABI is stored in `deployed-contract.json`.

To send a transaction:

```npx hardhat --network subevm run scripts/callF.ts```

To read the value from contract:

```npx hardhat --network subevm run scripts/readA.ts```

Use [this block explorer](https://evm-testscan.dev.opentensor.ai) to track transactions on chain.
