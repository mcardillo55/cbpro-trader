import logging
import numpy as np

class Candlestick:
    def __init__(self, isotime=None, existing_candlestick=None, prev_close=None):
        self.logger = logging.getLogger('trader-logger')
        self.new = True
        if isotime:
            self.time = isotime.replace(second=0, microsecond=0)
            self.volume = 0
            if prev_close:
                self.open = prev_close
                self.high = prev_close
                self.low = prev_close
                self.close = prev_close
            else:
                self.time = isotime.replace(second=0, microsecond=0)
                self.open = None
                self.high = None
                self.low = None
                self.close = None

        elif existing_candlestick is not None:
            self.new = False
            self.time, self.low, self.high, self.open, self.close, self.volume = existing_candlestick

    def add_trade(self, new_trade):
        self.new = False
        if not self.open:
            self.open = new_trade.price

        if not self.high:
            self.high = new_trade.price
        elif new_trade.price > self.high:
            self.high = new_trade.price

        if not self.low:
            self.low = new_trade.price
        elif new_trade.price < self.low:
            self.low = new_trade.price

        self.close = new_trade.price
        self.volume = self.volume + new_trade.volume
        self.logger.debug("[TRADE] Time: %s Price: %f Vol: %f" %
                          (new_trade.time, new_trade.price, new_trade.volume))

    def close_candlestick(self, period_name, prev_stick=None):
        self.logger.debug("Candlestick Closed!")
        if self.close is None:
            self.new = False
            self.open = prev_stick[4]  # Closing price
            self.high = prev_stick[4]
            self.low = prev_stick[4]
            self.close = prev_stick[4]
        self.print_stick(period_name)
        return np.array([self.time, self.low, self.high, self.open,
                        self.close, self.volume])

    def to_list(self):
        return [self.time, self.low, self.high, self.open,
                        self.close, self.volume]

    def print_stick(self, period_name):
        self.logger.debug("[CANDLESTICK %s] Time: %s Open: %s High: %s Low: %s Close: %s Vol: %s" %
                          (period_name, self.time, self.open, self.high, self.low,
                           self.close, self.volume))
