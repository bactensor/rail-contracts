#!/bin/bash

# Example usage:
# First set the required environment variables:
#   export DEPLOYER_PRIVATE_KEY="your-private-key"
#
#   # mainnet:
#   export RPC_URL="https://lite.chain.opentensor.ai"
#
#   # evm devnet:
#   export RPC_URL="https://evm-testnet.dev.opentensor.ai"
#
# Then run the script:
#   ./deploy.sh

# Check if there are no arguments
if [ "$#" -ne 0 ]; then
    echo "Error: Too many arguments"
    echo "Usage: $0"
    exit 1
fi

if [ -z "$DEPLOYER_PRIVATE_KEY" ]; then
    echo "Error: DEPLOYER_PRIVATE_KEY environment variable is not set"
    exit 1
fi

# Check if environment variables are set
if [ -z "$RPC_URL" ]; then
    echo "Error: RPC_URL environment variable is not set"
    exit 1
fi

# Execute the forge create command
forge create contracts/Checkpoint.sol:Checkpoint \
    --broadcast \
    --rpc-url "$RPC_URL" \
    --private-key "$DEPLOYER_PRIVATE_KEY" \
