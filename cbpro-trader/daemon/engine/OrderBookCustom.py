import cbpro
import time
import logging

class OrderBookCustom(cbpro.OrderBook):
    def __init__(self, product_id='BTC-USD', auth_client=None):
        self.logger = logging.getLogger('trader-logger')
        self.error_logger = logging.getLogger('error-logger')
        super(OrderBookCustom, self).__init__(product_id=product_id)
        if auth_client is not None:
            self._client = auth_client

    def is_ready(self):
        try:
            super(OrderBookCustom, self).get_ask()
        except (ValueError, AttributeError):
            return False
        return True
    def process_message(self, msg):
        try:
            super(OrderBookCustom, self).process_message(msg)
        except (ValueError, AttributeError):
            return False
        return True
    def get_ask(self):
        while not self.is_ready():
            time.sleep(0.01)
        return super(OrderBookCustom, self).get_ask()

    def get_bid(self):
        while not self.is_ready():
            time.sleep(0.01)
        return super(OrderBookCustom, self).get_bid()