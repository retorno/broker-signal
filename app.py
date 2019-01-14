from flask import Flask, request
from flask_restful import Api
from scrapy_clear import ScrapyClear

app = Flask(__name__)
api = Api(app)
clear = None

# quantity:2
# value:79890
# operation:Buy
# type_operation:['Limitada', 'Stop']


@app.route('/broker/position', methods=['GET'])
def getPosition():
    position = clear.getPosition()
    return str(position)


@app.route('/broker/last-price', methods=['GET'])
def getLastPrice():
    lastPrice = clear.getLastPrice()
    return str(lastPrice)


@app.route('/broker/zerar-all', methods=['GET'])
def zeraAll():
    return clear.zeraAll()


@app.route('/broker/cancel-all', methods=['GET'])
def cancelAll():
    return clear.cancelOrders()


@app.route('/broker/set-order', methods=['POST'])
def setOrder():
    clear.setOrderFast(stock=request.json)
    return "OK"


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
