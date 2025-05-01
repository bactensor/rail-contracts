// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.28;

/**
 * @title Map
 * @notice A simple key-value storage contract with admin-only write access
 * @dev This contract allows storing and deleting string key-value pairs. Only the admin can modify values.
 * The contract uses a mapping to store the key-value pairs and provides a function to store/delete values.
 */
contract Map {
    /// @notice The address of the contract administrator
    address public immutable ADMIN;

    /// @notice Mapping of string keys to string values
    mapping(string => string) public value;

    /// @notice Error thrown when a non-admin address tries to modify values
    error NotAdmin();

    /**
     * @notice Constructs the Map contract
     * @param admin The address that will have permission to modify values
     */
    constructor(address admin) {
        ADMIN = admin;
    }

    /**
     * @notice Stores or deletes a value for a given key
     * @dev Only the admin can call this function. If the newValue is empty, the key-value pair is deleted.
     * @param key The key to store the value under
     * @param newValue The value to store. If empty, the key-value pair will be deleted
     * @custom:throws NotAdmin if called by any address other than the admin
     */
    function store(string calldata key, string calldata newValue) external {
        if (msg.sender != ADMIN) revert NotAdmin();

        if (bytes(newValue).length == 0) {
            delete value[key];
        } else {
            value[key] = newValue;
        }
    }
}
