#!/bin/bash

# build the smart contract
forge build src/Map.sol

# store the ABI in a file
jq '.abi' out/Map.sol/Map.json >map_abi.json.temp

# check if the abi file changed
if [ -f abi.json ]; then
  diff -q map_abi.json map_abi.json.temp
  EXIT_CODE=$?
else
  EXIT_CODE=1
fi

mv map_abi.json.temp map_abi.json
exit $EXIT_CODE
