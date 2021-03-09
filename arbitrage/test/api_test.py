import ccxt

print(ccxt.exchanges)
#['aax', 'acx', 'aofex', 'bequant', 'bibox', 'bigone', 'binance', 'binanceus', 'bit2c', 'bitbank', 'bitbay', 'bitcoincom',
# 'bitfinex', 'bitfinex2', 'bitflyer', 'bitforex', 'bitget', 'bithumb', 'bitkk', 'bitmart', 'bitmax', 'bitmex', 'bitpanda',
# 'bitso', 'bitstamp', 'bitstamp1', 'bittrex', 'bitvavo', 'bitz', 'bl3p', 'bleutrade', 'braziliex', 'btcalpha', 'btcbox',
# 'btcmarkets', 'btctradeua', 'btcturk', 'buda', 'bw', 'bybit', 'bytetrade', 'cdax', 'cex', 'chilebit', 'coinbase',
# 'coinbaseprime', 'coinbasepro', 'coincheck', 'coinegg', 'coinex', 'coinfalcon', 'coinfloor', 'coingi', 'coinmarketcap',
# 'coinmate', 'coinone', 'coinspot', 'crex24', 'currencycom', 'delta', 'deribit', 'digifinex', 'dsx', 'eterbase', 'exmo',
# 'exx', 'fcoin', 'fcoinjp', 'flowbtc', 'foxbit', 'ftx', 'gateio', 'gemini', 'gopax', 'hbtc', 'hitbtc', 'hollaex',
# 'huobijp', 'huobipro', 'ice3x', 'idex', 'independentreserve', 'indodax', 'itbit', 'kraken', 'kucoin', 'kuna', 'lakebtc',
# 'latoken', 'lbank', 'liquid', 'luno', 'lykke', 'mercado', 'mixcoins', 'novadax', 'oceanex', 'okcoin', 'okex', 'paymium',
# 'phemex', 'poloniex', 'probit', 'qtrade', 'rightbtc', 'ripio', 'southxchange', 'stex', 'surbitcoin', 'therock', 'tidebit',
# 'tidex', 'timex', 'upbit', 'vaultoro', 'vbtc', 'vcc', 'wavesexchange', 'whitebit', 'xbtce', 'xena', 'yobit', 'zaif', 'zb']
# return up to ten bidasks on each side of the order book stack
limit = 10
# book = ccxt.cex().fetch_order_book('BTC/USD', limit)

# ex_kr = ccxt.kraken()
# ex_kr.timeout = 2000
# limit = 10
# book = ex_kr.fetch_order_book('BTC/USD', limit)
# print(book)


# ex_bittrex = ccxt.bittrex()
# book2 = ex_bittrex.fetch_order_book('BTC/USDT', 10)
# print(book2)

# print(ccxt.cex().fetch_order_book('BTC/USD', limit))

# tickers = ex_kr.fetch_tickers([
#     "ETH/USDT",
#     "BTC/USDT",
#     "LTC/USDT",
#     "EOS/USDT",
#     "BCH/USDT"
# ])
# print(tickers)
# print(ex_blue.countries)
# print(ex_kr.countries)

# book3 = ccxt.bittrex().fetch_order_book('BTC/USD', 25)
# print(book3)