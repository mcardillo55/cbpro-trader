#
# engine.py
# Mike Cardillo
#
# Subsystem containing all trading logic and execution
import time


class TradeEngine():
    def __init__(self, auth_client):
        self.auth_client = auth_client
        self.usd = self.get_usd()
        self.btc = self.get_btc()
        self.last_balance_update = time.time()

    def get_usd(self):
        usd_str = self.auth_client.get_accounts()[0]['available']
        usd_str = usd_str.split('.')
        return usd_str[0] + '.' + usd_str[1][:2]

    def get_btc(self):
        return self.auth_client.get_accounts()[3]['available']

    def update_amounts(self):
        if time.time() - self.last_balance_update > 10.0:
            self.btc = self.get_btc()
            self.usd = self.get_usd()
            self.last_balance_update = time.time()

    def print_amounts(self):
        print "[BALANCES] USD: %s BTC: %s" % (self.usd, self.btc)

    def buy(self, amount=None):
        if not amount:
            amount = self.get_usd()
        ret = {}
        skew = 0.01
        print "HELLO FROM buy()"
        while ret.get('status') != 'done':
            if ret.get('status') != 'open' and ret.get('status') != 'pending':
                spread = float(self.auth_client.get_product_ticker('BTC-USD')['ask']) - float(self.auth_client.get_product_ticker('BTC-USD')['bid'])
                if spread > 0.01:
                    skew += 0.01
                else:
                    skew = 0.0
                ask = round(float(self.auth_client.get_product_ticker('BTC-USD')['bid']) + skew, 2)
                size = round(float(amount) / float(ask), 8)
                ret = self.auth_client.buy(type='limit', size=size, post_only=True, price=ask, product_id='BTC-USD')
                print ret
            if ret.get('status') == 'pending' or ret.get('status') == 'open':
                time.sleep(6)
                ret = self.auth_client.get_order(ret.get('id'))
                print ret
                print "ASK: " + str(ask)
                print "skew: " + str(skew)
                print "ASK(new): " + self.auth_client.get_product_ticker('BTC-USD')['bid']
                if ret.get('status') != 'done' and ret.get('id') and ask < float(self.auth_client.get_product_ticker('BTC-USD')['bid']):
                    self.auth_client.cancel_order(ret.get('id'))
                    ret = self.auth_client.get_order(ret.get('id'))
                    print "FROM DONEEEEEEEE*******"
                    print ret
            amount = self.get_usd()
        return ret

    def sell(self, amount=None):
        if not amount:
            amount = self.get_btc()
        ret = {}
        skew = 0.01
        while ret.get('status') != 'done':
            if ret.get('status') != 'open' and ret.get('status') != 'pending':
                spread = float(self.auth_client.get_product_ticker('BTC-USD')['ask']) - float(self.auth_client.get_product_ticker('BTC-USD')['bid'])
                if spread > 0.01:
                    skew += 0.01
                else:
                    skew = 0.0
                bid = round(float(self.auth_client.get_product_ticker('BTC-USD')['ask']) - skew, 2)
                print bid
                if amount > 0.0:
                    ret = self.auth_client.sell(type='limit', size=amount, post_only=True, price=bid, product_id='BTC-USD')
                print ret
            if ret.get('status') == 'pending' or ret.get('status') == 'open':
                time.sleep(6)
                ret = self.auth_client.get_order(ret.get('id'))
                print ret
                print "BID: " + str(bid)
                print "skew: " + str(skew)
                print "BID(new)" + self.auth_client.get_product_ticker('BTC-USD')['ask']
                if ret.get('status') != 'done' and ret.get('id') and bid > float(self.auth_client.get_product_ticker('BTC-USD')['ask']):
                    self.auth_client.cancel_order(ret.get('id'))
                    ret = self.auth_client.get_order(ret.get('id'))
                    print "FROM DONEEEEEEEE*******"
                    print ret
            amount = self.get_btc()
        return ret

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
