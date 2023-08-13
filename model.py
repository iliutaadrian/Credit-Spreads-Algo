from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()


def get_db_url():
    return f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DATABASE')}"


def get_database_session():
    engine = create_engine(get_db_url())
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


class Trade(Base):
    __tablename__ = 'tradeideas'

    id = Column(Integer, primary_key=True)
    ticker = Column(String(255), nullable=False)
    strategy_name = Column(String(255), nullable=False)
    current_price = Column(Float, nullable=False)
    ma_std = Column(String(255), nullable=False)
    date_alerted = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    option_type = Column(String(255), nullable=False)
    strike_prices = Column(Float, nullable=False)
    min_credit = Column(Float, nullable=False)
    status = Column(String(255), nullable=False)

    def __init__(self, ticker, strategy_name, current_price, ma_std, date_alerted, expiration_date,
                 option_type, strike_prices, min_credit, status):
        self.ticker = ticker
        self.strategy_name = strategy_name
        self.current_price = current_price
        self.ma_std = ma_std
        self.date_alerted = date_alerted
        self.expiration_date = expiration_date
        self.option_type = option_type
        self.strike_prices = strike_prices
        self.min_credit = min_credit
        self.status = status

    @staticmethod
    def get_all(strategy=None):
        session = get_database_session()

        if strategy:
            result = session.query(Trade).filter_by(strategy_name=strategy, ticker='SPY').all()
        else:
            result = session.query(Trade).filter(Trade.status.is_(None)).order_by(Trade.expiration_date.desc()).limit(20).all()

        session.close()
        return result


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    amount = Column(Float)

    @staticmethod
    def check_login_credentials(email, password):
        session = get_database_session()

        user = session.query(User).filter_by(email=email).first()
        if user and user.password == password:
            return user.id
        return None

    @staticmethod
    def get_amount(user_id):
        session = get_database_session()

        user = session.query(User).filter_by(id=user_id).first()
        if user:
            return user.amount
        else:
            return 0


class UserTrade(Base):
    __tablename__ = 'usertrade'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    ticker = Column(String(10))
    trade_type = Column(String(20))
    sold_strike_price = Column(Float)
    credit_to_open = Column(Float, default=0.23)
    position_size = Column(Integer)
    commission = Column(Float, default=5.0)
    trade_open_date = Column(Date)
    trade_expiration_date = Column(Date)
    status = Column(String(20), default='open')
    credit_to_close = Column(Integer)
    trade_close_date = Column(Date)


    @staticmethod
    def get_all(user_id):
        session = get_database_session()

        trades = session.query(UserTrade).filter_by(user_id=user_id).all()

        return trades

    def create(self):
        session = get_database_session()

        session.add(self)
        session.commit()

    @classmethod
    def edit(cls, trade_id, ticker, trade_type, sold_strike_price, position_size,
             credit_to_open, commission, trade_open_date, trade_expiration_date):
        session = get_database_session()

        trade = session.query(UserTrade).filter_by(id=trade_id).first()
        if trade:
            trade.ticker = ticker
            trade.trade_type = trade_type
            trade.sold_strike_price = sold_strike_price
            trade.position_size = position_size
            trade.credit_to_open = credit_to_open
            trade.commission = commission
            trade.trade_open_date = trade_open_date
            trade.trade_expiration_date = trade_expiration_date
            session.commit()

    @classmethod
    def clone(cls, user_id, ticker, trade_type, sold_strike_price, position_size,
              credit_to_open, commission, trade_open_date, trade_expiration_date):
        session = get_database_session()

        new_trade = UserTrade(
            user_id=user_id,
            ticker=ticker,
            trade_type=trade_type,
            sold_strike_price=sold_strike_price,
            position_size=position_size,
            credit_to_open=credit_to_open,
            commission=commission,
            trade_open_date=trade_open_date,
            trade_expiration_date=trade_expiration_date,
            status='open'
        )
        session.add(new_trade)
        session.commit()

    @classmethod
    def delete(cls, trade_id):
        session = get_database_session()

        trade = session.query(UserTrade).filter_by(id=trade_id).first()
        if trade:
            session.delete(trade)
            session.commit()

    @classmethod
    def find(cls, trade_id):
        session = get_database_session()

        trade = session.query(UserTrade).filter_by(id=trade_id).first()
        return trade

    @classmethod
    def close(cls, trade_id, credit_to_close, commission, trade_close_date):
        session = get_database_session()

        trade = session.query(UserTrade).filter_by(id=trade_id).first()
        if trade:
            trade.status = 'closed'
            trade.credit_to_close = credit_to_close
            trade.commission = commission
            trade.trade_close_date = trade_close_date
            session.commit()