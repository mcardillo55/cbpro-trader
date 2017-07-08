#
# bitcoin-trade.py
# Mike Cardillo
#
# Main program for interacting with GDAX websocket and managing trade data

import gdax
import time
import dateutil.parser
import period
import trade

minute_period = None


class WebsocketMatchClient(gdax.WebsocketClient):
    def on_open(self):
        self.products = ["BTC-USD"]

    def on_message(self, msg):
        global minute_period

        if msg.get('type') == "match":
            cur_trade = trade.Trade(msg)
            if minute_period is None:
                minute_period = period.Period(cur_trade)
            else:
                minute_period.cur_candlestick.add_trade(cur_trade)


class HeartbeatClient(gdax.WebsocketClient):
    def on_open(self):
        self.type = "heartbeat"
        self.prev_minute = None

    def on_message(self, msg):
        global minute_period

        if msg.get('type') == "heartbeat":
            isotime = dateutil.parser.parse(msg.get('time'))
            if isotime:
                print str(isotime) + " " + str(msg.get('last_trade_id'))

            if self.prev_minute is None:
                self.prev_minute = isotime.minute
            elif isotime.minute != self.prev_minute:
                minute_period.new_candlestick()
                self.prev_minute = isotime.minute


gdax_websocket = WebsocketMatchClient()
heartbeat_websocket = HeartbeatClient()

gdax_websocket.start()
heartbeat_websocket.start()

while(True):
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        gdax_websocket.close()
        heartbeat_websocket.close()
        exit()
