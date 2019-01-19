from flask import Flask, request, session, redirect, url_for, escape, request
from flask_restful import reqparse, abort, Api, Resource
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import os, time, json
from flask import Flask, request, Response
from scrapy.scrapy_clear import ScrapyClear


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

api = Api(app)
clear = None
debug = False


@app.route('/scrapy/position', methods=['GET'])
def getPosition():
    position = clear.getPosition()
    return str(position)


@app.route('/scrapy/last-price', methods=['GET'])
def getLastPrice():
    lastPrice = clear.getLastPrice()
    return str(lastPrice)


@app.route('/scrapy/recipe', methods=['GET'])
def getRecipe():
    recipe = clear.getRecipe()
    return recipe


@app.route('/scrapy/zerar-all', methods=['GET'])
def zeraAll():
    zerar = clear.zeraAll()
    return zerar


@app.route('/scrapy/set-order', methods=['POST'])
def setOrder():
    order = clear.setOrderFast(stock=request.json)
    return order


@app.route('/scrapy/set-stop', methods=['POST'])
def setStop():
    order = clear.setStop(stock=request.json)
    return order


@app.route('/scrapy/cancel-order', methods=['GET'])
def cancelOrder():
    order = clear.cancelOrders()
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
    # sudo lsof -t -i tcp:5010 | xargs kill
    app.run(debug=debug, host='0.0.0.0', port=5010)
