import curses
import time
from decimal import Decimal


class cursesDisplay:
    def __init__(self, enable=True):
        self.enable = enable
        if not self.enable:
            return
        self.stdscr = curses.initscr()
        self.pad = curses.newpad(23, 120)
        self.order_pad = curses.newpad(10, 120)
        self.timestamp = ""
        self.last_order_update = 0
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
        self.stdscr.keypad(1)
        self.pad.addstr(1, 0, "Waiting for a trade...")

    def update_balances(self, trade_engine):
        self.pad.addstr(0, 0, "USD: %.2f BTC: %.8f ETH: %.8f LTC: %.8f USD_EQUIV: %.2f" %
                        (trade_engine.usd, trade_engine.btc,
                         trade_engine.eth, trade_engine.ltc, trade_engine.usd_equivalent))

    def update_candlesticks(self, period_list):
        starty = self.starty + 1
        if starty < self.signal_end_y + 1:
            starty = self.signal_end_y + 1
        for cur_period in period_list:
            cur_stick = cur_period.cur_candlestick
            if cur_stick.new is False:
                self.pad.addstr(starty, 0, "%s - %s O: %f H: %f L: %f C: %f V: %f" %
                                (cur_period.name, cur_stick.time, cur_stick.open,
                                 cur_stick.high, cur_stick.low, cur_stick.close,
                                 cur_stick.volume),
                                self.print_color(cur_stick.open, cur_stick.close))
            starty += 1
        self.starty = starty

    def update_heartbeat(self):
        self.pad.addstr(0, 83, self.timestamp)

    def update_indicators(self, period_list, indicators):
        starty = self.starty
        for cur_period in period_list:
            self.pad.addstr(starty, 0, "%s - MACD_DIFF: %f" %
                            (cur_period.name, indicators[cur_period.name]['macd_hist_diff']),
                            self.print_color('0.0',
                                             indicators[cur_period.name]['macd_hist_diff']))
            starty += 1
        self.starty = starty

    def update_fills(self, trade_engine):
        self.pad.addstr(9, 0, "Recent Fills")
        starty = 10
        for fill in trade_engine.auth_client.get_fills(limit=5)[0]:
            self.pad.addstr(starty, 0, "%s Price: %s Size: %s Time: %s" %
                            (fill.get('side').upper(), fill.get('price'),
                             fill.get('size'), fill.get('created_at')))
            starty += 1

    def update_orders(self, trade_engine):
        starty = 0
        self.order_pad.addstr(starty, 0, "Open Orders")

        if time.time() - self.last_order_update > 3.0:
            self.order_pad.erase()
            self.order_pad.addstr(starty, 0, "Open Orders")
            order_in_progress = False
            # First check if trade engine has any open orders
            for product in trade_engine.product_list:
                if trade_engine.order_in_progress[product]:
                    order_in_progress = True
            starty += 1
            if order_in_progress:
                for order in trade_engine.auth_client.get_orders()[0]:
                    self.order_pad.addstr(starty, 0, "%s %s Price: %s Size: %s Status: %s" %
                                          (order.get('side').upper(), order.get('product_id'),
                                           order.get('price'), order.get('size'),
                                           order.get('status')))
                    starty += 1
            else:
                self.order_pad.addstr(starty, 0, 'None')
            self.last_order_update = time.time()
            height, width = self.stdscr.getmaxyx()
            self.order_pad.refresh(0, 0, (self.starty + 1), 0, (height - 1), (width - 1))

    def update_signals(self, trade_engine):
        starty = 1
        for product_id in trade_engine.product_list:
            if trade_engine.buy_flag[product_id]:
                text = 'BUY'
                color = curses.color_pair(1)
            elif trade_engine.sell_flag[product_id]:
                text = 'SELL'
                color = curses.color_pair(2)
            else:
                text = 'NONE'
                color = curses.color_pair(0)
            self.pad.addstr(starty, 83, "%s: %s" % (product_id, text), color)
            starty += 1
        self.signal_end_y = starty

    def update(self, trade_engine, indicators, period_list, msg):
        if not self.enable:
            return

        self.starty = 1
        if msg.get('type') == "heartbeat":
            self.timestamp = msg.get('time')
        self.pad.erase()
        self.update_balances(trade_engine)
        self.update_heartbeat()
        self.update_signals(trade_engine)
        # Make sure indicator dict is populated
        if len(indicators[period_list[0].name]) > 0:
            self.update_indicators(period_list, indicators)
        self.update_candlesticks(period_list)

        #self.update_orders(trade_engine)

        height, width = self.stdscr.getmaxyx()
        self.pad.refresh(0, 0, 0, 0, (height - 1), (width - 1))

    def print_color(self, a, b):
        if Decimal(a) < Decimal(b):
            return curses.color_pair(1)
        else:
            return curses.color_pair(2)

    def close(self):
        if not self.enable:
            return
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()
