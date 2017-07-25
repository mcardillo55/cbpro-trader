#
# bitcoin-trade.py
# Mike Cardillo
#
# Main program for interacting with GDAX websocket and managing trade data

import gdax
import dateutil.parser
import period
import trade
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

    def on_close(self):
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


def process_trade(msg, cur_period):
    cur_trade = trade.Trade(msg)
    if cur_period is None:
        return period.Period(cur_trade)
    else:
        cur_period.cur_candlestick.add_trade(cur_trade)
        cur_period.cur_candlestick.print_stick()
        return cur_period


def process_heartbeat(msg, cur_period, prev_minute):
    isotime = dateutil.parser.parse(msg.get('time'))
    if isotime:
        print "[HEARTBEAT] " + str(isotime) + " " + str(msg.get('last_trade_id'))
        if cur_period and prev_minute and isotime.minute != prev_minute:
            cur_period.close_candlestick()
            cur_period.new_candlestick(isotime)
        return isotime.minute


gdax_websocket = TradeAndHeartbeatWebsocket()
indicator_subsys = indicators.IndicatorSubsystem()
auth_client = gdax.AuthenticatedClient(config.KEY, config.SECRET, config.PASSPHRASE)
trade_engine = engine.TradeEngine(auth_client)
cur_period = None
prev_minute = None
last_indicator_update = time.time()

gdax_websocket.start()

while(True):
    msg = gdax_websocket.websocket_queue.get(timeout=1000)
    if msg.get('type') == "match":
        cur_period = process_trade(msg, cur_period)
        if time.time() - last_indicator_update >= 1.0:
            indicator_subsys.recalculate_indicators(cur_period)
            trade_engine.determine_trades(indicator_subsys.current_indicators, cur_period)
            last_indicator_update = time.time()
    elif msg.get('type') == "heartbeat":
        prev_minute = process_heartbeat(msg, cur_period, prev_minute)
