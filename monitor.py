#!/usr/bin/env python3
# monitor.py - Monitor token balances in wallets with Debank API on Ethereum or PulseChain

import os
import requests
import time
import sys
import json
import subprocess
import logging
from datetime import datetime

# Configuration variables
DEBUG_ENABLED = True
EMAIL_ALERT = True
SLEEP_SECONDS = 600  # 10 minutes

# avoid notifications on small asset changes
MINIMUM_CHANGE = True # only notify on changes in asset amount >= MINIMUM_CHANGE_VALUE
MINIMUM_CHANGE_VALUE = 1

USD_MINIMUM = True # only notify on changes in asset amount >= USD_MINIMUM_VALUE
USD_MINIMUM_VALUE = 30

ACCESS_KEY = 'GET-ACCESS-KEY-FROM-DEBANK' # Your AccessKey here

# Ensure 'logs' directory exists
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Configure file handler with the current datetime for filename
from datetime import datetime
log_filename = f"{logs_dir}/monitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(console_formatter)  # Reuse the same formatter
logger.addHandler(file_handler)

def fetch_current_price(token_id):
    dex_screener_base_url = "https://api.dexscreener.com/latest/dex/tokens/"

    if token_id == "pls":
        token_id = "0xa1077a294dde1b09bb078844df40758a5d0f9a27"  # WPLS
    elif token_id == "eth":
        token_id = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH

    url = dex_screener_base_url + f"{token_id}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        pairs = data.get('pairs', [])
        found = False  # Flag to indicate if a matching pair has been found

        # Check for any pair with 'DAI', 'USDC', or 'USDT' as the quoteToken symbol
        for pair in pairs:
            if pair['quoteToken']['symbol'] in ['DAI', 'USDC', 'USDT']:
                if not found:  # Log the price only if a match hasn't been found yet
                    found = True  # Update the flag to indicate a match has been found
                    return pair['priceUsd']
        if not found:  # If no matching pair was found
            logger.info(f"USD Price not found for any of the specified tokens on chain.")
            return None
    else:
        logger.info(f"Failed to retrieve data from API.")
        return None


def send_notification(message):
    body = f"{message}"
    recipient = f"trigger@applet.ifttt.com"
    message = f"To: {recipient}\n\n{body}"

    try:
        # Command to send an email using msmtp
        command = f'echo "{message}" | msmtp {recipient}'
        subprocess.run(command, shell=True, check=True)
        if(DEBUG_ENABLED):
            logger.info("Notification sent.\n")
    except subprocess.CalledProcessError:
        logger.info("Failed to send notification.\n")

def read_config(file_path):
    with open(file_path, 'r') as file:
        try:
            config = json.load(file)
        except json.JSONDecodeError:
            logger.info("Error: The config file contains invalid JSON.")
            sys.exit(1)

    # Validate wallet_id
    if 'wallet_id' not in config or not isinstance(config['wallet_id'], str):
        logger.info("Error: 'wallet_id' is missing or not a string in the config file.")
        sys.exit(1)

    # Validate tokens list
    if 'tokens' not in config or not isinstance(config['tokens'], list):
        logger.info("Error: 'tokens' is missing or not a list in the config file.")
        sys.exit(1)

    # Validate each token entry
    for token in config['tokens']:
        if not isinstance(token, dict) or 'name' not in token or 'id' not in token or 'chain' not in token:
            logger.info("Error: Each token must be an object with 'name', 'id', and 'chain' keys.")
            sys.exit(1)
        if not isinstance(token['name'], str) or not isinstance(token['id'], str) or not isinstance(token['chain'], str):
            logger.info("Error: The 'name', 'id', and 'chain' keys for each token must be strings.")
            sys.exit(1)

    return config

def check_for_changes(wallet_id, tokens):
    global last_known_amounts

    history_url = f"https://debank.com/profile/{wallet_id}/history"

    max_token_name_length = max(len(token['name']) for token in tokens) + 1

    for token in tokens:
        response = requests.get(
            f'https://pro-openapi.debank.com/v1/user/token?id={wallet_id}&chain_id={token["chain"]}&token_id={token["id"]}',
            headers={'accept': 'application/json', 'AccessKey': ACCESS_KEY}
        )

        if response.status_code == 200:
            data = response.json()
            current_amount = float(data.get('amount', 0.0))
            last_amount = last_known_amounts.get(token['id'], None)

            if last_amount is None:
                last_known_amounts[token['id']] = current_amount
                #logger.info(f"{token['name']}: {current_amount:.0f}") # No change detection this cycle
                logger.info(f"{token['name'] + ':':{max_token_name_length}} {int(current_amount)}")
                continue

            logger.info(f"{token['name'] + ':':{max_token_name_length}} {int(current_amount)}")

            change_detected = abs(current_amount - last_amount) >= MINIMUM_CHANGE_VALUE if MINIMUM_CHANGE else current_amount != last_amount

            if change_detected:
                process_change(token, current_amount, last_amount, history_url)
                logger.info(f"{token['name'] + ':':{max_token_name_length}} {int(current_amount)}")
                last_known_amounts[token['id']] = current_amount
        else:
            logger.info(f"Failed to fetch data for {token['name']} ({token['id']}) on {token['chain']}.")

    logger.info(f"")

def process_change(token, current_amount, last_amount, history_url):
    # Fetch the current USD price
    current_price = fetch_current_price(token['id'])

    if current_price:
        # Calculate the USD value change
        usd_value_change = (current_amount - last_amount) * float(current_price)
        change_sign = "+" if usd_value_change >= 0 else ""

        if abs(usd_value_change) >= USD_MINIMUM_VALUE:
            logger.info(f"\n{token['name']} amount changed {change_sign}{abs((current_amount - last_amount)):.0f} ({change_sign}{abs(usd_value_change):.2f} USD value) to {current_amount:.0f} {token['name']}, meeting or exceeding the threshold of {USD_MINIMUM_VALUE} USD.\n")
            if EMAIL_ALERT:
                send_notification(history_url)
        else:
            logger.info(f"\n{token['name']} amount changed {change_sign}{abs((current_amount - last_amount)):.0f} ({change_sign}{abs(usd_value_change):.2f} USD value) to {current_amount:.0f} {token['name']}, below the threshold of {USD_MINIMUM_VALUE} USD.\nNot sending notification.\n")
    else:
        logger.info(f"Could not fetch current price for {token['name']}, skipping USD value change check.")

def main():
    if len(sys.argv) < 2:
        logger.info("Usage: monitor.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    # Check if the config file exists
    if not os.path.exists(config_file):
        logger.info(f"Error: The specified config file does not exist: {config_file}")
        sys.exit(1)

    config = read_config(config_file)

    wallet_id = config['wallet_id']
    tokens = config['tokens']

    # Initialize a dictionary to track the last known amounts for each token
    global last_known_amounts
    last_known_amounts = {token['id']: None for token in tokens}

    try:
        while True:
            check_for_changes(wallet_id, tokens)
            time.sleep(SLEEP_SECONDS)
    except KeyboardInterrupt:
        logger.info("Program terminated by user.")

if __name__ == '__main__':
    main()
