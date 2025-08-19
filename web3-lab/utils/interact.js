// interact.js - Example script to interact with deployed contract
require('dotenv').config();
const { ethers } = require('hardhat');

async function main() {
  const address = process.argv[2];
  if (!address) {
    console.error('Usage: node interact.js <contract-address>');
    process.exit(1);
  }
  const Example = await ethers.getContractFactory('Example');
  const example = Example.attach(address);
  const msg = await example.message();
  console.log('Current message:', msg);
  // Example: set new message (requires private key and signer)
  // await example.setMessage('New message');
}

main().catch(console.error);
