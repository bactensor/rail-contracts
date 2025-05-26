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
#   ./deploy_map.sh 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
#
# 1. admin_h160_address: Ethereum address of the admin (H160 format)
#    Example: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e


if [ "$#" -ne 1 ]; then
    echo "Error: Required arguments missing"
    echo "Usage: $0 <admin_h160_address>"
    exit 1
fi

# Assign command line arguments to variables
ADMIN_ADDRESS=$1

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
forge create src/Map.sol:Map \
    --broadcast \
    --rpc-url "$RPC_URL" \
    --private-key "$DEPLOYER_PRIVATE_KEY" \
    --constructor-args "$ADMIN_ADDRESS"
