import ccxt

# return up to ten bidasks on each side of the order book stack
limit = 10
# book = ccxt.cex().fetch_order_book('BTC/USD', limit)

#
# limit = 10
# book = ccxt.kraken().fetch_order_book('BTC/USD', limit)
# print(book)

limit = 10
book2 = ccxt.bleutrade().fetch_order_book('BTC/USDT', None)
print(book2)


# book3 = ccxt.bittrex().fetch_order_book('BTC/USD', 25)
# print(book3)