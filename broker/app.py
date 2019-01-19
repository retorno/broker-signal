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


@app.route('/broker/change-stop', methods=['POST'])
def changeStop():
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.ensure_future(web_server_handler(self)))
    # loop.run_until_complete(asyncio.gather(coroutine_1(), coroutine_2()))
    order = clear.changeStop(stock=request.json)
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
