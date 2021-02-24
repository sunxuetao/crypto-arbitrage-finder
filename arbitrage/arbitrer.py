#-*- coding: utf-8 -*-

# Copyright (C) 2013, Maxime Biais <maxime@biais.org>
# Copyright (C) 2016, Phil Song <songbohr@gmail.com>
import ccxt

import config
import time
import logging
from concurrent.futures import ThreadPoolExecutor, wait

from exchange import Exchange_V2


def sigint_handler(signum, frame):
    global is_sigint_up
    is_sigint_up = True
    print ('catched interrupt signal!')

is_sigint_up = False

class Arbitrer(object):
    def __init__(self):
        self.markets = []
        self.observers = []
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
                observer = eval('observers.' + observer_name.lower() + '.' +
                                observer_name + '()')
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
        if abs(sell_total-buy_total) > 0.00001:
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

    def arbitrage_depth_opportunity(self, asks, bids):
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

    def arbitrage_opportunity(self, kask, ask, kbid, bid):
        perc = (bid[0] - ask[0]) / bid[0] * 100
        profit, volume, buyprice, sellprice, weighted_buyprice, \
            weighted_sellprice = self.arbitrage_depth_opportunity(kask, kbid)
        if volume == 0 or buyprice == 0:
            return
        perc2 = (weighted_sellprice-weighted_buyprice)/buyprice * 100
        for observer in self.observers:
            observer.opportunity(
                profit, volume, buyprice, kask, sellprice, kbid, perc2, weighted_buyprice, weighted_sellprice)


    def arbitrage_opportunity_v2(self, kmarket, ex1_id, asks, ex2_id, bids):
        perc = (bids[0][0] - asks[0][0]) / bids[0][0] * 100
        profit, volume, buyprice, sellprice, weighted_buyprice, weighted_sellprice = \
            self.arbitrage_depth_opportunity_v2(kmarket, asks, bids)
        if volume == 0 or buyprice == 0:
            return
        perc2 = (weighted_sellprice-weighted_buyprice)/buyprice * 100
        for observer in self.observers:
            observer.opportunity(
                profit, volume, buyprice, ex1_id, sellprice, ex2_id, perc2, weighted_buyprice, weighted_sellprice)

    def __get_market_depth(self, market, depths):
        depths[market.name] = market.get_depth()

    def update_depths(self):
        depths = {}
        futures = []
        for market in self.markets:
            futures.append(self.threadpool.submit(self.__get_market_depth,
                                                  market, depths))
        wait(futures, timeout=20)
        return depths

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
        wait(futures, timeout=20)
        print("all depth: ", depths)
        return depths

    def tickers(self):
        for market in self.markets:
            logging.verbose("ticker: " + market.name + " - " + str(market.get_ticker()))

    def tickers_v2(self):
        for ex in self.ex_instances:
            logging.verbose("ticker: " + ex.get_ex_id() + " - " + str(ex.get_ticker()))

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

    def tick(self):
        for observer in self.observers:
            observer.begin_opportunity_finder(self.depths)

        for kmarket1 in self.depths:
            for kmarket2 in self.depths:
                if kmarket1 == kmarket2:  # same market
                    continue
                market1 = self.depths[kmarket1]
                market2 = self.depths[kmarket2]
                if market1["asks"] and market2["bids"] \
                   and len(market1["asks"]) > 0 and len(market2["bids"]) > 0:
                    if float(market1["asks"][0]['price']) \
                       < float(market2["bids"][0]['price']):
                        self.arbitrage_opportunity(kmarket1, market1["asks"][0], kmarket2, market2["bids"][0])

        for observer in self.observers:
            observer.end_opportunity_finder()

    def tick_v2(self):
        for observer in self.observers:
            observer.begin_opportunity_finder(self.depths)

        depths ={'ETH/USDT': {
            'bittrex': {'bids': [[1700.462, 0.5], [1617.4496722, 1.85321655], [1617.23166791, 1.85327294], [1616.84604878, 3.08869424], [1616.566, 2.2473], [1616.56539884, 1.93091783], [1616.436, 0.6088], [1616.26398853, 3.08878823], [1615.69800007, 1.1], [1615.54751211, 1.223], [1612.81061601, 0.06304947], [1612.81061599, 0.931], [1612.81061592, 0.6200356], [1612.6245432, 3.48], [1612.14265197, 0.01791436], [1611.82152448, 12.163], [1611.0, 0.0468078], [1610.78219028, 2.1], [1610.08668138, 0.06073958], [1609.78724468, 2.1], [1609.693554, 0.06212363], [1607.3948913, 0.01334966], [1606.97, 0.1], [1606.60039775, 0.01845442], [1605.53109934, 0.01866506]], 'asks': [[1520.90666657, 5.0], [1619.16433247, 1.85321655], [1619.2987315, 1.85307935], [1619.60044352, 3.08869424], [1621.38635487, 7.86604329], [1621.38635488, 6.5301096], [1621.38635489, 1.3290343], [1625.40275533, 16.866], [1625.40275534, 2.1], [1626.799779, 0.06217127], [1627.40153132, 12.49778264], [1629.75127839, 8.56850286], [1633.59206114, 0.61746688], [1633.59206115, 9.78556238], [1633.89861294, 94.117], [1640.6693231, 2.46849658], [1640.66932311, 46.491], [1645.78623084, 12.62497766], [1651.9187131, 0.0182631], [1652.52741335, 23.676], [1659.32071127, 1.68680809], [1661.20850976, 0.29336917], [1661.73306182, 11.589], [1669.22401326, 0.01807376], [1670.0, 2.0]], 'timestamp': None, 'datetime': None, 'nonce': 306758},
            'kraken': {'bids': [[1617.46, 0.188, 1614179738], [1617.34, 5.0, 1614179738], [1617.33, 2.8, 1614179738], [1617.26, 1.759, 1614179738], [1617.25, 7.3, 1614179738], [1617.24, 2.8, 1614179737], [1617.17, 2.617, 1614179737], [1617.16, 1.605, 1614179738], [1617.15, 3.335, 1614179738], [1616.92, 2.04, 1614179737], [1616.69, 0.644, 1614179736], [1616.54, 1.287, 1614179736], [1616.31, 0.846, 1614179738], [1616.3, 4.773, 1614179737], [1616.25, 2.895, 1614179736], [1616.22, 1.373, 1614179737], [1616.14, 2.03, 1614179737], [1616.03, 6.826, 1614179737], [1615.93, 1.932, 1614179735], [1615.22, 3.09, 1614179736], [1615.14, 4.818, 1614179732], [1614.35, 0.009, 1614179642], [1614.21, 0.354, 1614179738], [1614.19, 9.64, 1614179736], [1612.89, 2.1, 1614179731]], 'asks': [[1619.93, 18.453, 1614179737], [1619.94, 3.734, 1614179737], [1620.07, 3.463, 1614179732], [1620.14, 1.759, 1614179738], [1620.15, 3.399, 1614179737], [1620.22, 3.088, 1614179737], [1620.24, 3.281, 1614179729], [1620.33, 1.837, 1614179678], [1620.57, 4.819, 1614179738], [1620.7, 0.644, 1614179738], [1620.99, 9.638, 1614179738], [1621.04, 1.287, 1614179738], [1621.15, 3.087, 1614179729], [1621.17, 6.306, 1614179738], [1621.18, 2.895, 1614179738], [1621.44, 0.092, 1614179663], [1621.7, 7.3, 1614179730], [1621.99, 5.135, 1614179733], [1622.05, 6.18, 1614179736], [1622.27, 4.254, 1614179737], [1623.46, 1.557, 1614179725], [1623.89, 6.8, 1614179735], [1626.48, 0.063, 1614179737], [1627.03, 0.591, 1614179526], [1629.39, 34.34, 1614179736]], 'timestamp': None, 'datetime': None, 'nonce': None},
            'bleutrade': {'bids': [[1575.03, 0.00024], [1560.1, 0.00025], [1538.23, 0.00025], [1510.0, 0.00025], [1300.0, 1.32323], [1270.0, 0.99986], [916.0, 1.0254], [888.23, 0.00043], [650.0, 1.0], [600.0, 1.88568], [550.0, 1.0], [500.0, 2.0], [400.0, 1.0], [360.14, 0.22], [333.0, 0.02288], [259.01, 4e-05], [258.82, 0.19982], [258.71, 0.15838], [258.61, 0.10969], [258.41, 0.17517], [258.22, 0.18351], [258.11, 0.19133], [257.97, 0.18321], [257.74, 0.19777], [257.51, 0.17242]], 'asks': [[1754.18, 0.01191], [1770.96, 0.01191], [1796.15, 0.01191], [1829.72, 0.01191], [1900.0, 0.40253], [2010.62, 0.93193], [2011.0, 0.003], [2022.0, 0.003], [2033.0, 0.003], [2055.0, 0.003], [2066.0, 0.003], [2077.7, 0.003], [2088.0, 0.003], [2099.0, 0.003], [2111.0, 0.003], [2122.0, 0.003], [2144.0, 0.003], [2166.0, 0.003], [2177.0, 0.003], [2200.0, 0.34318], [2222.0, 0.49711], [2310.0, 1.0], [2510.0, 1.0], [2555.0, 0.001], [2777.0, 0.001]], 'timestamp': None, 'datetime': None, 'nonce': None},
            'liquid': {'bids': [[1618.61, 1.62264129], [1618.19, 0.37875], [1617.45, 0.35625], [1614.46, 4.12], [1614.33, 3.92], [1613.65, 1.18397079], [1613.56, 4.04], [1612.12, 0.6], [1611.75, 0.018819], [1610.37, 2.2], [1610.19, 1.6244], [1608.61, 4.6118959], [1606.61, 22.53286376], [1604.08, 4.58001111], [1603.94, 4.43003332], [1603.81, 7.3], [1602.06, 0.257], [1598.31, 0.1], [1597.78, 105.0], [1597.77, 153.34], [1595.92, 0.0115687]], 'asks': [[1636.35, 0.36], [1637.16, 0.0115687], [1643.5, 0.01], [1646.97, 4.2], [1647.25, 0.6], [1647.68, 3.76], [1649.02, 6.133], [1650.56, 15.084], [1652.33, 0.108], [1655.38, 0.2556], [1657.77, 0.0115687], [1658.1, 4.58001111], [1658.15, 4.43003332], [1658.28, 135.0], [1658.29, 153.34], [1659.0, 0.1], [1665.17, 7.14202222], [1666.6, 6.91206666], [1667.07, 76.503], [1678.39, 0.0115687], [1683.91, 43.684]], 'timestamp': None, 'datetime': None, 'nonce': None}},
            'BTC/USDT': {'bittrex': {'bids': [[1617.462, 0.5], [1617.4496722, 1.85321655], [1617.23166791, 1.85327294], [1616.84604878, 3.08869424], [1616.566, 2.2473], [1616.56539884, 1.93091783], [1616.436, 0.6088], [1616.26398853, 3.08878823], [1615.69800007, 1.1], [1615.54751211, 1.223], [1612.81061601, 0.06304947], [1612.81061599, 0.931], [1612.81061592, 0.6200356], [1612.6245432, 3.48], [1612.14265197, 0.01791436], [1611.82152448, 12.163], [1611.0, 0.0468078], [1610.78219028, 2.1], [1610.08668138, 0.06073958], [1609.78724468, 2.1], [1609.693554, 0.06212363], [1607.3948913, 0.01334966], [1606.97, 0.1], [1606.60039775, 0.01845442], [1605.53109934, 0.01866506]], 'asks': [[1618.90666657, 5.0], [1619.16433247, 1.85321655], [1619.2987315, 1.85307935], [1619.60044352, 3.08869424], [1621.38635487, 7.86604329], [1621.38635488, 6.5301096], [1621.38635489, 1.3290343], [1625.40275533, 16.866], [1625.40275534, 2.1], [1626.799779, 0.06217127], [1627.40153132, 12.49778264], [1629.75127839, 8.56850286], [1633.59206114, 0.61746688], [1633.59206115, 9.78556238], [1633.89861294, 94.117], [1640.6693231, 2.46849658], [1640.66932311, 46.491], [1645.78623084, 12.62497766], [1651.9187131, 0.0182631], [1652.52741335, 23.676], [1659.32071127, 1.68680809], [1661.20850976, 0.29336917], [1661.73306182, 11.589], [1669.22401326, 0.01807376], [1670.0, 2.0]], 'timestamp': None, 'datetime': None, 'nonce': 306758},
                         'kraken': {'bids': [[1500.46, 0.188, 1614179738], [1617.34, 5.0, 1614179738], [1617.33, 2.8, 1614179738], [1617.26, 1.759, 1614179738], [1617.25, 7.3, 1614179738], [1617.24, 2.8, 1614179737], [1617.17, 2.617, 1614179737], [1617.16, 1.605, 1614179738], [1617.15, 3.335, 1614179738], [1616.92, 2.04, 1614179737], [1616.69, 0.644, 1614179736], [1616.54, 1.287, 1614179736], [1616.31, 0.846, 1614179738], [1616.3, 4.773, 1614179737], [1616.25, 2.895, 1614179736], [1616.22, 1.373, 1614179737], [1616.14, 2.03, 1614179737], [1616.03, 6.826, 1614179737], [1615.93, 1.932, 1614179735], [1615.22, 3.09, 1614179736], [1615.14, 4.818, 1614179732], [1614.35, 0.009, 1614179642], [1614.21, 0.354, 1614179738], [1614.19, 9.64, 1614179736], [1612.89, 2.1, 1614179731]], 'asks': [[1619.93, 18.453, 1614179737], [1619.94, 3.734, 1614179737], [1620.07, 3.463, 1614179732], [1620.14, 1.759, 1614179738], [1620.15, 3.399, 1614179737], [1620.22, 3.088, 1614179737], [1620.24, 3.281, 1614179729], [1620.33, 1.837, 1614179678], [1620.57, 4.819, 1614179738], [1620.7, 0.644, 1614179738], [1620.99, 9.638, 1614179738], [1621.04, 1.287, 1614179738], [1621.15, 3.087, 1614179729], [1621.17, 6.306, 1614179738], [1621.18, 2.895, 1614179738], [1621.44, 0.092, 1614179663], [1621.7, 7.3, 1614179730], [1621.99, 5.135, 1614179733], [1622.05, 6.18, 1614179736], [1622.27, 4.254, 1614179737], [1623.46, 1.557, 1614179725], [1623.89, 6.8, 1614179735], [1626.48, 0.063, 1614179737], [1627.03, 0.591, 1614179526], [1629.39, 34.34, 1614179736]], 'timestamp': None, 'datetime': None, 'nonce': None},
                         'bleutrade': {'bids': [[1575.03, 0.00024], [1560.1, 0.00025], [1538.23, 0.00025], [1510.0, 0.00025], [1300.0, 1.32323], [1270.0, 0.99986], [916.0, 1.0254], [888.23, 0.00043], [650.0, 1.0], [600.0, 1.88568], [550.0, 1.0], [500.0, 2.0], [400.0, 1.0], [360.14, 0.22], [333.0, 0.02288], [259.01, 4e-05], [258.82, 0.19982], [258.71, 0.15838], [258.61, 0.10969], [258.41, 0.17517], [258.22, 0.18351], [258.11, 0.19133], [257.97, 0.18321], [257.74, 0.19777], [257.51, 0.17242]], 'asks': [[1754.18, 0.01191], [1770.96, 0.01191], [1796.15, 0.01191], [1829.72, 0.01191], [1900.0, 0.40253], [2010.62, 0.93193], [2011.0, 0.003], [2022.0, 0.003], [2033.0, 0.003], [2055.0, 0.003], [2066.0, 0.003], [2077.7, 0.003], [2088.0, 0.003], [2099.0, 0.003], [2111.0, 0.003], [2122.0, 0.003], [2144.0, 0.003], [2166.0, 0.003], [2177.0, 0.003], [2200.0, 0.34318], [2222.0, 0.49711], [2310.0, 1.0], [2510.0, 1.0], [2555.0, 0.001], [2777.0, 0.001]], 'timestamp': None, 'datetime': None, 'nonce': None},
                         'liquid': {'bids': [[1618.61, 1.62264129], [1618.19, 0.37875], [1617.45, 0.35625], [1614.46, 4.12], [1614.33, 3.92], [1613.65, 1.18397079], [1613.56, 4.04], [1612.12, 0.6], [1611.75, 0.018819], [1610.37, 2.2], [1610.19, 1.6244], [1608.61, 4.6118959], [1606.61, 22.53286376], [1604.08, 4.58001111], [1603.94, 4.43003332], [1603.81, 7.3], [1602.06, 0.257], [1598.31, 0.1], [1597.78, 105.0], [1597.77, 153.34], [1595.92, 0.0115687]], 'asks': [[1636.35, 0.36], [1637.16, 0.0115687], [1643.5, 0.01], [1646.97, 4.2], [1647.25, 0.6], [1647.68, 3.76], [1649.02, 6.133], [1650.56, 15.084], [1652.33, 0.108], [1655.38, 0.2556], [1657.77, 0.0115687], [1658.1, 4.58001111], [1658.15, 4.43003332], [1658.28, 135.0], [1658.29, 153.34], [1659.0, 0.1], [1665.17, 7.14202222], [1666.6, 6.91206666], [1667.07, 76.503], [1678.39, 0.0115687], [1683.91, 43.684]], 'timestamp': None, 'datetime': None, 'nonce': None}}}

        for kmarket in self.depths:
            self.cal_market_arbitrage(kmarket, depths[kmarket])

        for observer in self.observers:
            observer.end_opportunity_finder()

    def cal_market_arbitrage(self, kmarket, depths):

        for ex1_id in depths:
            for ex2_id in depths:
                if ex1_id == ex2_id:  # same exchange
                    continue
                depth1 = depths[ex1_id]
                depth2 = depths[ex2_id]
                if depth1["asks"] and depth2["bids"] and len(depth1["asks"]) > 0 and len(depth2["bids"]) > 0:
                    if float(depth1["asks"][0][0]) < float(depth2["bids"][0][0]):
                        #1 buy 2 sell
                        self.arbitrage_opportunity_v2(kmarket, ex1_id, depth1["asks"], ex2_id, depth2["bids"])
                    if float(depth1["bids"][0][0]) > float(depth2["asks"][0][0]):
                        #1 sell 2 buy
                        self.arbitrage_opportunity_v2(kmarket, ex1_id, depth2["asks"], ex2_id, depth1["bids"])

    def terminate(self):
        for observer in self.observers:
            observer.terminate()

        for market in self.markets:
            market.terminate()

    def loop(self):
        #
        # signal.signal(signal.SIGHUP, sigint_handler)

        #以下那句在windows python2.4不通过,但在freebsd下通过
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
                print ("Exit")
                break


    def loop_v2(self):
        #
        # signal.signal(signal.SIGHUP, sigint_handler)
        #以下那句在windows python2.4不通过,但在freebsd下通过
        # signal.signal(signal.SIGHUP, sigint_handler)
        # signal.signal(signal.SIGTERM, sigint_handler)

        while True:
            self.depths = self.update_depths_v2()
            print('total depths', self.depths)
            self.tickers_v2()
            self.tick_v2()
            time.sleep(config.refresh_rate)

            if is_sigint_up:
                # 中断时需要处理的代码
                self.terminate()
                print ("Exit")
                break
