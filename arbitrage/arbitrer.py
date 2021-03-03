# -*- coding: utf-8 -*-

# Copyright (C) 2013, Maxime Biais <maxime@biais.org>
# Copyright (C) 2016, Phil Song <songbohr@gmail.com>
import json

import ccxt
import config
import time
import logging
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, wait
import Postgres_helper

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
        self.tickers = {}
        self.depths = {}
        self.ex_instances = {}
        self.init_markets(config.markets)
        self.init_exchanges(config.exchanges)
        self.init_observers(config.observers)
        self.init_dbconn()
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
                self.ex_instances[exchange_id] = ex
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

    def init_dbconn(self):
        self.dbhelper = Postgres_helper.PostgresHelper()

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

    def arbitrage_opportunity_v2(self, kmarket, df):
        # 1 buy 2 sell
        buy_ex_id = df[df['buy'] == 1]['exchanger'].values[0]
        sell_ex_id = df[df['sell'] == 1]['exchanger'].values[0]
        ex1 = self.ex_instances[buy_ex_id]
        ex2 = self.ex_instances[sell_ex_id]
        # 1 asks, 2 bids
        depth1 = ex1.fetch_depth(kmarket)
        depth2 = ex2.fetch_depth(kmarket)

        logging.debug('depth1', depth1, 'depth2', depth2)
        profit, volume, buyprice, sellprice, weighted_buyprice, weighted_sellprice = \
            self.arbitrage_depth_opportunity_v2(kmarket, depth1['asks'], depth2['bids'])
        if volume == 0 or buyprice == 0:
            return
        perc2 = (weighted_sellprice - weighted_buyprice) / buyprice * 100
        profit_item = {
            'profit': profit,
            'volume': volume,
            'buyprice': buyprice,
            'buy_ex_id': buy_ex_id,
            'sellprice': sellprice,
            'sell_ex_id': sell_ex_id,
            'perc2': perc2,
            'weighted_buyprice': weighted_buyprice,
            'weighted_sellprice': weighted_sellprice,
        }
        ls = json.dumps(profit_item)
        sql = "INSERT INTO profit (profit) VALUES ('"+ls+"')"
        self.dbhelper.insert(sql)
        for observer in self.observers:
            observer.opportunity(
                profit, volume, buyprice, buy_ex_id, sellprice, sell_ex_id, perc2, weighted_buyprice, weighted_sellprice)

    def __get_market_depth_v2(self, ex, depths):
        for market in self.markets:
            setattr(ex, 'pair_code', market)
            if market not in depths:
                depths[market] = {}

            depths[market][ex.get_ex_id()] = ex.get_depth()

    def update_depths_v2(self):
        depths = {}
        futures = []
        for ex in self.ex_instances.values():
            futures.append(self.threadpool.submit(self.__get_market_depth_v2, ex, depths))
        wait(futures, timeout=2)
        print("all depth: ", depths)
        return depths

    def get_all_tickers(self):
        tickers = {}
        for ex in self.ex_instances.values():
            ex_tickers = ex.get_tickers()
            tickers[ex.get_ex_id()] = ex_tickers

        self.tickers = tickers
        return tickers

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

        self.cal_market_arbitrage_v2(self.tickers)

        for observer in self.observers:
            observer.end_opportunity_finder()

    def cal_market_arbitrage_v2(self, tickers):
        # 遍历嵌套字典
        df = pd.DataFrame.from_dict({(i, j): tickers[i][j]
                                     for i in tickers.keys()
                                     for j in tickers[i].keys()},
                                    orient='index')
        # index转列
        df.reset_index(inplace=True)
        # 选取所需要的列
        df = df.loc[:, ['level_0', 'level_1', 'bid', 'ask', 'timestamp', 'datetime']]
        # 修改列名
        df.rename(columns={'level_0': 'exchanger', 'level_1': 'market'}, inplace=True)
        # 去除ccxt 返回的价格为0的数据
        df = df[(df['bid'] > 0.00001) | (df['ask'] > 0.00001)]
        # group ticker，取得所有交易所相应ticker的最大值及最小值，并显示交易所名称
        df['max_count'] = df.groupby('market')['bid'].transform('max')
        df['min_count'] = df.groupby('market')['ask'].transform('min')
        # 计算最大值-最小值的百分比
        try:
            df['percentage'] = df.apply(lambda x: ((x['max_count'] - x['min_count']) / x['max_count']) * 100, axis=1)
        except ZeroDivisionError as e:
            logging.debug('divide zero', df)

        df = df[(df['percentage'] > 0) & ((df['bid'] == df['max_count']) | (df['ask'] == df['min_count']))]

        def function(a, b):
            if a == b:
                return 1
            else:
                return 0

        df['sell'] = df.apply(lambda x: function(x['bid'], x['max_count']), axis=1)
        df['buy'] = df.apply(lambda x: function(x['ask'], x['min_count']), axis=1)
        ls = df.reset_index().to_json(orient='records')
        logging.info(ls)
        # 插入数据库
        sql = "INSERT INTO arbitrage_opportunities (arbitrage_pair) VALUES ('"+ls+"')"
        self.dbhelper.insert(sql)
        for market in list(set(df['market'].values)):
            self.arbitrage_opportunity_v2(market, df[df['market'] == market])

    @staticmethod
    def get_markets_from_ticker(tickers_arr):
            return list(set(tickers_arr[:,1]))

    @staticmethod
    def filter_array_by_market(tickers_arr):
        a = np.asarray(tickers_arr)
        np(a[:, 1])
        mask = np.in1d(a[:, 1], filter)
        return a[mask]

    @staticmethod
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

    def loop_v2(self):
        while True:
            self.tickers = self.get_all_tickers()
            self.tick_v2()
            time.sleep(config.refresh_rate)
            if is_sigint_up:
                # 中断时需要处理的代码
                self.terminate()
                print("Exit")
                break
