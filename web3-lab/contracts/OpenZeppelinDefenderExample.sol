// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

contract OpenZeppelinDefenderExample is Ownable {
    // Example function that could be protected by Defender Relayer or Safe
    function protectedAction() public onlyOwner {
        // Do something sensitive
    }
}
