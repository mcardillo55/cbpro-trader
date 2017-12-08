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


class Product(object):
    def __init__(self, auth_client, product_id='BTC-USD'):
        self.product_id = product_id
        self.order_book = OrderBookCustom(product_id=product_id)
        self.order_in_progress = False
        self.buy_flag = False
        self.sell_flag = False
        self.last_signal_switch = time.time()
        for gdax_product in auth_client.get_products():
                if product_id == gdax_product.get('id'):
                    self.quote_increment = gdax_product.get('quote_increment')
                    self.min_size = gdax_product.get('base_min_size')


class TradeEngine():
    def __init__(self, auth_client, product_list=['BTC-USD', 'ETH-USD', 'LTC-USD'], is_live=False):
        self.logger = logging.getLogger('trader-logger')
        self.error_logger = logging.getLogger('error-logger')
        self.auth_client = auth_client
        self.product_list = product_list
        self.is_live = is_live
        self.products = []
        for product in self.product_list:
            self.products.append(Product(auth_client, product_id=product))
        self.last_balance_update = 0
        self.update_amounts()
        self.usd_equivalent = 0
        self.last_balance_update = time.time()
        self.order_thread = threading.Thread()

    def close(self):
        for product in self.products:
            # Setting both flags will close any open order threads
            product.buy_flag = False
            product.sell_flag = False
            # Cancel any orders that may still be remaining
            product.order_in_progress = False
        try:
            self.auth_client.cancel_all()
        except Exception:
            self.error_logger.exception(datetime.datetime.now())

    def get_product_by_product_id(self, product_id='BTC-USD'):
        for product in self.products:
            if product.product_id == product_id:
                return product
        return None

    def round_usd(self, money):
        return Decimal(money).quantize(Decimal('.01'), rounding=ROUND_DOWN)

    def round_coin(self, money):
        return Decimal(money).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)

    def update_amounts(self):
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
            for product in self.products:
                if product.order_book.get_current_ticker() and product.order_book.get_current_ticker().get('price'):
                    self.usd_equivalent += self.get_base_currency_from_product_id(product.product_id) * Decimal(product.order_book.get_current_ticker().get('price'))
            self.usd_equivalent += self.usd

    def print_amounts(self):
        self.logger.debug("[BALANCES] USD: %.2f BTC: %.8f" % (self.usd, self.btc))

    def place_buy(self, product=None, partial='1.0'):
        amount = self.get_quoted_currency_from_product_id(product.product_id) * Decimal(partial)
        bid = product.order_book.get_ask() - Decimal(product.quote_increment)
        amount = self.round_coin(Decimal(amount) / Decimal(bid))

        if amount < Decimal(product.min_size):
            amount = self.get_quoted_currency_from_product_id(product.product_id)
            bid = product.order_book.get_ask() - Decimal(product.quote_increment)
            amount = self.round_coin(Decimal(amount) / Decimal(bid))

        if amount >= Decimal(product.min_size):
            self.logger.debug("Placing buy... Price: %.8f Size: %.8f" % (bid, amount))
            return self.auth_client.buy(type='limit', size=str(amount),
                                        price=str(bid), post_only=True,
                                        product_id=product.product_id)
        else:
            ret = {'status': 'done'}
            return ret

    def buy(self, product=None, amount=None):
        product.order_in_progress = True
        try:
            ret = self.place_buy(product=product, partial='0.5')
            bid = ret.get('price')
            amount = self.get_quoted_currency_from_product_id(product.product_id)
            while product.buy_flag and (amount > Decimal('0.0') or len(self.auth_client.get_orders()[0]) > 0):
                if ret.get('status') == 'rejected' or ret.get('status') == 'done' or ret.get('message') == 'NotFound':
                    ret = self.place_buy(product=product, partial='0.5')
                    bid = ret.get('price')
                elif not bid or Decimal(bid) < product.order_book.get_ask() - Decimal(product.quote_increment):
                    if len(self.auth_client.get_orders()[0]) > 0:
                        ret = self.place_buy(product=product, partial='1.0')
                    else:
                        ret = self.place_buy(product=product, partial='0.5')
                    for order in self.auth_client.get_orders()[0]:
                        if order.get('id') != ret.get('id'):
                            self.auth_client.cancel_order(order.get('id'))
                    bid = ret.get('price')
                if ret.get('id'):
                    ret = self.auth_client.get_order(ret.get('id'))
                amount = self.get_quoted_currency_from_product_id(product.product_id)
            self.auth_client.cancel_all(product_id=product.product_id)
            amount = self.get_quoted_currency_from_product_id(product.product_id)
        except Exception:
            product.order_in_progress = False
            self.error_logger.exception(datetime.datetime.now())
        self.auth_client.cancel_all(product_id=product.product_id)
        product.order_in_progress = False

    def place_sell(self, product=None, partial='1.0'):
        amount = self.round_coin(self.get_base_currency_from_product_id(product.product_id) * Decimal(partial))
        if amount < Decimal(product.min_size):
            amount = self.get_base_currency_from_product_id(product.product_id)
        ask = product.order_book.get_bid() + Decimal(product.quote_increment)

        if amount >= Decimal(product.min_size):
            self.logger.debug("Placing sell... Price: %.2f Size: %.8f" % (ask, amount))
            return self.auth_client.sell(type='limit', size=str(amount),
                                         price=str(ask), post_only=True,
                                         product_id=product.product_id)
        else:
            ret = {'status': 'done'}
            return ret

    def sell(self, product=None, amount=None):
        product.order_in_progress = True
        try:
            ret = self.place_sell(product=product, partial='0.5')
            ask = ret.get('price')
            amount = self.get_base_currency_from_product_id(product.product_id)
            while product.sell_flag and (amount >= Decimal(product.min_size) or len(self.auth_client.get_orders()[0]) > 0):
                if ret.get('status') == 'rejected' or ret.get('status') == 'done' or ret.get('message') == 'NotFound':
                    ret = self.place_sell(product=product, partial='0.5')
                    ask = ret.get('price')
                elif not ask or Decimal(ask) > product.order_book.get_bid() + Decimal(product.quote_increment):
                    if len(self.auth_client.get_orders()[0]) > 0:
                        ret = self.place_sell(product=product, partial='1.0')
                    else:
                        ret = self.place_sell(product=product, partial='0.5')
                    for order in self.auth_client.get_orders()[0]:
                        if order.get('id') != ret.get('id'):
                            self.auth_client.cancel_order(order.get('id'))
                    ask = ret.get('price')
                if ret.get('id'):
                    ret = self.auth_client.get_order(ret.get('id'))
                amount = self.get_base_currency_from_product_id(product.product_id)
            self.auth_client.cancel_all(product_id=product.product_id)
            amount = self.get_base_currency_from_product_id(product.product_id)
        except Exception:
            product.order_in_progress = False
            self.error_logger.exception(datetime.datetime.now())
        self.auth_client.cancel_all(product_id=product.product_id)
        product.order_in_progress = False

    def get_base_currency_from_product_id(self, product_id):
        self.update_amounts()
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
        self.update_amounts()
        if product_id == 'BTC-USD':
            return self.usd
        elif product_id == 'ETH-USD':
            return self.usd
        elif product_id == 'LTC-USD':
            return self.usd
        elif product_id == 'ETH-BTC':
            return self.btc
        elif product_id == 'LTC-BTC':
            return self.btc

    def determine_trades(self, product_id, period_list, indicators):
        self.update_amounts()

        if self.is_live:
            amount_of_coin = self.get_base_currency_from_product_id(product_id)
            product = self.get_product_by_product_id(product_id)

            new_buy_flag = True
            new_sell_flag = False
            for cur_period in period_list:
                if cur_period.period_size == (60 * 30):
                    new_buy_flag = new_buy_flag and Decimal(indicators[cur_period.name]['macd_hist']) > Decimal('0.0') and \
                                                    Decimal(indicators[cur_period.name]['macd_hist_diff']) > Decimal('0.0') and \
                                                    Decimal(indicators[cur_period.name]['obv']) > Decimal(indicators[cur_period.name]['obv_ema'])
                    new_sell_flag = new_sell_flag or Decimal(indicators[cur_period.name]['macd_hist']) < Decimal('0.0') or \
                                                     Decimal(indicators[cur_period.name]['obv']) < Decimal(indicators[cur_period.name]['obv_ema'])
                elif cur_period.period_size == (60 * 5):
                    new_buy_flag = new_buy_flag and Decimal(indicators[cur_period.name]['macd_hist']) > Decimal('0.0') and \
                                                    Decimal(indicators[cur_period.name]['macd_hist_diff']) > Decimal('0.0')
                    new_sell_flag = new_sell_flag or Decimal(indicators[cur_period.name]['macd_hist']) < Decimal('0.0') or \
                                                     Decimal(indicators[cur_period.name]['macd_hist_diff']) < Decimal('0.0')

            if product_id == 'LTC-BTC' or product_id == 'ETH-BTC':
                ltc_or_eth_usd_product = self.get_product_by_product_id(product_id[:3] + '-USD')
                btc_usd_product = self.get_product_by_product_id('BTC-USD')
                new_buy_flag = new_buy_flag and ltc_or_eth_usd_product.buy_flag
                new_sell_flag = new_sell_flag and btc_usd_product.buy_flag

            if new_buy_flag:
                if product.sell_flag:
                    product.last_signal_switch = time.time()
                product.sell_flag = False
                product.buy_flag = True
                # Throttle to prevent flip flopping over trade signal
                if self.get_quoted_currency_from_product_id(product_id) > Decimal('0.0') and (time.time() - product.last_signal_switch) > 60.0:
                    if not product.order_in_progress:
                        self.order_thread = threading.Thread(target=self.buy, name='buy_thread', kwargs={'product': product})
                        self.order_thread.start()
            elif new_sell_flag:
                if product.buy_flag:
                    product.last_signal_switch = time.time()
                product.buy_flag = False
                product.sell_flag = True
                # Throttle to prevent flip flopping over trade signal
                if amount_of_coin > Decimal('0.0') and (time.time() - product.last_signal_switch) > 60.0:
                    if not product.order_in_progress:
                        self.order_thread = threading.Thread(target=self.sell, name='sell_thread', kwargs={'product': product})
                        self.order_thread.start()
            else:
                product.buy_flag = False
                product.sell_flag = False
