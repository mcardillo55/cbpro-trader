import datetime
import logging
import queue
import cbpro
from websocket import WebSocketConnectionClosedException

class TradeAndHeartbeatWebsocket(cbpro.WebsocketClient):
    def __init__(self, fiat='USD', sandbox=False):
        self.logger = logging.getLogger('trader-logger')
        self.error_logger = logging.getLogger('error-logger')
        self.fiat_currency = fiat
        self.products = ["BTC-" + self.fiat_currency, "ETH-" + self.fiat_currency]
        self.channels = ['full', 'heartbeat']
        if sandbox:
            url="wss://ws-feed-public.sandbox.pro.coinbase.com"
        else:
            url="wss://ws-feed.pro.coinbase.com"
        super(TradeAndHeartbeatWebsocket, self).__init__(products=self.products, channels=self.channels, url=url)


    def on_open(self):
        self.websocket_queue = queue.Queue()
        self.stop = False
        self.logger.debug("-- CBPRO Websocket Opened ---")

    def on_close(self):
        self.logger.debug("-- CBPRO Websocket Closed ---")

    def on_error(self, e):
        self.error_logger.exception(datetime.datetime.now())
        self.error = e
        self.stop = True
        raise e

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