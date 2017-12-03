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
    def __init__(self, product_id='BTC-USD'):
        self.logger = logging.getLogger('trader-logger')
        self.error_logger = logging.getLogger('error-logger')
        super(OrderBookCustom, self).__init__(product_id=product_id)

    def is_ready(self):
        try:
            super(OrderBookCustom, self).get_ask()
        except ValueError:
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


class TradeEngine():
    def __init__(self, auth_client, product_list=['BTC-USD', 'ETH-USD', 'LTC-USD'], is_live=False):
        self.logger = logging.getLogger('trader-logger')
        self.error_logger = logging.getLogger('error-logger')
        self.auth_client = auth_client
        self.product_list = product_list
        self.is_live = is_live
        self.quote_increment = {}
        self.min_size = {}
        self.order_book = {}
        self.order_in_progress = {}
        self.buy_flag = {}
        self.sell_flag = {}
        self.last_signal_switch = {}
        gdax_product_info = self.auth_client.get_products()
        # Should probably make Product class
        for product_id in self.product_list:
            for gdax_product in gdax_product_info:
                if product_id == gdax_product.get('id'):
                    self.quote_increment[product_id] = gdax_product.get('quote_increment')
                    self.min_size[product_id] = gdax_product.get('base_min_size')
            self.order_book[product_id] = OrderBookCustom(product_id=product_id)
            self.order_in_progress[product_id] = False
            self.buy_flag[product_id] = False
            self.sell_flag[product_id] = False
            self.last_signal_switch[product_id] = time.time()
        self.last_balance_update = 0
        self.update_amounts()
        self.usd_equivalent = 0
        self.last_balance_update = time.time()
        self.order_thread = threading.Thread()

    def close(self):
        for product_id in self.product_list:
            # Setting both flags will close any open order threads
            self.buy_flag[product_id] = False
            self.sell_flag[product_id] = False
            # Cancel any orders that may still be remaining
            self.order_in_progress[product_id] = False
        try:
            self.auth_client.cancel_all()
        except Exception:
            self.error_logger.exception(datetime.datetime.now())

    def get_currency(self, currency='USD'):
        try:
            for account in self.auth_client.get_accounts():
                if account.get('currency') == currency:
                    if currency == 'USD':
                        return self.round_usd(account.get('available'))
                    else:
                        return self.round_coin(account.get('available'))
        except AttributeError:
            self.error_logger.exception(datetime.datetime.now())
            return self.round_coin('0.0')

    def round_usd(self, money):
        return Decimal(money).quantize(Decimal('.01'), rounding=ROUND_DOWN)

    def round_coin(self, money):
        return Decimal(money).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)

    def update_amounts(self, indicators=None):
        if time.time() - self.last_balance_update > 10.0:
            try:
                self.last_balance_update = time.time()
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
                self.btc = Decimal('0.0')
                self.eth = Decimal('0.0')
                self.ltc = Decimal('0.0')
                self.usd = Decimal('0.0')
                return

            self.usd_equivalent = Decimal('0.0')
            for product in self.product_list:
                try:
                    quote = self.auth_client.get_product_ticker(product_id=product)['price']
                    if quote is not None:
                        self.usd_equivalent += self.get_base_currency_from_product_id(product) * Decimal(quote)
                except Exception:
                    self.error_logger.exception(datetime.datetime.now())
            self.usd_equivalent += self.usd

    def print_amounts(self):
        self.logger.debug("[BALANCES] USD: %.2f BTC: %.8f" % (self.usd, self.btc))

    def place_buy(self, product_id='BTC-USD', partial='1.0'):
        amount = self.get_currency(product_id[4:]) * Decimal(partial)
        bid = self.order_book[product_id].get_ask() - Decimal(self.quote_increment[product_id])
        amount = self.round_coin(Decimal(amount) / Decimal(bid))

        if amount < Decimal(self.min_size[product_id]):
            amount = self.get_currency(product_id[4:])
            bid = self.order_book[product_id].get_ask() - Decimal(self.quote_increment[product_id])
            amount = self.round_coin(Decimal(amount) / Decimal(bid))

        if amount >= Decimal(self.quote_increment[product_id]):
            self.logger.debug("Placing buy... Price: %.8f Size: %.8f" % (bid, amount))
            return self.auth_client.buy(type='limit', size=str(amount),
                                        price=str(bid), post_only=True,
                                        product_id=product_id)
        else:
            ret = {'status': 'done'}
            return ret

    def buy(self, product_id='BTC-USD', amount=None):
        self.order_in_progress[product_id] = True
        try:
            ret = self.place_buy(product_id=product_id, partial='0.5')
            bid = ret.get('price')
            amount = self.get_currency(product_id[4:])
            while self.buy_flag[product_id] and (amount > Decimal('0.0') or len(self.auth_client.get_orders()[0]) > 0):
                if ret.get('status') == 'rejected' or ret.get('status') == 'done' or ret.get('message') == 'NotFound':
                    ret = self.place_buy(product_id=product_id, partial='0.5')
                    bid = ret.get('price')
                elif not bid or Decimal(bid) < self.order_book[product_id].get_ask() - Decimal(self.quote_increment[product_id]):
                    if len(self.auth_client.get_orders()[0]) > 0:
                        ret = self.place_buy(product_id=product_id, partial='1.0')
                    else:
                        ret = self.place_buy(product_id=product_id, partial='0.5')
                    for order in self.auth_client.get_orders()[0]:
                        if order.get('id') != ret.get('id'):
                            self.auth_client.cancel_order(order.get('id'))
                    bid = ret.get('price')
                if ret.get('id'):
                    ret = self.auth_client.get_order(ret.get('id'))
                amount = self.get_currency(product_id[4:])
            self.auth_client.cancel_all(product_id=product_id)
            amount = self.get_currency(product_id[4:])
        except Exception:
            self.order_in_progress[product_id] = False
            self.error_logger.exception(datetime.datetime.now())
        self.auth_client.cancel_all(product_id=product_id)
        self.order_in_progress[product_id] = False

    def place_sell(self, product_id='BTC-USD', partial='1.0'):
        amount = self.round_coin(self.get_currency(product_id[:3]) * Decimal(partial))
        if amount < Decimal(self.min_size[product_id]):
            amount = self.get_currency(product_id[:3])
        ask = self.order_book[product_id].get_bid() + Decimal(self.quote_increment[product_id])

        if amount >= Decimal(self.min_size[product_id]):
            self.logger.debug("Placing sell... Price: %.2f Size: %.8f" % (ask, amount))
            return self.auth_client.sell(type='limit', size=str(amount),
                                    price=str(ask), post_only=True,
                                    product_id=product_id)
        else:
            ret = {'status': 'done'}
            return ret

    def sell(self, product_id='BTC-USD', amount=None):
        self.order_in_progress[product_id] = True
        try:
            ret = self.place_sell(product_id=product_id, partial='0.5')
            ask = ret.get('price')
            amount = self.get_currency(product_id[:3])
            while self.sell_flag[product_id] and (amount >= Decimal(self.min_size[product_id]) or len(self.auth_client.get_orders()[0]) > 0):
                if ret.get('status') == 'rejected' or ret.get('status') == 'done' or ret.get('message') == 'NotFound':
                    ret = self.place_sell(product_id=product_id, partial='0.5')
                    ask = ret.get('price')
                elif not ask or Decimal(ask) > self.order_book[product_id].get_bid() + Decimal(self.quote_increment[product_id]):
                    if len(self.auth_client.get_orders()[0]) > 0:
                        ret = self.place_sell(product_id=product_id, partial='1.0')
                    else:
                        ret = self.place_sell(product_id=product_id, partial='0.5')
                    for order in self.auth_client.get_orders()[0]:
                        if order.get('id') != ret.get('id'):
                            self.auth_client.cancel_order(order.get('id'))
                    ask = ret.get('price')
                if ret.get('id'):
                    ret = self.auth_client.get_order(ret.get('id'))
                amount = self.get_currency(product_id[:3])
            self.auth_client.cancel_all(product_id=product_id)
            amount = self.get_currency(product_id[:3])
        except Exception:
            self.order_in_progress[product_id] = False
            self.error_logger.exception(datetime.datetime.now())
        self.auth_client.cancel_all(product_id=product_id)
        self.order_in_progress[product_id] = False

    def get_base_currency_from_product_id(self, product_id):
        if product_id == 'BTC-USD':
            return self.btc
        elif product_id == 'ETH-USD':
            return self.eth
        elif product_id == 'LTC-USD':
            return self.ltc
        elif product_id == 'ETH-BTC':
            return self.eth
        elif product_id == 'LTC-BTC':
            return self.ltc

    def get_quoted_currency_from_product_id(self, product_id):
        if product_id == 'BTC-USD':
            return self.btc
        elif product_id == 'ETH-USD':
            return self.eth
        elif product_id == 'LTC-USD':
            return self.ltc
        elif product_id == 'ETH-BTC':
            return self.eth
        elif product_id == 'LTC-BTC':
            return self.ltc

    def determine_trades(self, product_id, period_list, indicators):
        self.update_amounts(indicators)

        if self.is_live:
            amount_of_coin = self.get_base_currency_from_product_id(product_id)

            new_buy_flag = True
            new_sell_flag = False
            for cur_period in period_list:
                new_buy_flag = new_buy_flag and Decimal(indicators[cur_period.name]['macd_hist_diff']) > Decimal('0.0')
                new_sell_flag = new_sell_flag or Decimal(indicators[cur_period.name]['macd_hist_diff']) < Decimal('0.0')

            if product_id == 'LTC-BTC' or product_id == 'ETH-BTC':
                new_buy_flag = new_buy_flag and self.buy_flag[product_id[4:] + '-USD']
                new_sell_flag = new_sell_flag and self.buy_flag['BTC-USD']

            if new_buy_flag:
                if self.sell_flag[product_id]:
                    self.last_signal_switch[product_id] = time.time()
                self.sell_flag[product_id] = False
                self.buy_flag[product_id] = True
                # Throttle to prevent flip flopping over trade signal
                if self.get_quoted_currency_from_product_id(product_id) > Decimal('0.0') and (time.time() - self.last_signal_switch[product_id]) > 60.0:
                    if not self.order_in_progress[product_id]:
                        self.order_thread = threading.Thread(target=self.buy, name='buy_thread', kwargs={'product_id': product_id})
                        self.order_thread.start()
            elif new_sell_flag:
                if self.buy_flag[product_id]:
                    self.last_signal_switch[product_id] = time.time()
                self.buy_flag[product_id] = False
                self.sell_flag[product_id] = True
                # Throttle to prevent flip flopping over trade signal
                if amount_of_coin > Decimal('0.0') and (time.time() - self.last_signal_switch[product_id]) > 60.0:
                    if not self.order_in_progress[product_id]:
                        self.order_thread = threading.Thread(target=self.sell, name='sell_thread', kwargs={'product_id': product_id})
                        self.order_thread.start()
            else:
                self.buy_flag[product_id] = False
                self.sell_flag[product_id] = False
