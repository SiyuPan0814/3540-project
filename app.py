from flask import Flask, url_for, redirect, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
import config
from models import db, Users, Blotter
from utils import validate, get_credit, get_btc, get_eth, get_ltc, buy_det, sell_det, get_prices, his_price
from werkzeug.security import generate_password_hash
import json
import time


btc_price, eth_price, ltc_price = get_prices()


app = Flask(__name__)
app.config.from_object(config)            # get arguments from config.py
db.init_app(app)                          # bind app and db

with app.test_request_context():
    # db.drop_all()
    db.create_all()


@app.context_processor
def my_context_processor1():
    status = session.get('status', '')
    return {'status': status}


@app.context_processor
def my_context_processor2():
    user = session.get('username')
    if user:
        return {'login_user': user, 'credit': get_credit(user), 'btc': get_btc(user), 'eth': get_eth(user), 'ltc': get_ltc(user)}
    return {}


@app.route('/')
def index():
    btc_price, eth_price, ltc_price = get_prices()
    return render_template('base.html', btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    btc_price, eth_price, ltc_price = get_prices()
    if request.method == 'GET':
        return render_template('register.html', btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)
    else:
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        message = validate(username, password1, password2)
        flash(message)
        if message == 'Register successful':
            session['status'] = 'YES'
            new_user = Users(username=username, password=generate_password_hash(password1), )
            db.session.add(new_user)
            # new_blotter = Blotter(username=new_user.username, )
            db.session.add(new_user)
            # db.session.add(new_blotter)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            session['status'] = 'NO'
            return render_template('register.html', btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    btc_price, eth_price, ltc_price = get_prices()
    if request.method == 'GET':
        return render_template('login.html', btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        message = validate(username, password)
        if message == 'Login successful':
            session['username'] = username
            session.permanent = True
            return redirect(url_for('trading'))
        else:
            session['status'] = 'NO'
            flash(message)
            return render_template('login.html', btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)


@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/trading/', methods=['GET', 'POST'])
def trading():
    btc_price, eth_price, ltc_price = get_prices()
    if request.method == 'GET':
        return render_template('trading.html', btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)
    else:
        if request.form["action"] == 'buy':
            btc_buy, eth_buy, ltc_buy = 0, 0, 0
            if request.form.get('btc_buy'):
                btc_buy = float(request.form.get('btc_buy'))
            if request.form.get('eth_buy'):
                eth_buy = float(request.form.get('eth_buy'))
            if request.form.get('ltc_buy'):
                ltc_buy = float(request.form.get('ltc_buy'))

            buy_info = buy_det(session['username'], btc_buy, eth_buy, ltc_buy, btc_price, eth_price, ltc_price)
            # print(buy_info)
            flash(buy_info)
            if buy_info == 'Buying successful':
                user = Users.query.filter(Users.username == session['username']).first()
                user.BTC = user.BTC + btc_buy
                user.ETH = user.ETH + eth_buy
                user.LTC = user.LTC + ltc_buy
                user.credit = user.credit - (btc_buy * btc_price + eth_buy * eth_price + ltc_buy * ltc_price)
                user.buyhis = user.buyhis + '%s,BTC: %s ||| ETH: %s ||| LTC: %s;' % \
                              (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), btc_buy, eth_buy, ltc_buy)
                user.btc_avg = (btc_buy * btc_price + user.btc_avg * (user.BTC - btc_buy))/(user.BTC)
                user.eth_avg = (eth_buy * eth_price + user.eth_avg * (user.ETH - eth_buy))/(user.ETH)
                user.ltc_avg = (ltc_buy * ltc_price + user.ltc_avg * (user.LTC - ltc_buy))/(user.LTC)

                db.session.commit()

                # record = Blotter.query.filter(Blotter.username == session['username']).first()
                record = Blotter(username=session['username'], trade_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                 BTC_qty=btc_buy, ETH_qty=eth_buy, LTC_qty=ltc_buy, BTC_price=btc_price,
                                 ETH_price=eth_price, LTC_price=ltc_price, btc_pft = 0, eth_pft = 0, ltc_pft = 0)
                # record.username = user.username
                # record.trade_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                # record.BTC_qty = btc_buy
                # record.ETH_qty = eth_buy
                # record.LTC_qty = ltc_buy
                # record.BTC_price = btc_price
                # record.ETH_price = eth_price
                # record.LTC_price = ltc_price
                db.session.add(record)
                db.session.commit()
                his_price(session['username'])
                session['status'] = 'YES'
            else:
                session['status'] = 'NO'

        elif request.form["action"] == 'sell':
            btc_sell, eth_sell, ltc_sell = 0, 0, 0
            if request.form.get('btc_sell'):
                btc_sell = float(request.form.get('btc_sell'))
            if request.form.get('eth_sell'):
                eth_sell = float(request.form.get('eth_sell'))
            if request.form.get('ltc_sell'):
                ltc_sell = float(request.form.get('ltc_sell'))

            sell_info = sell_det(session['username'], btc_sell, eth_sell, ltc_sell)
            flash(sell_info)
            if sell_info == 'Selling successful':
                user = Users.query.filter(Users.username == session['username']).first()
                user.BTC = user.BTC - btc_sell
                user.ETH = user.ETH - eth_sell
                user.LTC = user.LTC - ltc_sell
                user.credit = user.credit + (btc_sell * btc_price + eth_sell * eth_price + ltc_sell * ltc_price)
                user.sellhis = user.sellhis + '%s,BTC: %s ||| ETH: %s ||| LTC: %s;' % \
                               (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), btc_sell, eth_sell, ltc_sell)

                db.session.commit()

                # record = Blotter.query.filter(Blotter.username == session['username']).first()
                # record.username = user.username
                # record.trade_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                # record.BTC_qty = btc_sell
                # record.ETH_qty = eth_sell
                # record.LTC_qty = ltc_sell
                # record.BTC_price = btc_price * (-1)
                # record.ETH_price = eth_price * (-1)
                # record.LTC_price = ltc_price * (-1)

                record = Blotter(username=session['username'],
                                 trade_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                 BTC_qty=btc_sell * (-1), ETH_qty=eth_sell * (-1), LTC_qty=ltc_sell * (-1), BTC_price=btc_price,
                                 ETH_price=eth_price, LTC_price=ltc_price, btc_pft=(btc_price - user.btc_avg)*btc_sell, eth_pft=(eth_price - user.eth_avg)*eth_sell, ltc_pft=(ltc_price - user.ltc_avg)*ltc_price)
                db.session.add(record)
                db.session.commit()
                his_price(session['username'])
                session['status'] = 'YES'
            else:
                session['status'] = 'NO'
        return render_template('trading.html', btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)


@app.route('/deposit/', methods=['GET', 'POST'])
def deposit():
    btc_price, eth_price, ltc_price = get_prices()
    if request.method == 'GET':
        return render_template('deposit.html', btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)
    else:
        deposit = 0
        if request.form.get('deposit'):
            deposit = float(request.form.get('deposit'))
            user = Users.query.filter(Users.username == session['username']).first()
            user.credit = user.credit + deposit
            user.deposit = user.deposit + deposit
            user.deposithis = user.deposithis + '%s,Amount: %s;' % \
                           (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), deposit)
            db.session.commit()
            session['status'] = 'YES'
            flash('Deposit successful')

        return render_template('deposit.html', btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)


