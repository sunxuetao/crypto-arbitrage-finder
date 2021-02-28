import pandas as pd
import numpy as np
import ccxt
from pandas import json_normalize

tickers = {}
# ex_kr = ccxt.kraken()
# ex_kr.timeout = 5000
# t1 = ex_kr.fetch_tickers([
#     "ETH/USDT",
#     "BTC/USDT",
#     "LTC/USDT",
#     "EOS/USDT",
#     "BCH/USDT"
# ])
#
# tickers[ex_kr.id] = t1
#
# bt_kr = ccxt.bittrex()
# bt_kr.timeout = 5000
# t2 = bt_kr.fetch_tickers([
#     "ETH/USDT",
#     "BTC/USDT",
#     "LTC/USDT",
#     "EOS/USDT",
#     "BCH/USDT"
# ])
# tickers[bt_kr.id] = t2
#
#
# ex_li = ccxt.liquid()
# ex_li.timeout = 5000
# t3 = ex_li.fetch_tickers([
#     "ETH/USDT",
#     "BTC/USDT",
#     "LTC/USDT",
#     "EOS/USDT",
#     "BCH/USDT"
# ])
# tickers[ex_li.id] = t3

tickers = {'kraken': {
    'BCH/USDT': {'symbol': 'BCH/USDT', 'timestamp': 1614402846493, 'datetime': '2021-02-27T05:14:06.493Z',
                 'high': 507.43, 'low': 457.54, 'bid': 494.08, 'bidVolume': None, 'ask': 495.01, 'askVolume': None,
                 'vwap': 485.239395, 'open': 487.18, 'close': 490.69, 'last': 490.69, 'previousClose': None,
                 'change': None, 'percentage': None, 'average': None, 'baseVolume': 182.68721231,
                 'quoteVolume': 88647.03237554096,
                 'info': {'a': ['495.010000', '5', '5.000'], 'b': ['494.080000', '4', '4.000'],
                          'c': ['490.690000', '2.10861886'], 'v': ['40.96555009', '182.68721231'],
                          'p': ['488.528645', '485.239395'], 't': [47, 277], 'l': ['486.020000', '457.540000'],
                          'h': ['499.190000', '507.430000'], 'o': '487.180000'}},
    'EOS/USDT': {'symbol': 'EOS/USDT', 'timestamp': 1614402846493, 'datetime': '2021-02-27T05:14:06.493Z',
                 'high': 3.757, 'low': 3.4263, 'bid': 3.6963, 'bidVolume': None, 'ask': 3.7015, 'askVolume': None,
                 'vwap': 3.625613, 'open': 3.6026, 'close': 3.6615, 'last': 3.6615, 'previousClose': None,
                 'change': None, 'percentage': None, 'average': None, 'baseVolume': 37844.49712009,
                 'quoteVolume': 137209.50073706088,
                 'info': {'a': ['3.701500', '148', '148.000'], 'b': ['3.696300', '10', '10.000'],
                          'c': ['3.661500', '3.19991000'], 'v': ['1473.97971622', '37844.49712009'],
                          'p': ['3.640840', '3.625613'], 't': [28, 191], 'l': ['3.602600', '3.426300'],
                          'h': ['3.735400', '3.757000'], 'o': '3.602600'}},
    'ETH/USDT': {'symbol': 'ETH/USDT', 'timestamp': 1614402846493, 'datetime': '2021-02-27T05:14:06.493Z',
                 'high': 1561.81, 'low': 1401.0, 'bid': 1502.57, 'bidVolume': None, 'ask': 1504.31, 'askVolume': None,
                 'vwap': 1469.31698, 'open': 1444.41, 'close': 1503.71, 'last': 1503.71, 'previousClose': None,
                 'change': None, 'percentage': None, 'average': None, 'baseVolume': 9620.26306132,
                 'quoteVolume': 14135215.868064258,
                 'info': {'a': ['1504.31000', '12', '12.000'], 'b': ['1502.57000', '3', '3.000'],
                          'c': ['1503.71000', '4.01221452'], 'v': ['550.17310673', '9620.26306132'],
                          'p': ['1489.74684', '1469.31698'], 't': [524, 4319], 'l': ['1444.41000', '1401.00000'],
                          'h': ['1515.00000', '1561.81000'], 'o': '1444.41000'}},
    'LTC/USDT': {'symbol': 'LTC/USDT', 'timestamp': 1614402846493, 'datetime': '2021-02-27T05:14:06.493Z',
                 'high': 180.69139, 'low': 163.0, 'bid': 175.81019, 'bidVolume': None, 'ask': 176.03986,
                 'askVolume': None, 'vwap': 172.642665, 'open': 170.41999, 'close': 176.96569, 'last': 176.96569,
                 'previousClose': None, 'change': None, 'percentage': None, 'average': None,
                 'baseVolume': 4335.74185024, 'quoteVolume': 748534.0277774644,
                 'info': {'a': ['176.039860', '5', '5.000'], 'b': ['175.810190', '2', '2.000'],
                          'c': ['176.965690', '0.13001900'], 'v': ['173.60640459', '4335.74185024'],
                          'p': ['177.670930', '172.642665'], 't': [82, 856], 'l': ['170.419990', '163.000000'],
                          'h': ['179.879870', '180.691390'], 'o': '170.419990'}},
    'BTC/USDT': {'symbol': 'BTC/USDT', 'timestamp': 1614402846493, 'datetime': '2021-02-27T05:14:06.493Z',
                 'high': 48420.4, 'low': 44168.0, 'bid': 47647.0, 'bidVolume': None, 'ask': 47662.0, 'askVolume': None,
                 'vwap': 46406.53961, 'open': 46296.9, 'close': 47717.2, 'last': 47717.2, 'previousClose': None,
                 'change': None, 'percentage': None, 'average': None, 'baseVolume': 293.94338838,
                 'quoteVolume': 13640895.495954083,
                 'info': {'a': ['47662.00000', '1', '1.000'], 'b': ['47647.00000', '1', '1.000'],
                          'c': ['47717.20000', '0.02406214'], 'v': ['25.15208331', '293.94338838'],
                          'p': ['47397.15229', '46406.53961'], 't': [710, 6899], 'l': ['46296.90000', '44168.00000'],
                          'h': ['48017.40000', '48420.40000'], 'o': '46296.90000'}}}, 'bittrex': {
    'BCH/USDT': {'symbol': 'BCH/USDT', 'timestamp': None, 'datetime': None, 'high': None, 'low': None,
                 'bid': 494.23725369, 'bidVolume': None, 'ask': 494.91167206, 'askVolume': None, 'vwap': None,
                 'open': None, 'close': 497.90418321, 'last': 497.90418321, 'previousClose': None, 'change': None,
                 'percentage': None, 'average': None, 'baseVolume': None, 'quoteVolume': None,
                 'info': {'symbol': 'BCH-USDT', 'lastTradeRate': '497.90418321', 'bidRate': '494.23725369',
                          'askRate': '494.91167206'}},
    'BTC/USDT': {'symbol': 'BTC/USDT', 'timestamp': None, 'datetime': None, 'high': None, 'low': None,
                 'bid': 47669.63381701, 'bidVolume': None, 'ask': 47675.16717965, 'askVolume': None, 'vwap': None,
                 'open': None, 'close': 47675.16717965, 'last': 47675.16717965, 'previousClose': None, 'change': None,
                 'percentage': None, 'average': None, 'baseVolume': None, 'quoteVolume': None,
                 'info': {'symbol': 'BTC-USDT', 'lastTradeRate': '47675.16717965', 'bidRate': '47669.63381701',
                          'askRate': '47675.16717965'}},
    'EOS/USDT': {'symbol': 'EOS/USDT', 'timestamp': None, 'datetime': None, 'high': None, 'low': None, 'bid': 3.6953293,
                 'bidVolume': None, 'ask': 3.70133195, 'askVolume': None, 'vwap': None, 'open': None,
                 'close': 3.71334155, 'last': 3.71334155, 'previousClose': None, 'change': None, 'percentage': None,
                 'average': None, 'baseVolume': None, 'quoteVolume': None,
                 'info': {'symbol': 'EOS-USDT', 'lastTradeRate': '3.71334155', 'bidRate': '3.69532930',
                          'askRate': '3.70133195'}},
    'ETH/USDT': {'symbol': 'ETH/USDT', 'timestamp': None, 'datetime': None, 'high': None, 'low': None, 'bid': 1503.033,
                 'bidVolume': None, 'ask': 1503.81235669, 'askVolume': None, 'vwap': None, 'open': None,
                 'close': 1504.24303805, 'last': 1504.24303805, 'previousClose': None, 'change': None,
                 'percentage': None, 'average': None, 'baseVolume': None, 'quoteVolume': None,
                 'info': {'symbol': 'ETH-USDT', 'lastTradeRate': '1504.24303805', 'bidRate': '1503.03300000',
                          'askRate': '1503.81235669'}},
    'LTC/USDT': {'symbol': 'LTC/USDT', 'timestamp': None, 'datetime': None, 'high': None, 'low': None, 'bid': 176.0,
                 'bidVolume': None, 'ask': 176.03954516, 'askVolume': None, 'vwap': None, 'open': None, 'close': 176.0,
                 'last': 176.0, 'previousClose': None, 'change': None, 'percentage': None, 'average': None,
                 'baseVolume': None, 'quoteVolume': None,
                 'info': {'symbol': 'LTC-USDT', 'lastTradeRate': '176.00000000', 'bidRate': '176.00000000',
                          'askRate': '176.03954516'}}}, 'liquid': {
    'ETH/USDT': {'symbol': 'ETH/USDT', 'timestamp': 1614402860968, 'datetime': '2021-02-27T05:14:20.968Z',
                 'high': 1567.42, 'low': 1399.99, 'bid': 1498.09, 'bidVolume': None, 'ask': 1508.59, 'askVolume': None,
                 'vwap': None, 'open': 1488.83, 'close': 1508.59, 'last': 1508.59, 'previousClose': None,
                 'change': 19.75999999999999, 'percentage': 1.3272166734952944, 'average': 1498.71,
                 'baseVolume': 138.93590668, 'quoteVolume': None,
                 'info': {'id': '625', 'product_type': 'CurrencyPair', 'code': 'CASH', 'name': None,
                          'market_ask': '1508.59', 'market_bid': '1498.09', 'indicator': None, 'currency': 'USDT',
                          'currency_pair_code': 'ETHUSDT', 'symbol': None, 'btc_minimum_withdraw': None,
                          'fiat_minimum_withdraw': None, 'pusher_channel': 'product_cash_ethusdt_625',
                          'taker_fee': '0.003', 'maker_fee': '0.0', 'low_market_bid': '1399.99',
                          'high_market_ask': '1567.42', 'volume_24h': '138.93590668', 'last_price_24h': '1488.83',
                          'last_traded_price': '1508.59', 'last_traded_quantity': '0.1', 'average_price': '1508.59',
                          'quoted_currency': 'USDT', 'base_currency': 'ETH', 'tick_size': '0.01', 'disabled': False,
                          'margin_enabled': False, 'cfd_enabled': False, 'perpetual_enabled': False,
                          'last_event_timestamp': '1614402859.847978836', 'timestamp': '1614402859.847978836',
                          'multiplier_up': '1.4', 'multiplier_down': '0.6', 'average_time_interval': 300,
                          'progressive_tier_eligible': True}},
    'BTC/USDT': {'symbol': 'BTC/USDT', 'timestamp': 1614402860970, 'datetime': '2021-02-27T05:14:20.970Z',
                 'high': 48500.0, 'low': 44040.24, 'bid': 47656.41, 'bidVolume': None, 'ask': 48051.39,
                 'askVolume': None, 'vwap': None, 'open': 46609.79, 'close': 47736.56, 'last': 47736.56,
                 'previousClose': None, 'change': 1126.7699999999968, 'percentage': 2.417453500648677,
                 'average': 47173.175, 'baseVolume': 11.2340722, 'quoteVolume': None,
                 'info': {'id': '624', 'product_type': 'CurrencyPair', 'code': 'CASH', 'name': None,
                          'market_ask': '48051.39', 'market_bid': '47656.41', 'indicator': None, 'currency': 'USDT',
                          'currency_pair_code': 'BTCUSDT', 'symbol': None, 'btc_minimum_withdraw': None,
                          'fiat_minimum_withdraw': None, 'pusher_channel': 'product_cash_btcusdt_624',
                          'taker_fee': '0.003', 'maker_fee': '0.0', 'low_market_bid': '44040.24',
                          'high_market_ask': '48500.0', 'volume_24h': '11.2340722', 'last_price_24h': '46609.79',
                          'last_traded_price': '47736.56', 'last_traded_quantity': '0.00101993',
                          'average_price': '47736.56', 'quoted_currency': 'USDT', 'base_currency': 'BTC',
                          'tick_size': '0.01', 'disabled': False, 'margin_enabled': False, 'cfd_enabled': False,
                          'perpetual_enabled': False, 'last_event_timestamp': '1614402858.43980207',
                          'timestamp': '1614402858.43980207', 'multiplier_up': '1.4', 'multiplier_down': '0.6',
                          'average_time_interval': 300, 'progressive_tier_eligible': True}}}}

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
df.rename(columns={'level_0': 'exchanger', 'level_1': 'ticker'}, inplace=True)

