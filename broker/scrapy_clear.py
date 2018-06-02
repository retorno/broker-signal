# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from webselenium import WebDriver
from enum import Enum
import os, time

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
        # import ipdb; ipdb.set_trace()
        count = 0
        while count < self.tryGet:
            try:
                print('#### passou 111')
                _class = self.driver.find_element_by_class_name(seletorClass)
                print('#### passou 222' + str(_class))
                if _class:
                    if click:
                        _class.click()
                    print('#### passou 333')
                    return _class
            except:
                print('#### passou 444')
                # time.sleep(0.1)
                count += 1
                continue
                # pass

    def getId(self, seletorId):
        count = 0
        while count < self.tryGet:
            try:
                _id = self.driver.find_element_by_id(seletorId)
                if _id:
                    return _id
            except:
                # time.sleep(0.1)
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
        self.getClass('bt_signin').click()
        self.getClass('right').click()
        self.openBroker()

    def limitPosition(self, stock={}):
        # Verifica se existe margem para operação
        # import ipdb; ipdb.set_trace()
        sendQuantity = int(stock.get('quantity'))
        maxPosition = self.getMaxPosition()
        limit = round(maxPosition / 2)
        if sendQuantity <= limit:
            return True
        stock.get('status').append('limit max position ' + str(limit))

    def getMaxPosition(self):
        # import ipdb;ipdb.set_trace()
        maxPosition = int(self.driver.execute_script('return document.getElementsByClassName("container_garantia_exposicao")[0].lastElementChild.value'))
        return maxPosition

    def getLastPrice(self):
        # import ipdb; ipdb.set_trace()
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
        # import ipdb; ipdb.set_trace()
        tab_orders_fast = self.getClass('bt_fast_boleta')
        tab_orders_fast.click()
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
            self.getClass(btnClass).click()
            return str(stock)
        else:
            stock.get('status').append('running in test')

    def zeraAll(self, stock={}):
        self.driver.execute_script("document.getElementsByClassName('bt_action')[1].click()")
        self.assignOperation(type_order= TypeOrderEnum.ZERAR.value)
        self.exeCancelOrder(stock=stock)
        return str(stock)

    def cancelOrders(self, stock={}):
        # import ipdb; ipdb.set_trace()
        count = 0
        while count < self.tryGet:
            try:
                btn_order = self.getClass('bt_action')
                btn_order.click()
                self.assignOperation(stock= stock, type_order= TypeOrderEnum.CANCELAR.value)
                self.exeCancelOrder(stock= stock)
                return str(stock)
            except:
                self.openPanelOrderFast()
                count += 1

    def openPanelOrderFast(self):
        tab_ordens = self.getClass('bt_orders_boleta')
        tab_ordens.click()
        btn_orders_fast = self.getClass('bt_open_orders_f')
        btn_orders_fast.click()

    def exeCancelOrder(self, stock={}):
        count = 0
        # import ipdb; ipdb.set_trace()
        while count < self.tryGet:
            try:
                # time.sleep(0.1)
                if bool(int(stock.get('production'))):
                    btn_cancel = 'bt_comprar'
                else:
                    btn_cancel = 'bt_fechar'
                self.driver.execute_script('document.getElementsByClassName("%s")[2].click()' %btn_cancel)
                return True
            except:
                count += 1
                # pass

    def orderFail(self):
        self.driver.execute_script('document.getElementsByClassName("docket-msg")[4].innerHTML == "%s"' %"Processando ordem anterior...")

    def updateCanDouble(self, stock={}):
        pass

    def canDouble(self, stock= {}, beforePosition= 0):
        double = False
        can_double = 0
        sendOperation = stock.get('operation') 
        pt_double = int(stock.get('point_to_double'))
        last_price = float(stock.get('last_price'))
        if beforePosition == 0:
            order_price = last_price
            return True
        else:
            order_price = int(os.environ.get('LAST_ORDEM_PRICE'))
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
        return str(position)

    def getTruePosition(self, stock={}):
        position = 0
        count = 0
        # import ipdb; ipdb.set_trace()
        sendQuantity = stock.get('quantity')
        while count < self.tryGet:
            # time.sleep(0.1)
            currentPosition = self.getPosition()
            if sendQuantity == currentPosition:
                return True
            count += 1

    def getPriceStop(self, stock={}):
        lastPrice = float(self.getLastPrice())
        stopLoss = float(stock.get('stop_loss'))
        calc_stop = int(stock.get('calculate_stop'))
        sendOperation = stock.get('operation')
        if calc_stop and sendOperation == OperationEnum.COMPRA.value:
            stopLoss = lastPrice - stopLoss
        elif calc_stop and sendOperation == OperationEnum.VENDA.value:
            stopLoss = lastPrice + stopLoss
        print("###### lastPrice -> " + str(lastPrice) + " stop_loss -> " +  str(stopLoss)  + " calculate_stop -> " + str(calc_stop))
        return str(int(stopLoss))

    def setStop(self, stock= {}):
        # import ipdb; ipdb.set_trace()
        if self.getTruePosition(stock= stock):
            os.environ['LIMIT_ORDEM_PRICE'] = stock.get('last_price')
            limit_price = os.environ.get('LIMIT_ORDEM_PRICE')
            stock['stop_loss'] = self.getPriceStop(stock= stock)
            stock['type_operation'] = TypeOrderEnum.STOP.value
            self.setOrder(stock= stock)
        else:
            self.zeraAll()
            stock.get('status').append('position => %s in the broker is different' %stock.get('quantity'))
        return str(stock)

    def setFormOrder(self, stock={}):
        edtQuantity = self.getId('msg_quantity')
        edtQuantity.clear()
        edtQuantity.send_keys( stock.get('quantity') )
        edtStop = self.getId('msg_stoppx')
        edtStop.clear()
        edtStop.send_keys( stock.get('stop_loss') )

    def setOrder(self, stock={}):
        # condition to stop-loss
        # import ipdb; ipdb.set_trace()
        sendOperation = stock.get('operation')
        if sendOperation == OperationEnum.COMPRA.value:
            btnClass = 'bt_red_boleta'
        elif sendOperation == OperationEnum.VENDA.value:
            btnClass = 'bt_blue_boleta'
        print("### chamou tab_order --" + btnClass  + " sendOperation -> " + sendOperation )
        tab_buy_sell = self.getClass(btnClass, click=True)
        # tab_buy_sell.click()
        typeOperation = stock.get('type_operation')    # ['Limitada', 'Stop']
        comboTipo = self.driver.find_element_by_xpath("//select[@id='msg_exchangeordertype']/option[text()= '%s']" %typeOperation)
        comboTipo.click()
        self.setFormOrder(stock= stock)
        self.assignOperation( stock= stock, type_order= TypeOrderEnum.LIMITED.value )
        if bool(int(stock.get('production'))):
            self.getClass('bt_comprar').click()
        else:
            stock.get('status').append('running in test')
        stock.get('status').append('order -> %s position -> %s' %(sendOperation, stock.get('quantity')))
        #self.sayExecute(stock= stock)

    def assignOperation(self, stock={}, type_order=None):
        operation = {TypeOrderEnum.LIMITED.value: '0',
                     TypeOrderEnum.AGRESSION.value: '1',
                     TypeOrderEnum.ZERAR.value: '4',
                     TypeOrderEnum.CANCELAR.value: '4'}
        keyOper = operation.get(type_order)
        sign = os.environ.get('BROKER_SIGNATURE')
        self.driver.execute_script('document.getElementsByClassName("input_key")[%s].value = "%s"' %(keyOper, sign))

    def sayExecute(self, stock={}):
        # import ipdb; ipdb.set_trace()
        if os.name != 'posix':  # open in macOsx
            os.system('say %s %s' %(stock.get('operation'), stock.get('quantity')))
        else:
            winspeech.say('order %s %s %s' %(stock.get('quantity'), stock.get('operation'), stock.get('stop_loss')[2:]))

    def closeModal(self):
        try:
            # import ipdb; ipdb.set_trace()
            self.driver.execute_script('document.getElementsByClassName("bt_fechar_dis")[2].click()')
            btnClose = self.getId('ipo_close')
            if btnClose:
                btnClose.click()
        except:
            pass

    def testChangePrice(self, testValue):
        self.driver.execute_script('document.getElementsByClassName("lastPrice")[0].innerText = "%s"' %(testValue))