markets = [
    "NEO/USDT",
    "XTZ/USDT",
    "LTC/USDT",
    "EOS/USDT",
    "ETC/USDT",
    "DASH/USDT",
    "ZIL/USDT"
]
exchanges=['bittrex', 'bitflyer', 'liquid', 'gateio', 'zb', 'bitfinex']
# observers if any
# ["Logger", "DetailedLogger", "TraderBot", "TraderBotSim", "HistoryDumper", "Emailer", "SpecializedTraderBot"]
observers = ["Logger"]

market_expiration_time = 120  # in seconds: 2 minutes

refresh_rate = 5

trade_wait = 10
profit_perc = 1 # 1 - 100 percent

MAKER_TRADE_ENABLE = False
TAKER_TRADE_ENABLE = True
# maker
MAKER_MAX_VOLUME = 30
MAKER_MIN_VOLUME = 1
MAKER_BUY_QUEUE = 3
MAKER_BUY_STAGE = 1
MAKER_SELL_QUEUE = 3
MAKER_SELL_STAGE = 2

TAKER_MAX_VOLUME = 1
TAKER_MIN_VOLUME = 0.01

bid_fee_rate = 0.001
ask_fee_rate = 0.001
bid_price_risk = 0
ask_price_risk = 0


#hedger
balance_margin = 0.1  # 10%

profit_thresh = 3  # in CNY
perc_thresh = 0.01  # in 0.01%
max_tx_volume = 3  # in BTC
min_tx_volume = 0.5  # in BTC

reverse_profit_thresh = 1
reverse_perc_thresh = 0.01
reverse_max_tx_volume = 1  # in BTC

stage0_percent=0.1
stage1_percent=0.2

ARBITRAGER_BUY_QUEUE = 5
ARBITRAGER_SELL_QUEUE = 5

arbitrage_cancel_price_diff = 2

broker_min_amount = 0.01

#stata
cny_init = 60000000000
btc_init = 1200000
price_init = 4450

#### Emailer Observer Config
send_trade_mail = False

EMAIL_HOST = 'mail.FIXME.com'
EMAIL_HOST_USER = 'FIXME@FIXME.com'
EMAIL_HOST_PASSWORD = 'FIXME'
EMAIL_USE_TLS = True

EMAIL_RECEIVER = ['FIXME@FIXME.com']


#### XMPP Observer
xmpp_jid = "FROM@jabber.org"
xmpp_password = "FIXME"
xmpp_to = "TO@jabber.org"

# broker thrift server
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 18030

#### Trader Bot Config
# Access to Private APIs

paymium_username = "FIXME"
paymium_password = "FIXME"
paymium_address = "FIXME"  # to deposit btc from markets / wallets

bitstamp_username = "FIXME"
bitstamp_password = "FIXME"

HUOBI_API_KEY = ''
HUOBI_SECRET_TOKEN = ''

OKCOIN_API_KEY = ''
OKCOIN_SECRET_TOKEN = ''

HAOBTC_API_KEY = ''
HAOBTC_SECRET_TOKEN = ''

BITSTAR_API_KEY = ''
BITSTAR_SECRET_TOKEN = ''

Bitfinex_API_KEY = ''
Bitfinex_SECRET_TOKEN = ''

Bittrex_API_KEY = ''
Bittrex_SECRET_TOKEN = ''


SUPPORT_ZMQ = True
ZMQ_HOST = "127.0.0.1"
ZMQ_PORT = 18031

SUPPORT_WEBSOCKET = False
WEBSOCKET_HOST = 'http://localhost'
WEBSOCKET_PORT = 13001

ENV = 'local'

try:
    from config_local import *
except ImportError:
    pass
