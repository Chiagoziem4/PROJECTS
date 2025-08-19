// fetchTx.js - Fetch transaction receipt and events
require('dotenv').config();
const { ethers } = require('hardhat');

async function main() {
  const txHash = process.argv[2];
  if (!txHash) {
    console.error('Usage: node fetchTx.js <tx-hash>');
    process.exit(1);
  }
  const provider = ethers.provider;
  const receipt = await provider.getTransactionReceipt(txHash);
  console.log('Receipt:', receipt);
  if (receipt && receipt.logs) {
    console.log('Logs:', receipt.logs);
  }
}

main().catch(console.error);
