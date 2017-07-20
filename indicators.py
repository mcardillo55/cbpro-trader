#
# indicators.py
# Mike Cardillo
#
# System for containing all technical indicators and processing associated data

import talib
import numpy as np


class IndicatorSubsystem:
    def __init__(self):
        self.current_indicators = {}

    def recalculate_indicators(self, cur_period):
        total_periods = len(cur_period.candlesticks)
        if total_periods > 0:
            closing_prices = np.append(cur_period.get_closing_prices(),
                                       cur_period.cur_candlestick.close)
            volumes = np.append(cur_period.get_volumes(),
                                cur_period.cur_candlestick.volume)

            self.calculate_macd(closing_prices)
            self.calculate_vol_macd(volumes)
            self.calculate_avg_volume(volumes)

            self.current_indicators['total_periods'] = total_periods

        print "[INDICATORS] Periods: %d MACD Hist: %f Avg Vol: %f Vol MACD: %f" % \
              (self.current_indicators['total_periods'], self.current_indicators['macd_hist'],
               self.current_indicators['avg_volume'], self.current_indicators['vol_macd_hist'])

    def calculate_macd(self, closing_prices):
        macd, macd_sig, macd_hist = talib.MACD(closing_prices, fastperiod=10,
                                               slowperiod=26, signalperiod=9)
        self.current_indicators['macd'] = macd[-1]
        self.current_indicators['macd_sig'] = macd_sig[-1]
        self.current_indicators['macd_hist'] = macd_hist[-1]

    def calculate_vol_macd(self, volumes):
        macd, macd_sig, macd_hist = talib.MACD(volumes, fastperiod=10,
                                               slowperiod=26, signalperiod=9)
        self.current_indicators['vol_macd'] = macd[-1]
        self.current_indicators['vol_macd_sig'] = macd_sig[-1]
        self.current_indicators['vol_macd_hist'] = macd_hist[-1]

    def calculate_avg_volume(self, volumes):
        avg_vol = talib.SMA(volumes, timeperiod=15)

        self.current_indicators['avg_volume'] = avg_vol[-1]
