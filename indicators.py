#
# indicators.py
# Mike Cardillo
#
# System for containing all technical indicators and processing associated data

import talib
import logging
import numpy as np
from decimal import Decimal


class IndicatorSubsystem:
    def __init__(self, period_list):
        self.logger = logging.getLogger('trader-logger')
        self.current_indicators = {}
        for period in period_list:
            self.current_indicators[period.name] = {}
        for period in period_list:
            self.current_indicators[period.name]['bid'] = {}
            self.current_indicators[period.name]['ask'] = {}

    def recalculate_indicators(self, cur_period, order_book):
        total_periods = len(cur_period.candlesticks)
        if total_periods > 0:
            cur_bid = float(order_book.get_bid() + Decimal('0.01'))
            cur_ask = float(order_book.get_ask() - Decimal('0.01'))
            closing_prices = cur_period.get_closing_prices()
            closing_prices_bid = np.append(closing_prices,
                                           cur_bid)
            closing_prices_ask = np.append(closing_prices,
                                           cur_ask)

            volumes = np.append(cur_period.get_volumes(),
                                cur_period.cur_candlestick.volume)

            # Need to calculate Bollinger Bands first, to use in OBV
            self.calculate_bbands(cur_period.name, closing_prices_ask)

            self.calculate_macd(cur_period.name, closing_prices_ask, 'ask')
            self.calculate_obv(cur_period.name, closing_prices_ask, volumes, 'ask')

            self.calculate_macd(cur_period.name, closing_prices_bid, 'bid')
            self.calculate_obv(cur_period.name, closing_prices_bid, volumes, 'bid')

            self.current_indicators[cur_period.name]['total_periods'] = total_periods

            self.logger.debug("[INDICATORS %s] Periods: %d MACD_DIFF: %f OBV_ASK: %f OBV_ASK EMA: %f OBV_BID: %f OBV_BID EMA: %f BBAND_UPPER: %f BBAND_LOWER %f" %
                              (cur_period.name, self.current_indicators[cur_period.name]['total_periods'], self.current_indicators[cur_period.name]['macd_hist_diff'],
                               self.current_indicators[cur_period.name]['ask']['obv'], self.current_indicators[cur_period.name]['ask']['obv_ema'],
                               self.current_indicators[cur_period.name]['bid']['obv'], self.current_indicators[cur_period.name]['ask']['obv_ema'],
                               self.current_indicators[cur_period.name]['bband_upper'], self.current_indicators[cur_period.name]['bband_lower']))

    def calculate_bbands(self, period_name, close):
        upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

        self.current_indicators[period_name]['bband_upper'] = upperband[-1]
        self.current_indicators[period_name]['bband_lower'] = lowerband[-1]

    def calculate_macd(self, period_name, closing_prices, bid_or_ask):
        macd, macd_sig, macd_hist = talib.MACD(closing_prices, fastperiod=10,
                                               slowperiod=26, signalperiod=9)
        self.current_indicators[period_name]['macd'] = macd[-1]
        self.current_indicators[period_name]['macd_sig'] = macd_sig[-1]
        self.current_indicators[period_name]['macd_hist'] = macd_hist[-1]
        self.current_indicators[period_name]['macd_hist_diff'] = Decimal(macd_hist[-1]) - Decimal(macd_hist[-2])

    def calculate_vol_macd(self, period_name, volumes):
        macd, macd_sig, macd_hist = talib.MACD(volumes, fastperiod=10,
                                               slowperiod=26, signalperiod=9)
        self.current_indicators[period_name]['vol_macd'] = macd[-1]
        self.current_indicators[period_name]['vol_macd_sig'] = macd_sig[-1]
        self.current_indicators[period_name]['vol_macd_hist'] = macd_hist[-1]

    def calculate_avg_volume(self, period_name, volumes):
        avg_vol = talib.SMA(volumes, timeperiod=15)

        self.current_indicators[period_name]['avg_volume'] = avg_vol[-1]

    def calculate_obv(self, period_name, closing_prices, volumes, bid_or_ask):
        # cryptowat.ch does not include the first value in their OBV
        # calculation, we we won't either to provide parity
        obv = talib.OBV(closing_prices[1:], volumes[1:])
        obv_ema = talib.EMA(obv, timeperiod=21)

        self.current_indicators[period_name][bid_or_ask]['obv_ema'] = obv_ema[-1]
        self.current_indicators[period_name][bid_or_ask]['obv'] = obv[-1]
