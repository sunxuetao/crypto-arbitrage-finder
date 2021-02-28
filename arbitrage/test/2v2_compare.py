
arr_2 = [
    ['kraken', 'BTC/USDT', 50647.0, 50662.0, 1614402846493,'2021-02-27T05:14:06.493Z'],
    ['liquid', 'BTC/USDT', 47656.41, 48051.39, 1614402860970,'2021-02-27T05:14:20.970Z'],
    ['bittrex', 'BTC/USDT', 47669.63381701, 47675.16717965, None, None]
]

# arr columns [exchange, market, 'bid', 'ask', 'timestamp', 'datetime']
for ex1_id in arr_2:
    for ex2_id in arr_2:
        if ex1_id == ex2_id:  # same exchange
            continue
        depth1 = ex1_id
        depth2 = ex2_id
        if depth1[3] and depth2[2]:
            if (float(depth1[3]) > 0) \
                    and (float(depth2[2]) > 0) \
                    and (float(depth1[3]) < float(depth2[2])):
                print('1 buy 2 sell', 'btc/usdt', ex1_id[0], depth1[3], ex2_id[0], depth2[2])
                #1 buy 2 sell
                # self.arbitrage_opportunity_v2(kmarket, ex1_id, depth1[3], ex2_id, depth2[2])
            if (float(depth1[2]) > 0) \
                    and (float(depth2[3]) > 0) \
                    and (float(depth1[2]) > float(depth2[3])):
                #1 sell 2 buy
                print('1 sell 2 buy','btc/usdt', ex1_id[0], depth2[3], ex2_id[0], depth1[2])
                # self.arbitrage_opportunity_v2(kmarket, ex1_id, depth2[3], ex2_id, depth1[2])

