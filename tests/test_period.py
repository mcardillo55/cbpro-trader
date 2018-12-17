#
# test_period.py
# Mike Cardillo
#
# Pytest tests on the period file

import period
import trade
import datetime
import numpy as np
from decimal import Decimal


class TestCandlestick(object):
    def setup_class(self):
        fake_trade_dict = {"sequence": "12345",
                           "trade_id": "123",
                           "time": "2018-11-29T05:21:06Z",
                           "price": "38.50",
                           "size": "105.34"}
        self.fake_trade = trade.Trade(fake_trade_dict)
        self.test_datetime = datetime.datetime(2018, 6, 10, 11, 13, 58, 384)
        self.test_datetime_zero_sec_ms = datetime.datetime(2018, 6, 10, 11, 13, 0, 0)

    def test_init_with_isotime_and_prev_close(self):
        prev_close = Decimal("58.30")
        candlestick = period.Candlestick(isotime=self.test_datetime, prev_close=prev_close)

        assert candlestick.new is True
        assert candlestick.time == self.test_datetime_zero_sec_ms
        assert candlestick.open == Decimal("58.30")
        assert candlestick.high == Decimal("58.30")
        assert candlestick.low == Decimal("58.30")
        assert candlestick.close == Decimal("58.30")
        assert candlestick.volume == Decimal("0")

    def test_init_with_isotime_without_prev_close(self):
        candlestick = period.Candlestick(isotime=self.test_datetime)

        assert candlestick.new is True
        assert candlestick.time == self.test_datetime_zero_sec_ms
        assert candlestick.open is None
        assert candlestick.high is None
        assert candlestick.low is None
        assert candlestick.close is None
        assert candlestick.volume == Decimal("0")

    def test_init_without_isotime(self):
        existing_candlestick = [self.test_datetime_zero_sec_ms, Decimal("58.00"), Decimal("59.50"),
                                Decimal("58.10"), Decimal("58.50"), Decimal("15235.235")]
        candlestick = period.Candlestick(existing_candlestick=existing_candlestick)

        assert candlestick.new is False
        assert candlestick.time == self.test_datetime_zero_sec_ms
        assert candlestick.open == Decimal("58.10")
        assert candlestick.high == Decimal("59.50")
        assert candlestick.low == Decimal("58.00")
        assert candlestick.close == Decimal("58.50")
        assert candlestick.volume == Decimal("15235.235")

    def test_add_trade__new_open(self):
        candlestick = period.Candlestick(isotime=self.test_datetime)
        candlestick.add_trade(self.fake_trade)

        assert candlestick.new is False
        assert candlestick.open == Decimal("38.50")
        assert candlestick.high == Decimal("38.50")
        assert candlestick.low == Decimal("38.50")
        assert candlestick.close == Decimal("38.50")
        assert candlestick.volume == Decimal("105.34")

    def test_add_trade__higher_high(self):
        existing_candlestick = [self.test_datetime_zero_sec_ms, Decimal("25.57"), Decimal("35.57"),
                                Decimal("30.25"), Decimal("31.25"), Decimal("15235.235")]
        candlestick = period.Candlestick(existing_candlestick=existing_candlestick)
        candlestick.add_trade(self.fake_trade)

        assert candlestick.high == Decimal("38.50")
        assert candlestick.close == Decimal("38.50")
        assert candlestick.volume == Decimal("15235.235") + Decimal("105.34")

    def test_add_trade__lower_low(self):
        existing_candlestick = [self.test_datetime_zero_sec_ms, Decimal("39.57"), Decimal("42.45"),
                                Decimal("40.25"), Decimal("39.87"), Decimal("15235.235")]
        candlestick = period.Candlestick(existing_candlestick=existing_candlestick)
        candlestick.add_trade(self.fake_trade)

        assert candlestick.low == Decimal("38.50")
        assert candlestick.close == Decimal("38.50")
        assert candlestick.volume == Decimal("15235.235") + Decimal("105.34")

    def test_close_candlestick__all_fields_none(self):

        candlestick = period.Candlestick(isotime=self.test_datetime)
        prev_stick = [self.test_datetime_zero_sec_ms, Decimal("39.57"), Decimal("42.45"),
                      Decimal("40.25"), Decimal("39.87"), Decimal("15235.235")]
        ret = candlestick.close_candlestick("TEST STICK", prev_stick=prev_stick)

        assert candlestick.new is False
        assert isinstance(ret, type(np.array([])))
        np.testing.assert_array_equal(ret, [self.test_datetime_zero_sec_ms, Decimal("39.87"), Decimal("39.87"), Decimal("39.87"), Decimal("39.87"), Decimal("0")])

    def test_close_candlestick__close_not_none(self):
        existing_candlestick = [self.test_datetime_zero_sec_ms, Decimal("58.00"), Decimal("59.50"),
                                Decimal("58.10"), Decimal("58.50"), Decimal("15235.235")]
        candlestick = period.Candlestick(existing_candlestick=existing_candlestick)
        ret = candlestick.close_candlestick("TEST STICK")

        assert isinstance(ret, type(np.array([])))
        np.testing.assert_array_equal(ret, existing_candlestick)


class TestPeriod(object):
    def setup_class(self):
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.fake_hist_data = [[self.start_time.timestamp(), 123.4, 133.5, 124.6, 132.3, 3485.38],
                               [(self.start_time + datetime.timedelta(minutes=5)).timestamp(), 122.3, 135.4, 123.7, 133.4, 4385.25],
                               [(self.start_time + datetime.timedelta(minutes=10)).timestamp(), 120.2, 130.2, 132.5, 131.2, 3859.42]]

    def test_init__initalize_false(self):
        test_period = period.Period(period_size=15, name="BTC15", product="BTC-USD", initialize=False)

        assert isinstance(test_period, period.Period)
        assert test_period.period_size == 15
        assert test_period.name == "BTC15"
        assert test_period.product == "BTC-USD"
        assert test_period.verbose_heartbeat is False
        assert isinstance(test_period.candlesticks, type(np.array([])))
        np.testing.assert_array_equal(test_period.candlesticks, np.array([]))

    def test_init__initalize_true(self, mocker):
        mocker.patch("cbpro.PublicClient.get_product_historic_rates", return_value=self.fake_hist_data)
        test_period = period.Period(period_size=5, name="ETH5", product="ETH-USD", initialize=True)

        assert isinstance(test_period, period.Period)
        assert test_period.period_size == 5
        assert test_period.name == "ETH5"
        assert test_period.product == "ETH-USD"
        assert test_period.verbose_heartbeat is False

        assert isinstance(test_period.candlesticks, type(np.array([])))
        assert len(test_period.candlesticks) == len(self.fake_hist_data) - 1
        assert isinstance(test_period.cur_candlestick, period.Candlestick)
        assert test_period.cur_candlestick_start == self.start_time
        assert isinstance(test_period.candlesticks[0], type(np.array([])))
