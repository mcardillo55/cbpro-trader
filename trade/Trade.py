import dateutil.parser
import logging


class Trade:
    def __init__(self, msg):
        self.seq = int(msg.get('sequence'))
        self.trade_id = int(msg.get('trade_id'))
        self.time = dateutil.parser.parse(msg.get('time'))
        self.price = float(msg.get('price'))
        self.volume = float(msg.get('size'))
        self.logger = logging.getLogger('trader-logger')

    def print_trade(self):
        self.logger.debug("[TRADE] Trade ID: %d Price: %f Volume: %f" %
                          (self.trade_id, self.price, self.volume))