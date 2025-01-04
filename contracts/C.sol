// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

contract C {
    uint256 public a;

    function f() external {
        // trigger change in blockchain's state
        a = 42;
    }
}
