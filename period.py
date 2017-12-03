#
# period.py
# Mike Cardillo
#
# Classes relating to time period data

import numpy as np
import gdax
import datetime
import dateutil.parser
import trade
import pytz
import logging
import time


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

    def print_stick(self, period_name):
        self.logger.debug("[CANDLESTICK %s] Time: %s Open: %s High: %s Low: %s Close: %s Vol: %s" %
                          (period_name, self.time, self.open, self.high, self.low,
                           self.close, self.volume))


class Period:
    def __init__(self, period_size=60, name='Period', product='BTC-USD', initialize=True):
        self.period_size = period_size
        self.name = name
        self.product = product
        self.first_trade = True
        self.verbose_heartbeat = False
        self.logger = logging.getLogger('trader-logger')
        if initialize:
            self.initialize()
        else:
            self.candlesticks = np.array([])

    def initialize(self):
        self.candlesticks = self.get_historical_data()
        self.cur_candlestick = Candlestick(existing_candlestick=self.candlesticks[-1])
        self.candlesticks = self.candlesticks[:-1]
        self.cur_candlestick_start = self.cur_candlestick.time

    def get_historical_data(self):
        gdax_client = gdax.PublicClient()

        end = datetime.datetime.utcnow()
        end_iso = end.isoformat()
        start = end - datetime.timedelta(seconds=(self.period_size * 200))
        start_iso = start.isoformat()

        ret = gdax_client.get_product_historic_rates(self.product, granularity=self.period_size, start=start_iso, end=end_iso)
        # Check if we got rate limited, which will return a JSON message
        if isinstance(ret, list):
            time.sleep(3)
            ret = gdax_client.get_product_historic_rates(self.product, granularity=self.period_size, start=start_iso, end=end_iso)
        hist_data = np.array(ret, dtype='object')
        for row in hist_data:
            row[0] = datetime.datetime.fromtimestamp(row[0], pytz.utc)
        return np.flipud(hist_data)

    def process_heartbeat(self, msg):
        isotime = dateutil.parser.parse(msg.get('time'))
        if isotime:
            if self.verbose_heartbeat:
                self.logger.debug("[HEARTBEAT] " + str(isotime) + " " + str(msg.get('last_trade_id')))
            if isotime - self.cur_candlestick_start > datetime.timedelta(seconds=self.period_size):
                self.close_candlestick()
                self.new_candlestick(self.cur_candlestick.time + datetime.timedelta(seconds=self.period_size))

    def process_trade(self, msg):
        if msg.get('product_id') == self.product:
            cur_trade = trade.Trade(msg)
            isotime = dateutil.parser.parse(msg.get('time')).replace(microsecond=0)
            if isotime < self.cur_candlestick.time:
                prev_stick = Candlestick(existing_candlestick=self.candlesticks[-1])
                self.candlesticks = self.candlesticks[:-1]
                prev_stick.add_trade(cur_trade)
                self.add_stick(prev_stick)
            else:
                if isotime > self.cur_candlestick.time + datetime.timedelta(seconds=self.period_size):
                    self.close_candlestick()
                    self.new_candlestick(self.cur_candlestick.time + datetime.timedelta(seconds=self.period_size))
                self.cur_candlestick.add_trade(cur_trade)
                self.cur_candlestick.print_stick(self.name)

    def get_highs(self):
        return np.array(self.candlesticks[:, 2], dtype='f8')

    def get_lows(self):
        return np.array(self.candlesticks[:, 1], dtype='f8')

    def get_closing_prices(self):
        return np.array(self.candlesticks[:, 4], dtype='f8')

    def get_volumes(self):
        return np.array(self.candlesticks[:, 5], dtype='f8')

    def new_candlestick(self, isotime):
        prev_close = self.cur_candlestick.close
        self.cur_candlestick = Candlestick(isotime=isotime, prev_close=prev_close)
        self.cur_candlestick_start = isotime.replace(second=0, microsecond=0)

    def add_stick(self, stick_to_add):
        self.candlesticks = np.row_stack((self.candlesticks, stick_to_add.close_candlestick(self.name)))

    def close_candlestick(self):
        if len(self.candlesticks) > 0:
            self.candlesticks = np.row_stack((self.candlesticks,
                                              self.cur_candlestick.close_candlestick(period_name=self.name,
                                                                                     prev_stick=self.candlesticks[-1])))
        else:
            self.candlesticks = np.array([self.cur_candlestick.close_candlestick(self.name)])
