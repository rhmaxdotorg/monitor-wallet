# monitor-wallet
Monitor amount changes for a given wallet and list of tokens on Ethereum, PulseChain or any other chains supported by Debank

# Intro
This script uses the Debank API (requires subscription) to monitor token amount changes for a wallet.

# Example

# Configuration

JSON format with a few simple fields.

In this example, we monitor 0xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx for asset balance changes for PLS, PLSX, HEX and INC tokens.

```
{
    "wallet_id": "0xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "tokens": [
        {"chain": "pls", "name": "PLS", "id": "pls"},
        {"chain": "pls", "name": "PLSX", "id": "0x95b303987a60c71504d99aa1b13b4da07b0790ab"},
        {"chain": "pls", "name": "HEX", "id": "0x2b591e99afe9f32eaa6214f7b7629768c40eeb39"},
        {"chain": "pls", "name": "INC", "id": "0x2fa878ab3f87cc1c9737fc071108f904c0b0c95d"}
    ]
}
```

Where `wallet_id` is the wallet address to monitor, `chain` is the blockchain network, `name` is the name of the token and `id` is the address (or if native token, the ticker) of the asset to monitor.

# Setup

# Requirements

# Notes
