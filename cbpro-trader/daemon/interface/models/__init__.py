from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def create_all(engine):
    Base.metadata.create_all(engine)

class Period(Base):
    __tablename__ = 'periods'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    candlesticks = relationship("Candlestick")
    indicators = relationship("Indicator")

class Candlestick(Base):
    __tablename__ = 'candlesticks'

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey('periods.id'))
    time = Column(DateTime)
    open_price = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    close = Column(Numeric)
    volume = Column(Numeric)

class Indicator(Base):
    __tablename__ = 'indicators'

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey('periods.id'))
    name = Column(String)
    value = Column(Numeric)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    product_id = Column(String)
    signal = Column(String)