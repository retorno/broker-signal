from flask import Flask, request, session, redirect, url_for, escape, request
from flask_restful import reqparse, abort, Api, Resource
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import os, time, json
from flask import Flask, request, Response
from broker.scrapy_clear import ScrapyClear


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

api = Api(app)
clear = None
debug = False

@app.route('/broker/position', methods=['GET'])
def getPosition():
    position = clear.getTruePosition()
    return str(position)


@app.route('/broker/last-price', methods=['GET'])
def getLastPrice():
    lastPrice = clear.getLastPrice()
    return str(lastPrice)


@app.route('/broker/zerar-all', methods=['GET'])
def zeraAll():
    zerar = clear.zeraAll()
    return zerar


@app.route('/broker/set-order', methods=['POST'])
def setOrder():
    order = clear.setOrderFast(stock=request.json)
    return order


def connectBroker():
    global clear
    clear = ScrapyClear()
    clear.openBroker()
    print (" -----> OPEN BROKER OK")
    clear.setLogin()
    print (" -----> OPEN LOGIN OK")
    clear.closeModal()
    print (" -----> CLOSE MODAL OK")
    clear.openPanelOrderFast()
    print (" -----> OPEN PANEL ORDER FAST OK")
    return clear


if __name__ == '__main__':
    connectBroker()
    # sudo lsof -t -i tcp:5018 | xargs kill
    app.run(debug=debug, host='0.0.0.0', port=5018)
