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
    def __init__(self, auth_client, is_live=False):
        self.logger = logging.getLogger('trader-logger')
        self.error_logger = logging.getLogger('error-logger')
        self.auth_client = auth_client
        self.is_live = is_live
        self.order_book = {
                            'BTC-USD': OrderBookCustom(product_id='BTC-USD'),
                            'ETH-USD': OrderBookCustom(product_id='ETH-USD'),
                            'LTC-USD': OrderBookCustom(product_id='LTC-USD')
                          }
        self.last_balance_update = 0
        self.update_amounts()
        self.usd_equivalent = 0
        self.last_balance_update = time.time()
        self.order_thread = threading.Thread()
        self.order_in_progress= {
                                'BTC-USD': False,
                                'ETH-USD': False,
                                'LTC-USD': False
                                }

        self.buy_flag = {
                            'BTC-USD': False,
                            'ETH-USD': False,
                            'LTC-USD': False
                        }
        self.sell_flag = {
                            'BTC-USD': False,
                            'ETH-USD': False,
                            'LTC-USD': False
                        }

    def close(self):
        # Setting both flags will close any open order threads
        self.buy_flag = {
                            'BTC-USD': False,
                            'ETH-USD': False,
                            'LTC-USD': False
                        }
        self.sell_flag = {
                            'BTC-USD': False,
                            'ETH-USD': False,
                            'LTC-USD': False
                        }
        # Cancel any orders that may still be remaining
        self.order_in_progress= {
                                'BTC-USD': False,
                                'ETH-USD': False,
                                'LTC-USD': False
                                }
        try:
            self.auth_client.cancel_all()
        except Exception:
            self.error_logger.exception(datetime.datetime.now())

    def get_usd(self):
        try:
            for account in self.auth_client.get_accounts():
                if account.get('currency') == 'USD':
                    return self.round_usd(account.get('available'))
        except AttributeError:
            return self.round_usd('0.0')

    def get_btc(self, product_id='BTC-USD'):
        try:
            for account in self.auth_client.get_accounts():
                if account.get('currency') == product_id[:3]:
                    return self.round_coin(account.get('available'))
            return self.round_coin(auth_client.get_accounts()[0]['available'])
        except AttributeError:
            return self.round_coin('0.0')

    def round_usd(self, money):
        return Decimal(money).quantize(Decimal('.01'), rounding=ROUND_DOWN)

    def round_coin(self, money):
        return Decimal(money).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)

    def update_amounts(self, indicators=None):
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
            if indicators and indicators['LTC30'].get('close'):
                self.usd_equivalent = self.btc * Decimal(indicators['BTC30']['close']) + \
                                      self.eth * Decimal(indicators['ETH30']['close']) + \
                                      self.ltc * Decimal(indicators['LTC30']['close']) + self.usd
            self.last_balance_update = time.time()

    def print_amounts(self):
        self.logger.debug("[BALANCES] USD: %.2f BTC: %.8f" % (self.usd, self.btc))

    def place_buy(self, product_id='BTC-USD', partial='1.0'):
        amount = self.get_usd() * Decimal(partial)
        bid = self.order_book[product_id].get_ask() - Decimal('0.01')
        amount = self.round_coin(Decimal(amount) / Decimal(bid))

        if amount < Decimal('0.01'):
            amount = self.get_usd()
            bid = self.order_book[product_id].get_ask() - Decimal('0.01')
            amount = self.round_coin(Decimal(amount) / Decimal(bid))

        if amount >= Decimal('0.01'):
            self.logger.debug("Placing buy... Price: %.2f Size: %.8f" % (bid, amount))
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
            usd = self.get_usd()
            while self.buy_flag[product_id] and (usd > Decimal('0.0') or len(self.auth_client.get_orders()[0]) > 0):
                if ret.get('status') == 'rejected' or ret.get('status') == 'done' or ret.get('message') == 'NotFound':
                    ret = self.place_buy(product_id=product_id, partial='0.5')
                    bid = ret.get('price')
                elif not bid or Decimal(bid) < self.order_book[product_id].get_ask() - Decimal('0.01'):
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
                usd = self.get_usd()
            self.auth_client.cancel_all(product_id=product_id)
            usd = self.get_usd()
        except Exception as e:
            self.order_in_progress[product_id] = False
            self.error_logger.exception(datetime.datetime.now())
        self.auth_client.cancel_all(product_id=product_id)
        self.order_in_progress[product_id] = False

    def place_sell(self, product_id='BTC-USD', partial='1.0'):
        amount = self.round_coin(self.get_btc(product_id=product_id) * Decimal(partial))
        if amount < Decimal('0.01'):
            amount = self.get_btc(product_id=product_id)
        ask = self.order_book[product_id].get_bid() + Decimal('0.01')

        if amount >= Decimal('0.01'):
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
            btc = self.get_btc(product_id=product_id)
            while self.sell_flag[product_id] and (btc >= Decimal('0.01') or len(self.auth_client.get_orders()[0]) > 0):
                if ret.get('status') == 'rejected' or ret.get('status') == 'done' or ret.get('message') == 'NotFound':
                    ret = self.place_sell(product_id=product_id, partial='0.5')
                    ask = ret.get('price')
                elif not ask or Decimal(ask) > self.order_book[product_id].get_bid() + Decimal('0.01'):
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
                btc = self.get_btc(product_id=product_id)
            self.auth_client.cancel_all(product_id=product_id)
            btc = self.get_btc(product_id=product_id)
        except Exception as e:
            self.order_in_progress[product_id] = False
            self.error_logger.exception(datetime.datetime.now())
        self.auth_client.cancel_all(product_id=product_id)
        self.order_in_progress[product_id] = False

    def get_currency_size_and_product_id_from_period_name(self, period_name):
        if period_name is 'BTC30':
            return self.btc, 'BTC-USD'
        elif period_name is 'ETH30':
            return self.eth, 'ETH-USD'
        elif period_name is 'LTC30':
            return self.ltc, 'LTC-USD'

    def determine_trades(self, period_name, indicators):
        self.update_amounts(indicators)
        if not self.is_live:
            return

        amount_of_coin, product_id = self.get_currency_size_and_product_id_from_period_name(period_name)

        if Decimal(indicators[period_name]['close']) > Decimal(indicators[period_name]['bband_upper_1']):
            self.sell_flag[product_id] = False
            self.buy_flag[product_id] = True
            if self.usd > Decimal('0.0'):
                if not self.order_in_progress[product_id]:
                    self.order_thread = threading.Thread(target=self.buy, name='buy_thread', kwargs={'product_id': product_id})
                    self.order_thread.start()
        elif Decimal(indicators[period_name]['close']) < Decimal(indicators[period_name]['bband_upper_1']):
            self.buy_flag[product_id] = False
            self.sell_flag[product_id] = True
            if amount_of_coin > Decimal('0.0'):
                if not self.order_in_progress[product_id]:
                    self.order_thread = threading.Thread(target=self.sell, name='sell_thread', kwargs={'product_id': product_id})
                    self.order_thread.start()
        else:
            self.buy_flag[product_id] = False
            self.sell_flag[product_id] = False
