import { ethers } from "hardhat";

const deployedContract = require('../deployed-contract.json');

async function main() {
  // private key of the account that sends transactions is pulled from config - hardhat magic
  const c = await ethers.getContractAt(deployedContract.abi, deployedContract.address);
  const receipt = await c.checkpointBounded(ethers.zeroPadValue("0xff", 32));
  console.log(receipt);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});