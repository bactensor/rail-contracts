// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.28;

import {Test, console2} from "forge-std/Test.sol";
import {Map} from "../src/Map.sol";

contract MapTest is Test {
    Map public map;
    address public admin = makeAddr("admin");
    address public user = makeAddr("user");

    string constant TEST_KEY = "testKey";
    string constant TEST_VALUE = "testValue";

    function setUp() public {
        vm.prank(admin);
        map = new Map(admin);
    }

    function test_AdminIsSet() public view {
        assertEq(map.ADMIN(), admin);
    }

    function test_AdminCanStoreValue() public {
        vm.prank(admin);
        map.store(TEST_KEY, TEST_VALUE);
        assertEq(map.value(TEST_KEY), TEST_VALUE);
    }

    function test_AdminCanDeleteValue() public {
        vm.prank(admin);
        map.store(TEST_KEY, TEST_VALUE);
        assertEq(map.value(TEST_KEY), TEST_VALUE);

        vm.prank(admin);
        map.store(TEST_KEY, "");
        assertEq(map.value(TEST_KEY), "");
    }

    function test_AdminCanUpdateValue() public {
        vm.prank(admin);
        map.store(TEST_KEY, "initialValue");
        assertEq(map.value(TEST_KEY), "initialValue");

        vm.prank(admin);
        map.store(TEST_KEY, "updatedValue");
        assertEq(map.value(TEST_KEY), "updatedValue");
    }

    function test_revert_NonAdminCannotStoreValue() public {
        vm.prank(user);
        vm.expectRevert(Map.NotAdmin.selector);
        map.store(TEST_KEY, TEST_VALUE);
    }

    function test_revert_NonAdminCannotDeleteValue() public {
        vm.prank(admin);
        map.store(TEST_KEY, TEST_VALUE);

        vm.prank(user);
        vm.expectRevert(Map.NotAdmin.selector);
        map.store(TEST_KEY, "");
    }

    function test_revert_NonAdminCannotUpdateValue() public {
        vm.prank(admin);
        map.store(TEST_KEY, TEST_VALUE);

        vm.prank(user);
        vm.expectRevert(Map.NotAdmin.selector);
        map.store(TEST_KEY, "updatedValue");
    }

    function test_NonAdminCanReadValue() public {
        vm.prank(admin);
        map.store(TEST_KEY, TEST_VALUE);

        vm.prank(user);
        assertEq(map.value(TEST_KEY), TEST_VALUE);
    }
}
