#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
#
# Copyright 2013 SOABER, Inc.
#
import pymssql
import csv,codecs,cStringIO

class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
    def __iter__(self):
        return self
    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]
    def __iter__(self):
        return self

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

#with open('xxx.csv','rb') as fin, open('lll.csv','wb') as fout:
#   reader = UnicodeReader(fin)
#    writer = UnicodeWriter(fout,quoting=csv.QUOTE_ALL)
#    for line in reader:
#        writer.writerow(line)
def readcustomerfromdatabase():
    zh_rows=[]
    en_rows=[]
    conn=pymssql.connect(host="192.1.8.202",user="sa",password="p@ssw0rd",database="MDM_Customer",as_dict=True,charset="UTF8")
    cur=conn.cursor()
    #cur.execute("SELECT top 10 * FROM Customer_Sap where customercode='USH0000044'")
    cur.execute("SELECT * FROM Customer_Sap ")
    for row in cur:
        result={
            "customercode":row["CustomerCode"],
            "companyName":row["CompanyName"] and " ".join(row["CompanyName"].split()) or "",
            "companyNameEn":row["CompanyNameEn"] or "",
            "address":row["RegisterAddress"] or "",            
        }        
        if row["CurrencyType"] and row["CurrencyType"]=="RMB":
            zh_rows.append(result)
        else:
            en_rows.append(result)
    conn.close()
    return zh_rows,en_rows

def readdpelfromdatabase():
    zh_rows=[]
    en_rows=[]
    conn=pymssql.connect(host="192.1.8.202",user="sa",password="p@ssw0rd",database="MDM_Customer",as_dict=True,charset="UTF8")
    cur=conn.cursor()
    cur.execute("SELECT * FROM DPELCustomers")
    for row in cur:
        #if not row["CustomerName"] or row["CustomerName"].strip()=="":
        #    continue
        result={"companyName":row["CustomerName"] and row["CustomerName"].strip().replace("\"",'') or "","address":row["Address"] and row["Address"].strip().replace("\"",""),"language":row["Language"]}
        if row["Language"]==1:
            zh_rows.append(result)
        else:
            en_rows.append(result)        
    conn.close()
    return zh_rows,en_rows

def comparerow(data,dpel,iszh):
    result=[]
    for item in data:
        row={"companyName":item["companyName"],"customercode":item["customercode"],"companyNameEn":item["companyNameEn"],"address":item["address"],"match_zh_name":"False","match_en_name":"False","match_address":"","names":"","addresses":""}
        match_names=[]
        match_addresses=[]
        for ditem in dpel:
            if iszh:
                if (ditem["companyName"] and item["companyName"] and item["companyName"].strip()<>'') and ( item["companyName"].find(ditem["companyName"])>=0 or ditem["companyName"].find(item["companyName"])>=0):
                    row["match_zh_name"]="True"
                    match_names.append(ditem["companyName"])
            else:
                if (ditem["companyName"] and item["companyNameEn"] and item["companyNameEn"].strip()<>'') and( item["companyNameEn"].find(ditem["companyName"])>=0 or ditem["companyName"].find(item["companyNameEn"])>=0):
                    row["match_en_name"]="True"
                    match_names.append(ditem["companyName"])
            if (ditem["address"] and ditem["address"].strip()<>'' and item["address"] and item["address"].strip()<>'') and ( item["address"].find(ditem["address"])>=0 or ditem["address"].find(item["address"])>=0):
                row["match_address"] = "True"
                match_addresses.append(ditem["address"])
                #print "company address is %s,dpel address is '%s'"%(item["address"],ditem["address"])                            
        row["names"]="|".join(match_names)
        row["addresses"]="|".join(match_addresses)
        result.append(row)
    return result

def compare():
    result =[]
    zh_data,en_data=readcustomerfromdatabase()
    zh_dpel,en_dpel=readdpelfromdatabase()
    result=comparerow(zh_data,zh_dpel,True)
    result.extend(comparerow(en_data,en_dpel,False))
    return result

def writedate(result):
    result = compare()
    
import csv
def write_dict_to_csv(items,filepath):
    if not items:
        return 0
    header = items[0].keys()
    rows = []    
    header.sort()
       
    for item in items:
        row = [item[key] for key in header]
        rows.append(row)           
    try:
        with open(filepath,'wb') as csvfile:
            spmwriter = UnicodeWriter(csvfile,delimiter=',')
            spmwriter.writerow(header)
            for row in rows:
                spmwriter.writerow(row)        
    except IOError:
        print "result.csv Io Error"
        return 0
    return 1

if __name__=="__main__":
    #en,zh=readcustomerfromdatabase()
    #print en,zh
    #print readdpelfromdatabase()
    result =compare()
    write_dict_to_csv(result,"test.csv")
    #for row in result:
    #    if row["match_en_name"] or row["match_zh_name"]:
    #            print row["companyName"],row["match_en_name"],row["match_zh_name"],row["names"],row["addresses"]                                                                            
