import curses


class cursesDisplay:
    def __init__(self, enable=True):
        self.enable = enable
        if not self.enable:
            return
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
        self.stdscr.keypad(1)
        self.stdscr.addstr(1, 0, "Waiting for a trade...")

    def update_balances(self, btc, usd):
        if not self.enable:
            return
        self.stdscr.addstr(0, 0, "USD: %.2f BTC: %.8f" % (usd, btc))
        self.stdscr.refresh()

    def update_candlesticks(self, period_list):
        if not self.enable:
            return

        starty = 5
        for cur_period in period_list:
            cur_stick = cur_period.cur_candlestick
            self.stdscr.addstr(starty, 0, "%s O: %f H: %f L: %f C: %f V: %f" %
                               (cur_stick.time, cur_stick.open, cur_stick.high,
                                cur_stick.low, cur_stick.close, cur_stick.volume),
                               self.print_color(cur_stick.open, cur_stick.close))
            starty += 1
        self.stdscr.refresh()

    def update_heartbeat(self, msg):
        if not self.enable:
            return
        self.stdscr.addstr(0, 35, msg.get('time'))
        self.stdscr.refresh()

    def update_indicators(self, indicators):
        if not self.enable:
            return
        self.stdscr.addstr(1, 0, "BTC30 - BBAND_TOP: %f MACD_HIST_DIFF: %f" %
                           (indicators['BTC30']['bband_upper'], indicators['BTC30']['macd_hist']))
        self.stdscr.addstr(2, 0, "ETH30 - BBAND_TOP: %f MACD_HIST_DIFF: %f" %
                           (indicators['ETH30']['bband_upper'], indicators['ETH30']['macd_hist']))
        self.stdscr.addstr(3, 0, "LTC30 - BBAND_TOP: %f MACD_HIST_DIFF: %f" %
                           (indicators['LTC30']['bband_upper'], indicators['LTC30']['macd_hist']))
        self.stdscr.refresh()

    def update_orders(self, trade_engine):
        if not self.enable:
            return

        self.stdscr.addstr(9, 0, "Recent Fills")
        starty = 10
        for fill in trade_engine.auth_client.get_fills(limit=5)[0]:
            self.stdscr.addstr(starty, 0, "%s Price: %s Size: %s Time: %s" %
                               (fill.get('side').upper(), fill.get('price'),
                                fill.get('size'), fill.get('created_at')))
            starty += 1

        self.stdscr.addstr(16, 0, "Open Orders")

        # Clear the next 5 rows
        for idx in xrange(17, 22):
            self.stdscr.addstr(idx, 0, " " * 70)

        starty = 17
        if trade_engine.order_thread.is_alive():
            for order in trade_engine.auth_client.get_orders()[0]:
                self.stdscr.addstr(starty, 0, "%s Price: %s Size: %s Status: %s" %
                                   (order.get('side').upper(), order.get('price'),
                                    order.get('size'), order.get('status')))
                starty += 1
        else:
            self.stdscr.addstr(17, 0, "None")
        self.stdscr.refresh()

    def print_color(self, a, b):
        if a < b:
            return curses.color_pair(1)
        else:
            return curses.color_pair(2)

    def close(self):
        if not self.enable:
            return
        self.stop = True
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()