@app.route('/buyhis/')
def buyhis():
    btc_price, eth_price, ltc_price = get_prices()
    user = Users.query.filter(Users.username == session['username']).first()
    his = user.buyhis
    his_dict = {}
    info = his.strip().split(';')
    # print(info)
    for i in info[:-1]:
        # print(i)
        tmp = i.strip().split(',')
        his_dict[tmp[0]] = tmp[1]

    return render_template('buyhis.html', his_dict=his_dict, btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)


@app.route('/sellhis/')
def sellhis():
    btc_price, eth_price, ltc_price = get_prices()
    user = Users.query.filter(Users.username == session['username']).first()
    his = user.sellhis
    his_dict = {}
    info = his.strip().split(';')
    # print(info)
    for i in info[:-1]:
        # print(i)
        tmp = i.strip().split(',')
        his_dict[tmp[0]] = tmp[1]

    return render_template('sellhis.html', his_dict=his_dict, btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price)


@app.route('/deposithis/')
def deposithis():
    btc_price, eth_price, ltc_price = get_prices()
    user = Users.query.filter(Users.username == session['username']).first()
    his = user.deposithis
    his_dict = {}
    info = his.strip().split(';')
    # print(info)
    for i in info[:-1]:
        # print(i)
        tmp = i.strip().split(',')
        his_dict[tmp[0]] = tmp[1]

    return render_template('deposithis.html', his_dict=his_dict, btc_price=btc_price, eth_price=eth_price,
                           ltc_price=ltc_price)


@app.route('/pl/')
def pl():
    btc_price, eth_price, ltc_price = get_prices()
    #btc_upl, eth_upl, ltc_upl = 0
    records = Blotter.query.filter(Blotter.username == session['username'])
    btc_rpl = 0
    eth_rpl = 0
    ltc_rpl = 0
    for record in records:
        btc_rpl = btc_rpl + record.btc_pft
        eth_rpl = eth_rpl + record.eth_pft
        ltc_rpl = ltc_rpl + record.ltc_pft
    total_rpl = btc_rpl + eth_rpl + ltc_rpl

    user = Users.query.filter(Users.username == session['username']).first()
    btc_upl = (btc_price - user.btc_avg) * user.BTC
    eth_upl = (eth_price - user.eth_avg) * user.ETH
    ltc_upl = (ltc_price - user.ltc_avg) * user.LTC
    total_upl = btc_upl + eth_upl + ltc_upl

    return render_template('PL.html', btc_price=btc_price, eth_price=eth_price, ltc_price=ltc_price, btc_rpl=btc_rpl, eth_rpl=eth_rpl, ltc_rpl=ltc_rpl, btc_upl=btc_upl, eth_upl=eth_upl,
                           ltc_upl=ltc_upl, total_rpl=total_rpl, total_upl=total_upl)


if __name__ == '__main__':
    app.run()
