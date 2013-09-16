#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
#
# Copyright 2013 SOABER, Inc.
#
import pymssql

def readcustomerfromdatabase():
    rows=[]
    conn=pymssql.connect(host="192.1.8.202",user="sa",password="p@ssw0rd",database="BPMForNC2",as_dict=True,charset="cp936")
    cur=conn.cursor()
    cur.execute("SELECT * FROM MDM_Customer_Sap")
    for row in cur:
        result={
            "companyName":row["CompanyName"] and " ".join(row["CompanyName"].split()) or "",
            "companyNameEn":row["CompanyNameEn"],
            "address":row["RegisterAddress"]
        }        
        rows.append(result)
    conn.close()
    return rows

def readdpelfromdatabase():
    rows=[]
    conn=pymssql.connect(host="192.1.8.202",user="sa",password="p@ssw0rd",database="MDM_Customer",as_dict=True,charset="cp936")
    cur=conn.cursor()
    cur.execute("SELECT * FROM DPELCustomers")
    for row in cur:
        result={"companyName":row["CustomerName"] and row["CustomerName"].strip().replace("\"",'') or "","address":row["Address"] and row["Address"].strip().replace("\"",""),"language":row["Language"]}        
        rows.append(result)
    conn.close()
    return rows

if __name__=="__main__":
    print readcustomerfromdatabase()
    print readdpelfromdatabase()
