#
# trade.py
# Mike Cardillo
#
# Objects relating to individual trade data

import dateutil.parser
import logging
from decimal import Decimal


class Trade:
    def __init__(self, msg):
        self.seq = Decimal(msg.get('sequence'))
        self.trade_id = Decimal(msg.get('trade_id'))
        self.time = dateutil.parser.parse(msg.get('time'))
        self.price = Decimal(msg.get('price'))
        self.volume = Decimal(msg.get('size'))
        self.logger = logging.getLogger('trader-logger')

    def print_trade(self):
        self.logger.debug("[TRADE] Trade ID: %d Price: %f Volume: %f" %
                          (self.trade_id, self.price, self.volume))
