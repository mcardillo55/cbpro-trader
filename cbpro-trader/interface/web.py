from flask import Flask, jsonify

class ProductsView(object):
    def index(self):
        return "Hello World!"

class web(object):
    def __init__(self, indicator_subsys):
        self.indicator_subsys = indicator_subsys
        self.app = Flask(__name__)
        self.app.add_url_rule('/periods/', 'periods', self.periods)
    
    def periods(self):
        return jsonify(self.indicator_subsys.get_period_data())

    def start(self):
        self.app.run()