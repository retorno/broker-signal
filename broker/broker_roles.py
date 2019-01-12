# -*- coding: utf-8 -*-
from enum import Enum
import os, time, json
from utils import Config, Logger, Firebase
from utils import WebDriver


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


class BrokerRoles(WebDriver, Logger):

    tryGet = 13
    priceLastOrder = 0    # verify canDouble
    priceLastStop = 0     # virify canAdjustPriceStop
    env = None

    def __init__(self, *args, **kwargs):
        Config.__init__(self)
        self.env = self.conf.get("enviroment")
        Firebase.__init__(self)
        Logger.__init__(self)
        super().__init__()

    def getClass(self, seletorClass, click=None):
        count = 0
        while count < self.tryGet:
            try:
                _class = self.driver.find_element_by_class_name(seletorClass)
                if _class:
                    if click: _class.click()
                    return _class
            except:
                count += 1
                # pass

    def getId(self, seletorId, click=None):
        count = 0
        while count < self.tryGet:
            try:
                _id = self.driver.find_element_by_id(seletorId)
                if _id:
                    if click: _id.click()
                    return _id
            except:
                count += 1
                # pass

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

    def canAdjustPriceStop(self, stock= {}):
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

    def skipStop(self, stock= {}):
        lastPrice = float(stock.get("last_price"))
        sendOperation = stock.get('operation')
        if sendOperation == OperationEnum.COMPRA.value and lastPrice <= self.priceLastStop:
            return True
        elif sendOperation == OperationEnum.VENDA.value and lastPrice >= self.priceLastStop:
            return True
        return False

    def funcname(self, parameter_list):
        saveFirebase(stock= stock)
        pass

    def hasOrdersOpen(self):
        orders_open = self.ordersOpen()
        print("orders_open => " + str(orders_open))
        qtd_open = orders_open.get("qtd_open")
        qtd_buy = orders_open.get("qtd_buy")
        qtd_sell = orders_open.get("qtd_sell")
        currentPosition = abs(int(self.getPosition()))
        stock["quantity"] = str(currentPosition)
        stock["last_price"] = self.getLastPrice()
        if qtd_open == currentPosition and (qtd_buy + qtd_sell) == currentPosition and self.canAdjustPriceStop(stock=stock):
            self.setStop(stock=stock)
            return True
        elif qtd_open == 0:
            self.setStop(stock=stock)
        elif currentPosition == 0 or self.skipStop(stock=stock):
            self.zeraAll()
            return False

    def checkStop(self, stock={}):
        count = 0
        while count < self.tryGet:
            orders_open = self.ordersOpen()
            print("orders_open => " + str(orders_open))
            qtd_open = orders_open.get("qtd_open")
            qtd_buy = orders_open.get("qtd_buy")
            qtd_sell = orders_open.get("qtd_sell")
            currentPosition = abs(int(self.getPosition()))
            stock["quantity"] = str(currentPosition)
            stock["last_price"] = self.getLastPrice()
            if qtd_open == currentPosition and (qtd_buy + qtd_sell) == currentPosition and self.canAdjustPriceStop(stock=stock):
                self.setStop(stock=stock)
                return True
            elif qtd_open == 0:
                self.setStop(stock=stock)
            elif currentPosition == 0 or self.skipStop(stock=stock):
                self.zeraAll()
                return False
            count += 1
        self.zeraAll()

    def changeStop(self, stock={}):
        print("init => " + str(stock))
        changePosition = int(stock.get('change_position'))
        position = abs(int(self.getPosition()))
        stock['status'] = []
        if position == 0 or clear.canDouble(stock=stock):
            if changePosition == 1 and position != 0:
                stock["quantity"] = str(position)
            if clear.limitPosition(stock=stock):
                clear.setOrderFast(stock=stock)
            else:
                clear.zeraAll(stock=stock)
                stock.get('status').append('Not possible send order, is limit position')
        clear.checkStop(stock=stock)
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