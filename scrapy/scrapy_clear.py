# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os, sys
here = os.environ.get("PROJECT_BROKER")
sys.path.append(here)
from utils.WebDriver import *
from utils.WebDriver import WebDriver
from model.broker_model import OperationEnum, TypeOrderEnum
from utils import Config, Logger
import os, time, re


class ScrapyClear(WebDriver, Logger):
    env = None

    def __init__(self):
        Config.__init__(self)
        Logger.__init__(self)
        self.env = self.conf.get("enviroment")
        if self.env.get("RUN_CONTEINER"):
            super().__init__(self)
        else:
            WebDriver.__init__(self)

    def login(self, username=None):
        self.get(os.environ.get('URL_BROKER'))
        broker_cpf_cnpj = os.environ.get('BROKER_CPF_CNPJ')
        broker_password = os.environ.get('BROKER_PASSWORD')
        broker_dt_nasc = os.environ.get('BROKER_DT_NASC')
        cpf_cnpj = self.element(ID('identificationNumber'))
        cpf_cnpj.clear()
        cpf_cnpj.send_keys(broker_cpf_cnpj)
        password = self.element(ID('password'))
        password.clear()
        password.send_keys(broker_password)
        dt_nasc = self.wait_until(present(CLASS('input_date')))
        dt_nasc.clear()
        dt_nasc.send_keys(broker_dt_nasc)
        self.element(CLASS('bt_signin')).click()
        self.element(CLASS('right')).click()
        self.get(os.environ.get('URL_BROKER'))

    def getMaxPosition(self):
        maxPosition = self.execute_script('return document.getElementsByClassName("container_garantia_exposicao")[0].lastElementChild.value')
        if not maxPosition:
            return 0
        return int(maxPosition)

    def getLastPrice(self):
        lastPrice = self.element(CLASS('lastPrice'))
        if lastPrice:
            lastPrice = lastPrice.text.replace(',','.')
            return lastPrice
        else:
            return '0'

    def getRecipe(self, stock={}):
        recipe = self.element(CLASS('ng-binding'))
        if recipe:
            recipe = recipe.text[3:].replace(',','.')
            return recipe
        else:
            return '0'

    def setOrderFast(self, stock={}):
        tab_orders_fast = self.element(CLASS('bt_fast_boleta'))
        tab_orders_fast.click()
        quantity = stock.get('quantity')
        self.execute_script("document.getElementsByClassName('ng-valid-min')[4].value = %s" %quantity)
        self.assignOperation( type_order= TypeOrderEnum.AGRESSION.value )
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
            self.element(CLASS(btnClass)).click()
        else:
            stock.get('status').append('running in test')
        self.priceLastOrder = float(stock.get("last_price"))
        self.priceLastStop = 0
        return str(stock)

    def zeraAll(self):
        self.cancelOrders()
        self.execute_script("document.getElementsByClassName('bt_action')[1].click()")
        self.assignOperation( type_order= TypeOrderEnum.ZERAR.value )
        self.exeCancelOrder()
        self.priceLastOrder = 0
        self.priceLastStop = 0
        return {}

    def cancelOrders(self):
        btn_order = self.element(CLASS('bt_action'))
        btn_order.click()
        self.assignOperation( type_order= TypeOrderEnum.CANCELAR.value )
        self.exeCancelOrder()
        return {}

    def exeCancelOrder(self):
        btn_execute = 'bt_comprar'
        btn_cancel = 'bt_fechar'
        self.execute_script('document.getElementsByClassName("%s")[2].click()' %btn_execute)
        self.execute_script('document.getElementsByClassName("%s")[2].click()' %btn_cancel)

    def orderFail(self):
        self.execute_script('document.getElementsByClassName("docket-msg")[4].innerHTML == "%s"' %"Processando ordem anterior...")

    def updatePosition(self):
        self.element(CLASS("bt_red_boleta")).click()
        self.element(CLASS("bt_blue_boleta")).click()

    def getPosition(self):
        self.updatePosition()
        position = self.execute_script('return document.getElementsByClassName("input_gray")[3].value')
        if not position:
            return "0"
        return str(position)

    def ordersOpen(self):
        qtd_open = 0
        qtd_buy = 0
        qtd_sell = 0
        orders = self.element(CLASS('middle_orders_overflow')).text
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
        stock['type_operation'] = TypeOrderEnum.STOP.value
        self.cancelOrders()
        self.setOrder(stock= stock)
        print('Send stop => %s quant => %s in price => %s' %(stock.get('operation'), stock.get('quantity'), price_stop))
        print("------------------------------------------------------------------------------------------------")

    def setOrder(self, stock={}):
        sendOperation = stock.get('operation')
        if sendOperation == OperationEnum.COMPRA.value:
            btnClass = 'bt_red_boleta'
        elif sendOperation == OperationEnum.VENDA.value:
            btnClass = 'bt_blue_boleta'
        tab_buy_sell = self.element(CLASS(btnClass))
        tab_buy_sell.click()
        typeOperation = stock.get('type_operation')    # ['Limitada', 'Stop']
        comboTipo = self.find_element_by_xpath("//select[@id='msg_exchangeordertype']/option[text()= '%s']" %typeOperation)
        comboTipo.click()
        self.setFormOrder(stock= stock)
        self.assignOperation( type_order= TypeOrderEnum.LIMITED.value )
        if int(stock.get('production')):
            self.element(CLASS('bt_comprar')).click()

    def setFormOrder(self, stock={}):
        edtQuantity = self.element(ID('msg_quantity'))
        edtQuantity.clear()
        edtQuantity.send_keys( stock.get('quantity') )
        edtStop = self.element(ID('msg_stoppx'))
        edtStop.clear()
        edtStop.send_keys( stock.get('price_stop') )

    def assignOperation(self, type_order=None):
        operation = {TypeOrderEnum.LIMITED.value: '0',
                     TypeOrderEnum.AGRESSION.value: '1',
                     TypeOrderEnum.ZERAR.value: '4',
                     TypeOrderEnum.CANCELAR.value: '4'}
        keyOper = operation.get(type_order)
        sign = os.environ.get('BROKER_SIGNATURE')
        self.execute_script('document.getElementsByClassName("input_key")[%s].value = "%s"' %(keyOper, sign))

    def openPanelOrderFast(self):
        tab_ordens = self.element(CLASS("bt_orders_boleta"))
        tab_ordens.click()
        btn_orders_fast = self.element(CLASS('bt_open_orders_f'))
        btn_orders_fast.click()
        return True

    def closeModal(self):
        try:
            self.execute_script('document.getElementsByClassName("bt_fechar_dis")[3].click()')
            self.execute_script('document.getElementsByClassName("bt_fechar_dis")[2].click()')
            btnClose = self.wait_until(present(ID('ipo_close')))
            btnClose.click()
        except:
            pass

    def testChangePrice(self, testValue):
        self.execute_script('document.getElementsByClassName("lastPrice")[0].innerText = "%s"' %(testValue))
