// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

contract Checkpoint {
    uint256 public a;

    function checkpointBounded(bytes32 /*b*/) external {
        // trigger change in blockchain's state
        a = 42;
    }

    function checkpointUnbounded(bytes calldata /*b*/) external {
        // trigger change in blockchain's state
        a = 42;
    }
}
