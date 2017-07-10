#
# period.py
# Mike Cardillo
#
# Classes relating to time period data

import numpy as np


class Candlestick:
    def __init__(self, first_trade=None, isotime=None):
        if first_trade:
            self.time = first_trade.time.replace(second=0, microsecond=0)
            self.open = first_trade.price
            self.high = first_trade.price
            self.low = first_trade.price
            self.volume = first_trade.volume
            self._last = first_trade.price

            print("Trade Added!")
            first_trade.print_trade()
        elif isotime:
            self.time = isotime.replace(second=0, microsecond=0)
            self.open = None
            self.high = None
            self.low = None
            self.volume = 0
            self._last = None

    def add_trade(self, new_trade):
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

        self._last = new_trade.price
        self.volume = self.volume + new_trade.volume

        print("Trade Added!")
        new_trade.print_trade()

    def close(self):
        self.close = self._last
        print("Candlestick Closed!")
        self.print_stick()
        return [self.time, self.open, self.high, self.low,
                self.close, self.volume]

    def print_stick(self):
        print("Time: %s Open: %s High: %s Low: %s Close: %s Vol: %s" %
              (self.time, self.open, self.high, self.low,
               self.close, self.volume))


class Period:
    def __init__(self, first_trade):
        self.cur_candlestick = Candlestick(first_trade=first_trade)
        self.candlesticks = np.array([])

    def new_candlestick(self, isotime):
        self.cur_candlestick = Candlestick(isotime=isotime)

    def close_candlestick(self):
        np.append(self.candlesticks, np.array(self.cur_candlestick.close()))
