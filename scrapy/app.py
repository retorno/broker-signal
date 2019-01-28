# -*- coding: utf-8 -*-
from flask import Flask, request, session, redirect, url_for, escape, Response
from flask_restful import reqparse, abort, Api, Resource
import os, time, json
from scrapy_clear import ScrapyClear


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

# api = Api(app)
clear = None
debug = False


@app.route('/scrapy/last-price', methods=['GET'])
def getLastPrice():
    lastPrice = clear.getLastPrice()
    return str(lastPrice)


@app.route('/scrapy/set-order', methods=['POST'])
def setOrder():
    order = clear.setOrderFast(stock=request.values)
    return order


@app.route('/scrapy/position', methods=['GET'])
def getPosition():
    position = clear.getPosition()
    return str(position)


@app.route('/scrapy/max-position', methods=['GET'])
def getMaxPosition():
    max_position = clear.getMaxPosition()
    return str(max_position)


@app.route('/scrapy/orders-open', methods=['GET'])
def getOrdersOpen():
    orders_open = clear.ordersOpen()
    return str(orders_open)


@app.route('/scrapy/set-stop', methods=['POST'])
def setStop():
    order = clear.setStop(stock=request.values)
    return order


@app.route('/scrapy/cancel-order', methods=['GET'])
def cancelOrder():
    order = clear.cancelOrders()
    return str(order)


@app.route('/scrapy/zerar-all', methods=['GET'])
def zeraAll():
    zerar = clear.zeraAll()
    return str(zerar)


@app.route('/scrapy/recipe', methods=['GET'])
def getRecipe():
    recipe = clear.getRecipe()
    return recipe


def connectBroker():
    global clear
    clear = ScrapyClear()
    clear.login()
    # clear.closeModal()
    clear.openPanelOrderFast()
    return clear


if __name__ == '__main__':
    clear = connectBroker()
    # sudo lsof -t -i tcp:5010 | xargs kill
    app.run(debug=False, host='0.0.0.0', port=5011)
