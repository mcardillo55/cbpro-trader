#
# bitcoin-trade.py
# Mike Cardillo
#
# Main program for interacting with GDAX websocket and managing trade data

import gdax
import dateutil.parser
import period
import trade
import Queue

websocket_queue = Queue.Queue()


class TradeAndHeartbeatWebsocket(gdax.WebsocketClient):
    def on_open(self):
        self.products = ["BTC-USD"]
        self.type = "heartbeat"

    def on_message(self, msg):
        global websocket_queue

        if msg.get('type') == "heartbeat" or msg.get('type') == "match":
            websocket_queue.put(msg)


def process_trade(msg, cur_period):
    cur_trade = trade.Trade(msg)
    if cur_period is None:
        return period.Period(cur_trade)
    else:
        cur_period.cur_candlestick.add_trade(cur_trade)
        return cur_period


def process_heartbeat(msg, cur_period, prev_minute):
    isotime = dateutil.parser.parse(msg.get('time'))
    if isotime:
        print str(isotime) + " " + str(msg.get('last_trade_id'))
        if prev_minute and isotime.minute != prev_minute:
            cur_period.close_candlestick()
            cur_period.new_candlestick(isotime)
        return isotime.minute


gdax_websocket = TradeAndHeartbeatWebsocket()

gdax_websocket.start()

cur_period = None
prev_minute = None

while(True):
    try:
        if not websocket_queue.empty():
            msg = websocket_queue.get_nowait()
            if msg.get('type') == "match":
                cur_period = process_trade(msg, cur_period)
            elif msg.get('type') == "heartbeat":
                prev_minute = process_heartbeat(msg, cur_period, prev_minute)
    except KeyboardInterrupt:
        gdax_websocket.close()
        exit()
