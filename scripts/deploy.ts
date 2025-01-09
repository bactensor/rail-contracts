import { ethers } from "hardhat";
import fs from "fs";

async function main() {
  const c = await ethers.deployContract("Checkpoint", []);
  await c.waitForDeployment();

  console.log(
    `Checkpoint deployed to ${c.target}`
  );

  // Save deployment address and ABI
  const deployedContract = {
    address: c.target,
    abi: JSON.parse(c.interface.formatJson())
  };
  fs.writeFileSync("./deployed-contract.json", JSON.stringify(deployedContract));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});