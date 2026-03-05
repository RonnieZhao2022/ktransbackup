#!/usr/bin/env python

import sqlite3


def connectDB(sql):
    conn = sqlite3.connect("/home/KTRANS/mysite/KTRANS.db")
    cur = conn.cursor()
    cur.execute(sql)
    myresultTuple = cur.fetchall()
    if myresultTuple is None:
        return None
    myresult = list(myresultTuple)
    cur.close()
    conn.commit()
    conn.close()
    return myresult


def noReturnConnectDB(sql):
    conn = sqlite3.connect("/home/KTRANS/mysite/KTRANS.db")
    cur = conn.cursor()
    cur.execute(sql)

    cur.close()
    conn.commit()
    conn.close()
    return

def fillComboBox(column, tableName):
    conn = sqlite3.connect("/home/KTRANS/mysite/KTRANS.db")
    cur = conn.cursor()
    sql = "SELECT DISTINCT `%s` FROM `%s` ORDER BY `%s` ASC" % (column, tableName,column)
    cur.execute(sql)
    myresult = cur.fetchall()
    cur.close()
    conn.close()
    list = []
    for i in myresult:
        list.append(i[0])

    return list