from __future__ import unicode_literals
from webselenium import WebDriver
from envi import config


class OperationEnum:
    def __init__(self):
        pass

    COMPRA = 'Buy'
    VENDA = 'Sell'
    ZERAR = 'Zerar'
    INVERT = 'Invert'


class TypeOrderEnum:
    def __init__(self):
        pass

    STOP = 'Stop'
    LIMITED = 'Limited'
    AGRESSION = 'Aggression'
    CANCELAR = 'Cancelar'
    ZERAR = 'Zerar'


class ScrapyClear(WebDriver):
    def __init__(self):
        super(ScrapyClear, self).__init__()


    def openBroker(self):
        self.driver.get(config["URL_BROKER"])


    def getClass(self, seletorclass, click=None):
        count = 0
        while count < 15:
            try:
                _class = self.driver.find_element_by_class_name(seletorclass)
                if _class:
                    if click:
                        _class.click()
                    return _class
            except:
                count += 1


    def getId(self, seletorid, click=None):
        count = 0
        while count < 15:
            try:
                _id = self.driver.find_element_by_id(seletorid)
                if _id:
                    if click:
                        _id.click()
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


    def getLastPrice(self):
        lastPrice = self.getClass('lastPrice')
        if lastPrice:
            lastPrice = lastPrice.text.replace(',', '.')
            return lastPrice
        else:
            return '0'


    def zeraAll(self):
        self.driver.execute_script("document.getElementsByClassName('bt_action')[1].click()")
        self.assignOperation(type_order=TypeOrderEnum.ZERAR)
        self.exeCancelOrder()
        return "OK"


    def cancelOrders(self):
        self.getClass('bt_action', click=True)  # btn_order
        self.assignOperation(type_order=TypeOrderEnum.CANCELAR)
        self.exeCancelOrder()
        return "OK"


    def openPanelOrderFast(self):
        self.getClass('bt_orders_boleta', click=True)  # tab_ordens
        self.getClass('bt_open_orders_f', click=True)  # btn_orders_fast


    def exeCancelOrder(self):
        count = 0
        while count < 15:
            try:
                btn_cancel = 'bt_comprar'
                self.driver.execute_script('document.getElementsByClassName("%s")[2].click()' % btn_cancel)
                return True
            except:
                count += 1


    def getPosition(self):
        position = self.driver.execute_script('return document.getElementsByClassName("input_gray")[3].value')
        return str(position)


    def setOrderFast(self, stock):
        tab_orders_fast = self.element(CLASS('bt_fast_boleta'))
        tab_orders_fast.click()
        quantity = stock['quantity']
        self.execute_script("document.getElementsByClassName('ng-valid-min')[4].value = %s" % quantity)
        self.assignOperation(type_order=TypeOrderEnum.AGRESSION.value)
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
            self.element(CLASS(btnClass)).click()
        else:
            print('running in test')


    def assignOperation(self, type_order=None):
        operation = {TypeOrderEnum.LIMITED: '0',
                     TypeOrderEnum.AGRESSION: '1',
                     TypeOrderEnum.ZERAR: '4',
                     TypeOrderEnum.CANCELAR: '4'}
        keyOper = operation.get(type_order)
        sign = config["BROKER_SIGNATURE"]
        self.driver.execute_script('document.getElementsByClassName("input_key")[%s].value = "%s"' % (keyOper, sign))


    def closeModal(self):
        try:
            self.driver.execute_script('document.getElementsByClassName("bt_fechar_dis")[2].click()')
            self.getId('ipo_close', click=True)  # btnClose
        except:
            pass

