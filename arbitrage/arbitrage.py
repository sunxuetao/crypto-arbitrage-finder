# Copyright (C) 2013, Maxime Biais <maxime@biais.org>
# Copyright (C) 2016, Phil Song <songbohr@gmail.com>

import logging
import argparse
import sys
import glob
import os
import inspect
from logging.handlers import RotatingFileHandler
from arbitrer import Arbitrer
from observers.emailer import send_email
import datetime
import time
import config
import traceback

class ArbitrerCLI:
    def __init__(self):
        self.inject_verbose_info()

    def inject_verbose_info(self):
        logging.VERBOSE = 15
        logging.verbose = lambda x: logging.log(logging.VERBOSE, x)
        logging.addLevelName(logging.VERBOSE, "VERBOSE")

    def exec_command(self, args):
        logging.debug('exec_command:%s' % args)
        if "watch" in args.command:
            self.create_arbitrer(args)
            self.arbitrer.loop_v2()
        if "replay-history" in args.command:
            self.create_arbitrer(args)
            self.arbitrer.replay_history(args.replay_history)
        if "get-balance" in args.command:
            self.get_balance(args)
        if "list-public-markets" in args.command:
            self.list_markets()
        if "get-broker-balance" in args.command:
            self.get_broker_balance(args)

    def list_markets(self):
        logging.debug('list_markets')
        print(config.markets)
        sys.exit(0)

    def get_balance(self, args):
        if not args.markets:
            logging.error("You must use --markets argument to specify markets")
            sys.exit(2)
        pmarkets = args.markets.split(",")
        pmarketsi = []
        for pmarket in pmarkets:
            exec('import private_markets.' + pmarket.lower())
            market = eval('private_markets.' + pmarket.lower()
                          + '.Private' + pmarket + '()')
            pmarketsi.append(market)
        for market in pmarketsi:
            print(market)

    def create_arbitrer(self, args):
        self.arbitrer = Arbitrer()
        if args.observers:
            self.arbitrer.init_observers(args.observers.split(","))
        if args.markets:
            self.arbitrer.init_markets(args.markets.split(","))

    def init_logger(self, args):
        level = logging.INFO
        if args.verbose:
            level = logging.VERBOSE
        if args.debug:
            level = logging.DEBUG
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                            level=level)

        Rthandler = RotatingFileHandler('arbitrage.log', maxBytes=100*1024*1024,backupCount=10)
        Rthandler.setLevel(level)
        formatter = logging.Formatter('%(asctime)-12s [%(levelname)s] %(message)s')  
        Rthandler.setFormatter(formatter)
        logging.getLogger('').addHandler(Rthandler)

        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--debug", help="debug verbose mode",
                            action="store_true")
        parser.add_argument("-v", "--verbose", help="info verbose mode",
                            action="store_true")
        parser.add_argument("-o", "--observers", type=str,
                            help="observers, example: -oLogger,Emailer")
        parser.add_argument("-m", "--markets", type=str,
                            help="markets, example: -mHaobtcCNY,Bitstamp")
        parser.add_argument("-s", "--status", help="status", action="store_true")
        parser.add_argument("command", nargs='*', default="watch",
                            help='verb: "watch|replay-history|get-balance|list-public-markets|get-broker-balance"')
        args = parser.parse_args()
        self.init_logger(args)
        self.exec_command(args)

def main():
    cli = ArbitrerCLI()
    cli.main()

if __name__ == "__main__":
    main()
