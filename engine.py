#
# engine.py
# Mike Cardillo
#
# Subsystem containing all trading logic and execution


class TradeEngine():
    def __init__(self, auth_client):
        self.auth_client = auth_client
        self.usd = self.get_usd()
        self.btc = self.get_btc()

    def get_usd(self):
        usd_str = self.auth_client.get_accounts()[0]['available']
        usd_str = usd_str.split('.')
        return usd_str[0] + '.' + usd_str[1][:2]

    def get_btc(self):
        return self.auth_client.get_accounts()[3]['available']

    def update_amounts(self):
        self.get_btc()
        self.get_usd()

    def print_amounts(self):
        print "USD: %s BTC: %s" % (self.usd, self.btc)

    def buy(self, amount=None):
        if not amount:
            amount = self.get_usd()
        return self.auth_client.buy(type='market', funds=amount, product_id='BTC-USD')

    def sell(self, amount=None):
        if not amount:
            amount = self.get_btc()
        return self.auth_client.sell(type='market', size=amount, product_id='BTC-USD')

    def determine_trades(self, indicators, cur_period):
        if cur_period.cur_candlestick.volume > indicators['avg_volume']:
            if indicators['macd_hist'] > 0.0:
                # buy btc
                if float(self.usd) > 0.0:
                    print "BUYING BTC!"
                    self.buy()
                    self.update_amounts()
            elif indicators['macd_hist'] < 0.0:
                # sell btc
                if float(self.btc) > 0.0:
                    print "SELLING BTC!"
                    self.sell()
                    self.update_amounts()
        self.print_amounts()
