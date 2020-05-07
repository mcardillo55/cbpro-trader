import os
from flask import Flask, jsonify
from gevent.pywsgi import WSGIServer

class web(object):
    def __init__(self, indicator_subsys, trade_engine):
        self.indicator_subsys = indicator_subsys
        self.trade_engine = trade_engine
        app = Flask(__name__)
        self.app = app
    
        @app.route('/periods/')
        @app.route('/periods/<periodName>')
        def periods(periodName=None):
            period_data = []
            if periodName is None:
                for period in self.indicator_subsys.period_list:
                    period_data.append(period.name)
            else:
                for period in self.indicator_subsys.period_list:
                    if period.name == periodName:
                        period_data = period.candlesticks.tolist() + [period.cur_candlestick.to_list()]
            return jsonify(period_data)

        @app.route('/indicators/')
        @app.route('/indicators/<periodName>')
        def indicators(periodName=None):
            if periodName is None:
                return jsonify(self.indicator_subsys.current_indicators)
            else:
                return jsonify(self.indicator_subsys.current_indicators.get(periodName))

        @app.route('/orders/')
        @app.route('/orders/<productId>')
        def orders(productId=None):
            return jsonify({'orders': trade_engine.all_open_orders, 'fills': trade_engine.recent_fills})

        @app.route('/balances/')
        @app.route('/balances/<currency>')
        def balances(currency=None):
            balances = trade_engine.balances.copy()
            for key in balances:
                balances[key] = '{0:.8f}'.format(balances[key])
            return jsonify(balances)

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
        if 'PRODUCTION' in os.environ:
            http_server = WSGIServer(('', 8080), self.app)
            http_server.serve_forever()
        else:
            self.app.run(host='0.0.0.0')