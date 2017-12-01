import curses


class cursesDisplay:
    def __init__(self, enable=True):
        self.enable = enable
        if not self.enable:
            return
        self.stdscr = curses.initscr()
        self.pad = curses.newpad(20, 120)
        self.timestamp = ""
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
        starty = 8
        for cur_period in period_list:
            cur_stick = cur_period.cur_candlestick
            if cur_stick.new is False:
                self.pad.addstr(starty, 0, "%s - %s O: %f H: %f L: %f C: %f V: %f" %
                                   (cur_period.name, cur_stick.time, cur_stick.open,
                                    cur_stick.high, cur_stick.low, cur_stick.close,
                                    cur_stick.volume),
                                   self.print_color(cur_stick.open, cur_stick.close))
            starty += 1

    def update_heartbeat(self):
        self.pad.addstr(0, 83, self.timestamp)

    def update_indicators(self, indicators):
        self.pad.addstr(1, 0, "BTC5 - BBAND_TOP_1: %f BBAND_TOP_2: %f" %
                           (indicators['BTC5']['bband_upper_1'], indicators['BTC5']['bband_upper_2']),
                           self.print_color(indicators['BTC5']['bband_upper_1'], indicators['BTC5']['close']))
        self.pad.addstr(2, 0, "BTC15 - BBAND_TOP_1: %f BBAND_TOP_2: %f" %
                           (indicators['BTC15']['bband_upper_1'], indicators['BTC15']['bband_upper_2']),
                           self.print_color(indicators['BTC15']['bband_upper_1'], indicators['BTC15']['close']))
        self.pad.addstr(3, 0, "ETH5 - BBAND_TOP_1: %f BBAND_TOP_2: %f" %
                           (indicators['ETH5']['bband_upper_1'], indicators['ETH5']['bband_upper_2']),
                           self.print_color(indicators['ETH5']['bband_upper_1'], indicators['ETH5']['close']))
        self.pad.addstr(4, 0, "ETH15 - BBAND_TOP_1: %f BBAND_TOP_2: %f" %
                           (indicators['ETH15']['bband_upper_1'], indicators['ETH15']['bband_upper_2']),
                           self.print_color(indicators['ETH15']['bband_upper_1'], indicators['ETH15']['close']))
        self.pad.addstr(5, 0, "LTC5 - BBAND_TOP_1: %f BBAND_TOP_2: %f" %
                           (indicators['LTC5']['bband_upper_1'], indicators['LTC5']['bband_upper_2']),
                           self.print_color(indicators['LTC15']['bband_upper_1'], indicators['LTC15']['close']))
        self.pad.addstr(6, 0, "LTC15 - BBAND_TOP_1: %f BBAND_TOP_2: %f" %
                           (indicators['LTC15']['bband_upper_1'], indicators['LTC15']['bband_upper_2']),
                           self.print_color(indicators['LTC15']['bband_upper_1'], indicators['LTC15']['close']))

    def update_orders(self, trade_engine):
        self.pad.addstr(9, 0, "Recent Fills")
        starty = 10
        for fill in trade_engine.auth_client.get_fills(limit=5)[0]:
            self.pad.addstr(starty, 0, "%s Price: %s Size: %s Time: %s" %
                               (fill.get('side').upper(), fill.get('price'),
                                fill.get('size'), fill.get('created_at')))
            starty += 1

        self.pad.addstr(16, 0, "Open Orders")

        # Clear the next 5 rows
        for idx in xrange(17, 22):
            self.pad.addstr(idx, 0, " " * 70)

        starty = 17
        if trade_engine.order_thread.is_alive():
            for order in trade_engine.auth_client.get_orders()[0]:
                self.pad.addstr(starty, 0, "%s Price: %s Size: %s Status: %s" %
                                   (order.get('side').upper(), order.get('price'),
                                    order.get('size'), order.get('status')))
                starty += 1
        else:
            self.pad.addstr(17, 0, "None")

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

    def update(self, trade_engine, indicators, period_list, msg):
        if not self.enable:
            return

        if msg.get('type') == "heartbeat":
            self.timestamp = msg.get('time')
        self.pad.erase()
        self.update_candlesticks(period_list)
        self.update_signals(trade_engine)
        self.update_balances(trade_engine)
        # Make sure indicator dict is populated
        if len(indicators[period_list[0].name]) > 0:
            self.update_indicators(indicators)
        self.update_heartbeat()
        height, width = self.stdscr.getmaxyx()
        self.pad.refresh(0, 0, 0, 0, (height - 1), (width - 1))

    def print_color(self, a, b):
        if a < b:
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
