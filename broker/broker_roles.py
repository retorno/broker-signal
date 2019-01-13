# -*- coding: utf-8 -*-
from enum import Enum
import os, time, json
from utils import Config, Logger, Firebase
from utils import WebDriver
import asyncio


class OperationEnum(Enum):
    COMPRA = 'Buy'
    VENDA = 'Sell'
    ZERAR = 'Zerar'
    INVERT = 'Invert'


class TypeOrderEnum(Enum):
    STOP = 'Stop'
    LIMITED = 'Limited'
    AGRESSION = 'Aggression'
    CANCELAR = 'Cancelar'
    ZERAR = 'Zerar'


class BrokerRoles(Logger):
    tryGet = 13
    priceLastOrder = 0    # verify canDouble
    priceLastStop = 0     # virify canAdjustPriceStop
    env = None
    firebase = None

    def __init__(self, *args, **kwargs):
        Config.__init__(self)
        self.env = self.conf.get("enviroment")
        self.firebase = Firebase.__init__(self)
        Logger.__init__(self)

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
        last_price = float(self.getLastPrice())
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
        pass

    def ordersOpen(self):
        pass

    def zeraAll(self):
        pass

    def setStop(self, stock={}):
        pass

    def getMaxPosition(self):
        pass

    def setOrderFast(self, stock={}):
        pass

    def getPosition(self):
        pass

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
            currentPosition = abs(self.getPosition())
            stock["quantity"] = currentPosition
            stock["last_price"] = self.getLastPrice()
            if not self.hasOrdersOpen(stock=stock) and self.canAdjustPriceStop(stock=stock):
                self.setStop(stock=stock)
            elif int(currentPosition) or self.skipStop(stock=stock):
                self.zeraAll()
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

    def changeStop(self, stock={}):
        print("init => " + str(stock))
        changePosition = int(stock.get('change_position'))
        position = abs(int(self.getPosition()))
        stock['status'] = []
        if position == 0 or self.canDouble(stock=stock):
            if changePosition == 1 and position != 0:
                stock["quantity"] = str(position)
            if self.limitPosition(stock=stock):
                self.setOrderFast(stock=stock)
                self.firebase.saveFirebase(stock=stock)
            else:
                self.zeraAll(stock=stock)
                stock.get('status').append('Not possible send order, is limit position')
        self.checkStop(stock=stock)
        print("final => " + str(stock))
        return json.dumps(stock)
    
    def sayExecute(self, stock={}):
        if os.name != 'posix':  # only in win speech operation
            os.system('say %s %s' %(stock.get('operation'), stock.get('quantity')))
        else:
            import winspeech
            winspeech.say('order %s %s %s' %(stock.get('quantity'), stock.get('operation'), stock.get('stop_loss')[2:]))

    def limitPosition(self, stock={}):
        sendQuantity = int(stock.get('quantity'))
        maxPosition = self.getMaxPosition()
        limit = round(maxPosition / 2)
        if sendQuantity <= limit:
            return True
        stock.get('status').append('limit max position ' + str(limit))