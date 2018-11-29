#
# test_period.py
# Mike Cardillo
#
# Pytest tests on the period file

import period
import datetime
from decimal import Decimal


class TestCandlestick(object):
    def test_init_with_isotime_and_prev_close(self):
        isotime = datetime.datetime(2018, 6, 10, 11, 13, 58, 384)
        prev_close = Decimal("58.30")
        candlestick = period.Candlestick(isotime=isotime, prev_close=prev_close)

        assert candlestick.new is True
        assert candlestick.time == datetime.datetime(2018, 6, 10, 11, 13, 0, 0)
        assert candlestick.open == Decimal("58.30")
        assert candlestick.high == Decimal("58.30")
        assert candlestick.low == Decimal("58.30")
        assert candlestick.close == Decimal("58.30")
        assert candlestick.volume == Decimal("0")

    def test_init_with_isotime_without_prev_close(self):
        isotime = datetime.datetime(2018, 6, 10, 11, 13, 58, 384)
        candlestick = period.Candlestick(isotime=isotime)

        assert candlestick.new is True
        assert candlestick.time == datetime.datetime(2018, 6, 10, 11, 13, 0, 0)
        assert candlestick.open is None
        assert candlestick.high is None
        assert candlestick.low is None
        assert candlestick.close is None
        assert candlestick.volume == Decimal("0")

    def test_init_without_isotime(self):
        test_datetime = datetime.datetime(2018, 6, 10, 11, 15, 0, 0)
        existing_candlestick = [test_datetime, Decimal("58.00"), Decimal("59.50"),
                                Decimal("58.10"), Decimal("58.50"), Decimal("15235.235")]
        candlestick = period.Candlestick(existing_candlestick=existing_candlestick)

        assert candlestick.new is False
        assert candlestick.time == datetime.datetime(2018, 6, 10, 11, 15, 0, 0)
        assert candlestick.open == Decimal("58.10")
        assert candlestick.high == Decimal("59.50")
        assert candlestick.low == Decimal("58.00")
        assert candlestick.close == Decimal("58.50")
        assert candlestick.volume == Decimal("15235.235")
