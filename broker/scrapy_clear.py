# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from broker.broker_roles import OperationEnum, TypeOrderEnum, BrokerRoles
import os
import time
import re


class ScrapyClear(BrokerRoles):

    def __init__(self, *args, **kwargs):
        super().__init__()

    def openBroker(self):
        self.driver.get(os.environ.get('URL_BROKER'))

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

    def setStop(self, stock= {}):
        if stock.get("quantity") != "0":
            price_stop = self.getPriceStop(stock= stock)
            stock['price_stop'] = price_stop
            stock['type_operation'] = TypeOrderEnum.STOP.value
            self.cancelOrders(stock=stock)
            self.setOrder(stock= stock)
            stock["recipe"] = self.getRecipe()
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
