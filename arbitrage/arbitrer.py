# -*- coding: utf-8 -*-

# Copyright (C) 2013, Maxime Biais <maxime@biais.org>
# Copyright (C) 2016, Phil Song <songbohr@gmail.com>
import ccxt
import config
import time
import logging
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, wait

from exchange import Exchange_V2


def sigint_handler(signum, frame):
    global is_sigint_up
    is_sigint_up = True
    print('catched interrupt signal!')


is_sigint_up = False


class Arbitrer(object):
    def __init__(self):
        self.markets = []
        self.observers = []
        self.tickers = []
        self.depths = {}
        self.ex_instances = []
        self.init_markets(config.markets)
        self.init_exchanges(config.exchanges)
        self.init_observers(config.observers)
        self.threadpool = ThreadPoolExecutor(max_workers=10)

    def init_exchanges(self, _exchanges):
        logging.debug("_exchanges:%s" % _exchanges)
        self.exchanges = _exchanges
        for exchange_id in _exchanges:
            try:
                exchange_class = getattr(ccxt, exchange_id)
                exchange = exchange_class()
                exchange.timeout = 1000
                ex = Exchange_V2(exchange)
                self.ex_instances.append(ex)
            except (ImportError, AttributeError) as e:
                print("%s exchange name is invalid: Ignored (you should check your config file)" % (exchange_id))
                logging.warn("exception create exchange instance :%s" % e)

    def init_markets(self, _markets):
        logging.debug("_markets:%s" % _markets)
        self.market_names = _markets
        for market_name in _markets:
            try:
                # exec('import public_markets.' + market_name.lower())
                # market = eval('public_markets.' + market_name.lower() + '.' + market_name + '()')
                self.markets.append(market_name)
            except (ImportError, AttributeError) as e:
                print("%s market name is invalid: Ignored (you should check your config file)" % (market_name))
                logging.warn("exception import:%s" % e)
                # traceback.print_exc()

    def init_observers(self, _observers):
        logging.debug("_observers:%s" % _observers)
        self.observer_names = _observers
        for observer_name in _observers:
            try:
                exec('import observers.' + observer_name.lower())
                observer = eval('observers.' + observer_name.lower() + '.' + observer_name + '()')
                self.observers.append(observer)
            except (ImportError, AttributeError) as e:
                print("%s observer name is invalid: Ignored (you should check your config file)" % (observer_name))
                # print(e)

    def get_profit_for(self, mi, mj, asks, bids):
        if asks[mi][0] >= bids[mj][0]:
            return 0, 0, 0, 0

        max_amount_buy = 0
        for i in range(mi + 1):
            max_amount_buy += asks[i][1]

        max_amount_sell = 0
        for j in range(mj + 1):
            max_amount_sell += bids[j][1]

        max_amount = min(max_amount_buy, max_amount_sell, config.max_tx_volume)

        buy_total = 0
        w_buyprice = 0
        for i in range(mi + 1):
            price = asks[i][0]
            amount = min(max_amount, buy_total + asks[i][1]) - buy_total
            if amount <= 0:
                break
            buy_total += amount
            if w_buyprice == 0:
                w_buyprice = price
            else:
                w_buyprice = (w_buyprice * (buy_total - amount) + price * amount) / buy_total

        sell_total = 0
        w_sellprice = 0
        for j in range(mj + 1):
            price = bids[j][0]
            amount = min(max_amount, sell_total + bids[j][1]) - sell_total
            if amount < 0:
                break
            sell_total += amount
            if w_sellprice == 0 or sell_total == 0:
                w_sellprice = price
            else:
                w_sellprice = (w_sellprice * (sell_total - amount) + price * amount) / sell_total
        if abs(sell_total - buy_total) > 0.00001:
            logging.warn("sell_total=%s,buy_total=%s", sell_total, buy_total)

        profit = sell_total * w_sellprice - buy_total * w_buyprice
        return profit, sell_total, w_buyprice, w_sellprice

    def get_max_depth(self, asks, bids):
        i = 0
        if len(bids) != 0 and \
                len(asks) != 0:
            while asks[i][0] \
                    < bids[0][0]:
                if i >= len(asks) - 1:
                    break
                # logging.debug("i:%s,%s/%s,%s/%s", i, kask, self.depths[kask]["asks"][i][0],
                #   kbid, self.depths[kbid]["bids"][0][0])

                i += 1

        j = 0
        if len(asks) != 0 and \
                len(bids) != 0:
            while asks[0][0] \
                    < bids[j][0]:
                if j >= len(bids) - 1:
                    break
                # logging.debug("j:%s,%s/%s,%s/%s", j, kask, self.depths[kask]["asks"][0][0],
                #     kbid, self.depths[kbid]["bids"][j][0])

                j += 1

        return i, j

    def arbitrage_depth_opportunity_v2(self, kmarket, asks, bids):
        maxi, maxj = self.get_max_depth(asks, bids)
        best_profit = 0
        best_i, best_j = (0, 0)
        best_w_buyprice, best_w_sellprice = (0, 0)
        best_volume = 0
        for i in range(maxi + 1):
            for j in range(maxj + 1):
                profit, volume, w_buyprice, w_sellprice = self.get_profit_for(i, j, asks, bids)
                if profit >= 0 and profit >= best_profit:
                    best_profit = profit
                    best_volume = volume
                    best_i, best_j = (i, j)
                    best_w_buyprice, best_w_sellprice = (
                        w_buyprice, w_sellprice)
        return best_profit, best_volume, asks[best_i][0], bids[best_j][0], best_w_buyprice, best_w_sellprice

    def arbitrage_opportunity_v2(self, kmarket, ex1_id, asks, ex2_id, bids):
        perc = (bids - asks) / bids * 100
        for observer in self.observers:
            observer.opportunity(0, 0, asks, ex1_id[0], bids, ex2_id[0], perc, 0, 0)


        profit, volume, buyprice, sellprice, weighted_buyprice, weighted_sellprice = \
            self.arbitrage_depth_opportunity_v2(kmarket, asks, bids)
        if volume == 0 or buyprice == 0:
            return
        perc2 = (weighted_sellprice - weighted_buyprice) / buyprice * 100
        for observer in self.observers:
            observer.opportunity(
                profit, volume, buyprice, ex1_id, sellprice, ex2_id, perc2, weighted_buyprice, weighted_sellprice)

    def __get_market_depth_v2(self, ex, depths):
        for market in self.markets:
            setattr(ex, 'pair_code', market)
            if market not in depths:
                depths[market] = {}

            depths[market][ex.get_ex_id()] = ex.get_depth()
        print('__get market depth v2:', depths)

    def update_depths_v2(self):
        depths = {}
        futures = []
        for ex in self.ex_instances:
            futures.append(self.threadpool.submit(self.__get_market_depth_v2, ex, depths))
        wait(futures, timeout=2)
        print("all depth: ", depths)
        return depths

    def get_all_tickers(self):
        tickers = {}
        for ex in self.ex_instances:
            ex_tickers = ex.get_tickers()
            tickers[ex.get_ex_id()] = ex_tickers

        self.tickers = self.convert_tickers_to_arr(tickers)
        return self.tickers

    def replay_history(self, directory):
        import os
        import json
        files = os.listdir(directory)
        files.sort()
        for f in files:
            depths = json.load(open(directory + '/' + f, 'r'))
            self.depths = {}
            for market in self.market_names:
                if market in depths:
                    self.depths[market] = depths[market]
            self.tick()

    def tick_v2(self):
        for observer in self.observers:
            observer.begin_opportunity_finder(self.depths)

        for kmarket in self.get_markets_from_ticker(self.tickers):
            arr = self.filter_array_by_market(kmarket, self.tickers)
            self.cal_market_arbitrage(kmarket, arr)

        for observer in self.observers:
            observer.end_opportunity_finder()


    def cal_market_arbitrage(self, kmarket, arr_2):
        # arr columns [exchange, market, 'bid', 'ask', 'timestamp', 'datetime']
        for ex1_id in arr_2:
            for ex2_id in arr_2:
                if ex1_id[0] == ex2_id[0]:  # same exchange
                    continue
                if ex1_id[3] and ex2_id[2]:
                    if (float(ex1_id[3]) > 0) \
                            and (float(ex2_id[2]) > 0) \
                            and (float(ex1_id[3]) < float(ex2_id[2])):
                        print('1 buy 2 sell', 'btc/usdt', ex1_id[0], ex1_id[3], ex2_id[0], ex2_id[2])
                        #1 buy 2 sell
                        self.arbitrage_opportunity_v2(kmarket, ex1_id, ex1_id[3], ex2_id, ex2_id[2])
                    if (float(ex1_id[2]) > 0) \
                            and (float(ex2_id[3]) > 0) \
                            and (float(ex1_id[2]) > float(ex2_id[3])):
                        #1 sell 2 buy
                        print('1 sell 2 buy','btc/usdt', ex1_id[0], ex2_id[3], ex2_id[0], ex1_id[2])
                        self.arbitrage_opportunity_v2(kmarket, ex1_id, ex2_id[3], ex2_id, ex1_id[2])



    def get_markets_from_ticker(tickers_arr):
        return list(set(tickers_arr[:,1]))


    def filter_array_by_market(kmarket, tickers_arr):
        a = np.asarray(tickers_arr)
        np(a[:,1])
        mask = np.in1d(a[:, 1], filter)
        return a[mask]

    def convert_tickers_to_arr(tickers):
        tickers_arr = []
        for key in tickers:
            t = tickers[key]
            if isinstance(t, dict):
                for k1 in t:
                    t_info = t[k1]
                    if isinstance(t, dict):
                        arr = [key, k1, t_info['bid'], t_info['ask'], t_info['timestamp'], t_info['datetime']]
                        tickers_arr.append(arr)
        print(tickers_arr)
        return tickers_arr

    def terminate(self):
        for observer in self.observers:
            observer.terminate()

        for market in self.markets:
            market.terminate()

    def loop(self):
        #
        # signal.signal(signal.SIGHUP, sigint_handler)

        # 以下那句在windows python2.4不通过,但在freebsd下通过
        # signal.signal(signal.SIGHUP, sigint_handler)

        # signal.signal(signal.SIGTERM, sigint_handler)

        while True:
            self.depths = self.update_depths()
            print('total depths', self.depths)
            self.tickers()
            self.tick()
            time.sleep(config.refresh_rate)

            if is_sigint_up:
                # 中断时需要处理的代码
                self.terminate()
                print("Exit")
                break

    def loop_v2(self):
        #
        # signal.signal(signal.SIGHUP, sigint_handler)
        # 以下那句在windows python2.4不通过,但在freebsd下通过
        # signal.signal(signal.SIGHUP, sigint_handler)
        # signal.signal(signal.SIGTERM, sigint_handler)

        while True:
            # TODO read markets config
            self.tickers = self.get_all_tickers()
            # self.depths = self.update_depths_v2()
            # print('total depths', self.depths)
            self.tick_v2()
            time.sleep(config.refresh_rate)

            if is_sigint_up:
                # 中断时需要处理的代码
                self.terminate()
                print("Exit")
                break
