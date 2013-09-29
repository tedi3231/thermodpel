#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
#
# Copyright 2013 SOABER, Inc.
#
import xmlrpclib
import dealcsv
import uuid
import os.path
import datetime

producttemplate = {
    'categories':[],
    'websites':[],
    'name':'',
    'description':'',
    'short_description':'',
    'weight':'',
    'status':'',
    'url_key':'',
    'price':'',
    'tax_class_id':1,
    'meta_title':'',
    'meta_keyword':'',
    'meta_description':'',
    'stock_data':{
        'qty':'100000000',
        'is_in_stock':1,
        'manage_stock':1,
    }
}

hasproc_count = 0
totalcount = 0

server = None
session = None

def testconfig( url , username , password ):
    result = True
    message = ''
    s = xmlrpclib.Server(url)
    try:
        sessionid = s.login(username,password)
    except Exception as e:
        result = False
        message = e.message
    return result,message

def convertimg2base64(imgpath):
    with open(imgpath,'rb') as f:
        data = f.read()
        return data.encode('base64')

def loginserver(url,username,password):
    global server
    global session
    server = xmlrpclib.Server(url)
    try:
        session = server.login(username,password)
    except Exception as e:
        raise Exception('连接服务器失败，错误如下:%s'%e.message)
    return server,session

def create_product(producttype,attrsetids,sku,item):
    print 'create_product starttime is %s' % datetime.datetime.now()
    productid = server.call(session,'catalog_product.create',[producttype,attrsetids,sku,item])
    print 'create product success'
    product_media = {
        'mime':'image/jpeg',
        #'content':convertimg2base64('girls.jpg'),
    }

    if item.get('image') and os.path.exists(item.get('image','')):
        product_media['content'] = convertimg2base64(item['image'])
        server.call(session,'catalog_product_attribute_media.create',[
            productid,{'file':product_media,'label':'image','position':'100','types':['image'],'exclude':0}
        ])
    if item.get('small_image') and os.path.exists(item.get('small_image','')):
        product_media['content'] = convertimg2base64(item['small_image'])
        server.call(session,'catalog_product_attribute_media.create',[
            productid,{'file':product_media,'label':'small image','position':'100','types':['small_image'],'exclude':0}
        ])
    #print item.get('thumbnail')
    if item.get('thumbnail') and os.path.exists(item.get('thumbnail','')):
        product_media['content'] = convertimg2base64(item['thumbnail'])
        result = server.call(session,'catalog_product_attribute_media.create',[
            productid,{'file':product_media,'label':'thumbnail','position':'100','types':['thumbnail'],'exclude':0}
        ])
        #print 'create thumbnail result is %s'%result
    print 'create image success'
    print 'create_product endtime is %s'%datetime.datetime.now()
    return productid

def getproductsfromfile(filepath):
    items = []
    items = dealcsv.get_content_with_directory(filepath)

    for item in items:
        print item.get('category_ids',None).split(',')
        item['category_ids'] =  item.get('category_ids','').split(',')
        item['website_ids'] =   item.get('website_ids','').split(',')
        item['stock_data'] = {
            'qty':item.get('stock_data_qty',''),
            'is_in_stock':int(item.get('stock_data_is_in_stock','0')),
            'manage_stock':int(item.get('stock_data_manage_stock','0')),
        }
        del item['stock_data_is_in_stock']
        del item['stock_data_manage_stock']
        del item['stock_data_qty']
    return items

def importproducts(url,username,password,filepath):
    global totalcount
    global hasproc_count
    loginserver(url,username,password)
    items = getproductsfromfile(filepath)
    totalcount = len(items)
    for item in items:
        create_product('simple','4',uuid.uuid4().get_hex(),item)
        hasproc_count = hasproc_count + 1
    print 'create product success'

if __name__ == '__main__':
    """
    item ={
        'category_ids':[8,9],
        'website_ids':[2],
        'name':'Product for test',
        'description':'description for test',
        'short_description':'short description for test',
        'weight':'10',
        'status':'1',
        'url_key':'url_key_for test',
        'price':'100',
        'tax_class_id':2,
        'meta_title':'Meta tiel for test',
        'meta_keyword':'key word for test',
        'meta_description':'product meta description',
        'stock_data':{
            'qty':'100000000',
            'is_in_stock':1,
            'manage_stock':1,
        }
    }
    loginserver('http://localhost/magento/index.php/api/xmlrpc','tedi','loveyuanyuan')
    print session
    result = create_product('simple','4','test_sku_010',item)
    #result = server.call(session,'catalog_product.create',['simple','4',
    #                     'test_sku_001',item])
    print result
    """
    #import dealcsv
    #print dealcsv.get_headers('products.csv')
    #print dealcsv.get_content_with_directory('products.csv')
    #print getproductsfromfile('products.csv')
    importproducts('http://localhost/magento/index.php/api/xmlrpc','tedi','loveyuanyuan','products.csv')
