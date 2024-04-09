# monitor-wallet
Monitor amount changes for a given wallet and list of tokens on Ethereum, PulseChain or any other chains supported by Debank.

**Get Console and SMS alerts when asset values change.**

# Intro
This script uses the [Debank API](https://cloud.debank.com) (requires subscription for `units`) to monitor token amount changes for a wallet.

![sms-2](https://github.com/rhmaxdotorg/monitor-wallet/assets/100790377/a2136440-e3ce-4d6b-9659-1b453b435b36)

![sms-1](https://github.com/rhmaxdotorg/monitor-wallet/assets/100790377/723d7318-5a09-4ef2-84f1-2fab40b1cbb4)

# Usage
**Command line**

```
$ ./monitor.py (json config file)
```

**Quick run**
```
$ ./monitor.py config.json

PLS:  500
PLSX: 500
HEX:  50000
INC:  1

PLSX: 5500

PLSX amount changed +5000 (+0.23 USD value) to 5500 PLSX, below the threshold of 30 USD.
Not sending notification.

PLS:  500
PLSX: 5500
HEX:  50000
INC:  1

PLSX: 1005500

PLSX amount changed +1000000 (+41.33 USD value) to 1005500 PLSX, meeting or exceeding the threshold of 30 USD.

Notification sent.

(continues monitoring from here...)
```

As you can see, the user is notified only on the console when smaller amounts change the asset values, but SMS notification can be sent when larger changes occur in asset amounts. This is to prevent lots of notifications from small changes, can be enabled/disabled and of course will be more or less useful depending on the activity in the wallet and the granularity of notifications the user prefers.

The notification sent is a ifttt shortened link which redirects to https://debank.com/profile/0xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/history, so from there you can check the latest TXs including the one that triggered the notification.

`MINIMUM_CHANGE` and `USD_MINIMUM` in the code are adjustable as necessary to avoid notifications due to small changes in asset amounts. For example, you could adjust them to only alert on large asset value or big dollar amount changes.

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

# Requirements / Environment
**Just the basics + Debank API units are required to run the script**
- Linux server
- Python
- Debank API (paid subscription)

**And in addition to those, these apps and services are required to get SMS alerts**
- msmtp client
- Email address (gmail)
- IFTTT (pro account)

# Setup
The code as-is can be used in two primary ways, for running in the console, monitoring for changes and logging automatically to disk OR in addition to that, sending SMS alerts when asset amounts change. However, it can be also modified to be part of the backend for a bigger project or web UI, there are a ton of possibilities with the Debank API.

So you can have a Linux computer, or a server, and run the script on it. Recommend to run it in `tmux` to keep the session alive during disconnects OR create a service for it, something to make sure it runs over periods of time without interruption for continous monitoring. This also requires [Debank API](https://cloud.debank.com) units to call the API.

## Console Alerts
Before running it, update the script line `ACCESS_KEY` with the API key you get from Debank, else the calls will fail without a valid key.

This is as simple as running the script with a JSON configuration file, in this example it's called `wallet.json`, but it can named anything you choose.

```
$ ./monitor.py wallet.json
```

## SMS Alerts
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
from YOUR-EMAIL-ADDRESS@gmail.com
user YOUR-EMAIL-ADDRESS@gmail.com
password "YOUR-APP-PASSWORD"

account default : gmail
```

And the script will call `msmtp` to send emails once enabled. This requires a quick code change, just flip `EMAIL_ALERT` to True to enable SMS alerts in the script.

### SMS
It requires sign-up for a service such as [IFTTT](https://www.ifttt.com) for alerts over SMS message. This works by sending an email to IFTTT, triggering an applet and it sending a txt message to the specified number.

- Sign up for IFTTT Pro account
- Create applet -> Classic -> If This -> Add
- Choose Email -> Send IFTTT Any Email -> Then That -> Add
- Choose SMS -> Send Me an SMS -> Create Action -> Continue -> Finish

Configure SMS numbers and email addresses as necessary. When complete, it should look something like this...

`Choose If Send trigger@applet.ifttt.com any email from YOUREMAILADDRESS@gmail.com, then Send me an SMS at PHONENUMBER`

And once configured, the command line remains the same.

# Testing
Afer you are setup with the services and requirements, here's how you can test monitoring on a wallet.

- Create `config.json` and set `wallet_id` to the wallet you want to monitor (or you have keys to) and token to HEX
- Run the script
- Send HEX to the wallet (ensure it meets `MINIMUM_CHANGE` and `USD_MINIMUM` threshold values if enabled)
- Wait 10 minutes (or whatever `SLEEP_SECONDS` value is, can be configured for more or less)
- Check for SMS message with link to Debank portfolio transaction list to view recent activity (see which TX triggered the change in asset amount)

# Notes
- Adjust `SLEEP_SECONDS` in the script for how often to make calls to check for asset amount updates, default time is 10 minutes (more often = using more Debank API units, so be aware of that)
- Adjust `MINIMUM_CHANGE` and `USD_MINIMUM` as necessary to avoid notifications due to small changes in asset amounts (default is 30 USD and it uses Dexsceener API to fetch asset prices)
- Logs (text format) are kept in the local `logs` directory for every run
