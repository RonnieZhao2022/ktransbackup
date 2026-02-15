#!/usr/bin/env python
import sqlite3
import tools

import os
import time

from docx import Document

def connectDB(sql):
    conn = sqlite3.connect("/home/KTRANS/mysite/KTRANS.db")
    cur = conn.cursor()
    cur.execute(sql)
    cur = conn.cursor()
    cur.execute(sql)
    myresultTuple = cur.fetchone()
    myresult=list(myresultTuple)
    cur.close()
    conn.commit()
    conn.close()
    return myresult


def deliveryorder(ID):

    DO = Document('/home/KTRANS/mysite/static/Delivery_Order_Template.docx')


    sql = "SELECT order_id, ccn ,client , Orders.phone,cargo_type , Warehouse.company , Warehouse.address,   Orders.address ,amount , weight,volume,delivery_type, User.name \
           FROM Orders JOIN Warehouse ON Warehouse.warehouse_id = Orders.warehouse  JOIN User ON User.user_id = Orders.operator WHERE order_id = '%s' " % ID

    results = tools.queryMysql(sql)[0]
    result = []
    for item in results:
        if item:
            result.append(item)
        else:
            result.append('')


    filename = DO.tables[0].cell(0,0).paragraphs[0]
    filename.text = 'File No.' + ID
    DO.tables[0].cell(0,0).add_paragraph('CCN#' + result[1])

    consignee = DO.tables[0].cell(0,1).paragraphs[0]
    consignee.text = 'Consignee：' + result[2]
    DO.tables[0].cell(0,1).add_paragraph('Phone number：' + result[3])

    today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
    DO.tables[0].cell(1,0).add_paragraph('Issue Date:%s operator:  %s'%(today,result[12] ))
    DO.tables[0].cell(1,1).add_paragraph('Goods description: %s '%result[4] )


    DO.tables[0].cell(3,0).add_paragraph('From:   %s warehouse at: %s'%(result[5],result[6]))

    DO.tables[0].cell(4,0).add_paragraph('To:   %s '%result[7])

    DO.tables[0].cell(5,0).add_paragraph('Piece:  %s '%result[8])
    DO.tables[0].cell(5,1).add_paragraph('Weight：  %s '%result[9])
    DO.tables[0].cell(5,3).add_paragraph('Dimension:  %s '%result[10])

    DO.tables[1].cell(1,1).add_paragraph('REMARK:  %s '%result[11])


    DO.save('/home/KTRANS/mysite/static/files/deliveryOrder/Delivery_Order_%s.docx'%(ID))

