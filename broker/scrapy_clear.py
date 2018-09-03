# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from webselenium import WebDriver
from enum import Enum
import os, time
from stock_firebase import saveFirebase
import re

if os.name != 'posix':
    import winspeech


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

class ScrapyClear(WebDriver):

    tryGet = 13
    lastOrderPrice = 0
    limitOrdemPrice = 0
    def __init__(self, *args, **kwargs):
        config_chrome = {}
        # config_chrome['donwload_dir'] = settings.DOWNLOAD_DIR
        # config_chrome['screenshot_dir'] = settings.SCREENSHOT_DIR
        # config_chrome['never_ask_savetodisk'] = 'application/pdf,text/plain,application/octet-stream'
        # config_chrome['screenshot_mask'] = '{0}/screenshot_{1}.png'
        # config_chrome['screenshot_date_mask'] = '%Y-%m-%d__%H:%M:%S'
        # config_chrome['command_executor_ip'] = 'localhost'
        # config_chrome['command_executor_mask'] = 'http://{0}:4444/wd/hub'
        super(ScrapyClear, self).__init__(config= config_chrome)

    def openBroker(self):
        # self.driver.manage().window().setSize(windowMinSize)
        # self.driver.find_element_by_tag_name('body').send_keys(Keys.LEFT_CONTROL + Keys.COMMAND + 'f')
        # actions = ActionChains(self.driver)
        # actions.send_keys(Keys.LEFT_SHIFT + Keys.COMMAND + 'j')
        # actions.perform()
        # if len(self.driver.window_handles) > 1:
        #   self.driver.switch_to_window(self.driver.window_handles[0])
        # import ipdb; ipdb.set_trace()
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
            return str(stock)
        else:
            stock.get('status').append('running in test')

    def zeraAll(self, stock={}):
        self.driver.execute_script("document.getElementsByClassName('bt_action')[1].click()")
        self.assignOperation(type_order= TypeOrderEnum.ZERAR.value)
        self.exeCancelOrder(stock=stock)
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

    def orderFail(self):
        self.driver.execute_script('document.getElementsByClassName("docket-msg")[4].innerHTML == "%s"' %"Processando ordem anterior...")

    def canDouble(self, stock= {}, beforePosition= 0):
        double = False
        can_double = 0
        sendOperation = stock.get('operation')
        pt_double = float(stock.get('point_to_double'))
        last_price = float(stock.get('last_price'))
        if beforePosition == 0:
            order_price = last_price
            return True
        else:
            order_price = float(self.lastOrderPrice)
        print("order_price => " + str(order_price) + " pt_double => " + str(pt_double))
        if sendOperation == OperationEnum.COMPRA.value:  
            can_double = order_price + pt_double
            double = last_price > can_double
        elif sendOperation == OperationEnum.VENDA.value:
            can_double = order_price - pt_double
            double = last_price < can_double
        stock['can_double'] = str(can_double)
        return double

    def getPosition(self):
        position = self.driver.execute_script('return document.getElementsByClassName("input_gray")[3].value')
        if not position:
            return "0"
        return str(position)

    def getPriceStop(self, stock={}):
        lastPrice = float(self.getLastPrice())
        stopLoss = float(stock.get('stop_loss'))
        # calc_stop = int(stock.get('calculate_stop'))
        sendOperation = stock.get('operation')
        # if calc_stop and 
        if sendOperation == OperationEnum.COMPRA.value:
            stopLoss = lastPrice - stopLoss
        # elif calc_stop and 
        elif sendOperation == OperationEnum.VENDA.value:
            stopLoss = lastPrice + stopLoss
        return str(int(stopLoss))

    def ordersOpen(self):
        qtd_open = 0
        qtd_buy = 0
        qtd_sell = 0
        orders = self.getClass('middle_orders_overflow').text
        #orders = 'WINV18 - Compra Stop\n1\nMarket\nExecutada\nWINV18 - Venda\n1\nMarket\nExecutada\nWINV18 - Compra Stop\n1\nMarket\nExecutada\nWINV18 - Venda\n1\nMarket\nExecutada\nWINV18 - Venda Stop\n1\nMarket\nExecutada\nWINV18 - Compra\n1\nMarket\nExecutada\nWINV18 - Compra Stop\n1\nMarket\nExecutada\nWINV18 - Venda\n1\nMarket\nExecutada\nWINV18 - Compra Stop\n1\nMarket\nExecutada\nWINV18 - Venda\n1\nMarket\nExecutada'
        #import ipdb; ipdb.set_trace()

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

    def isOpenOrders(self, stock={}):
        count = 0
        sendOperation = stock.get('operation')
        while count < self.tryGet:
            try:
                time.sleep(0.2)
                orders_open = self.ordersOpen()
                if orders_open.get("qtd_open") == stock.get("quantity"):
                    if sendOperation == OperationEnum.COMPRA.value and orders_open.get("qtd_buy") == stock.get("quantity"):
                        return True
                    elif sendOperation == OperationEnum.VENDA.value and orders_open.get("qtd_sell") == stock.get("quantity"):
                        return True
                count += 1
            except:
                count += 1

    def getTruePosition(self, stock={}):
        count = 0
        sendQuantity = int(stock.get('quantity'))
        currentPosition = 0
        while count < self.tryGet:
            time.sleep(0.2)
            currentPosition = abs(int(self.getPosition()))
            if sendQuantity == currentPosition and currentPosition != 0:
                return True
            count += 1
        return currentPosition

    def checkStop(self, stock={}):
        count = 0
        if True: #self.getTruePosition(stock=stock):
            while count < self.tryGet:
                if self.isOpenOrders(stock=stock):
                    stock["recipe"] = self.getRecipe()
                    saveFirebase(stock= stock)
                    return True
                else:
                    self.cancelOrders(stock=stock)
                    print("=>>  acabou de cancelar tudo !!!")
                    self.setStop(stock=stock)
                count += 1
        else:
            self.zeraAll()
        stock.get('status').append('position => %s in the broker is different' %stock.get('quantity'))

    def setStop(self, stock= {}):
        limitOrdemPrice = stock.get('last_price')
        stock['stop_loss_final'] = self.getPriceStop(stock= stock)
        stock['type_operation'] = TypeOrderEnum.STOP.value
        self.setOrder(stock= stock)

    def setFormOrder(self, stock={}):
        edtQuantity = self.getId('msg_quantity')
        edtQuantity.clear()
        edtQuantity.send_keys( stock.get('quantity') )
        edtStop = self.getId('msg_stoppx')
        edtStop.clear()
        edtStop.send_keys( stock.get('stop_loss_final') )

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
                count += 1
                self.closeModal()

    def closeModal(self):
        # import ipdb; ipdb.set_trace()
        try:
            self.driver.execute_script('document.getElementsByClassName("bt_fechar_dis")[3].click()')
            self.driver.execute_script('document.getElementsByClassName("bt_fechar_dis")[2].click()')
            self.getId('ipo_close', click=True) # btnClose
        except:
            pass

    def testChangePrice(self, testValue):
        self.driver.execute_script('document.getElementsByClassName("lastPrice")[0].innerText = "%s"' %(testValue))