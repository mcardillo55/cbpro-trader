import copy
import cbpro
import datetime
import time
import numpy as np
import pytz
from decimal import Decimal
from .Period import Period

class MetaPeriod(Period):
    def __init__(self, period_size=60, name='Period', product='BTC-USD', fiat='USD', initialize=True, cbpro_client=cbpro.PublicClient()):
        self.base = product[:3] + '-' + fiat
        self.quoted = product[4:] + '-' + fiat
        super(MetaPeriod, self).__init__(period_size=period_size, name=name, product=product, initialize=True, cbpro_client=cbpro_client)

    def process_trade(self, msg):
        newmsg = copy.deepcopy(msg)
        if msg.get('product_id') == self.base:
            newmsg['product_id'] = self.product
            quoted_last = Decimal(msg.get('price')) / Decimal(self.cur_candlestick.close)
            total_price = quoted_last + Decimal(msg.get('price'))
            newmsg['size'] = Decimal(msg.get('size')) * (Decimal(msg.get('price')) / total_price)
            newmsg['price'] = Decimal(msg.get('price')) / quoted_last
        elif msg.get('product_id') == self.quoted:
            newmsg['product_id'] = self.product
            base_last = Decimal(self.cur_candlestick.close) * Decimal(msg.get('price'))
            total_price = base_last + Decimal(msg.get('price'))
            newmsg['size'] = Decimal(msg.get('size')) * (Decimal(msg.get('price')) / total_price)
            newmsg['price'] = base_last / Decimal(msg.get('price'))
        super(MetaPeriod, self).process_trade(msg=newmsg)

    def get_historical_data(self, num_periods=200):
        end = datetime.datetime.utcnow()
        end_iso = end.isoformat()
        start = end - datetime.timedelta(seconds=(self.period_size * num_periods))
        start_iso = start.isoformat()

        ret_base = self.cbpro_client.get_product_historic_rates(self.base, granularity=self.period_size, start=start_iso, end=end_iso)
        ret_quoted = self.cbpro_client.get_product_historic_rates(self.quoted, granularity=self.period_size, start=start_iso, end=end_iso)
        # Check if we got rate limited, which will return a JSON message
        while not isinstance(ret_base, list):
            time.sleep(3)
            ret_base = self.cbpro_client.get_product_historic_rates(self.base, granularity=self.period_size, start=start_iso, end=end_iso)
        while not isinstance(ret_quoted, list):
            time.sleep(3)
            ret_quoted = self.cbpro_client.get_product_historic_rates(self.quoted, granularity=self.period_size, start=start_iso, end=end_iso)
        hist_data_base = np.array(ret_base, dtype='object')
        hist_data_quoted = np.array(ret_quoted, dtype='object')
        array_size = min(len(ret_base), len(ret_quoted))
        hist_data_base.resize(array_size, 6)
        hist_data_quoted.resize(array_size, 6)

        for row in hist_data_base:
            row[0] = datetime.datetime.fromtimestamp(row[0], pytz.utc)
        for row in hist_data_quoted:
            row[0] = datetime.datetime.fromtimestamp(row[0], pytz.utc)

        hist_data = np.ndarray((len(hist_data_base), 6), dtype='object')
        hist_data[:, 0] = hist_data_base[:, 0]
        hist_data[:, [1,2,3,4]] = hist_data_base[:, [1,2,3,4]]/hist_data_quoted[:, [1,2,3,4]]
        total_price = (hist_data_base[:, 4] + hist_data_quoted[:, 4])
        hist_data[:, 5] = ((hist_data_base[:, 4] / total_price) * hist_data_base[:, 5]) + ((hist_data_base[:, 4] / total_price)  * hist_data_quoted[:, 5])
        hist_data[:, 5] = hist_data[:, 5] * hist_data[:, 4]
        return np.flipud(hist_data)