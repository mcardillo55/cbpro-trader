#
# bitcoin-trade.py
# Mike Cardillo
#
# Main program for interacting with GDAX websocket and managing trade data

import gdax
import period
import indicators
import engine
import config
import Queue
import time
import traceback
import curses_interface
import logging
from websocket import WebSocketConnectionClosedException


class TradeAndHeartbeatWebsocket(gdax.WebsocketClient):
    def __init__(self):
        self.logger = logging.getLogger('trader-logger')
        super(TradeAndHeartbeatWebsocket, self).__init__()

    def on_open(self):
        self.products = ["BTC-USD"]
        self.type = "heartbeat"
        self.websocket_queue = Queue.Queue()
        self.stop = False
        self.logger.debug("-- GDAX Websocket Opened ---")

    def on_close(self):
        self.logger.debug("-- GDAX Websocket Closed ---")

    def on_error(self, e):
        raise e

    def close(self):
        if not self.stop:
            self.on_close()
            self.stop = True
            self.thread.join()
            try:
                if self.ws:
                    self.ws.close()
            except WebSocketConnectionClosedException as e:
                pass

    def on_message(self, msg):
        if msg.get('type') == "heartbeat" or msg.get('type') == "match":
            self.websocket_queue.put(msg)


logger = logging.getLogger('trader-logger')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("debug.log"))
if config.FRONTEND == 'debug':
    logger.addHandler(logging.StreamHandler())

gdax_websocket = TradeAndHeartbeatWebsocket()
auth_client = gdax.AuthenticatedClient(config.KEY, config.SECRET, config.PASSPHRASE)
trade_engine = engine.TradeEngine(auth_client, is_live=config.LIVE)
one_min = period.Period(period_size=(60 * 1), name='1')
period_list = [one_min]
gdax_websocket.start()
period_list[0].verbose_heartbeat = True
indicator_subsys = indicators.IndicatorSubsystem(period_list)
last_indicator_update = time.time()

if config.FRONTEND == 'curses':
    curses_enable = True
else:
    curses_enable = False
interface = curses_interface.cursesDisplay(enable=curses_enable)

while(True):
    try:
        msg = gdax_websocket.websocket_queue.get(timeout=15)
        if msg.get('type') == "match":
            for cur_period in period_list:
                cur_period.process_trade(msg)
            interface.update_candlesticks(one_min)
            if time.time() - last_indicator_update >= 1.0:
                for cur_period in period_list:
                    indicator_subsys.recalculate_indicators(cur_period, trade_engine.order_book)
                trade_engine.determine_trades(indicator_subsys.current_indicators)
                interface.update_indicators(indicator_subsys.current_indicators)
                interface.update_orders(trade_engine)
                last_indicator_update = time.time()
        elif msg.get('type') == "heartbeat":
            for cur_period in period_list:
                cur_period.process_heartbeat(msg)
                if len(indicator_subsys.current_indicators[cur_period.name]['bid']) > 0:
                    trade_engine.determine_trades(indicator_subsys.current_indicators)
            trade_engine.print_amounts()
            interface.update_heartbeat(msg)
            interface.update_balances(trade_engine.get_btc(), trade_engine.get_usd())
    except KeyboardInterrupt:
        trade_engine.close()
        gdax_websocket.close()
        interface.close()
        break
    except Exception as e:
        logger.debug(traceback.format_exc())
        trade_engine.close()
        gdax_websocket.close()
        # Period data cannot be trusted. Re-initialize
        for cur_period in period_list:
            cur_period.initialize()
        time.sleep(10)
        gdax_websocket.start()
        trade_engine.start()
