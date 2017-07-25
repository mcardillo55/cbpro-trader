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
from websocket import WebSocketConnectionClosedException



class TradeAndHeartbeatWebsocket(gdax.WebsocketClient):
    def on_open(self):
        self.products = ["BTC-USD"]
        self.type = "heartbeat"
        self.websocket_queue = Queue.Queue()

    def close(self):
        if not self.stop:
            self.on_close()
            self.stop = True
            try:
                if self.ws:
                    self.ws.close()
            except WebSocketConnectionClosedException as e:
                pass

    def on_message(self, msg):
        if msg.get('type') == "heartbeat" or msg.get('type') == "match":
            self.websocket_queue.put(msg)

    def on_error(self, e):
        print e
        print "websocket onerror"
        self.close()
        self.websocket_queue = Queue.Queue()
        time.sleep(10)
        self.start()


gdax_websocket = TradeAndHeartbeatWebsocket()
indicator_subsys = indicators.IndicatorSubsystem()
auth_client = gdax.AuthenticatedClient(config.KEY, config.SECRET, config.PASSPHRASE)
trade_engine = engine.TradeEngine(auth_client)
cur_period = period.Period()
last_indicator_update = time.time()

gdax_websocket.start()

while(True):
    msg = gdax_websocket.websocket_queue.get(timeout=1000)
    if msg.get('type') == "match":
        cur_period.process_trade(msg)
        if time.time() - last_indicator_update >= 1.0:
            indicator_subsys.recalculate_indicators(cur_period)
            trade_engine.determine_trades(indicator_subsys.current_indicators, cur_period)
            last_indicator_update = time.time()
    elif msg.get('type') == "heartbeat":
        if cur_period:
            cur_period.process_heartbeat(msg)
