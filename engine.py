#
# engine.py
# Mike Cardillo
#
# Subsystem containing all trading logic and execution
import time
import gdax
from decimal import *


class OrderBookNoRestart(gdax.OrderBook):
    def on_error(self, e):
        print e


class TradeEngine():
    def __init__(self, auth_client):
        self.auth_client = auth_client
        self.order_book = OrderBookNoRestart()
        self.usd = self.get_usd()
        self.btc = self.get_btc()
        self.last_balance_update = time.time()
        self.order_book.start()
        self.last_balance_update = time.time()

    def get_usd(self):
        return self.round_usd(self.auth_client.get_accounts()[1]['available'])

    def get_btc(self):
        return self.round_btc(self.auth_client.get_accounts()[0]['available'])

    def round_usd(self, money):
        return Decimal(money).quantize(Decimal('.01'), rounding=ROUND_DOWN)

    def round_btc(self, money):
        return Decimal(money).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)

    def update_amounts(self):
        if time.time() - self.last_balance_update > 10.0:
            self.btc = self.get_btc()
            self.usd = self.get_usd()
            self.last_balance_update = time.time()

    def print_amounts(self):
        print "[BALANCES] USD: %.2f BTC: %.8f" % (self.usd, self.btc)

    def place_buy(self):
        amount = self.get_usd()
        bid = self.order_book.get_ask() - Decimal('0.01')
        amount = self.round_btc(Decimal(amount) / Decimal(bid))

        return self.auth_client.buy(type='limit', size=str(amount),
                                    price=str(bid), post_only=True,
                                    product_id='BTC-USD')

    def buy(self, amount=None):
        ret = self.place_buy()
        bid = ret.get('price')
        while ret.get('status') != 'done':
            if ret.get('status') == 'rejected':
                ret = self.place_buy()
                bid = ret.get('price')
            elif Decimal(bid) < self.order_book.get_ask() - Decimal('0.01'):
                if ret.get('id'):
                    self.auth_client.cancel_order(ret.get('id'))
                while self.get_usd() == Decimal('0.0') and ret.get('status') != 'done':
                    time.sleep(1)
                    if ret.get('id'):
                        ret = self.auth_client.get_order(ret.get('id'))
                if ret.get('status') != 'done':
                    ret = self.place_buy()
                    bid = ret.get('price')
            if ret.get('id'):
                ret = self.auth_client.get_order(ret.get('id'))

    def place_sell(self):
        amount = self.get_btc()
        ask = self.order_book.get_bid() + Decimal('0.01')

        return self.auth_client.sell(type='limit', size=str(amount),
                                     price=str(ask), post_only=True,
                                     product_id='BTC-USD')

    def sell(self, amount=None):
        ret = self.place_sell()
        ask = ret.get('price')
        while ret.get('status') != 'done':
            if ret.get('status') == 'rejected':
                ret = self.place_sell()
                ask = ret.get('price')
            elif Decimal(ask) > self.order_book.get_bid() + Decimal('0.01'):
                if ret.get('id'):
                    self.auth_client.cancel_order(ret.get('id'))
                while self.get_btc() == Decimal('0.0') and ret.get('status') != 'done':
                    time.sleep(1)
                    if ret.get('id'):
                        ret = self.auth_client.get_order(ret.get('id'))
                if ret.get('status') != 'done':
                    ret = self.place_sell()
                    ask = ret.get('price')
            if ret.get('id'):
                ret = self.auth_client.get_order(ret.get('id'))

    def determine_trades(self, indicators, cur_period):
        self.update_amounts()
        if indicators['vol_macd_hist'] > 0.0:
            if indicators['macd_hist'] > 0.0:
                # buy btc
                if float(self.usd) > 0.0:
                    print "BUYING BTC!"
                    self.buy()
                    self.usd = self.get_usd()
            elif indicators['macd_hist'] < 0.0:
                # sell btc
                if float(self.btc) >= 0.01:
                    print "SELLING BTC!"
                    self.sell()
                    self.btc = self.get_btc()
        self.print_amounts()
