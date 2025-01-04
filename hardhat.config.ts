import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const ethPrivateKey = require('./ethPrivateKey.json');

const config: HardhatUserConfig = {
  solidity: "0.8.28",
  defaultNetwork: "subevm",
  networks: {
    subevm: {
      url: "https://evm-testnet.dev.opentensor.ai",
      accounts: [ethPrivateKey]
    },
  },
  mocha: {
    timeout: 300000
  },
};

export default config;
