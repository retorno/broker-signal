from flask import Flask, request, session, redirect, url_for, escape, request
from flask_restful import reqparse, abort, Api, Resource
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from worker import WorkerConnect
from scrapy_clear import ScrapyClear
import os, time, json

app = Flask(__name__)
api = Api(app)
clear = None
# conda activate py36

# to use set WINFUT = WINM18
# test => post localhost:5000/broker/change-stop
# active:WINM18
# quantity:5
# operation:Sell
# stop_loss:25
# production:1
# change_position:1
# calculate_stop:1
# point_to_double:200

@app.route('/broker/position', methods=['GET'])
def getPosition():
    position = clear.getTruePosition()
    return str(position)


@app.route('/broker/last-price', methods=['GET'])
def getLastPrice():
    lastPrice = clear.getLastPrice()
    return str(lastPrice)


@app.route('/broker/recipe', methods=['GET'])
def getRecipe():
    recipe = clear.getRecipe()
    return recipe


@app.route('/broker/zerar-all', methods=['GET'])
def zeraAll():
    zerar = clear.zeraAll()
    return zerar


def getHeaders(request):
    #changePosition (0 = False, 1 = True)
    print(request.headers)
    stock = {'active': request.headers['active'],
             'quantity': request.headers['quantity'],
             'operation': request.headers['operation'],
             'stop_loss': request.headers['stop_loss'],
             'production': request.headers['production'],
             'change_position': request.headers['change_position'],
             'calculate_stop': request.headers['calculate_stop'],
             'point_to_double': request.headers['point_to_double']}
    return stock


@app.route('/broker/set-order', methods=['POST'])
def setOrder():
    stock = getHeaders(request)
    order = clear.setOrderFast(stock=stock)
    return order


@app.route('/broker/set-stop', methods=['POST'])
def setStop():
    stock = getHeaders(request)
    order = clear.setStop(stock=stock)
    return order


@app.route('/broker/cancel-order', methods=['POST'])
def cancelOrder():
    # import ipdb; ipdb.set_trace()
    stock = getHeaders(request)
    order = clear.cancelOrders(stock=stock)
    # order = clear.allOrderCancel()
    return order


@app.route('/broker/change-stop', methods=['POST'])
def changeStop():
    stock = getHeaders(request)
    # import ipdb; ipdb.set_trace()
    changePosition = int(stock.get('change_position'))
    position = abs(int(clear.getPosition()))
    stock['last_price'] = str(clear.getLastPrice())
    stock['status'] = []
    if clear.canDouble(stock=stock, beforePosition=position):
        if changePosition == 1 and position != 0:
            stock["quantity"] = str(position)
        if clear.limitPosition(stock=stock):
            clear.setOrderFast(stock=stock)
            clear.lastOrderPrice = stock.get('last_price')
            if changePosition == 1 and position != 0:
                stock["quantity"] = str(position * 2)
        else:
            stock["quantity"] = str(position)
    else:
        stock["quantity"] = str(position)
        stock.get('status').append('did not reach value, not possible to double')
    clear.checkStop(stock=stock)
    return json.dumps(stock)


def connectBroker():
    global clear
    clear = ScrapyClear()
    clear.openBroker()
    clear.setLogin()
    clear.closeModal()
    clear.openPanelOrderFast()
    return clear


if __name__ == '__main__':
    connectBroker()
    # worker = WorkerConnect()
    # worker.execute('broker.run', args={'test': 'sim'})
    app.run(debug=True, host='0.0.0.0', port=5005)