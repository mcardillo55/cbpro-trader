#
# indicators.py
# Mike Cardillo
#
# System for containing all technical indicators and processing associated data

import talib


class IndicatorSubsystem:
    def __init__(self):
        self.current_indicators = {}

    def recalculate_indicators(self, cur_period):
        total_periods = len(cur_period.candlesticks)
        if total_periods > 0:
            self.calculate_macd(cur_period.get_closing_prices())
            self.calculate_avg_volume(cur_period.get_volumes())
            self.current_indicators['total_periods'] = total_periods

        print self.current_indicators

    def calculate_macd(self, closing_prices):
        macd, macd_sig, macd_hist = talib.MACD(closing_prices, fastperiod=10,
                                               slowperiod=26, signalperiod=9)
        self.current_indicators['macd'] = macd[-1]
        self.current_indicators['macd_sig'] = macd_sig[-1]
        self.current_indicators['macd_hist'] = macd_hist[-1]

    def calculate_avg_volume(self, volumes):
        avg_vol = talib.SMA(volumes, timeperiod=15)

        self.current_indicators['avg_volume'] = avg_vol[-1]
