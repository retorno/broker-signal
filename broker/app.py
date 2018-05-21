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


# to use set WINFUT = WINM18
# test => post localhost:5005/broker/change-stop
# active:WINFUT
# quantity:1
# operation:Buy
# stop_loss:35
# production:1


@app.route('/broker/position', methods=['GET'])
def getPosition():
    position = clear.getPosition()
    return position


@app.route('/broker/last-price', methods=['GET'])
def getLastPrice():
    stock = getHeaders(request)
    lastPrice = clear.getLastPrice()
    return lastPrice

@app.route('/broker/recipe', methods=['GET'])
def getRecipe():
    recipe = clear.getRecipe()
    return recipe

def getHeaders(request):
    
    stock = {'active': request.headers['active'],
             'quantity': request.headers['quantity'],
             'operation': request.headers['operation'],
             'stop_loss': request.headers['stop_loss'],
             'production': request.headers['production']}
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
    return order


@app.route('/broker/change-stop', methods=['POST'])
def changeStop():
    stock = getHeaders(request)
    # import ipdb; ipdb.set_trace()
    sendQuantity = int(stock.get('quantity'))
    position = abs(int(clear.getPosition()))
    if clear.limitPosition(stock=stock) and sendQuantity != position:
        clear.setOrderFast(stock=stock)
    clear.cancelOrders(stock=stock)
    clear.setStop(stock=stock, beforePosition=position)
    return json.dumps(stock)


def connectBroker():
    global clear
    clear = ScrapyClear()
    clear.openBroker()
    clear.setLogin()
    clear.closeModal()
    return clear


if __name__ == '__main__':
    connectBroker()
    # worker = WorkerConnect()
    # worker.execute('broker.run', args={'test': 'sim'})
    app.run(debug=True, host='0.0.0.0', port=5000)
