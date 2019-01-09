# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from webselenium import WebDriver
from utils.stock_firebase import saveFirebase
from broker.scrapy_clear import OperationEnum, TypeOrderEnum
import os
import time
import re

if os.name != 'posix':
    import winspeech


class ScrapyClear(WebDriver):

    tryGet = 13
    priceLastOrder = 0    # verify canDouble
    priceLastStop = 0     # virify canAdjustPriceStop

    def __init__(self, *args, **kwargs):
        config_chrome = {}
        super().__init__(config= config_chrome)

    def openBroker(self):
        self.driver.get(os.environ.get('URL_BROKER'))

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

    def setLogin(self, username=None):
        broker_cpf_cnpj = os.environ.get('BROKER_CPF_CNPJ')
        broker_password = os.environ.get('BROKER_PASSWORD')
        broker_dt_nasc = os.environ.get('BROKER_DT_NASC')
        cpf_cnpj = self.getId('identificationNumber')
        cpf_cnpj.clear()
        cpf_cnpj.send_keys(broker_cpf_cnpj)
        password = self.getId('password')
        password.clear()
        password.send_keys(broker_password)
        dt_nasc = self.getClass('input_date')
        dt_nasc.clear()
        dt_nasc.send_keys(broker_dt_nasc)
        self.getClass('bt_signin', click=True)
        self.getClass('right', click=True)
        self.openBroker()

    def limitPosition(self, stock={}):
        sendQuantity = int(stock.get('quantity'))
        maxPosition = self.getMaxPosition()
        limit = round(maxPosition / 2)
        if sendQuantity <= limit:
            return True
        stock.get('status').append('limit max position ' + str(limit))

    def getMaxPosition(self):
        maxPosition = self.driver.execute_script('return document.getElementsByClassName("container_garantia_exposicao")[0].lastElementChild.value')
        if not maxPosition:
            return 0
        return int(maxPosition)

    def getLastPrice(self):
        lastPrice = self.getClass('lastPrice')
        if lastPrice:
            lastPrice = lastPrice.text.replace(',','.')
            return lastPrice
        else:
            return '0'

    def getRecipe(self, stock={}):
        recipe = self.getClass('ng-binding').text[3:]
        return recipe

    def setOrderFast(self, stock={}):
        self.getClass('bt_fast_boleta', click=True)  # tab_orders_fast
        quantity = stock.get('quantity')
        self.driver.execute_script("document.getElementsByClassName('ng-valid-min')[4].value = %s" %quantity)
        self.assignOperation( stock= stock, type_order= TypeOrderEnum.AGRESSION.value )
        if bool(int(stock.get('production'))):
            operation = stock.get('operation')
            if operation == OperationEnum.COMPRA.value:
                btnClass = 'bt_fast_buy'
            elif operation == OperationEnum.VENDA.value:
                btnClass = 'bt_fast_sell'
            elif operation == OperationEnum.ZERAR.value:
                btnClass = 'bt_fast_rollback'
            elif operation == OperationEnum.INVERT.value:
                btnClass = 'bt_fast_flip'
            self.getClass(btnClass, click=True)
        else:
            stock.get('status').append('running in test')
        self.priceLastOrder = 0
        self.priceLastStop = 0
        return str(stock)

    def zeraAll(self, stock={}):
        self.cancelOrders(stock= stock)
        self.driver.execute_script("document.getElementsByClassName('bt_action')[1].click()")
        self.assignOperation(type_order= TypeOrderEnum.ZERAR.value)
        self.exeCancelOrder(stock=stock)
        self.priceLastOrder = 0
        self.priceLastStop = 0
        return str(stock)

    def cancelOrders(self, stock={}):
        self.getClass('bt_action', click=True)  # btn_order
        self.assignOperation(stock= stock, type_order= TypeOrderEnum.CANCELAR.value)
        self.exeCancelOrder(stock= stock)

    def exeCancelOrder(self, stock={}):
        count = 0
        while count < self.tryGet:
            try:
                btn_execute = 'bt_comprar'
                btn_cancel = 'bt_fechar'
                self.driver.execute_script('document.getElementsByClassName("%s")[2].click()' %btn_execute)
                self.driver.execute_script('document.getElementsByClassName("%s")[2].click()' %btn_cancel)
                return True
            except:
                count += 1
                # pass

    def orderFail(self):
        self.driver.execute_script('document.getElementsByClassName("docket-msg")[4].innerHTML == "%s"' %"Processando ordem anterior...")

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

    def updatePosition(self):
        self.getClass("bt_red_boleta", click= True)
        self.getClass("bt_blue_boleta", click= True)

    def getPosition(self):
        self.updatePosition()
        position = self.driver.execute_script('return document.getElementsByClassName("input_gray")[3].value')
        if not position:
            return "0"
        return str(position)

    def ordersOpen(self):
        qtd_open = 0
        qtd_buy = 0
        qtd_sell = 0
        orders = self.getClass('middle_orders_overflow').text
        orders_open = list(filter(lambda x: "Aberta" in x, orders.split(" - ")))
        for order in orders_open:
            position = re.split("\n", order)
            if len(position) > 1:
                qtd_open += int(position[1])
                operation = position[0].split(" ")[0]
                if operation == "Compra":
                    qtd_buy += int(position[1])
                elif operation == "Venda":
                    qtd_sell += int(position[1])
        return {"qtd_open": qtd_open, "qtd_buy": qtd_buy, "qtd_sell": qtd_sell}

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

    def setStop(self, stock= {}):
        if stock.get("quantity") != "0":
            price_stop = self.getPriceStop(stock= stock)
            stock['price_stop'] = price_stop
            stock['type_operation'] = TypeOrderEnum.STOP.value
            self.cancelOrders(stock=stock)
            self.setOrder(stock= stock)
            stock["recipe"] = self.getRecipe()
            saveFirebase(stock= stock)
            print('Send stop => %s quant => %s in price => %s' %(stock.get('operation'), stock.get('quantity'), price_stop))
            print("------------------------------------------------------------------------------------------------")

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

    def setOrder(self, stock={}):
        sendOperation = stock.get('operation')
        if sendOperation == OperationEnum.COMPRA.value:
            btnClass = 'bt_red_boleta'
        elif sendOperation == OperationEnum.VENDA.value:
            btnClass = 'bt_blue_boleta'
        self.getClass(btnClass, click=True)  # tab_buy_sell
        typeOperation = stock.get('type_operation')    # ['Limitada', 'Stop']
        comboTipo = self.driver.find_element_by_xpath("//select[@id='msg_exchangeordertype']/option[text()= '%s']" %typeOperation)
        comboTipo.click()
        self.setFormOrder(stock= stock)
        self.assignOperation( stock= stock, type_order= TypeOrderEnum.LIMITED.value )
        if bool(int(stock.get('production'))):
            self.getClass('bt_comprar', click=True)
        # self.sayExecute(stock= stock)

    def setFormOrder(self, stock={}):
        edtQuantity = self.getId('msg_quantity')
        edtQuantity.clear()
        edtQuantity.send_keys( stock.get('quantity') )
        edtStop = self.getId('msg_stoppx')
        edtStop.clear()
        edtStop.send_keys( stock.get('price_stop') )

    def assignOperation(self, stock={}, type_order=None):
        operation = {TypeOrderEnum.LIMITED.value: '0',
                     TypeOrderEnum.AGRESSION.value: '1',
                     TypeOrderEnum.ZERAR.value: '4',
                     TypeOrderEnum.CANCELAR.value: '4'}
        keyOper = operation.get(type_order)
        sign = os.environ.get('BROKER_SIGNATURE')
        self.driver.execute_script('document.getElementsByClassName("input_key")[%s].value = "%s"' %(keyOper, sign))

    def sayExecute(self, stock={}):
        if os.name != 'posix':  # open in macOsx
            os.system('say %s %s' %(stock.get('operation'), stock.get('quantity')))
        else:
            winspeech.say('order %s %s %s' %(stock.get('quantity'), stock.get('operation'), stock.get('stop_loss')[2:]))

    def openPanelOrderFast(self):
        count = 0
        while count < self.tryGet:
            try:
                tab_ordens = self.driver.find_element_by_class_name("bt_orders_boleta")
                tab_ordens.click()
                self.getClass('bt_open_orders_f', click=True) # btn_orders_fast
                return True
            except:
                self.closeModal()
                count += 1

    def closeModal(self):
        try:
            self.driver.execute_script('document.getElementsByClassName("bt_fechar_dis")[3].click()')
            self.driver.execute_script('document.getElementsByClassName("bt_fechar_dis")[2].click()')
            self.getId('ipo_close', click=True) # btnClose
        except:
            pass

    def testChangePrice(self, testValue):
        self.driver.execute_script('document.getElementsByClassName("lastPrice")[0].innerText = "%s"' %(testValue))
