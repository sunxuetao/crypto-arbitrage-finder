import ccxt

# return up to ten bidasks on each side of the order book stack
limit = 10
# book = ccxt.cex().fetch_order_book('BTC/USD', limit)

ex_kr = ccxt.kraken()
ex_kr.timeout = 2000
# limit = 10
# book = ex_kr.fetch_order_book('BTC/USD', limit)
# print(book)


# ex_blue = ccxt.bittrex()
# book2 = ex_blue.fetch_order_book('BTC/USDT', 1)
# print(book2)

# print(ccxt.cex().fetch_order_book('BTC/USD', limit))

tickers = ex_kr.fetch_tickers([
    "ETH/USDT",
    "BTC/USDT",
    "LTC/USDT",
    "EOS/USDT",
    "BCH/USDT"
])
print(tickers)
# print(ex_blue.countries)
# print(ex_kr.countries)

# book3 = ccxt.bittrex().fetch_order_book('BTC/USD', 25)
# print(book3)