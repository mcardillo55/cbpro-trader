#
# period.py
# Mike Cardillo
#
# Classes relating to time period data

import numpy as np
import gdax
import datetime


class Candlestick:
    def __init__(self, first_trade=None, isotime=None, existing_candlestick=None):
        if first_trade:
            self.time = first_trade.time.replace(second=0, microsecond=0)
            self.open = first_trade.price
            self.high = first_trade.price
            self.low = first_trade.price
            self.close = first_trade.price
            self.volume = first_trade.volume

        elif isotime:
            self.time = isotime.replace(second=0, microsecond=0)
            self.open = None
            self.high = None
            self.low = None
            self.close = None
            self.volume = 0
        elif existing_candlestick is not None:
            self.time, self.low, self.high, self.open, self.close, self.volume = existing_candlestick

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

        self.close = new_trade.price
        self.volume = self.volume + new_trade.volume

    def close_candlestick(self):
        print("Candlestick Closed!")
        self.print_stick()
        return np.array([self.time, self.open, self.high, self.low,
                        self.close, self.volume])

    def print_stick(self):
        print("[CANDLESTICK] Time: %s Open: %s High: %s Low: %s Close: %s Vol: %s" %
              (self.time, self.open, self.high, self.low,
               self.close, self.volume))


class Period:
    def __init__(self, first_trade, initialize=True):
        if initialize:
            self.candlesticks = self.get_historical_data()
            if first_trade.time.minute == self.candlesticks[-1][0].minute:
                self.cur_candlestick = Candlestick(existing_candlestick=self.candlesticks[-1])
                self.candlesticks = self.candlesticks[:-1]
            else:
                self.cur_candlestick = Candlestick(first_trade=first_trade)
        else:
            self.candlesticks = np.array([])
            self.cur_candlestick = Candlestick(first_trade=first_trade)

    def get_historical_data(self, period_size=60):
        gdax_client = gdax.PublicClient()
        gdax_hist_data = np.array(gdax_client.get_product_historic_rates('BTC-USD', granularity=period_size), dtype='object')

        for row in gdax_hist_data:
            row[0] = datetime.datetime.fromtimestamp(row[0])

        return np.flipud(gdax_hist_data)

    def get_closing_prices(self):
        return np.array(self.candlesticks[:, 4], dtype='f8')

    def get_volumes(self):
        return np.array(self.candlesticks[:, 5], dtype='f8')

    def new_candlestick(self, isotime):
        self.cur_candlestick = Candlestick(isotime=isotime)

    def close_candlestick(self):
        if len(self.candlesticks) > 0:
            self.candlesticks = np.row_stack((self.candlesticks,
                                              self.cur_candlestick.close_candlestick()))
        else:
            self.candlesticks = np.array([self.cur_candlestick.close_candlestick()])
