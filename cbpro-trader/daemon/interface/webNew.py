import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from . import models

class Web(object):
    def __init__(self, indicator_subsys, trade_engine):
        self.indicator_subsys = indicator_subsys
        self.trade_engine = trade_engine
        self.last_update_time = 0
        try:
            os.remove('data.db')
        except FileNotFoundError:
            pass
        engine = create_engine('sqlite:///data.db')
        models.create_all(engine)

        self.Session = sessionmaker(bind=engine)
        session = self.Session()

        for period in indicator_subsys.period_list:
            period_object = models.Period(name=period.name)
            session.add(period_object)
            session.flush()
            
            for candlestick in period.candlesticks:
                session.add(models.Candlestick(period_id=period_object.id,
                                               time=candlestick[0],
                                               low=candlestick[1],
                                               high=candlestick[2],
                                               open_price=candlestick[3],
                                               close=candlestick[4],
                                               volume=candlestick[5]))

        
        session.commit()
        session.close()
        return

    def update_balances(self, trade_engine):
        return

    def update_candlesticks(self, period_list):
        session = self.Session()
        for period in self.indicator_subsys.period_list:
            period_object = session.query(models.Period).filter_by(name=period.name).one()
            try:
                cur_candlestick = session.query(models.Candlestick).filter_by(period_id=period_object.id, time=period.cur_candlestick.time).one()
            except NoResultFound:
                session.add(models.Candlestick(period_id=period_object.id,
                                               time=period.cur_candlestick.time,
                                               low=period.cur_candlestick.low,
                                               high=period.cur_candlestick.high,
                                               open_price=period.cur_candlestick.open,
                                               close=period.cur_candlestick.close,
                                               volume=period.cur_candlestick.volume))
            else:
                cur_candlestick.low = period.cur_candlestick.low
                cur_candlestick.high = period.cur_candlestick.high
                cur_candlestick.open_price = period.cur_candlestick.open
                cur_candlestick.close = period.cur_candlestick.close
                cur_candlestick.volume = period.cur_candlestick.volume
        session.commit()
        session.close()
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
        if time.time() > self.last_update_time + 1:
            self.update_balances(trade_engine)
            self.update_heartbeat()
            self.update_signals(trade_engine)
            # Make sure indicator dict is populated
            if len(indicators[period_list[0].name]) > 0:
                self.update_indicators(period_list, indicators)
            self.update_candlesticks(period_list)
            self.update_orders(trade_engine)
            self.last_update_time = time.time()

    def close(self):
        return