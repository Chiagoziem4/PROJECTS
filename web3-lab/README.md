# Web3 Lab

A professional, modular Web3 development environment for Ethereum smart contract and dApp development.

## Structure
```
web3-lab/
├── contracts/   # Solidity contracts (Hardhat/Foundry)
├── scripts/     # Deployment and utility scripts
├── tests/       # Test files (JS/TS or Foundry)
├── front-end/   # Front-end dApp code
├── utils/       # Helper scripts (JS/Python)
├── .vscode/     # VS Code tasks
└── README.md    # This file
```

## Quick Start
1. Run `setup.sh` to install Node.js, Hardhat, dependencies, and scaffold the project.
2. Configure your RPC keys in `.env`.
3. Use VS Code tasks or npm scripts to compile, deploy, and test.

## Example Commands
- `npm run compile` — Compile contracts
- `npm run deploy` — Deploy to local Hardhat node
- `npm test` — Run tests

## Extending
- Add new contracts to `contracts/`
- Add new scripts to `scripts/` or `utils/`
- Integrate Chainlink, OpenZeppelin, and more

---
See below for more details on configuration, usage, and advanced features.
