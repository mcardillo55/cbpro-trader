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
import requests
import logging


class Candlestick:
    def __init__(self, isotime=None, existing_candlestick=None):
        self.logger = logging.getLogger('trader-logger')
        if isotime:
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

    def close_candlestick(self, period_name, prev_stick=None):
        self.logger.debug("Candlestick Closed!")
        if self.close is None:
            self.open = prev_stick[4]  # Closing price
            self.high = prev_stick[4]
            self.low = prev_stick[4]
            self.close = prev_stick[4]
        self.print_stick(period_name)
        return np.array([self.time, self.open, self.high, self.low,
                        self.close, self.volume])

    def print_stick(self, period_name):
        self.logger.debug("[CANDLESTICK %s] Time: %s Open: %s High: %s Low: %s Close: %s Vol: %s" %
                          (period_name, self.time, self.open, self.high, self.low,
                           self.close, self.volume))


class Period:
    def __init__(self, period_size=60, name='Period', initialize=True):
        self.period_size = period_size
        self.name = name
        self.first_trade = True
        self.verbose_heartbeat = False
        self.logger = logging.getLogger('trader-logger')
        if initialize:
            self.candlesticks = self.get_historical_data()
            self.cur_candlestick = Candlestick(existing_candlestick=self.candlesticks[-1])
            self.candlesticks = self.candlesticks[:-1]
            self.cur_candlestick_start = self.cur_candlestick.time
        else:
            self.candlesticks = np.array([])

    def get_historical_data(self):
        r = requests.get('https://api.cryptowat.ch/markets/gdax/btcusd/ohlc', data={'periods': self.period_size})
        if r.status_code == 200:
            # Prefer data from cryptowat.ch since it is more up-to-date
            hist_data = np.array(r.json().get('result').get(str(self.period_size)), dtype='object')
            for row in hist_data:
                row[0] = datetime.datetime.fromtimestamp(row[0], pytz.utc) - datetime.timedelta(minutes=5)
            return hist_data
        else:
            # Use GDAX API as backup
            gdax_client = gdax.PublicClient()
            hist_data = np.array(gdax_client.get_product_historic_rates('BTC-USD', granularity=self.period_size), dtype='object')
            for row in hist_data:
                row[0] = datetime.datetime.fromtimestamp(row[0], pytz.utc)
            return np.flipud(hist_data)

    def process_heartbeat(self, msg):
        isotime = dateutil.parser.parse(msg.get('time'))
        if isotime:
            if self.verbose_heartbeat:
                self.logger.debug("[HEARTBEAT] " + str(isotime) + " " + str(msg.get('last_trade_id')))
            if isotime - self.cur_candlestick_start >= datetime.timedelta(seconds=self.period_size):
                self.close_candlestick()
                self.new_candlestick(isotime)

    def process_trade(self, msg):
        cur_trade = trade.Trade(msg)
        self.cur_candlestick.add_trade(cur_trade)
        self.cur_candlestick.print_stick(self.name)

    def get_closing_prices(self):
        return np.array(self.candlesticks[:, 4], dtype='f8')

    def get_volumes(self):
        return np.array(self.candlesticks[:, 5], dtype='f8')

    def new_candlestick(self, isotime):
        self.cur_candlestick = Candlestick(isotime=isotime)
        self.cur_candlestick_start = isotime.replace(second=0, microsecond=0)

    def close_candlestick(self):
        if len(self.candlesticks) > 0:
            self.candlesticks = np.row_stack((self.candlesticks,
                                              self.cur_candlestick.close_candlestick(period_name=self.name,
                                                                                     prev_stick=self.candlesticks[-1])))
        else:
            self.candlesticks = np.array([self.cur_candlestick.close_candlestick(self.name)])
