from models import Users, Blotter
from werkzeug.security import check_password_hash
import requests
import re
import xlwt
import xlrd


def validate(username, password1, password2=None):
    user = Users.query.filter(Users.username == username).first()
    if password2:
        if user:
            return 'Username exists'
        else:
            if len(username) < 4:
                return 'Username should be at least 4 characters'
            elif password1 != password2:
                return "Two passwords not match"
            elif len(password1) < 6:
                return 'Password should be at least 6 characters'
            else:
                return 'Register successful'
    else:
        if user:
            if check_password_hash(user.password, password1):
                return 'Login successful'
            else:
                return 'Wrong password'
        else:
            return "User not exist"


def get_credit(username):
    user = Users.query.filter(Users.username == username).first()
    if user:
        return user.credit
    else:
        return 'NULL'


def get_btc(username):
    user = Users.query.filter(Users.username == username).first()
    if user:
        return user.BTC
    else:
        return 'NULL'


def get_eth(username):
    user = Users.query.filter(Users.username == username).first()
    if user:
        return user.ETH
    else:
        return 'NULL'


def get_ltc(username):
    user = Users.query.filter(Users.username == username).first()
    if user:
        return user.LTC
    else:
        return 'NULL'


def sell_det(username, btc_sell, eth_sell, ltc_sell):
    user = Users.query.filter(Users.username == username).first()
    if user:
        if user.BTC < btc_sell:
            return 'Not enough BTC'
        elif user.ETH < eth_sell:
            return 'Not enough ETH'
        elif user.LTC < ltc_sell:
            return 'Not enough LTC'
        else:
            return 'Selling successful'
    return 'NULL'


def buy_det(username, btc_buy, eth_buy, ltc_buy, btc_price, eth_price, ltc_price):
    user = Users.query.filter(Users.username == username).first()
    if user:
        if btc_buy * btc_price + eth_buy * eth_price + ltc_buy * ltc_price > float(user.credit):
            return 'Not enough money'
        else:
            return 'Buying successful'
    return 'NULL'


def get_prices(biturl='https://coinmarketcap.com/currencies/bitcoin/historical-data/',
              ethurl='https://coinmarketcap.com/currencies/ethereum/historical-data/',
              liturl='https://coinmarketcap.com/currencies/litecoin/historical-data/'):
    bitinf = requests.get(biturl)
    content = bitinf.text
    bitres = re.search('"price":.*?(\d+).*",', content)
    # print(res.group(0).strip().split('"')[3])
    bitprice = bitres.group(0).strip().split('"')[3]

    ethinf = requests.get(ethurl)
    content = ethinf.text
    ethres = re.search('"price":.*?(\d+).*",', content)
    # print(res.group(0).strip().split('"')[3])
    ethprice = ethres.group(0).strip().split('"')[3]

    litinf = requests.get(liturl)
    content = litinf.text
    litres = re.search('"price":.*?(\d+).*",', content)
    # print(res.group(0).strip().split('"')[3])
    litprice = litres.group(0).strip().split('"')[3]

    # print('test')
    bitprice, ethprice, litprice = float(bitprice), float(ethprice), float(litprice)
    return bitprice, ethprice, litprice

def his_price(username):
    wbk = xlwt.Workbook('historic_price.xls')
    sheet = wbk.add_sheet('data')

    sheet.write(0, 0, 'trade_date')
    sheet.write(0, 1, 'btc_price')
    sheet.write(0, 2, 'eth_price')
    sheet.write(0, 3, 'ltc_price')

    records = Blotter.query.filter(Blotter.username == username)
    for record in records:
        sheet.write(record.trade_id, 0, record.trade_date)
        sheet.write(record.trade_id, 1, record.BTC_price)
        sheet.write(record.trade_id, 2, record.ETH_price)
        sheet.write(record.trade_id, 3, record.LTC_price)

    wbk.save('historic_price.xls')


if __name__ == '__main__':
    get_prices()
    his_price(session['username'])
