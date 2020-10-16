#
# bitcoin-trade.py
# Mike Cardillo
#
# Main program for interacting with Coinbase Pro websocket and managing trade data

import cbpro
import period
import indicators
import engine
import yaml
import queue
import time
import interface
import logging
import datetime
import threading
from decimal import Decimal
from websocket import WebSocketConnectionClosedException

class CBProTrader(object):
    def __init__(self):
        with open("config.yml", 'r') as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.Loader)
        
        self.logger = logging.getLogger('trader-logger')
        self.logger.setLevel(logging.DEBUG)
        if config['logging']:
            self.logger.addHandler(logging.FileHandler("debug.log"))
        if config['frontend'] == 'debug':
            self.logger.addHandler(logging.StreamHandler())
        self.error_logger = logging.getLogger('error-logger')
        self.error_logger.addHandler(logging.FileHandler("error.log"))

        # Periods to update indicators for
        self.indicator_period_list = []
        # Periods to actively trade on (typically 1 per product)
        self.trade_period_list = {}
        # List of products that we are actually monitoring
        self.product_list = set()
        fiat_currency = config['fiat']

        if config['sandbox']:
            api_url = "https://api-public.sandbox.pro.coinbase.com"
        else:
            api_url = "https://api.pro.coinbase.com"

        auth_client = cbpro.AuthenticatedClient(config['key'], config['secret'], config['passphrase'], api_url=api_url)

        for cur_period in config['periods']:
            if cur_period.get('meta'):
                new_period = period.MetaPeriod(period_size=(60 * cur_period['length']), fiat=fiat_currency,
                                            product=cur_period['product'], name=cur_period['name'], cbpro_client=auth_client)
            else:
                new_period = period.Period(period_size=(60 * cur_period['length']),
                                        product=cur_period['product'], name=cur_period['name'], cbpro_client=auth_client)
            self.indicator_period_list.append(new_period)
            self.product_list.add(cur_period['product'])
            if cur_period['trade']:
                if self.trade_period_list.get(cur_period['product']) is None:
                    self.trade_period_list[cur_period['product']] = []
                self.trade_period_list[cur_period['product']].append(new_period)

        max_slippage = Decimal(str(config['max_slippage']))
        self.trade_engine = engine.TradeEngine(auth_client, product_list=self.product_list, fiat=fiat_currency, is_live=config['live'], max_slippage=max_slippage)
        self.cbpro_websocket = engine.TradeAndHeartbeatWebsocket(fiat=fiat_currency, sandbox=config['sandbox'])
        self.cbpro_websocket.start()
        self.indicator_period_list[0].verbose_heartbeat = True
        self.indicator_subsys = indicators.IndicatorSubsystem(self.indicator_period_list)
        self.last_indicator_update = time.time()

        if config['frontend'] == 'curses':
            curses_enable = True
        else:
            curses_enable = False
        self.interface = interface.cursesDisplay(enable=curses_enable)

        if config['frontend'] == 'web':
            web_interface = interface.web(self.indicator_subsys, self.trade_engine)
            server_thread = threading.Thread(target=web_interface.start, daemon=True)
            server_thread.start()

    def start(self):
        while(True):
            try:
                if self.cbpro_websocket.error:
                    raise self.cbpro_websocket.error
                msg = self.cbpro_websocket.websocket_queue.get(timeout=15)
                for product in self.trade_engine.products:
                    product.order_book.process_message(msg)
                if msg.get('type') == "match":
                    for cur_period in self.indicator_period_list:
                        cur_period.process_trade(msg)
                    if time.time() - self.last_indicator_update >= 1.0:
                        for cur_period in self.indicator_period_list:
                            self.indicator_subsys.recalculate_indicators(cur_period)
                        for product_id, period_list in self.trade_period_list.items():
                            self.trade_engine.determine_trades(product_id, period_list, self.indicator_subsys.current_indicators)
                        self.last_indicator_update = time.time()
                elif msg.get('type') == "heartbeat":
                    for cur_period in self.indicator_period_list:
                        cur_period.process_heartbeat(msg)
                    for product_id, period_list in self.trade_period_list.items():
                        if len(self.indicator_subsys.current_indicators[cur_period.name]) > 0:
                            self.trade_engine.determine_trades(product_id, period_list, self.indicator_subsys.current_indicators)
                    self.trade_engine.print_amounts()
                self.interface.update(self.trade_engine, self.indicator_subsys.current_indicators,
                                self.indicator_period_list, msg)
            except KeyboardInterrupt:
                self.trade_engine.close(exit=True)
                self.cbpro_websocket.close()
                self.interface.close()
                break
            except Exception as e:
                self.error_logger.exception(datetime.datetime.now())
                self.trade_engine.close()
                self.cbpro_websocket.close()
                self.cbpro_websocket.error = None
                # Period data cannot be trusted. Re-initialize
                for cur_period in self.indicator_period_list:
                    cur_period.initialize()
                time.sleep(10)
                self.cbpro_websocket.start()

cbprotrader = CBProTrader()
cbprotrader.start()