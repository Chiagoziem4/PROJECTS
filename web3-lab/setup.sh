#!/bin/bash
# setup.sh - Web3 Lab setup script
# Installs Node.js, Hardhat, dependencies, and scaffolds the project

set -e

LABDIR="$HOME/Projects/web3-lab"

# Install Node.js and npm if not present
if ! command -v node >/dev/null; then
  echo "[+] Installing Node.js..."
  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
  sudo apt-get install -y nodejs
else
  echo "[+] Node.js already installed."
fi

# Create project directory
mkdir -p "$LABDIR"
cd "$LABDIR"

# Initialize npm project if not present
if [ ! -f package.json ]; then
  npm init -y
fi

# Install Hardhat and core dependencies
npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers @openzeppelin/contracts dotenv

# Install Foundry (optional, if user wants)
if ! command -v forge >/dev/null; then
  echo "[+] Installing Foundry..."
  curl -L https://foundry.paradigm.xyz | bash
  ~/.foundry/bin/foundryup
else
  echo "[+] Foundry already installed."
fi

# Install other useful tools
npm install --save-dev web3 @chainlink/contracts hardhat-gas-reporter

# Create .env for RPC keys
if [ ! -f .env ]; then
  echo "ALCHEMY_API_KEY=your-alchemy-key" > .env
  echo "INFURA_API_KEY=your-infura-key" >> .env
  echo "PRIVATE_KEY=your-private-key" >> .env
fi

# Scaffold Hardhat project
if [ ! -f hardhat.config.js ]; then
  npx hardhat --yes
fi

# Copy example contract
cat > contracts/Example.sol <<EOF
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

contract Example is Ownable {
    string public message;
    event MessageChanged(string newMessage);
    constructor(string memory _msg) { message = _msg; }
    function setMessage(string memory _msg) public onlyOwner {
        message = _msg;
        emit MessageChanged(_msg);
    }
}
EOF

# Copy example deploy script
mkdir -p scripts
cat > scripts/deploy.js <<EOF
// scripts/deploy.js
require("dotenv").config();
const { ethers } = require("hardhat");

async function main() {
  const Example = await ethers.getContractFactory("Example");
  const example = await Example.deploy("Hello, Web3!");
  await example.deployed();
  console.log("Example deployed to:", example.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
EOF

# Copy example test
mkdir -p tests
cat > tests/example.js <<EOF
const { expect } = require("chai");
describe("Example", function () {
  it("Should set the right message", async function () {
    const Example = await ethers.getContractFactory("Example");
    const example = await Example.deploy("Hello");
    await example.deployed();
    expect(await example.message()).to.equal("Hello");
  });
});
EOF

# NPM scripts
npx npm-add-script -k "compile" -v "npx hardhat compile"
npx npm-add-script -k "deploy" -v "npx hardhat run scripts/deploy.js --network localhost"
npx npm-add-script -k "test" -v "npx hardhat test"
npx npm-add-script -k "lint" -v "npx hardhat lint || echo 'No linter configured'"

# Permissions
chmod +x setup.sh

echo "[+] Web3 Lab setup complete!"
