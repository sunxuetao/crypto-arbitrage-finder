import logging
from .observer import Observer


class Logger(Observer):
    def opportunity(self, profit, coin, volume, currency, buyprice, kask, sellprice, kbid, perc2,
                    weighted_buyprice, weighted_sellprice):
        logging.info("profit: %f coin: %s with volume: %f currency: %s - buy at %.4f (%s) sell at %.4f (%s) ~%.2f%%" \
                     % (profit, coin, volume, currency, buyprice, kask, sellprice, kbid, perc2))
