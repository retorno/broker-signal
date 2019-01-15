# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from utils.webselenium import WebDriver
from utils.stock_firebase import saveFirebase
from broker.broker_roles import OperationEnum, TypeOrderEnum
import os
import time
import re

if os.name != 'posix':
    import winspeech


class ScrapyClear(WebDriver):

    tryGet = 13

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

    def getLastPrice(self):
        lastPrice = self.getClass('lastPrice')
        if lastPrice:
            lastPrice = lastPrice.text.replace(',','.')
            return lastPrice
        else:
            return '0'

    def setOrderFast(self, stock={}):
        self.getClass('bt_fast_boleta', click=True)  # tab_orders_fast
        quantity = stock['quantity']
        self.driver.execute_script("document.getElementsByClassName('ng-valid-min')[4].value = %s" %quantity)
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
            self.getClass(btnClass, click=True)
        else:
            return str('running in test')
        return str('Ok')

    def zeraAll(self, stock={}):
        self.driver.execute_script("document.getElementsByClassName('bt_action')[1].click()")
        self.assignOperation(type_order= TypeOrderEnum.ZERAR.value)
        return str(stock)

    def updatePosition(self):
        self.getClass("bt_red_boleta", click= True)
        self.getClass("bt_blue_boleta", click= True)

    def getPosition(self):
        self.updatePosition()
        position = self.driver.execute_script('return document.getElementsByClassName("input_gray")[3].value')
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
        