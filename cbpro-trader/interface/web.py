from flask import Flask, jsonify

class web(object):
    def __init__(self, indicator_subsys, trade_engine):
        self.indicator_subsys = indicator_subsys
        self.trade_engine = trade_engine
        app = Flask(__name__)
        self.app = app
    
        @app.route('/periods/')
        @app.route('/periods/<periodName>')
        def periods(periodName=None):
            return jsonify(self.indicator_subsys.get_period_data(periodName))

        @app.route('/indicators/')
        @app.route('/indicators/<periodName>')
        def indicators(periodName=None):
            return jsonify(self.indicator_subsys.get_indicator_data(periodName))

        @app.route('/flags/')
        def flags():
            flags = {}
            for product in self.trade_engine.products:
                if product.buy_flag is True:
                    flags[product.product_id] = "buy"
                else:
                    flags[product.product_id] = "sell"
            return jsonify(flags)

    def start(self):
        self.app.run(host='0.0.0.0')