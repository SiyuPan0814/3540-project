from flask_sqlalchemy import SQLAlchemy
import time

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    BTC = db.Column(db.Float, nullable=False, default=0)
    ETH = db.Column(db.Float, nullable=False, default=0)
    LTC = db.Column(db.Float, nullable=False, default=0)
    credit = db.Column(db.Float, nullable=False, default=0)
    deposit = db.Column(db.Float, nullable=False, default=0)
    buyhis = db.Column(db.Text, default='')
    sellhis = db.Column(db.Text, default='')
    deposithis = db.Column(db.Text, default='')
    btc_avg = db.Column(db.Float, nullable=False, default=0)
    eth_avg = db.Column(db.Float, nullable=False, default=0)
    ltc_avg = db.Column(db.Float, nullable=False, default=0)



class Blotter(db.Model):
    __tablename__ = 'blotter'
    trade_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
#    username = db.relationship('Users', backref=db.backref('all_users'))
    trade_date = db.Column(db.Text, default='')
    BTC_qty = db.Column(db.Float, nullable=False, default=0.0)
    ETH_qty = db.Column(db.Float, nullable=False, default=0.0)
    LTC_qty = db.Column(db.Float, nullable=False, default=0.0)
    BTC_price = db.Column(db.Float, nullable=False, default=0.0)
    ETH_price = db.Column(db.Float, nullable=False, default=0.0)
    LTC_price = db.Column(db.Float, nullable=False, default=0.0)
    btc_pft = db.Column(db.Float, nullable=False, default=0)
    eth_pft = db.Column(db.Float, nullable=False, default=0)
    ltc_pft = db.Column(db.Float, nullable=False, default=0)




