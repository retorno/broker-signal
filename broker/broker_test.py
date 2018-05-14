#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import connectBroker
# import json
# from bson import ObjectId
# import os
# from correios import findCep, createPessoa, findPessoa
# from pymongo import MongoClient
# client = MongoClient(os.environ.get('DOCKER_HOST'), 27017)
# db = client.test_database
# enderecos = db.enderecos


class BrokerTest(unittest.TestCase):

	scrapy = connectBroker()
	def test_start_scrapy(self):
		# changeStop
		pass

	def test_limit_position(self):
		pass

	# def test_find_cep(self):
	# 	valor_esperado = {'sucesso': 'true', 
	# 					  'endereco': {'cep': '04113000', 
	# 							       'logr': 'Colônia da Glória', 
	# 								   'compl': 'Rua', 
	# 							       'bairro': 'Vila Mariana', 
	# 								   'cidade': 'São Paulo', 
	# 								   'uf': 'SP'}
	# 					 }
	# 	valor = eval(findCep('04113000'))
	# 	del valor.get('endereco')['_id']
	# 	self.assertDictEqual(valor_esperado, valor)

	# def test_endereco_mongo(self):
	# 	valor_esperado = {'cep': '04113000', 
	# 					'logr': 'Colônia da Glória', 
	# 					'compl': 'Rua', 
	# 					'bairro': 'Vila Mariana',
	# 					'cidade': 'São Paulo', 
	# 					'uf': 'SP'}
	# 	valor = eval(findCep('04113000'))
	# 	del valor.get('endereco')['_id']
	# 	enderecos.find(valor)

	# def test_find_pessoa(self):
	# 	test = {"_id": "57823417936", "nome": "joao", "idade": "23"}
	# 	valor_esperado = eval(createPessoa(test))
	# 	valor = eval(findPessoa(cpf="57823417936"))
	# 	self.assertDictEqual(valor_esperado, valor)


if __name__ == '__main__':
	unittest.main()