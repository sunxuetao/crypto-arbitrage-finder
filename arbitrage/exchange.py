import time
import urllib.request
import urllib.error
import urllib.parse
import logging
import sys
import config
from fiatconverter import FiatConverter
from utils import log_exception
import traceback
import threading

class Exchange_V2(object):
    def __init__(self, exchange):
        self.name = exchange.id
        self.exchange = exchange
        # self.pair_code = pair_code
        self.depth_updated = 0
        self.update_rate = 1
        self.fc = FiatConverter()
        self.fc.update()
        self.is_terminated = False
        self.request_timeout = 5 #5s

    def get_ex_id(self):
        return self.exchange.id

    def terminate(self):
        self.is_terminated = True

    def get_depth(self):
        timediff = time.time() - self.depth_updated
        # logging.warn('Market: %s order book1:(%s>%s)', self.name, timediff, self.depth_updated)
        if timediff > self.update_rate:
            # print('should update...')
            self.ask_update_depth()
        

        timediff = time.time() - self.depth_updated
        # logging.warn('Market: %s order book2:(%s>%s)', self.name, timediff, self.depth_updated)

        if timediff > config.market_expiration_time:
            logging.warn('Market: %s order book is expired(%s>%s)', self.name, timediff, config.market_expiration_time)
            self.depth = {'asks': [[0, 0]], 'bids': [[0, 0]]}
        return self.depth

    def convert_to_cny(self):
        if self.currency == "CNY":
            return
        for direction in ("asks", "bids"):
            for order in self.depth[direction]:
                order["price"] = self.fc.convert(order["price"], self.currency, "CNY")

    def subscribe_depth(self):
        if config.SUPPORT_ZMQ:
            t = threading.Thread(target = self.subscribe_zmq_depth)
            t.start()  
        elif config.SUPPORT_WEBSOCKET:
            t = threading.Thread(target = self.subscribe_websocket_depth)
            t.start()
        else:
            pass

    def subscribe_zmq_depth(self):
        import lib.push as push

        push_s = push.Push(config.ZMQ_PORT)
        push_s.msg_server()

    def subscribe_websocket_depth(self):
        import json
        from socketIO_client import SocketIO

        def on_message(data):
            data = data.decode('utf8')
            if data[0] != '2':
                return

            data = json.loads(data[1:])
            depth = data[1]

            logging.debug("depth coming: %s", depth['market'])
            self.depth_updated = int(depth['timestamp']/1000)
            self.depth = self.format_depth(depth)
        
        def on_connect():
            logging.info('[Connected]')

            socketIO.emit('land', {'app': 'haobtcnotify', 'events':[self.event]});

        with SocketIO(config.WEBSOCKET_HOST, port=config.WEBSOCKET_PORT) as socketIO:

            socketIO.on('connect', on_connect)
            socketIO.on('message', on_message)

            socketIO.wait()
    
    def ask_update_depth(self):
        try:
            self.update_depth()
            # self.convert_to_usd()
            self.depth_updated = time.time()
        except Exception as e:
            logging.error("Can't update market: %s - %s" % (self.name, str(e)))
            log_exception(logging.DEBUG)
            # traceback.print_exc()

    def get_ticker(self):
        depth = self.get_depth()
        res = {'ask': 0, 'bid': 0}
        if len(depth['asks']) > 0 and len(depth["bids"]) > 0:
            res = {'ask': depth['asks'][0], 'bid': depth['bids'][0]}
        return res

    def sort_and_format_v2(self, l):
        r = []
        r.append({'price': l[0], 'amount': float(l[1])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format_v2(depth['bids'])
        asks = self.sort_and_format_v2(depth['asks'])
        return {'asks': asks, 'bids': bids}

    ## Abstract methods
    def update_depth(self):
        self.depth = self.exchange.fetch_order_book(self.pair_code, 25)
        # self.depth = self.format_depth(raw_depth)
        print(self.exchange.id, self.pair_code, '--update depth: ', self.depth)
        return self.depth

    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass
