# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2020 grandizzy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging
import sys
import tornado
from oracle_price_feed.feed import FeedSocketHandler
from oracle_price_feed.config import Config
from web3 import Web3, HTTPProvider

from pymaker import Address

class OraclePriceFeed:
    """Oracle Price Feed server."""

    logger = logging.getLogger()

    def __init__(self, args: list, **kwargs):
        parser = argparse.ArgumentParser(prog='oracle-price-feed')

        parser.add_argument("--rpc-host", type=str, default="localhost",
                            help="JSON-RPC host (default: `localhost')")

        parser.add_argument("--rpc-port", type=int, default=8545,
                            help="JSON-RPC port (default: `8545')")

        parser.add_argument("--rpc-timeout", type=int, default=10,
                            help="JSON-RPC timeout (in seconds, default: 10)")

        parser.add_argument("--http-address", type=str, default='',
                            help="Address of the Oracle Price Feed")

        parser.add_argument("--http-port", type=int, default=7777,
                            help="Port of the Oracle Price Feed")

        parser.add_argument("--token", type=str, default='ETH',
                            help="Token symbol")

        parser.add_argument("--report-time", type=int, default=10,
                            help="Time interval to report price")

        parser.add_argument("--fetch-time", type=int, default=30,
                            help="Time interval to get price from Oracle")

        parser.add_argument("--ro-account", type=str,
                            help="Credentials of the read-only user (format: username:password)")

        parser.add_argument("--rw-account", type=str,
                            help="Credentials of the read-write user (format: username:password)")

        self.arguments = parser.parse_args(args)

        if self.arguments.rpc_host.startswith("https"):
            endpoint_uri = f"{self.arguments.rpc_host}"
        else:
            endpoint_uri = f"http://{self.arguments.rpc_host}:{self.arguments.rpc_port}"

        self.web3 = kwargs['web3'] if 'web3' in kwargs else Web3(HTTPProvider(endpoint_uri=endpoint_uri,
                                                                              request_kwargs={"timeout": self.arguments.rpc_timeout}))

        self.web3.eth.defaultAccount = "0x0000000000000000000000000000000000000000"

        if self.arguments.token == 'ETH':
            self.oracle_address = Address('0x81FE72B5A8d1A857d176C3E7d5Bd2679A9B85763')
        elif self.arguments.token == 'BAT':
            self.oracle_address = Address('0xB4eb54AF9Cc7882DF0121d26c5b97E802915ABe6')
        else:
            raise Exception(f'no Oracle for {self.arguments.token}')

        self.config = Config(
            oracle_address=self.oracle_address,
            token=self.arguments.token,
            report_time=self.arguments.report_time,
            fetch_time=self.arguments.fetch_time,
            ro_account=self.arguments.ro_account,
            rw_account=self.arguments.rw_account)

        application = tornado.web.Application([
            (f"/price/{self.arguments.token}-USD_ORACLE/socket", FeedSocketHandler,
                dict(config=self.config, web3=self.web3))
        ])
        application.listen(port=self.arguments.http_port,address=self.arguments.http_address)
        logging.info(f"Price feed for {self.arguments.token}-USD_ORACLE started "
                     f"on port {self.arguments.http_port}, waiting for websocket clients")
        tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=logging.INFO)
    OraclePriceFeed(sys.argv[1:]).main()
