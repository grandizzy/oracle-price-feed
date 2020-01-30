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

import tornado
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import logging
import time
import threading

from pymaker import Wad
from oracle_price_feed.auth import AuthenticationMixin, auth_required
from oracle_price_feed.config import Config

from tornado import concurrent
from web3 import Web3

class FeedSocketHandler(tornado.websocket.WebSocketHandler, AuthenticationMixin):

    def initialize(self, config: Config, web3: Web3):
        self.config = config
        self.web3 = web3
        self.feed_name = f"{config.token}-USD_ORACLE"
        self.price = None
        self.executor = concurrent.futures.ThreadPoolExecutor(1)

        def calculate_price():
            while True:
                try:
                    logging.debug("Fetching prices from chain")

                    slot = self.web3.eth.getStorageAt(config.oracle_address.address, 3)
                    self.price = float(Wad(Web3.toInt(hexstr=f'0x{Web3.toHex(slot)[34:].lstrip("0")}')))

                    logging.info(f"price read from chain {self.price}, sleep for {config.fetch_time} seconds")
                    time.sleep(config.fetch_time)
                except Exception as ex:
                    logging.error(ex)
                    logging.error("Cannot calculate price, sleep for 5 seconds")
                    self.price = None
                    time.sleep(5)

        self.executor.submit(calculate_price)


    @tornado.web.asynchronous
    @auth_required(write=False)
    def get(self, *args, **kwargs):
        return super(FeedSocketHandler, self).get(*args, **kwargs)

    @gen.coroutine
    def open(self):
        self.id = Counter.next()
        self.set_nodelay(True)

        self.callback = tornado.ioloop.PeriodicCallback(self.send_price, self.config.report_time * 1000)
        self.callback.start()

    def send_price(self):
        logging.info(f"{self._prefix()} Sending price'")

        self.write_message({
            "timestamp": int(time.time()),
            "data": {
                "price": self.price
            }
        })

    def on_message(self, message):
        logging.warning(f"{self._prefix()} Unexpected message '{message}' received, ignoring")

    def on_close(self):
        logging.info(f"{self._prefix()} Socket with {self.request.remote_ip} closed")
        self.callback.stop()

    def _prefix(self):
        return f"[{self.feed_name}] [WebSocket #{self.id:06d}]"


class Counter:
    lock = threading.Lock()
    value = 0

    @classmethod
    def next(cls):
        with cls.lock:
            cls.value += 1
            return cls.value
