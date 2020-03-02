import logging
import cbpro
import datetime
import time
import dateutil
import pytz
import trade
import numpy as np
from .Candlestick import Candlestick

class Period:
    def __init__(self, period_size=60, name='Period', product='BTC-USD', initialize=True, cbpro_client=cbpro.PublicClient()):
        self.period_size = period_size
        self.name = name
        self.product = product
        self.first_trade = True
        self.verbose_heartbeat = False
        # CBPRO historical data is not up-to-date
        # We need to update data 10 minutes after closing the first period
        self.updated_hist_data = False
        self.time_of_first_candlestick_close = None
        self.logger = logging.getLogger('trader-logger')
        self.error_logger = logging.getLogger('error-logger')
        self.cbpro_client = cbpro_client
        if initialize:
            self.initialize()
        else:
            self.candlesticks = np.array([])

    def initialize(self):
        self.candlesticks = self.get_historical_data()
        self.cur_candlestick = Candlestick(existing_candlestick=self.candlesticks[-1])
        self.candlesticks = self.candlesticks[:-1]
        self.cur_candlestick_start = self.cur_candlestick.time

    def get_historical_data(self, num_periods=200):
        end = datetime.datetime.utcnow()
        end_iso = end.isoformat()
        start = end - datetime.timedelta(seconds=(self.period_size * num_periods))
        start_iso = start.isoformat()

        ret = None

        # Check if we got rate limited, which will return a JSON message
        while not isinstance(ret, list):
            try:
                time.sleep(3)
                ret = self.cbpro_client.get_product_historic_rates(self.product, granularity=self.period_size, start=start_iso, end=end_iso)
            except Exception:
                self.error_logger.exception(datetime.datetime.now())
        hist_data = np.array(ret, dtype='object')
        for row in hist_data:
            row[0] = datetime.datetime.fromtimestamp(row[0], pytz.utc)
        return np.flipud(hist_data)

    def update_historical_data(self):
        updated_sticks = self.get_historical_data(num_periods=5)
        for new_stick in updated_sticks:
            for idx, old_stick in enumerate(self.candlesticks[-10:]):
                if new_stick[0] == old_stick[0]:
                    self.candlesticks[-10 + idx] = new_stick
        self.updated_hist_data = True

    def process_heartbeat(self, msg):
        if not self.updated_hist_data and self.time_of_first_candlestick_close \
           and datetime.datetime.now() - self.time_of_first_candlestick_close >= datetime.timedelta(minutes=10):
            self.update_historical_data()

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
        if not self.updated_hist_data:
            self.time_of_first_candlestick_close = datetime.datetime.now()
        if len(self.candlesticks) > 0:
            self.candlesticks = np.row_stack((self.candlesticks,
                                              self.cur_candlestick.close_candlestick(period_name=self.name,
                                                                                     prev_stick=self.candlesticks[-1])))
        else:
            self.candlesticks = np.array([self.cur_candlestick.close_candlestick(self.name)])