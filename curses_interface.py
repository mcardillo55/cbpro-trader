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

    def update_candlesticks(self, period):
        if not self.enable:
            return
        cur_stick = period.cur_candlestick

        self.stdscr.addstr(4, 0, "%s O: %f H: %f L: %f C: %f V: %f" %
                           (cur_stick.time, cur_stick.open, cur_stick.high,
                            cur_stick.low, cur_stick.close, cur_stick.volume),
                           self.print_color(cur_stick.open, cur_stick.close))
        starty = 5
        for cur_stick in period.candlesticks[:-6:-1]:
            self.stdscr.addstr(starty, 0, "%s O: %f H: %f L: %f C: %f V: %f" %
                               (cur_stick[0], cur_stick[1], cur_stick[2],
                                cur_stick[3], cur_stick[4], cur_stick[5]),
                               self.print_color(cur_stick[1], cur_stick[4]))
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
        self.stdscr.addstr(1, 0, "1 - OBV: %f OBV_EMA: %f" %
                           (indicators['1']['obv'], indicators['1']['obv_ema']))
        self.stdscr.addstr(2, 0, "5 - OBV: %f OBV_EMA: %f" %
                           (indicators['5']['obv'], indicators['5']['obv_ema']))
        self.stdscr.refresh()

    def update_orders(self, trade_engine):
        if not self.enable:
            return

        self.stdscr.addstr(11, 0, "Recent Fills")
        starty = 12
        for fill in trade_engine.auth_client.get_fills(limit=5)[0]:
            self.stdscr.addstr(starty, 0, "%s Price: %s Size: %s Time: %s" %
                               (fill.get('side').upper(), fill.get('price'),
                                fill.get('size'), fill.get('created_at')))
            starty += 1


        self.stdscr.addstr(18, 0, "Open Orders")

        # Clear the next 5 rows
        for idx in xrange(19, 24):
            self.stdscr.addstr(idx, 0, " " * 70)

        starty = 19
        if trade_engine.order_thread.is_alive():
            for order in trade_engine.auth_client.get_orders()[0]:
                self.stdscr.addstr(starty, 0, "%s Price: %s Size: %s Status: %s" %
                                   (order.get('side').upper(), order.get('price'),
                                    order.get('size'), order.get('status')))
                starty += 1
        else:
            self.stdscr.addstr(19, 0, "None")
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
