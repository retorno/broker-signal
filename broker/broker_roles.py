# -*- coding: utf-8 -*-
import os, time, json, sys
import asyncio, requests
here = os.environ.get("PROJECT_BROKER")
sys.path.append(here)
from model.broker_model import OperationEnum, TypeOrderEnum, TypeMethod
# from utils import Config, Logger, Firebase


class BrokerRoles: #(Logger):
    tryGet = 13
    priceLastOrder = 0    # verify canDouble
    priceLastStop = 0     # virify canAdjustPriceStop
    env = None
    firebase = None

    # def __init__(self, *args, **kwargs):
        # Config.__init__(self)
        # Logger.__init__(self)
        # self.env = self.conf.get("enviroment")

    async def fake_network_request(self, request):
        print('making network call for request:  ' + request)
        await asyncio.sleep(5)
        return 'got network response for request: ' + request

    async def web_server_handler(self):
        task1 = asyncio.ensure_future(self.fake_network_request('one'))
        task2 = asyncio.get_event_loop().create_task(self.fake_network_request('two'))
        await asyncio.sleep(0.5)
        print('doing useful work while network calls are in progress...')
        await asyncio.wait([task1, task2])
        print(task1.result())
        print(task2.result())

    def canDouble(self, stock= {}):
        can_double = False
        point_to_double = 0
        send_operation = stock.get('operation')
        pt_double = float(stock.get('point_to_double'))
        last_price = float(stock.get("last_price"))
        if self.priceLastOrder == 0:
            self.priceLastOrder = last_price
        if send_operation == OperationEnum.COMPRA.value:
            point_to_double = float(self.priceLastOrder) + pt_double
            can_double = last_price > point_to_double
        elif send_operation == OperationEnum.VENDA.value:
            point_to_double = float(self.priceLastOrder) - pt_double
            can_double = last_price < point_to_double
        stock['point_to_double'] = str(point_to_double)
        print("price_last_order => " + str(float(self.priceLastOrder)) + " to double => " + str(point_to_double))
        return can_double

    def getLastPrice(self):
        endPoint = '/scrapy/last-price'
        ret = self.request('get', endPoint)
        return str(ret)

    def cancelOrder(self):
        endPoint = '/scrapy/cancel-order'
        ret = self.request('get', endPoint)
        return ret

    def ordersOpen(self):
        endPoint = '/scrapy/orders-open'
        ret = self.request('get', endPoint)
        return ret

    def zeraAll(self):
        endPoint = '/scrapy/zerar-all'
        ret = self.request('get', endPoint)
        return ret

    def getRecipe(self):
        endPoint = '/scrapy/recipe'
        ret = self.request('get', endPoint)
        return str(ret)

    def getPosition(self):
        endPoint = '/scrapy/position'
        ret = self.request('get', endPoint)
        return str(ret)

    def getMaxPosition(self):
        endPoint = '/scrapy/max-position'
        ret = self.request('get', endPoint)
        return str(ret)

    def request(self, method, endPoint, data={}):
        ret = None
        srvScrapy = 'http://localhost:5011'
        url = srvScrapy + endPoint
        if method == TypeMethod.GET.value:
            ret = requests.get(url)
        elif method == TypeMethod.POST.value:
            ret = requests.post(url, data)
        if ret.status_code == 200:
            return eval(ret.content)

    def setStop(self, stock={}):
        stock = self.getStock()
        endPoint = '/scrapy/set-stop'     # methods=['POST'])
        ret = self.request('post', endPoint, stock)
        return ret

    def setOrderFast(self, stock={}):
        stock = self.getStock()
        endPoint = '/scrapy/set-order'    # methods=['POST'])
        ret = self.request('post', endPoint, stock)
        return ret

    def hasOrdersOpen(self, stock={}):
        orders_open = self.ordersOpen()
        print("orders_open => " + str(orders_open))
        qtd_open = orders_open.get("qtd_open")
        qtd_buy = orders_open.get("qtd_buy")
        qtd_sell = orders_open.get("qtd_sell")
        if qtd_open == (qtd_buy + qtd_sell) == stock.get("quantity"):
            return True
        else:
            return False

    def checkStop(self, stock={}):
        count = 0
        while count < self.tryGet:
            currentPosition = abs(int(self.getPosition()))
            stock["quantity"] = str(currentPosition)
            stock["last_price"] = self.getLastPrice()
            if not self.hasOrdersOpen(stock=stock) and self.canAdjustPriceStop(stock=stock):
                if not currentPosition:
                    return
                self.setStop(stock=stock)
            elif currentPosition and self.skipStop(stock=stock):
                self.zeraAll()
                return
            count += 1
        self.zeraAll()

    def canAdjustPriceStop(self, stock={}):
        sendOperation = stock.get('operation')
        price_stop = float(self.getPriceStop(stock=stock))
        if self.priceLastStop == 0:
            self.priceLastStop = price_stop
        if sendOperation == OperationEnum.COMPRA.value and self.priceLastStop <= price_stop:
            self.priceLastStop = price_stop
            return True
        elif sendOperation == OperationEnum.VENDA.value and self.priceLastStop >= price_stop:
            self.priceLastStop = price_stop
            return True
        return False

    def hasChangePosition(self):
        stock = self.getStock()
        changePosition = int(stock.get('change_position'))
        return changePosition      

    def skipStop(self, stock={}):
        lastPrice = float(stock.get("last_price"))
        sendOperation = stock.get('operation')
        if sendOperation == OperationEnum.COMPRA.value and lastPrice <= self.priceLastStop:
            return True
        elif sendOperation == OperationEnum.VENDA.value and lastPrice >= self.priceLastStop:
            return True
        return False

    def getPriceStop(self, stock= {}):
        #calculate_stop (0 = False, 1 = True)
        lastPrice = float(stock.get("last_price"))
        stopLoss = float(stock.get('stop_loss'))
        sendOperation = stock.get('operation')
        calc_stop = int(stock.get('calculate_stop'))
        if calc_stop == 1:
            if sendOperation == OperationEnum.COMPRA.value:
                stopLoss = lastPrice - stopLoss
            if sendOperation == OperationEnum.VENDA.value:
                stopLoss = lastPrice + stopLoss
        return str(int(stopLoss))

    def saveFirebase(self, stock={}):
        if os.environ.get("USE_FIREBASE"):
            if not self.firebase:
                self.firebase = Firebase()
            stock["recipe"] = self.getRecipe()
            self.firebase.saveFirebase(stock=stock)

    def changeStop(self, stock={}):
        stock = self.getStock()
        print("init => " + str(stock))
        positionCurrent = abs(int(self.getPosition()))
        stock["last_price"] = self.getLastPrice()
        if not positionCurrent or self.canDouble(stock=stock):
            if self.hasChangePosition() and positionCurrent:
                stock["quantity"] = str(positionCurrent)
            if self.limitPosition(stock=stock):
                self.setOrderFast(stock=stock)
                self.saveFirebase(stock=stock)
        self.checkStop(stock=stock)
        print("final => " + str(stock))
        return json.dumps(stock)
    
    def sayExecute(self, stock={}):
        if os.name == 'posix':  # only in win speech operation
            os.system('say %s %s' %(stock.get('operation'), stock.get('quantity')))
        else:
            import winspeech
            winspeech.say('order %s %s %s' %(stock.get('quantity'), stock.get('operation'), stock.get('stop_loss')[2:]))

    def limitPosition(self, stock={}):
        sendQuantity = int(stock.get('quantity'))
        maxPosition = int(self.getMaxPosition())
        limit = round(maxPosition / 2)
        if sendQuantity <= limit:
            return True
        stock.get('status').append('limit max position ' + str(limit))