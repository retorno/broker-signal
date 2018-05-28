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

    tryGet = 25
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

    def getClass(self, seletorClass):
        count = 0
        while count < self.tryGet:
            try:
                # time.sleep(0.2)
                _class = self.driver.find_element_by_class_name( seletorClass )
                if _class:
                    return _class
            except:
                count += 1
                pass

    def getId(self, seletorId):
        count = 0
        while count < self.tryGet:
            try:
                # time.sleep(0.2)
                _id = self.driver.find_element_by_id( seletorId )
                if _id:
                    return _id
            except:
                count += 1
                pass

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
        maxPosition = self.getMaxPosition(stock= stock)
        limit = round(maxPosition / 2)
        if sendQuantity <= limit:
            return True
        stock['status'] = 'limit max position ' + str(limit)

    def getTruePosition(self, stock={}):
        position = int(self.driver.execute_script('return document.getElementsByClassName("input_gray")[3].value'))
        return str(position)

    # def getPosition(self, stock={}):
    #     position = 0
    #     count = 0
    #     # import ipdb; ipdb.set_trace()
    #     while count < self.tryGet:
    #         time.sleep(0.1)
    #         position = int(self.driver.execute_script('return document.getElementsByClassName("input_gray")[3].value'))
    #         if position == stock.get('quantity'):
    #             return int(position)
    #         count += 1
    #     return str('0')

    def getMaxPosition(self, stock={}):
        # import ipdb;ipdb.set_trace()
        maxPosition = int(self.driver.execute_script('return document.getElementsByClassName("container_garantia_exposicao")[0].lastElementChild.value'))
        return maxPosition

    def getLastPrice(self):
        # import ipdb; ipdb.set_trace()
        lastPrice = self.getClass('lastPrice').text
        if lastPrice:
            lastPrice.replace(',','.')
        return lastPrice

    def getRecipe(self, stock={}):
        recipe = self.getClass('ng-binding').text[3:]
        return recipe

    def zeraAll(self, stock={}):
        tab_ordens = self.getClass('bt_orders_boleta')
        tab_ordens.click()
        self.driver.execute_script("document.getElementsByClassName('bt_action')[1].click()")
        self.assignOperation(type_order= TypeOrderEnum.ZERAR.value)
        self.driver.execute_script("document.getElementsByClassName('bt_comprar')[2].click()")
        return str(stock)

    def setOrderFast(self, stock={}):
        # import ipdb; ipdb.set_trace()
        self.getClass('bt_fast_boleta').click()
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
            stock['status'] = 'Test'

    def cancelOrders(self, stock={}):
        # import ipdb; ipdb.set_trace()
        self.getClass('bt_orders_boleta').click()
        self.getClass('bt_open_orders_f').click()
        btn_order = self.getClass('bt_action')
        btn_order.click()
        self.assignOperation(stock= stock, type_order= TypeOrderEnum.CANCELAR.value)
        self.exeCancelOrder(stock=stock)
        return str(stock)

    def exeCancelOrder(self, stock={}):
        count = 0
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
                pass

    def canDouble(self, stock= {}, beforePosition= 0):
        double = False
        if beforePosition == 0:
            return True
        sendOperation = stock.get('operation') 
        pt_double = int(stock.get('point_to_double'))
        order_price = int(os.environ.get('LAST_ORDEM_PRICE'))
        last_price = float(stock.get('last_price'))
        if sendOperation == OperationEnum.COMPRA.value:  
            double = last_price > (order_price + pt_double)
        elif sendOperation == OperationEnum.VENDA.value:
            double = last_price < (order_price - pt_double)
        if not double:
            stock['status'] = 'did not reach value, not possible to double'
        return double

    def setStop(self, stock= {}):
        count = 0
        currentPosition = 0
        # import ipdb; ipdb.set_trace()
        sendOperation = stock.get('operation')
        lastPrice = float(self.getLastPrice())
        stopLoss = float(stock.get('stop_loss'))
        calc_stop = int(stock.get('calculate_stop'))
        if sendOperation == OperationEnum.COMPRA.value:
            if calc_stop:
                stopLoss = lastPrice - stopLoss
        elif sendOperation == OperationEnum.VENDA.value:
            if calc_stop:
                stopLoss = lastPrice + stopLoss
        print("###### lastPrice -> " + str(lastPrice) + " stopLoss -> " +  str(stopLoss)  + " calc stop -> " + str(stock.get('calculate_stop')))
        # currentPosition = abs(int(self.getPosition(stock= stock)))

        stock['stop_loss'] = str(int(stopLoss))
        stock['type_operation'] = TypeOrderEnum.STOP.value
        self.setOrder(stock= stock)
        stock['status'] = "order %s position %s" %(sendOperation, currentPosition)
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
        if stock.get('operation') == OperationEnum.COMPRA.value:
            btnClass = 'bt_red_boleta'
        if stock.get('operation') == OperationEnum.VENDA.value:
            btnClass = 'bt_blue_boleta'
        self.getClass(btnClass).click()
        typeOperation = stock.get('type_operation')    # ['Limitada', 'Stop']
        comboTipo = self.driver.find_element_by_xpath("//select[@id='msg_exchangeordertype']/option[text()= '%s']" %typeOperation)
        comboTipo.click()
        self.setFormOrder(stock= stock)
        self.assignOperation( stock= stock, type_order= TypeOrderEnum.LIMITED.value )
        if bool(int(stock.get('production'))):
            self.getClass('bt_comprar').click()
        else:
            stock['status'] = 'Test'
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