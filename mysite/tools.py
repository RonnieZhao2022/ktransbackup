import re
import math

import jsonpickle

import requests

import pymysql



def cmToInch(text):


    rate = 0.3937



    while True:
        dataList = re.search(r"(\d+)(cm)",text,re.IGNORECASE)
        if not dataList :
            return text
        cmData = dataList.group(1)
        inData = math.ceil(int(cmData) * rate)
        inString = str(inData) + 'IN'
        cmDataToReplaced = re.search(r"(\d+(cm))",text,re.IGNORECASE)
        tempData = cmDataToReplaced.group(1)
        text = text.replace(tempData, inString, 1)

    return text




def weather(city):
    API_KEY = '1aef85a4b73f8d3bceb1243b3088947c'
    CITY_NAME = city
    url = f'http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    data = response.json()

    temperature = data['main']['temp']
    weather_description = data['weather'][0]['description']

    city_weather = f'{CITY_NAME}天气 : 温度{temperature}°C,   {weather_description}'

    return city_weather



def queryMysql(sql):

    conn, cursor = connectMysql()

    cursor.execute(sql)
    # 使用 fetchone() 方法获取数据
    result = cursor.fetchall()
    cursor.close()

    return result



def connectMysql():
    conn = pymysql.connect(
    host='KTRANS.mysql.pythonanywhere-services.com',
    user='KTRANS',  # 用户名
    passwd='ktrans6477021238',  # 密码
    port=3306,  # 端口，默认为3306
    db='KTRANS$ktrans',  # 数据库名称
    charset='utf8' # 字符编码）
    )
    cursor = conn.cursor()

    return conn, cursor




def insertMysql(sql,info):

    conn, cursor = connectMysql()

    try:
        # 执行SQL语句
        cursor.execute(sql,info)

        # 提交到数据库执行
        conn.commit()
        #cursor.close()
    except pymysql.Error as e:
        # 发生错误时回滚
        conn.rollback()
        cursor.close()
        return jsonpickle.encode(e)

def updateMysql(sql, params=None):
    """
    支持两种模式：
    1. updateMysql(sql)
    2. updateMysql(sql, params)
    """

    conn, cursor = connectMysql()

    try:
        # 如果有参数数组
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except pymysql.Error as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonpickle.encode(e)

def fillComboBox(id,column, tableName, condition = ''):

    sql = f"SELECT `{id}`,`{column}` FROM `{tableName}` {condition}   ORDER BY `{column}` ASC;"
    list = queryMysql(sql)


    return list

def fillComboBoxNoID(column, tableName, condition = ''):

    sql = f"SELECT `{column}` FROM `{tableName}` {condition}   ORDER BY `{column}` ASC;"
    list = queryMysql(sql)


    return list





