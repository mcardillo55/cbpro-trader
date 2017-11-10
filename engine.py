#
# engine.py
# Mike Cardillo
#
# Subsystem containing all trading logic and execution
import time
import gdax
import threading
import logging
import datetime
from decimal import *


class OrderBookCustom(gdax.OrderBook):
    def __init__(self):
        self.logger = logging.getLogger('trader-logger')
        self.error_logger = logging.getLogger('error-logger')
        super(OrderBookCustom, self).__init__()

    def is_ready(self):
        try:
            super(OrderBookCustom, self).get_ask()
        except ValueError:
            #self.error_logger.exception(datetime.datetime.now())
            return False
        return True

    def get_ask(self):
        while not self.is_ready():
            time.sleep(0.01)
        return super(OrderBookCustom, self).get_ask()

    def get_bid(self):
        while not self.is_ready():
            time.sleep(0.01)
        return super(OrderBookCustom, self).get_bid()

    def on_open(self):
        self.stop = False
        self._sequence = -1
        self.logger.debug("-- Order Book Opened ---")

    def on_close(self):
        self.logger.debug("-- Order Book Closed ---")

    def on_error(self, e):
        raise e


class TradeEngine():
    def __init__(self, auth_client, is_live=False):
        self.auth_client = auth_client
        self.is_live = is_live
        self.order_book = OrderBookCustom()
        self.last_balance_update = 0
        self.update_amounts()
        self.last_balance_update = time.time()
        self.order_book.start()
        self.order_thread = threading.Thread()
        self.logger = logging.getLogger('trader-logger')
        self.error_logger = logging.getLogger('error-logger')

        self.buy_flag = False
        self.sell_flag = False

    def close(self):
        # Setting both flags will close any open order threads
        self.buy_flag = False
        self.sell_flag = False
        # Cancel any orders that may still be remaining
        try:
            self.auth_client.cancel_all(product_id='BTC-USD')
        except Exception:
            self.error_logger.exception(datetime.datetime.now())
        self.order_book.close()

    def start(self):
        self.order_book.start()

    def get_usd(self):
        try:
            for account in self.auth_client.get_accounts():
                if account.get('currency') == 'USD':
                    return self.round_usd(account.get('available'))
        except AttributeError:
            return self.round_usd('0.0')

    def round_usd(self, money):
        return Decimal(money).quantize(Decimal('.01'), rounding=ROUND_DOWN)

    def round_coin(self, money):
        return Decimal(money).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)

    def update_amounts(self):
        if time.time() - self.last_balance_update > 10.0:
            try:
                for account in self.auth_client.get_accounts():
                    if account.get('currency') == 'BTC':
                        self.btc = self.round_coin(account.get('available'))
                    elif account.get('currency') == 'ETH':
                        self.eth = self.round_coin(account.get('available'))
                    elif account.get('currency') == 'LTC':
                        self.ltc = self.round_coin(account.get('available'))
                    elif account.get('currency') == 'USD':
                        self.usd = self.round_usd(account.get('available'))
            except Exception:
                self.error_logger.exception(datetime.datetime.now())
            self.last_balance_update = time.time()

    def print_amounts(self):
        self.logger.debug("[BALANCES] USD: %.2f BTC: %.8f" % (self.usd, self.btc))

    def place_buy(self, partial='1.0'):
        amount = self.get_usd() * Decimal(partial)
        bid = self.order_book.get_ask() - Decimal('0.01')
        amount = self.round_coin(Decimal(amount) / Decimal(bid))

        if amount < Decimal('0.01'):
            amount = self.get_usd()
            bid = self.order_book.get_ask() - Decimal('0.01')
            amount = self.round_coin(Decimal(amount) / Decimal(bid))

        if amount >= Decimal('0.01'):
            self.logger.debug("BUYING BTC!")
            return self.auth_client.buy(type='limit', size=str(amount),
                                        price=str(bid), post_only=True,
                                        product_id='BTC-USD')
        else:
            ret = {'status': 'done'}
            return ret

    def buy(self, amount=None):
        try:
            ret = self.place_buy('0.5')
            bid = ret.get('price')
            while ret.get('status') != 'done' and self.buy_flag:
                if ret.get('status') == 'rejected' or ret.get('message') == 'NotFound':
                    ret = self.place_buy('0.5')
                    bid = ret.get('price')
                elif not bid or Decimal(bid) < self.order_book.get_ask() - Decimal('0.01'):
                    if len(self.auth_client.get_orders()[0]) > 0:
                        ret = self.place_buy('1.0')
                    else:
                        ret = self.place_buy('0.5')
                    for order in self.auth_client.get_orders()[0]:
                        if order.get('id') != ret.get('id'):
                            self.auth_client.cancel_order(order.get('id'))
                    bid = ret.get('price')
                if ret.get('id'):
                    ret = self.auth_client.get_order(ret.get('id'))
                self.usd = self.get_usd()
            if not self.buy_flag and ret.get('id'):
                self.auth_client.cancel_all(product_id='BTC-USD')
            self.usd = self.get_usd()
        except Exception:
            self.error_logger.exception(datetime.datetime.now())


    def place_sell(self, partial='1.0'):
        self.update_amounts()
        amount = self.round_coin(self.btc * Decimal(partial))
        if amount < Decimal('0.01'):
            amount = self.btc
        ask = self.order_book.get_bid() + Decimal('0.01')

        if amount >= Decimal('0.01'):
            self.logger.debug("SELLING BTC!")
            return self.auth_client.sell(type='limit', size=str(amount),
                                  price=str(ask), post_only=True,
                                  product_id='BTC-USD')
        else:
            ret = {'status': 'done'}
            return ret

    def sell(self, amount=None):
        try:
            ret = self.place_sell('0.5')
            ask = ret.get('price')
            while ret.get('status') != 'done' and self.sell_flag:
                if ret.get('status') == 'rejected' or ret.get('message') == 'NotFound':
                    ret = self.place_sell('0.5')
                    ask = ret.get('price')
                elif not ask or Decimal(ask) > self.order_book.get_bid() + Decimal('0.01'):
                    if len(self.auth_client.get_orders()[0]) > 0:
                        ret = self.place_sell('1.0')
                    else:
                        ret = self.place_sell('0.5')
                    for order in self.auth_client.get_orders()[0]:
                        if order.get('id') != ret.get('id'):
                            self.auth_client.cancel_order(order.get('id'))
                    ask = ret.get('price')
                if ret.get('id'):
                    ret = self.auth_client.get_order(ret.get('id'))
                self.update_amounts()
            if not self.sell_flag:
                self.auth_client.cancel_all(product_id='BTC-USD')
            self.update_amounts
        except Exception:
            self.error_logger.exception(datetime.datetime.now())

    def get_currency_size_and_product_id_from_period_name(self, period_name):
        if period_name is 'BTC30':
            return self.btc, 'BTC-USD'
        elif period_name is 'ETH30':
            return self.eth, 'ETH-USD'
        elif period_name is 'LTC30':
            return self.ltc, 'LTC-USD'


    def determine_trades(self, period_name, indicators):
        if not self.is_live:
            return

        self.update_amounts()
        amount_of_coin, product_id = self.get_currency_size_and_product_id_from_period_name(period_name)

        if Decimal(indicators[period_name]['close']) > Decimal(indicators[period_name]['bband_upper_2']):
            if self.usd > Decimal('0.0'):
                self.auth_client.buy(type='market', funds=str(self.usd), product_id=product_id)
        elif Decimal(indicators[period_name]['close']) < Decimal(indicators[period_name]['bband_upper_1']):
            if amount_of_coin > Decimal('0.0'):
                self.auth_client.sell(type='market', size=str(amount_of_coin), product_id=product_id)
