# uniswap-price-feed

This repository contains a testing / standalone service for publishing Oracle current prices over Websockets.


## Rationale

This is a testing service that facilitates distribution of current Oracle prices to keeper bots from the `market-maker-keeper`
<https://github.com/makerdao/market-maker-keeper> repository. Prices are retrieved from chain at configured `fetch-time` interval (defaults to 30 seconds).


## Installation

This project uses *Python 3.6.6* and requires *virtualenv* to be installed.

In order to clone the project and install required third-party packages please execute:
```
git clone https://github.com/makerdao/oracle-price-feed.git
cd oracle-price-feed
git submodule update --init --recursive
./install.sh
```


## Running

```
usage: oracle-price-feed [-h] [--rpc-host RPC_HOST] [--rpc-port RPC_PORT]
                         [--rpc-timeout RPC_TIMEOUT]
                         [--http-address HTTP_ADDRESS] [--http-port HTTP_PORT]
                         [--token TOKEN] [--report-time REPORT_TIME]
                         [--fetch-time FETCH_TIME] [--ro-account RO_ACCOUNT]
                         [--rw-account RW_ACCOUNT]

optional arguments:
  -h, --help            show this help message and exit
  --rpc-host RPC_HOST   JSON-RPC host (default: `localhost')
  --rpc-port RPC_PORT   JSON-RPC port (default: `8545')
  --rpc-timeout RPC_TIMEOUT
                        JSON-RPC timeout (in seconds, default: 10)
  --http-address HTTP_ADDRESS
                        Address of the Oracle Price Feed
  --http-port HTTP_PORT
                        Port of the Oracle Price Feed
  --token TOKEN         Token symbol
  --report-time REPORT_TIME
                        Time interval to report price to clients
  --fetch-time FETCH_TIME
                        Time interval to get price from Oracle
  --ro-account RO_ACCOUNT
                        Credentials of the read-only user (format:
                        username:password)
  --rw-account RW_ACCOUNT
                        Credentials of the read-write user (format:
                        username:password)
```

## Sample scripts

- ETH-USD price feed (e.g. pass `--token ETH` command line argument) published at `ws://user:readonly@localhost:7777/price/ETH-USD_ORACLE/socket`
```
bin/oracle-price-feed \
    --token ETH \
    --ro-account user:readonly \
    --rw-account user:readwrite \
    --fetch-time 10 \
    --report-time 2
```

- BAT-USD price feed (e.g. pass `--token BAT` command line argument) published at `ws://user:readonly@localhost:7777/price/BAT-USD_ORACLE/socket`
```
bin/oracle-price-feed \
    --token BAT \
    --ro-account user:readonly \
    --rw-account user:readwrite \
    --fetch-time 10 \
    --report-time 2
```

## API

The primary and only entity this service operates on is _feed_. Each feed is effectively a stream
of timestamped records. Timestamps never go back and it is always guaranteed that
new records will be added 'after' the existing ones. This simplification makes feed streams
consumption much easier for clients.

Each record is represented throughout the service as a JSON structure with two fields: `timestamp`
and `data`. The first one is a UNIX epoch timestamp represented as a number (either integer or floating-point).
The latter can be basically anything. Sample record may look as follows:
```json
{
    "data": {
        "price": 173.03457395327663
    },
    "timestamp": 1571747588
}
```

All endpoints require and support only HTTP Basic authentication. Only one type of credentials
is supported at the moment: (`--ro-account`) gives read-only access to
the feeds.


### `ws://<service-location>/price/<feed-name>/socket`

Opens a new socket subscription to a feed. Each new subscriber will immediately receive the last record
from the feed, and will be promptly sent any new records posted by producer(s). Subscribers
can assume that timestamps of records received over the WebSocket will always increase.

This is a receive-only WebSocket. Any messages sent by consumers to the service will be ignored.

