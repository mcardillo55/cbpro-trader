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
            closing_prices_bid = np.append(closing_prices, cur_bid)
            closing_prices_ask = np.append(closing_prices, cur_ask)
            closing_prices_close = np.append(closing_prices, cur_period.cur_candlestick.close)

            volumes = np.append(cur_period.get_volumes(),
                                cur_period.cur_candlestick.volume)
            highs = np.append(cur_period.get_highs(), cur_period.cur_candlestick.high)
            lows = np.append(cur_period.get_lows(), cur_period.cur_candlestick.low)

            # Need to calculate Bollinger Bands first, to use in OBV
            self.calculate_bbands(cur_period.name, closing_prices_close)
            #self.calculate_sar(cur_period.name, highs, lows)
            #self.calculate_mfi(cur_period.name, highs, lows, closing_prices_close, volumes)

            self.calculate_macd(cur_period.name, closing_prices_close)
            #self.calculate_obv(cur_period.name, closing_prices_ask, volumes, 'ask')

            #self.calculate_macd(cur_period.name, closing_prices_bid, 'bid')
            #self.calculate_obv(cur_period.name, closing_prices_bid, volumes, 'bid')

            self.current_indicators[cur_period.name]['total_periods'] = total_periods

            self.logger.debug("[INDICATORS %s] Periods: %d MACD: %f MACD_SIG: %f MACD_HIST: %f" %
                              (cur_period.name, self.current_indicators[cur_period.name]['total_periods'], self.current_indicators[cur_period.name]['macd'],
                               self.current_indicators[cur_period.name]['macd_sig'], self.current_indicators[cur_period.name]['macd_hist']))

    def calculate_bbands(self, period_name, close):
        upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

        self.current_indicators[period_name]['bband_upper'] = upperband[-1]
        self.current_indicators[period_name]['bband_lower'] = lowerband[-1]

    def calculate_macd(self, period_name, closing_prices):
        macd, macd_sig, macd_hist = talib.MACD(closing_prices, fastperiod=10,
                                               slowperiod=26, signalperiod=9)
        self.current_indicators[period_name]['macd'] = macd[-1]
        self.current_indicators[period_name]['macd_sig'] = macd_sig[-1]
        self.current_indicators[period_name]['macd_hist'] = macd_hist[-1]
        self.current_indicators[period_name]['macd_hist_diff'] = Decimal(macd_hist[-1]) - Decimal(macd_hist[-2])

    def calculate_vol_macd(self, period_name, volumes):
        macd, macd_sig, macd_hist = talib.MACD(volumes, fastperiod=50,
                                               slowperiod=200, signalperiod=14)
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

    def calculate_sar(self, period_name, highs, lows):
        sar = talib.SAR(highs, lows)

        self.current_indicators[period_name]['sar'] = sar[-1]

    def calculate_mfi(self, period_name, highs, lows, closing_prices, volumes):
        mfi = talib.MFI(highs, lows, closing_prices, volumes)

        self.current_indicators[period_name]['mfi'] = mfi[-1]
