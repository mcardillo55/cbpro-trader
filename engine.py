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
            self.error_logger.exception(datetime.datetime.now())
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
        self.usd = self.get_usd()
        self.btc = self.get_btc()
        self.last_balance_update = time.time()
        self.order_book.start()
        self.order_thread = threading.Thread()
        self.last_balance_update = time.time()
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

    def get_btc(self):
        try:
            for account in self.auth_client.get_accounts():
                if account.get('currency') == 'BTC':
                    return self.round_btc(account.get('available'))
            return self.round_btc(self.auth_client.get_accounts()[0]['available'])
        except AttributeError:
            return self.round_btc('0.0')

    def round_usd(self, money):
        return Decimal(money).quantize(Decimal('.01'), rounding=ROUND_DOWN)

    def round_btc(self, money):
        return Decimal(money).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)

    def update_amounts(self):
        if time.time() - self.last_balance_update > 10.0:
            try:
                self.btc = self.get_btc()
                self.usd = self.get_usd()
            except Exception:
                self.error_logger.exception(datetime.datetime.now())
            self.last_balance_update = time.time()

    def print_amounts(self):
        self.logger.debug("[BALANCES] USD: %.2f BTC: %.8f" % (self.usd, self.btc))

    def place_buy(self, partial='1.0'):
        amount = self.get_usd() * Decimal(partial)
        bid = self.order_book.get_ask() - Decimal('0.01')
        amount = self.round_btc(Decimal(amount) / Decimal(bid))

        if amount < Decimal('0.01'):
            amount = self.get_usd()
            bid = self.order_book.get_ask() - Decimal('0.01')
            amount = self.round_btc(Decimal(amount) / Decimal(bid))

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
                    ret = self.get_order(ret.get('id'))
                self.usd = self.get_usd()
            if not self.buy_flag and ret.get('id'):
                self.auth_client.cancel_all(product_id='BTC-USD')
            self.usd = self.get_usd()
        except Exception:
            self.error_logger.exception(datetime.datetime.now())


    def place_sell(self, partial='1.0'):
        amount = self.round_btc(self.get_btc() * Decimal(partial))
        if amount < Decimal('0.01'):
            amount = self.get_btc()
        ask = self.order_book.get_bid() + Decimal('0.01')

        if amount >= Decimal('0.01'):
            self.logger.debug("SELLING BTC!")
            self.auth_client.sell(type='limit', size=str(amount),
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
                self.btc = self.get_btc()
            if not self.sell_flag:
                self.auth_client.cancel_all(product_id='BTC-USD')
            self.btc = self.get_btc()
        except Exception:
            self.error_logger.exception(datetime.datetime.now())

    def determine_trades(self, indicators):
        if not self.is_live:
            return
        self.update_amounts()
        if Decimal(indicators['1']['macd_hist_diff']) > Decimal('0.0') \
           and Decimal(indicators['1']['mfi']) < Decimal('20.0'):
            self.sell_flag = False
            # buy btc
            self.buy_flag = True
            if self.order_thread.is_alive():
                if self.order_thread.name == 'sell_thread':
                    # Wait for thread to close
                    while self.order_thread.is_alive():
                        time.sleep(0.1)
                else:
                    pass
            else:
                self.order_thread = threading.Thread(target=self.buy, name='buy_thread')
                self.order_thread.start()
        elif Decimal(indicators['1']['macd_hist_diff']) < Decimal('0.0') \
             and Decimal(indicators['1']['macd_hist']) < Decimal('0.0'):
            self.buy_flag = False
            # sell btc
            self.sell_flag = True
            if self.order_thread.is_alive():
                if self.order_thread.name == 'buy_thread':
                    # Wait for thread to close
                    while self.order_thread.is_alive():
                        time.sleep(0.1)
                else:
                    pass
            else:
                self.order_thread = threading.Thread(target=self.sell, name='sell_thread')
                self.order_thread.start()
