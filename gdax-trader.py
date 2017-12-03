#
# bitcoin-trade.py
# Mike Cardillo
#
# Main program for interacting with GDAX websocket and managing trade data

import gdax
import period
import indicators
import engine
import yaml
import Queue
import time
import curses_interface
import logging
import datetime
from websocket import WebSocketConnectionClosedException


class TradeAndHeartbeatWebsocket(gdax.WebsocketClient):
    def __init__(self):
        self.logger = logging.getLogger('trader-logger')
        self.error_logger = logging.getLogger('error-logger')
        super(TradeAndHeartbeatWebsocket, self).__init__()

    def on_open(self):
        self.products = ["BTC-USD", 'ETH-USD', 'LTC-USD', 'ETH-BTC', 'LTC-BTC']
        self.type = "heartbeat"
        self.websocket_queue = Queue.Queue()
        self.stop = False
        self.logger.debug("-- GDAX Websocket Opened ---")

    def on_close(self):
        self.logger.debug("-- GDAX Websocket Closed ---")

    def on_error(self, e):
        self.error_logger.exception(datetime.datetime.now())

    def close(self):
        if not self.stop:
            self.on_close()
            self.stop = True
            self.thread.join()
            try:
                if self.ws:
                    self.ws.close()
            except WebSocketConnectionClosedException:
                self.error_logger.exception(datetime.datetime.now())
                pass

    def on_message(self, msg):
        self.websocket_queue.put(msg)


with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)
logger = logging.getLogger('trader-logger')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("debug.log"))
if config['frontend'] == 'debug':
    logger.addHandler(logging.StreamHandler())
error_logger = logging.getLogger('error-logger')
error_logger.addHandler(logging.FileHandler("error.log"))

# Periods to update indicators for
indicator_period_list = []
# Periods to actively trade on (typically 1 per product)
trade_period_list = []
# List of products that we are actually monitoring
product_list = set()
for cur_period in config['periods']:
    new_period = period.Period(period_size=(60 * cur_period['length']),
                               product=cur_period['product'], name=cur_period['name'])
    indicator_period_list.append(new_period)
    product_list.add(cur_period['product'])
    if cur_period['trade']:
        trade_period_list.append(new_period)

auth_client = gdax.AuthenticatedClient(config['key'], config['secret'], config['passphrase'])
trade_engine = engine.TradeEngine(auth_client, product_list=product_list, is_live=config['live'])
gdax_websocket = TradeAndHeartbeatWebsocket()
gdax_websocket.start()
indicator_period_list[0].verbose_heartbeat = True
indicator_subsys = indicators.IndicatorSubsystem(indicator_period_list)
last_indicator_update = time.time()

if config['frontend'] == 'curses':
    curses_enable = True
else:
    curses_enable = False
interface = curses_interface.cursesDisplay(enable=curses_enable)

while(True):
    try:
        msg = gdax_websocket.websocket_queue.get(timeout=15)
        for product_id, order_book in trade_engine.order_book.iteritems():
            order_book.process_message(msg)
        if msg.get('type') == "match":
            for cur_period in indicator_period_list:
                cur_period.process_trade(msg)
            if time.time() - last_indicator_update >= 1.0:
                for cur_period in indicator_period_list:
                    indicator_subsys.recalculate_indicators(cur_period)
                for cur_period in trade_period_list:
                    trade_engine.determine_trades(cur_period, indicator_subsys.current_indicators)
                last_indicator_update = time.time()
        elif msg.get('type') == "heartbeat":
            for cur_period in indicator_period_list:
                cur_period.process_heartbeat(msg)
            for cur_period in trade_period_list:
                if len(indicator_subsys.current_indicators[cur_period.name]) > 0:
                    trade_engine.determine_trades(cur_period, indicator_subsys.current_indicators)
            trade_engine.print_amounts()
        interface.update(trade_engine, indicator_subsys.current_indicators,
                         indicator_period_list, msg)
    except KeyboardInterrupt:
        trade_engine.close()
        gdax_websocket.close()
        interface.close()
        break
    except Exception as e:
        error_logger.exception(datetime.datetime.now())
        trade_engine.close()
        gdax_websocket.close()
        # Period data cannot be trusted. Re-initialize
        for cur_period in indicator_period_list:
            cur_period.initialize()
        time.sleep(10)
        gdax_websocket.start()
