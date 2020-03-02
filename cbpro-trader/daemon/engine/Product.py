import time
from .OrderBookCustom import OrderBookCustom

class Product(object):
    def __init__(self, auth_client, product_id='BTC-USD'):
        self.product_id = product_id
        self.order_book = OrderBookCustom(product_id=product_id, auth_client=auth_client)
        self.order_in_progress = False
        self.buy_flag = False
        self.sell_flag = False
        self.open_orders = []
        self.order_thread = None
        self.meta = True
        self.last_signal_switch = time.time()

        cbpro_products = auth_client.get_products()
        while not isinstance(cbpro_products, list):
            # May be rate limited
            time.sleep(3)
            cbpro_products = auth_client.get_products()

        for cbpro_product in cbpro_products:
            if product_id == cbpro_product.get('id'):
                self.meta = False # If product_id is in response, it must be a real product
                self.quote_increment = cbpro_product.get('quote_increment')
                self.min_size = cbpro_product.get('base_min_size')