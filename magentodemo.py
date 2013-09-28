#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
#
# Copyright 2013 SOABER, Inc.
#
import xmlrpclib

if __name__ == '__main__':
    server = xmlrpclib.Server("http://localhost/magento/index.php/api/xmlrpc")
    print server
    session = server.login("tedi3231","loveyuanyuan")
    print session
    products = server.call(session,'catalog_product.list')

    #for item in products:
    #    print item['name']
    
    item ={
        'categories':[12],
        'websites':[2],
        'name':'Product for test',
        'description':'description for test',
        'short_description':'short description for test',
        'weight':'10',
        'status':'1',
        'url_key':'url_key_for test',
        'price':'100',
        'tax_calss_id':1,
        'meta_title':'Meta tiel for test',
        'meta_keyword':'key word for test',
        'meta_description':'product meta description'
    }
    result = server.call(session,'catalog_product.create',['simple','9',
                         'test_sku_001',item])
    print result
    
