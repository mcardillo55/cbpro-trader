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


logging.basicConfig(format='%(message)s')
logger = logging.getLogger('trader-logger')
if config.FRONTEND == 'debug':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.CRITICAL)

gdax_websocket = TradeAndHeartbeatWebsocket()
auth_client = gdax.AuthenticatedClient(config.KEY, config.SECRET, config.PASSPHRASE)
trade_engine = engine.TradeEngine(auth_client)
five_min = period.Period(period_size=(60 * 5), name='5')
thirty_min = period.Period(period_size=(60 * 30), name='30')
period_list = [five_min, thirty_min]
period_list[0].verbose_heartbeat = True
indicator_subsys = indicators.IndicatorSubsystem(period_list)
last_indicator_update = time.time()

gdax_websocket.start()

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
            interface.update_candlesticks(five_min)
            if time.time() - last_indicator_update >= 1.0:
                for cur_period in period_list:
                    indicator_subsys.recalculate_indicators(cur_period)
                trade_engine.determine_trades(indicator_subsys.current_indicators)
                interface.update_indicators(indicator_subsys.current_indicators)
                interface.update_orders(trade_engine)
                last_indicator_update = time.time()
        elif msg.get('type') == "heartbeat":
            for cur_period in period_list:
                cur_period.process_heartbeat(msg)
                if len(indicator_subsys.current_indicators[cur_period.name]) > 0:
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
        traceback.print_exc()
        trade_engine.close()
        gdax_websocket.close()
        time.sleep(10)
        gdax_websocket.start()
        trade_engine.start()
