from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import Interface
from . import models

class Web(Interface):
    def __init__(self, indicator_subsys):
        engine = create_engine('sqlite:///data.db')
        models.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        for period in indicator_subsys.period_list:
            session.add(models.Period(name=period.name))
        session.commit()
        return

    def update_balances(self, trade_engine):
        return

    def update_candlesticks(self, period_list):
        return

    def update_heartbeat(self):
        return

    def update_indicators(self, period_list, indicators):
        return

    def update_fills(self, trade_engine):
        return

    def update_orders(self, trade_engine):
        return

    def update_signals(self, trade_engine):
        return

    def update(self, trade_engine, indicators, period_list, msg):
        self.update_balances(trade_engine)
        self.update_heartbeat()
        self.update_signals(trade_engine)
        # Make sure indicator dict is populated
        if len(indicators[period_list[0].name]) > 0:
            self.update_indicators(period_list, indicators)
        self.update_candlesticks(period_list)
        self.update_orders(trade_engine)

        height, width = self.stdscr.getmaxyx()
        self.pad.refresh(0, 0, 0, 0, (height - 1), (width - 1))

    def close(self):
        return