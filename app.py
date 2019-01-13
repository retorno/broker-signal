from flask import Flask, request, session, redirect, url_for, escape, request
from flask_restful import reqparse, abort, Api, Resource
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import os, time, json
from flask import Flask, request, Response
from broker.scrapy_clear import ScrapyClear
from broker.scrapy_clear import BrokerRoles

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

api = Api(app)
clear = None
debug = False


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


@app.route('/broker/position', methods=['GET'])
def getPosition():
    position = clear.getPosition()
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
    stock = getHeaders(request)
    order = clear.cancelOrders(stock=stock)
    return order


@app.route('/broker/change-stop', methods=['POST'])
def changeStop():
    stock = getHeaders(request)
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.ensure_future(web_server_handler(self)))
    # loop.run_until_complete(asyncio.gather(coroutine_1(), coroutine_2()))
    order = clear.changeStop(stock=stock)
    return order


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
    # sudo lsof -t -i tcp:5018 | xargs kill
    app.run(debug=debug, host='0.0.0.0', port=5018)
