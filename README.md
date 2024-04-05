# monitor-wallet
Monitor amount changes for a given wallet and list of tokens on Ethereum, PulseChain or any other chains supported by Debank

# Intro
This script uses the [Debank API](https://cloud.debank.com) (requires subscription for `units`) to monitor token amount changes for a wallet.

# Usage
**Command line**

```
$ ./monitor.py (json config file)
```

**Quick run**
```
$ ./monitor.py config.json
PLS:  100
PLSX: 1000
HEX:  10000
INC:  1

Change detected for PLS: 100 -> 105 -- https://debank.com/profile/0xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/history
Notification sent.

PLS:  105
PLSX: 1000
HEX:  10000
INC:  1

(continues monitoring from here...)
```

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
The code as-is can be used in two primary ways, for running in the console, monitoring for changes and logging automatically to disk OR in addition to that, sending email/sms alerts when asset amounts change. However, it can be also modified to be part of the backend for a bigger project or web UI, there are a ton of possibilities with the Debank API.

So you can have a Linux computer, or a server, and run the script on it. Recommend to run it in `tmux` to keep the session alive during disconnects OR create a service for it, something to make sure it runs over periods of time without interruption for continous monitoring. This also requires [Debank API](https://cloud.debank.com) units to call the API.

## Console Alerts
Before running it, update the script line `ACCESS_KEY` with the API key you get from Debank, else the calls will fail without a valid key.

This is as simple as running the script with a JSON configuration file, in this example it's called `wallet.json`, but it can named anything you choose.

```
$ ./monitor.py wallet.json
```

## Email + SMS Alerts
There are two parts to this.
- Setup the msmtp email client (for example, using gmail account)
- Setup IFTTT (requires Pro account)

### Email
You can use msmtp email client. And if using gmail, create an app password and use it (not the actual gmail password).

**Create a config file in ~/.msmtprc**
```
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile ~/.msmtp.log

account gmail
host smtp.gmail.com
port 587
from YOUREMAILADDRESS@gmail.com
user YOUREMAILADDRESS@gmail.com
password "YOURPASSWORD"

account default : gmail
```

And the script will call `msmtp` to send emails once enabled. This requires a quick code change, just flip `EMAIL_ALERT` to True to enable email+sms alerts in the script.

### SMS
It requires sign-up for a service such as [IFTTT](https://www.ifttt.com) for alerts over email and text message.

- Sign up for IFTTT Pro account
- Create applet -> Classic -> If This -> Add
- Choose Email -> Send IFTTT Any Email -> Then That -> Add
- Choose SMS -> Send Me an SMS -> Create Action -> Continue -> Finish

Configure SMS numbers and email addresses as necessary. When complete, it should look something like this...

`Choose If Send trigger@applet.ifttt.com any email from YOUREMAILADDRESS@gmail.com, then Send me an SMS at PHONENUMBER`

And once configured, the command line remains the same.

# Requirements / Environment
- Linux server
- Python
- msmtp client
- Debank API (paid subscription)
- IFTTT (pro account)

# Notes
- Adjust `SLEEP_SECONDS` in the script for how often to make calls to check for asset amount updates, default time is 10 minutes (more often = using more Debank API units, so be aware of that)
- Logs (text format) are kept in the local `logs/` directory for every run
- 