# group ticker，取得所有交易所相应ticker的最大值及最小值。
# 此方法显示不了交易所名称
# df = df.groupby(['ticker']).agg(
#     min_count=pd.NamedAgg(column='bid', aggfunc='min'),
#     max_count=pd.NamedAgg(column='ask', aggfunc='max')
# ).reset_index(drop=False)

# group ticker，取得所有交易所相应ticker的最大值及最小值，并显示交易所名称
df['max_count'] = df.groupby('ticker')['bid'].transform('max')
df['min_count'] = df.groupby('ticker')['ask'].transform('min')

# 计算最大值-最小值的百分比
df['percentage'] = df.apply(lambda x: ((x['max_count'] - x['min_count']) / x['max_count']) * 100, axis=1)
print(df)

df = df[(df['percentage'] > 0) & ((df['bid'] == df['max_count']) | (df['ask'] == df['min_count']))]
# print(df1)

def function(a, b):
    if a == b:
        return 1
    else:
        return 0


df['sell'] = df.apply(lambda x : function(x['bid'], x['max_count']), axis=1)
df['buy'] = df.apply(lambda x : function(x['ask'], x['min_count']), axis=1)
# df1['sell'] = df[df['bid'] == df['max_count']]
# df1['buy'] = df[df['ask'] == df['min_count']]
print(df)
ls = df.reset_index().to_json(orient='records')
print(ls)


# 遍历ticker, 判断搬砖可能性
# group = df.groupby(['ticker', 'percentage']).groups
# for ticker, percentage in group:
#     if percentage > 0:
#         print(ticker)
#         print(percentage)
