# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from utils.WebDriver import *
from utils.WebDriver import WebDriver
import os
import time
import re
from enum import Enum
from utils import Config


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



class ScrapyClear():

    def __init__(self):
        # super().__init__()
        self.driver = WebDriver()

    def openBroker(self):
        self.driver.get(os.environ.get('URL_BROKER'))

    def setLogin(self, username=None):
        print ("AKKKKKKKKKKKKKKK")
        # import ipdb; ipdb.set_trace()
        broker_cpf_cnpj = os.environ.get('BROKER_CPF_CNPJ')
        broker_password = os.environ.get('BROKER_PASSWORD')
        broker_dt_nasc = os.environ.get('BROKER_DT_NASC')
        cpf_cnpj = self.driver.element(ID('identificationNumber'))
        cpf_cnpj.clear()
        cpf_cnpj.send_keys(broker_cpf_cnpj)
        password = self.driver.element(ID('password'))
        password.clear()
        password.send_keys(broker_password)
        dt_nasc = self.driver.element(CLASS('input_date'))
        dt_nasc.clear()
        dt_nasc.send_keys(broker_dt_nasc)
        self.driver.element(CLASS('bt_signin')).click()
        self.driver.element(CLASS('right')).click()
        self.openBroker()

    def getLastPrice(self):
        lastPrice = self.driver.element(CLASS('lastPrice'))
        if lastPrice:
            lastPrice = lastPrice.text.replace(',','.')
            return lastPrice
        else:
            return '0'

    def setOrderFast(self, stock={}):
        tab_orders_fast = self.driver.element(CLASS('bt_fast_boleta'))
        tab_orders_fast.click()
        quantity = stock['quantity']
        self.execute_script("document.getElementsByClassName('ng-valid-min')[4].value = %s" %quantity)
        self.assignOperation( type_order= TypeOrderEnum.AGRESSION.value )
        if bool(int(stock['production'])):
            operation = stock['operation']
            if operation == OperationEnum.COMPRA.value:
                btnClass = 'bt_fast_buy'
            elif operation == OperationEnum.VENDA.value:
                btnClass = 'bt_fast_sell'
            elif operation == OperationEnum.ZERAR.value:
                btnClass = 'bt_fast_rollback'
            elif operation == OperationEnum.INVERT.value:
                btnClass = 'bt_fast_flip'
                self.driver.element(CLASS(btnClass)).click()
        else:
            print('running in test')
        return "Ok"

    def zeraAll(self):
        self.driver.execute_script("document.getElementsByClassName('bt_action')[1].click()")
        self.assignOperation(type_order=TypeOrderEnum.ZERAR.value)
        self.exeCancelOrder()
        return "OK"

    def exeCancelOrder(self):
        btn_execute = 'bt_comprar'
        btn_cancel = 'bt_fechar'
        self.execute_script('document.getElementsByClassName("%s")[2].click()' %btn_execute)
        self.execute_script('document.getElementsByClassName("%s")[2].click()' %btn_cancel)

    def updatePosition(self):
        self.driver.element(CLASS("bt_red_boleta")).click()
        self.driver.element(CLASS("bt_blue_boleta")).click()

    def getPosition(self):
        self.updatePosition()
        position = self.execute_script('return document.getElementsByClassName("input_gray")[3].value')
        if not position:
            return "0"
        return str(position)

    def assignOperation(self, type_order=None):
        operation = {TypeOrderEnum.LIMITED.value: '0',
                     TypeOrderEnum.AGRESSION.value: '1',
                     TypeOrderEnum.ZERAR.value: '4',
                     TypeOrderEnum.CANCELAR.value: '4'}
        keyOper = operation.get(type_order)
        sign = os.environ.get('BROKER_SIGNATURE')
        self.execute_script('document.getElementsByClassName("input_key")[%s].value = "%s"' %(keyOper, sign))

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
