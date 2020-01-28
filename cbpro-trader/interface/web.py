from flask import Flask, jsonify

class ProductsView(object):
    def index(self):
        return "Hello World!"

class web(object):
    def __init__(self, indicator_subsys, trade_engine):
        self.indicator_subsys = indicator_subsys
        self.trade_engine = trade_engine
        self.app = Flask(__name__)

        self.app.add_url_rule('/periods/', 'periods', self.periods)
        self.app.add_url_rule('/periods/<periodName>', 'periods', self.periods)
        self.app.add_url_rule('/indicators/', 'indicators', self.indicators)
        self.app.add_url_rule('/indicators/<periodName>', 'indicators', self.indicators)
        self.app.add_url_rule('/flags/', 'flags', self.flags)
    
    def periods(self, periodName=None):
        return jsonify(self.indicator_subsys.get_period_data(periodName))

    def indicators(self, periodName=None):
        return jsonify(self.indicator_subsys.get_indicator_data(periodName))

    def flags(self):
        flags = {}
        for product in self.trade_engine.products:
            if product.buy_flag is True:
                flags[product.product_id] = "buy"
            else:
                flags[product.product_id] = "sell"
        return jsonify(flags)

    def start(self):
        self.app.run(host='0.0.0.0')