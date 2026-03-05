# -*- coding: utf-8 -*-

'''mysql 数据库

website username: zhaoyue20131023@gmail.com
password: ronnie6477021238

bitbucket push mima:ATBBSSU54W9byWn7xQmWnrvQtvGYF105BDCA

Database host address:KTRANS.mysql.pythonanywhere-services.com
Username:KTRANS
Password: ktrans6477021238'''




from flask import Flask , render_template, redirect, url_for , request , flash , session, send_from_directory

import EmailSender

import pytz

import deliveryOrder

from flask_login import LoginManager, login_user, current_user, UserMixin, login_required, logout_user

import requests

import re

import json

import html2text


login_manager = LoginManager()

import markdown

from pathlib import Path

import time

from datetime import datetime


from os import path

import datetime

import excelreader

from pymysql.cursors import DictCursor
import pymysql

from collections import defaultdict

import uuid



#from app import app as application

from markupsafe import Markup

from markupsafe import escape


from flask_sqlalchemy import SQLAlchemy

import tools




from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length



import random

import copy
import sqlite3

import connectDB
import sre_constants

import os

import sys

import codecs, markdown

import sshtunnel




app = Flask(__name__, static_folder='/home/KTRANS/mysite/static')


app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#app.config['UPLOAD_FOLDER']= "/home/KTRANS/mysite/files/Ronnie/"


# PROD
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{hostname}/{databasename}".format(
    username="KTRANS",
    password="ktrans6477021238",
    hostname="KTRANS.mysql.pythonanywhere-services.com",
    databasename="KTRANS$ktrans",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
}








# LOCAL
''' sshtunnel.SSH_TIMEOUT = 15.0
sshtunnel.TUNNEL_TIMEOUT = 15.0
tunnel = sshtunnel.SSHTunnelForwarder(
    ('ssh.pythonanywhere.com'), ssh_username='KTRANS', ssh_password='ronnie6477021238',
    remote_bind_address=('KTRANS.mysql.pythonanywhere-services.com', 3306)
)
tunnel.start()
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql://KTRANS:ktrans6477021238@127.0.0.1:{}/KTRANS$ktrans'.format(
    tunnel.local_bind_port) '''

db=SQLAlchemy(app=app)
db.session.close()
db.get_engine(app).dispose()
with app.app_context():
    db.create_all()



login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Welcome back, '
login_manager.init_app(app)

def addSpace(string,length):
            while len(string) <length:
                string += " "
            return string



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column('user_id', db.Integer, primary_key=True)
    job_id = db.Column('job_id', db.String(20))
    password = db.Column('password', db.String(20))
    email = db.Column('email', db.String(50), unique=True)
    role = db.Column('role', db.String(20), unique=True)
    company = db.Column('company', db.String(20), unique=True)
    name = db.Column('name', db.String(20))


@app.route('/homepage/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form.get('userid')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user is not None and request.form['password'] == password:
            # 通过Flask-Login的login_user方法登录用户
            flash('欢迎进入KTrans货单操作系统！')
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Wrong username or password!')

    return render_template('login.html')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully!'




#上传文件
@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():

     return render_template('upload.html')





#文件上传成功
@app.route('/success/<path:filePath>/', methods=['POST'])

def success_file(filePath):

    if request.method == 'POST':

        f = request.files['file']

        route = "/home/KTRANS/mysite/static/files/" + filePath + "/"

        f.save( route + f.filename)

        return render_template('success.html', name = f.filename)



#生成数据库模型
@app.route('/createdb/')
@login_required

def creat_db():
    db.create_all()

    return 'DB Created!'


#搜索操作界面
@app.route('/search/', methods=['POST'])
@login_required
def search():

    if request.method == 'POST':

        search = request.form.get('search')

        sql = f"select order_id, remark, container_number,  Orders.company ,Orders.email, phone,address, ccn,old_ccn,User.name from Orders JOIN User ON Orders.operator = User.user_id where order_id LIKE '%{search}%' OR remark LIKE '%{search}%' OR container_number LIKE'%{search}%' OR Orders.company LIKE'%{search}%' OR Orders.email LIKE '%{search}%' OR phone LIKE '%{search}%' OR address LIKE '%{search}%' OR CCN LIKE '%{search}%' OR OLD_CCN LIKE '%{search}%' ORDER BY order_id ASC ;"

        myresult = tools.queryMysql(sql)


        return render_template('search.html', myresult = myresult )


    return render_template('index.html' )





#首页操作界面
@app.route('/index/', methods=['GET'])
@login_required
def index():

    toronto = tools.weather('Toronto')
    vancouver = tools.weather('Vancouver')
    losangeles= tools.weather('Los Angeles')


    return render_template('index.html', toronto =toronto ,vancouver =vancouver , losangeles= losangeles )



#常见各种回复
@app.route('/reply/')
@login_required
def reply():
    sql = "select `content`,`field`,`receiver` from UserReply"

    myresult = tools.queryMysql(sql)

    list = ['国内', '上家', '收货人', '清关代理', '卡车司机', '海关仓库', 'AP', 'AR', 'KATHIE']
    fieldList = ["货物状态", "清关相关", "放货", "各项费用", "派送相关"]

    return render_template('reply.html', reply = myresult, list = list , fieldList = fieldList )


#CNCP铁路货柜状态查询模板
@app.route('/railstatus/<terminal>/')
@login_required

def railstatus(terminal):

    if current_user.job_id in ['kathie','ronnie','david','tina','anna']:
        condition = ''
    else:
        operatorid = current_user.id
        condition = f"and operator = {operatorid}"

    sql = f"select `order_id`,`hold`,`container_number`,`train_company`,CASE  WHEN LEFT(eta, 1) = '2' THEN SUBSTRING(eta, 6) ELSE eta   END AS eta_safe,`status`, Warehouse.company , Warehouse.website , `dest_city`,Orders.address from Orders JOIN Warehouse ON Orders.warehouse = Warehouse.warehouse_id where (status ='IN PORT' or status =  'ON RAIL' or status =  'AT SEA') and (train_company = '{terminal}' or train_company = '未知')  {condition} ORDER BY container_number ASC"

    myresult = tools.queryMysql(sql)

    containerList = []
    text = ''

    for i in myresult:
        if terminal == 'CN' :
            CNTR = i[2][:10]
            containerList.append(CNTR)
            text += CNTR + '\n'
        else:
            containerList.append(i[2])
            text += i[2] + '\n'



    return render_template('/status/railstatus.html', myresult = myresult , terminal = terminal, containerList = containerList, text = text)



#新单录入
@app.route('/newOrder/', methods = ["GET","POST"])
@login_required

def newOrder():

    if current_user.job_id not in ["tor1","tor2","tor3","ronnie","Kathie","tina","kevin","op3","op5"]:
        return "对不起，您没有新单录入的权限!"



    if request.method == "POST":


        order_id = request.form.get('order_id')
        regular_client = request.form.get('regular_client')
        operator = request.form.get('operator')
        import_or_export = request.form.get('import_or_export')

        remark = request.form.get('remark')
        remark = remark.replace("'","")
        create_date = datetime.date.today()

        hold = request.form.get('hold')
        shipping_type = request.form.get('shipping_type')
        service_type = request.form.get('service_type')
        bln = request.form.get('bln') #标注Bill of landing number

        container_number = request.form.get('container_number')
        ssl_info = request.form.get('ssl_info') #标注船公司名称
        vessel_name = request.form.get('vessel_name')
        cargo_type = request.form.get('cargo_type').strip()

        amount = request.form.get('amount').strip()
        weight = request.form.get('weight').strip()
        volume = request.form.get('volume').strip()
        size = request.form.get('size').strip().strip()

        origin_city = request.form.get('origin_city')
        origin_city = origin_city.strip()
        origin_city = origin_city.upper()

        dest_country = request.form.get('dest_country')
        dest_city = request.form.get('dest_city').strip()
        dest_city = dest_city.upper()

        broker = request.form.get('broker')
        broker = int(broker)
        oversea = request.form.get('oversea')
        oversea = int(oversea)



        coloader = request.form.get('coloader')
        coloader = int(coloader)
        client = request.form.get('client').strip()
        company = request.form.get('company').strip()
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address').strip()
        delivery_type = request.form.get('delivery_type')
        ccn = request.form.get('ccn')
        old_ccn = request.form.get('old_ccn')

        warehouse = request.form.get('warehouse')
        warehouse = int(warehouse)
        onboard_date = request.form.get('onboard_date')
        if not onboard_date :
            onboard_date = ''
        payment_methods = request.form.get('payment_methods')



        info = (order_id, operator , regular_client, import_or_export , remark , create_date, hold, shipping_type, service_type , bln , container_number,ssl_info, vessel_name ,cargo_type , amount , weight, volume ,size , dest_country, origin_city, dest_city, broker, oversea , coloader , client ,company, email, phone, address,delivery_type , ccn, old_ccn,  warehouse , onboard_date, payment_methods)
        sql = "INSERT INTO Orders (order_id, operator , regular_client, import_or_export , remark , create_date, hold, shipping_type, service_type , bln , container_number,ssl_info, vessel_name ,cargo_type , amount , weight, volume ,size , dest_country,origin_city, dest_city, broker, oversea , coloader , client ,company, email, phone, address,delivery_type , ccn, old_ccn,  warehouse , onboard_date, payment_methods) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        erro = tools.insertMysql(sql,info)
        if not erro:
            flash('New Order and folder are created!', category='success')
            return redirect(url_for('change', ID = order_id ))  # 重定向回登录页面


        filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator, order_id)

        folder = os.path.exists(filePath)

        if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹

            os.makedirs(filePath)  # makedirs 创建文件时如果路径不存在会创建这个路径


        flash('New Order and folder are created!', category='success')

        #return redirect(url_for('change', ID = order_id ))  # 重定向回登录页面

        return erro

    sslList = tools.fillComboBoxNoID('company', 'SSLInfo')

    # 获取操作员列表
    operatorList = tools.fillComboBox('user_id','job_id', 'User', ' WHERE role = "operator" ')

    # 获取清关方式
    brokerList = tools.fillComboBox('broker_id','company', 'Broker')

    # 获取发货方
    overseaList = tools.fillComboBox('oversea_id','company', 'Oversea')

    # 获取上家联系人
    coloaderList = tools.fillComboBox('coloader_id','company', 'Coloader')


    # 获取海关仓库
    warehouseList = tools.fillComboBox('warehouse_id','company', 'Warehouse')

    sql = "SELECT DISTINCT `dest_city` FROM Orders ORDER BY dest_city ;"
    dest_cityList =  tools.queryMysql(sql)

    sql = "SELECT DISTINCT `origin_city` FROM Orders ORDER BY origin_city;"
    origin_cityList =  tools.queryMysql(sql)






    return render_template('newOrder.html',  operatorList =  operatorList , brokerList = brokerList, overseaList = overseaList,  coloaderList = coloaderList ,  warehouseList = warehouseList, sslList = sslList, dest_cityList = dest_cityList, origin_cityList = origin_cityList)




#货物信息修改，全部


@app.route('/change/<ID>/', methods = ["GET","POST"])
@login_required

def change(ID):
    #获取单号下所有信息
    sql = f"select * from Orders where order_id = '{ID}'"

    myresult = tools.queryMysql(sql)
    if not myresult:
         return "系统中没有此票记录，请重新核实！"



    '''filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)'''


    if request.method == "POST":


        order_id = request.form.get('order_id')

        operator = int(request.form.get('operator'))
        regular_client = request.form.get('regular_client')
        import_or_export = request.form.get('import_or_export')

        remark = request.form.get('remark') or ""
        create_date = request.form.get('create_date')
        hold = request.form.get('hold')

        shipping_type = request.form.get('shipping_type')
        service_type = request.form.get('service_type')
        status = request.form.get('status')
        bln = request.form.get('bln')
        container_number = request.form.get('container_number')

        ssl_info = request.form.get('ssl_info')
        vessel_name = request.form.get('vessel_name')
        cargo_type = request.form.get('cargo_type')

        amount = (request.form.get('amount') or "").strip()
        weight = (request.form.get('weight') or "").strip()
        volume = (request.form.get('volume') or "").strip()
        size = (request.form.get('size') or "").strip()

        train_company = request.form.get('train_company')

        origin_city = (request.form.get('origin_city') or "").strip().upper()
        dest_country = request.form.get('dest_country')
        dest_city = (request.form.get('dest_city') or "").strip().upper()

        eta = request.form.get('eta')

        broker = int(request.form.get('broker'))
        oversea = int(request.form.get('oversea'))
        coloader = int(request.form.get('coloader'))

        client = request.form.get('client')
        company = request.form.get('company')
        email = request.form.get('email')
        phone = request.form.get('phone')

        address = (request.form.get('address') or "").strip()
        delivery_type = request.form.get('delivery_type')

        ccn = request.form.get('ccn')
        old_ccn = request.form.get('old_ccn')

        warehouse = int(request.form.get('warehouse'))
        lfdwarehouse = request.form.get('lfdwarehouse')

        onboard_date = request.form.get('onboard_date')
        payment_methods = request.form.get('payment_methods')

        trucker = request.form.get('trucker')
        readyForDeliver = request.form.get('readyForDeliver')
        close_date = request.form.get('close_date')

        eta_to_client = request.form.get('eta_to_client')

        profit_in_CAD = float(request.form.get('profit_in_CAD') or 0)
        profit_in_USD = float(request.form.get('profit_in_USD') or 0)

        processList = request.form.getlist('process')
        if processList:
            remark = ''.join(processList) + remark


        # ===============================
        # 参数化 SQL
        # ===============================

        sql = """
        UPDATE Orders SET
        operator = %s,
        regular_client = %s,
        import_or_export = %s,
        remark = %s,
        create_date = %s,
        hold = %s,
        shipping_type = %s,
        service_type = %s,
        status = %s,
        bln = %s,
        container_number = %s,
        ssl_info = %s,
        vessel_name = %s,
        cargo_type = %s,
        amount = %s,
        weight = %s,
        volume = %s,
        size = %s,
        train_company = %s,
        origin_city = %s,
        dest_country = %s,
        dest_city = %s,
        eta = %s,
        broker = %s,
        oversea = %s,
        coloader = %s,
        client = %s,
        company = %s,
        email = %s,
        phone = %s,
        address = %s,
        delivery_type = %s,
        ccn = %s,
        old_ccn = %s,
        warehouse = %s,
        lfdwarehouse = %s,
        onboard_date = %s,
        payment_methods = %s,
        trucker = %s,
        readyForDeliver = %s,
        close_date = %s,
        profit_in_CAD = %s,
        profit_in_USD = %s,
        eta_to_client = %s
        WHERE order_id = %s
        """

        params = (
            operator,
            regular_client,
            import_or_export,
            remark,
            create_date,
            hold,
            shipping_type,
            service_type,
            status,
            bln,
            container_number,
            ssl_info,
            vessel_name,
            cargo_type,
            amount,
            weight,
            volume,
            size,
            train_company,
            origin_city,
            dest_country,
            dest_city,
            eta,
            broker,
            oversea,
            coloader,
            client,
            company,
            email,
            phone,
            address,
            delivery_type,
            ccn,
            old_ccn,
            warehouse,
            lfdwarehouse,
            onboard_date,
            payment_methods,
            trucker,
            readyForDeliver,
            close_date,
            profit_in_CAD,
            profit_in_USD,
            eta_to_client,
            order_id
        )

        erro = tools.updateMysql(sql, params)

        if erro is None:
            flash('Modification completed!', category='success')
            return redirect(url_for('change', ID=order_id))
        else:
            app.logger.error(f"DB Error: {erro}")
            flash('Database error occurred. Please contact admin.', category='danger')
            return redirect(url_for('change', ID=order_id))







     # 获取操作员列表
    operatorList = tools.fillComboBox('user_id','job_id', 'User', ' WHERE role = "operator" ')


    # 获取清关方式
    brokerList = tools.fillComboBox('broker_id','company', 'Broker')

    # 获取发货方
    overseaList = tools.fillComboBox('oversea_id','company', 'Oversea')

    # 获取上家联系人
    coloaderList = tools.fillComboBox('coloader_id','company', 'Coloader')


    # 获取海关仓库
    warehouseList = tools.fillComboBox('warehouse_id','company', 'Warehouse')

    sslList = tools.fillComboBoxNoID('company', 'SSLInfo')




    operatorid = int(myresult[0][1])
    brokerid = int(myresult[0][23])
    overseaid = int(myresult[0][24])
    coloaderid = int(myresult[0][25])
    warehouseid = int(myresult[0][34])


    sql = f"SELECT `job_id` FROM User WHERE user_id = {operatorid};"
    operator = tools.queryMysql(sql)[0][0]

    sql = f"SELECT `company` FROM Broker WHERE broker_id = {brokerid};"
    broker = tools.queryMysql(sql)[0][0]

    sql = f"SELECT `company` FROM Oversea WHERE oversea_id = {overseaid};"
    oversea = tools.queryMysql(sql)[0][0]


    sql = f"SELECT `company` FROM Coloader WHERE coloader_id = {coloaderid};"
    coloader = tools.queryMysql(sql)[0][0]


    sql = f"SELECT `company` FROM Warehouse WHERE warehouse_id = {warehouseid};"
    warehouse = tools.queryMysql(sql)[0][0]

    sql = "SELECT DISTINCT `dest_city` FROM Orders ORDER BY dest_city ;"
    dest_cityList =  tools.queryMysql(sql)

    sql = "SELECT DISTINCT `origin_city` FROM Orders ORDER BY origin_city;"
    origin_cityList =  tools.queryMysql(sql)




    return render_template('change.html' , operatorid = operatorid , brokerid = brokerid, overseaid = overseaid, coloaderid = coloaderid , warehouseid = warehouseid, operator = operator , broker = broker, oversea = oversea, coloader = coloader , warehouse = warehouse, myresult = myresult ,  operatorList =  operatorList , brokerList = brokerList, overseaList = overseaList,  coloaderList = coloaderList ,  warehouseList = warehouseList, sslList = sslList, dest_cityList = dest_cityList, origin_cityList = origin_cityList)



#询价仓库

@app.route('/xjck/<ID>/')

@login_required

def xjck(ID):

    sql = f"SELECT `ccn`,`amount`,`weight`,`volume`,`address`,`delivery_type`,`size` ,`warehouse` , `dest_city`,`operator` FROM Orders WHERE order_id = '{ID}' "


    myresult = tools.queryMysql(sql)

    CCN = myresult[0][0]
    amount = myresult[0][1]
    weight = myresult[0][2]
    volume = myresult[0][3]
    address = myresult[0][4]
    deliveryType = myresult[0][5]
    size = myresult[0][6]
    size = size if size else ''
    warehouseid = myresult[0][7]
    city = myresult[0][8]

    operator = myresult[0][9]

    '''filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)
    else:
        os.mkdir(filePath)
        fileList = []  '''

    sql = f"SELECT `company`,`inquiry_Email` FROM Warehouse WHERE warehouse_id = {warehouseid}  "


    email = tools.queryMysql(sql)[0][1]
    warehouse = tools.queryMysql(sql)[0][0]




    subtitle = "Please kindly quote us delivery fee for CCN# " + CCN + "  with FILE#  " + ID


    content = """Good Day,

Please kindly quote us delivery fee for  CCN# %s

Ship From: your warehouse

Ship To: **%s**

**%s**,**%s**,**%s**

**%s**

**%s**

I am looking forward for your reply. Thank you!

Best regards



""" % (CCN, address, amount, weight, volume, size, deliveryType)
    receiverList = [email]
    attachment = []
    ActionItems = '向仓库询价'

    return render_template('mail.html', subtitle =  subtitle ,  content = content, receiverList = receiverList, attachment = attachment , ActionItems = ActionItems, ID = ID, operator = operator)



#三方询价

@app.route('/sfxj/<ID>/')

@login_required

def sfxj(ID):

    sql = "SELECT ccn , amount , weight, volume , Orders.address , delivery_type, size , Warehouse.company , dest_city , shipping_type, User.job_id , Warehouse.address FROM Orders JOIN Warehouse ON Warehouse.warehouse_id = Orders.warehouse  JOIN User ON User.user_id = Orders.operator WHERE order_id = '%s' " % ID
    myresult = tools.queryMysql(sql)



    CCN = myresult[0][0]
    amount = myresult[0][1]
    weight = myresult[0][2]
    volume = myresult[0][3]
    address = myresult[0][4]
    deliveryType = myresult[0][5]
    size = myresult[0][6]
    size = size if size else ''
    warehouse = myresult[0][7]
    city = myresult[0][8]
    shippingType = myresult[0][9]

    operator = myresult[0][10]

    warehouseAddress = myresult[0][11]

    filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)
    else:
        os.mkdir(filePath)
        fileList = []

    sql = "select  email from Trucker where field = '%s' and city = '%s'" % (shippingType, city)

    emailList = tools.queryMysql(sql)




    subtitle = "Please kindly quote us delivery fee for CCN# " + CCN + "  with FILE#  " + ID


    content = """Good Day,

Please kindly quote us delivery fee for  CCN# %s

Ship From:

**%s warehouse:  %s**

Ship To:

**%s**

**%s,%s,%s**

**%s**

**%s**

**Call consignee ahead to book appointment.**

I am looking forward for your reply. Thank you!

Best regards



""" % (CCN, warehouse, warehouseAddress, address, amount, weight, volume, size, deliveryType)
    receiverList = []
    if emailList:
        for email in emailList:

            receiverList.append(email[0])



    attachment = []
    ActionItems = '三方询价'

    return render_template('mail.html', subtitle =  subtitle ,  content = content, receiverList = receiverList, attachment = attachment , ActionItems = ActionItems,  ID = ID, fileList = fileList, operator = operator)




#仓库放货

@app.route('/ckfh/<ID>/')

@login_required

def ckfh(ID):


    sql = "SELECT ccn, amount , Warehouse.company , dest_city , User.job_id , Warehouse.email FROM Orders JOIN Warehouse ON Warehouse.warehouse_id = Orders.warehouse  JOIN User ON User.user_id = Orders.operator WHERE order_id = '%s' " % ID

    myresult = tools.queryMysql(sql)


    CCN = myresult[0][0]
    amount = myresult[0][1]
    warehouse = myresult[0][2]
    city = myresult[0][3]

    operator = myresult[0][4]
    email = myresult[0][5]


    filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)
    else:
        os.mkdir(filePath)
        fileList = []


    subtitle = 'Please release this shipment with CCN# %s and FILE# %s' % (CCN, ID)



    content = '''Good Day,

Please Kindly release this shipment to **Ktrans**. Dock fee is paid. Our driver will drop off %s skids for exchange.Thank you.

Best regards


''' % amount



    receiverList = [email]
    attachment = []
    ActionItems = '通知仓库放货'

    return render_template('mail.html', subtitle =  subtitle ,  content = content, receiverList = receiverList, attachment = attachment , ActionItems = ActionItems, ID = ID, fileList = fileList, operator = operator)



#更新仓库
@app.route('/gxck/<ID>/')

@login_required

def gxck(ID):


    sql = "SELECT  ccn , old_ccn , Warehouse.company , dest_city , User.job_id , Warehouse.email FROM Orders JOIN Warehouse ON Warehouse.warehouse_id = Orders.warehouse  JOIN User ON User.user_id = Orders.operator WHERE order_id = '%s' " % ID

    myresult = tools.queryMysql(sql)


    CCN = myresult[0][0]
    OLD_CCN = myresult[0][1]

    warehouse = myresult[0][2]
    city = myresult[0][3]

    operator = myresult[0][4]

    email = myresult[0][5]

    filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)
    else:
        os.mkdir(filePath)
        fileList = []


    subtitle = 'Please help to update CCN# %s  instead of the old one %s with FILE# %s' % (CCN,OLD_CCN, ID)


    content = '''Good Day

Attached please find **EMNFT** and **CLOSEMESSAGE** attached for CCN# **%s** , please kindly update your system.Thank you.

Best regards


''' %  CCN



    receiverList = [email]
    attachment = []
    ActionItems = '更新仓库'

    return render_template('mail.html', subtitle =  subtitle ,  content = content, receiverList = receiverList, attachment = attachment , ActionItems = ActionItems, ID = ID, fileList = fileList, operator = operator)



#敦促清关
@app.route('/dcqg/<ID>/')

@login_required

def dcqg(ID):


    sql = "SELECT eta, dest_city , User.job_id FROM Orders JOIN User ON User.user_id = Orders.operator WHERE order_id = '%s' " % ID
    myresult = tools.queryMysql(sql)


    ETA = myresult[0][0]
    city = myresult[0][1]

    operator = myresult[0][2]

    filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)
    else:
        os.mkdir(filePath)
        fileList = []








    subtitle = '请在此前邮件上回复'



    content = '''Good Day

 This shipment is on rail **ETA  %s   %s**.  Please advise your broker to submit and clear customs accordingly. Thanks! ''' % ( city, ETA)



    receiverList = []
    attachment = []
    ActionItems = '敦促清关'

    return render_template('mail.html', subtitle =  subtitle ,  content = content, receiverList = receiverList, attachment = attachment , ActionItems = ActionItems, ID = ID, fileList = fileList, operator = operator)


#整柜派送

@app.route('/zgps/<ID>/')

@login_required

def zgps(ID):

    sql = "SELECT container_number ,cargo_type ,amount ,weight ,volume ,Orders.address , train_company , Orders.company , phone ,User.job_id, shipping_type,delivery_type , shipping_type, eta_to_client , dest_city, dest_country FROM Orders JOIN User ON User.user_id = Orders.operator  WHERE order_id = '%s'" %ID

    myresult = tools.queryMysql(sql)
    shipping_type = myresult[0][12]
    if shipping_type == "LCL":
        return "请确认这票是整柜之后再进行相关操作，多谢！"


    CNTR = myresult[0][0]
    cargoType = myresult[0][1]
    amount = myresult[0][2]
    weight = myresult[0][3]
    volume = myresult[0][4]
    address = myresult[0][5]
    trainCompany = myresult[0][6]
    company = myresult[0][7]
    phone = myresult[0][8]



    operator = myresult[0][9]
    shipping_type = myresult[0][10]
    delivery_type = myresult[0][11]

    eta_to_client = myresult[0][13]

    dest_city = myresult[0][14]

    dest_country= myresult[0][15]

    filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)
    else:
        os.mkdir(filePath)
        fileList = []





    subtitle = "Please kindly arrange delivery CNTR#  %s 1* %s to below address on %s Ronnie file %s " % (CNTR , shipping_type,eta_to_client,  ID)


    content = """Good Day,

Please kindly delivery CNTR# %s to below address on %s


Ship form:  **%s Yard**

ship to : **%s**
          %s

选择地址类型：Commercial Residential address %s

    %s   Phone:  %s

    %s %s %s %s 1* %s

Pick up number is Empty return instruction is as the file attached.

Best regards



""" % (CNTR,eta_to_client, trainCompany,company, address,delivery_type, company, phone, cargoType, amount, weight, volume, shipping_type)

    sql = f"select email from Trucker where (city LIKE '%{dest_city}%' OR city = 'ALL ') and (country = '{dest_country}') and (field in ('FCL','ALL ')) ;" #找到符合条件Trucker邮箱
    result = tools.queryMysql(sql)
    receiverList = []
    for item in result:
        receiverList.append(item[0])


    attachment = []
    ActionItems = '整柜派送'

    return render_template('mail.html', subtitle =  subtitle ,  content = content, receiverList = receiverList, attachment = attachment , ActionItems = ActionItems, ID = ID, fileList = fileList, operator = operator)



#国内放货
@app.route('/gnfh/<ID>/')

@login_required

def gnfh(ID):


    sql = "SELECT eta, origin_city , dest_city , Oversea.company , User.job_id, Oversea.contact FROM Orders JOIN User ON User.user_id = Orders.operator JOIN Oversea ON Oversea.oversea_id = Orders.oversea WHERE order_id = '%s' " % ID
    myresult = tools.queryMysql(sql)


    ETA = myresult[0][0]
    departure = myresult[0][1]
    destination = myresult[0][2]
    oversea = myresult[0][3]

    operator = myresult[0][4]

    overseaName = myresult[0][5]
    if overseaName is None:
        overseaName = ''

    filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)
    else:
        os.mkdir(filePath)
        fileList = []



    subtitle = '请在此前邮件上回复'



    content = '''Dear %s

贵司从%s发至%s的货物已上火车。目前**ETA %s 为%s**。麻烦请确认一下此票是否可以放货。多谢！

Best regards ''' % (overseaName , departure, destination, destination, ETA)



    receiverList = []
    attachment = []
    ActionItems = '国内放货'

    return render_template('mail.html', subtitle =  subtitle ,  content = content, receiverList = receiverList, attachment = attachment , ActionItems = ActionItems, ID = ID, fileList = fileList, operator = operator)






#局部修改
@app.route('/pchange/<ID>/', methods = ["GET","POST"])

@login_required

def pchange(ID):

    sql = f"SELECT hold , status , train_company , eta , amount , size  , Orders.remark ,  address  , delivery_type , lfdwarehouse  , payment_methods  ,  Orders.email , broker ,Broker.company, User.job_id , container_number FROM Orders JOIN Broker ON Orders.broker = Broker.broker_id JOIN User ON Orders.operator = User.user_id WHERE order_id = '{ID}' "

    myresult = tools.queryMysql(sql)

    broker_id = myresult[0][12]
    broker = myresult[0][13]
    operator = myresult[0][14]

    # 获取清关方式
    brokerList = tools.fillComboBox('broker_id','company', 'Broker')

    if request.method == 'POST':

        hold = request.form.get('hold')
        status = request.form.get('status')
        train_company = request.form.get('train_company')
        eta = request.form.get('eta')


        remark = request.form.get('remark')
        remark = remark.replace("'","")
        amount = request.form.get('amount')
        size = request.form.get('size')


        address = request.form.get('address')
        delivery_type = request.form.get('delivery_type')
        lfdwarehouse = request.form.get('lfdwarehouse')
        payment_methods = request.form.get('payment_methods')
        broker = request.form.get('broker')
        broker = int(broker)
        email = request.form.get('email')
        processList = request.form.getlist('process')
        if processList:
            process = ''.join(processList)
            remark = process + remark



        sql = f"update Orders  SET `hold` = '{hold}' ,`status` = '{status}' ,`remark` = '{remark}' ,`amount` = '{amount}' ,`size`  = '{size}'  ,`train_company` = '{train_company}' ,`eta`  = '{eta}' , `address` = '{address}'  ,`delivery_type` = '{delivery_type}' ,  `lfdwarehouse` = '{lfdwarehouse}'  ,`payment_methods` = '{payment_methods}' , `email`  = '{email}'  , `broker`  = {broker} WHERE order_id = '{ID}' "


        erro = tools.updateMysql(sql)

        if not erro:
            flash('Modification completed!', category='success')
            return redirect(url_for('pchange', ID = ID ))  # 重定向回登录页面
        else:
            return erro


    return render_template('pchange.html', ID = ID , myresult = myresult, brokerList = brokerList, broker = broker, broker_id = broker_id, operator = operator )


#David货物信息查询
@app.route('/david/')

@login_required


def david():
    sql = "select `ID`, `是否扣货`, `状态`,  `派送方式`, `紧急事项`, `抵达终端时间` , `海关仓库`,`CCN`,`LFDwarehouse`,`收货人地址` ,`货物种类`,`货物数量`,`货物重量`,`货物体积`,`长宽高` from 货单基本信息  where ((状态 = 'ON FLOOR') or (状态 = 'ON RAIL') or (状态 = 'PICKEDUP')) and (海关仓库 != '整柜') and (目的地 = 'TORONTO') ORDER BY 状态 DESC , LFDwarehouse ASC , 抵达终端时间 ASC"

    myresult = connectDB.connectDB(sql)

    sql = "SELECT  `海关仓库` ,  `登录网址` FROM 海关仓库信息表 "

    wareshouseInfo = connectDB.connectDB(sql)

    warehouseInfoDict = {}

    for warehouse in wareshouseInfo:
        warehouseInfoDict.update({ warehouse[0]: warehouse[1]})





    return render_template('david.html', myresult = myresult, warehouseInfoDict = warehouseInfoDict)



#出具账单

@app.route('/cjzd/<ID>/')

@login_required

def cjzd(ID):

    sql = "SELECT client ,address ,delivery_type ,User.job_id FROM Orders JOIN User ON User.user_id = Orders.operator  WHERE order_id = '%s'" %ID
    myresult = tools.queryMysql(sql)

    consignee = myresult[0][0]
    address = myresult[0][1]
    deliveryType = myresult[0][2]

    operator = myresult[0][3]

    filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)
    else:
        os.mkdir(filePath)
        fileList = []

    if  deliveryType == 'DOCK':
        deliveryTypeEN = 'WITH LOADING DOCK AVAIABKE'
        deliveryTypeCH = '有loading dock'


    elif  deliveryType == 'TAILGATE':
        deliveryTypeEN = 'CURBSIDE WITH TAILGATE NEEDED'
        deliveryTypeCH = '没有loading dock 需要尾板卸货'

    else:
        deliveryTypeEN = deliveryType
        deliveryTypeCH = deliveryType





    subtitle = "请在此前邮件上回复 "


    content = """ Hi %s

Your shipment is on floor. Invoice is attached. Please make payment ASAP.

Attached please find invoice 账单 , in an amount of CAD$ 金额 and please kindly settle this payment. Pls make a payment by E-transfer to email address:

**accountant@ktranslogistics.com**

**Please write down your shipment's file number %s in 'Memo'when arrange payment.**

**Please reply payment receipt to us， so our accountant can check payment in time.**

Please confirm your deliver address is %s delivery type : %s

Best Regards


%s你好：

您的这票货已经清关完毕，税费账单详见附件。请尽快支付。

账单号INT#      , 总金额 CAD $

付款请使用 E-transfer 到如下电子邮箱地址:

**accountant@ktranslogistics.com**


**支付时，请在备注一栏表明货单文件号：%s**

**支付后，记得截屏，电子邮件寄回我处，以便于公司会计查询确认。**

最后，请确认您的收货地址为%s 派送方式为   %s

Best Regards

""" % (consignee, ID, address, deliveryTypeEN, consignee, ID, address, deliveryTypeCH)


    receiverList = []
    attachment = []
    ActionItems = '等待收货人支付'

    return render_template('mail.html', subtitle =  subtitle ,  content = content, receiverList = receiverList, attachment = attachment , ActionItems = ActionItems, ID = ID, fileList = fileList, operator = operator)




#递送清关

@app.route('/dsqg/<ID>/')

@login_required

def dsqg(ID):

    sql = "SELECT regular_client , shipping_type , container_number , Orders.company , Broker.company, onboard_date, User.job_id ,Broker.email , Broker.contact FROM Orders JOIN User ON User.user_id = Orders.operator JOIN Broker ON Orders.broker = Broker.broker_id  where order_id = '%s'" % ID
    myresult = tools.queryMysql(sql)

    regularClient = myresult[0][0]
    shippingType = myresult[0][1]
    CNTR = myresult[0][2]
    clientCompany = myresult[0][3]
    broker = myresult[0][4]
    onboarddate = myresult[0][5]

    operator = myresult[0][6]
    email = myresult[0][7]
    name = myresult[0][8]

    filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)
    else:
        os.mkdir(filePath)
        fileList = []



    if  regularClient == '是':
        regularClient = 'This is our regular customer.'

    else :
        regularClient = ''




    subtitle = "Customs Document for %s  %s   ON BOARD DATE %s with CNTR# %s File# %s " % (clientCompany, shippingType,onboarddate,CNTR,  ID)


    content = """Good day %s

Now we have a shipment needed your help for customs clearance. Documents related is attached.  **On board date is  %s  %s.**

Please feel free to let us know if you need more information about this shipment.

Thank you so much for your help.

Best regards

""" % (name, onboarddate, regularClient)


    receiverList = [(email)]
    attachment = []
    ActionItems = '递送清关资料'

    return render_template('mail.html', subtitle =  subtitle ,  content = content, receiverList = receiverList, attachment = attachment , ActionItems = ActionItems, ID = ID, fileList = fileList , operator = operator )


#出派送单
@app.route('/dpsd/<ID>/')

@login_required

def dpsd(ID):

    filePath = '/home/KTRANS/mysite/static/files/deliveryOrder/'
    fileName = 'Delivery_Order_%s.docx' %(ID)
    exists = os.path.isfile(filePath)

    if not exists:

        deliveryOrder.deliveryorder(ID)


    return send_from_directory(filePath, fileName, as_attachment=True)


#确认地址
@app.route('/qrdz/<ID>/')

@login_required

def qrdz(ID):

    sql = "select Broker.company , origin_city, dest_city, client , Orders.email, Orders.address , container_number , User.job_id  FROM Orders JOIN User ON User.user_id = Orders.operator JOIN Broker ON Orders.broker = Broker.broker_id  where order_id = '%s'" % ID

    myresult = tools.queryMysql(sql)

    broker = myresult[0][0]
    departure = myresult[0][1]
    destination = myresult[0][2]
    consignee = myresult[0][3]
    clientEmail = myresult[0][4]
    clientAddress = myresult[0][5]
    CNTR = myresult[0][6]

    operator = myresult[0][7]

    filePath = "/home/KTRANS/mysite/static/files/%s/%s/" %(operator,ID)

    fileList = []

    my_file = Path(filePath)

    if my_file.is_dir():
        fileList = os.listdir(filePath)
    else:
        os.mkdir(filePath)
        fileList = []

    subtitle = "Documents for custom clearance with FILE# " + ID + " and CNTR# " + CNTR

    if broker not in ('apace', 'william', 'URT','IMAX', 'Portside'):
        content_for_customs_clearance = ''
        subtitle = "Documents for FILE# " + ID + " and CNTR# " + CNTR + " for delivery address confirmation"
    else:
        content_for_customs_clearance = '''Based on our oversea's instruction, we will help you clear customs and arrange delivery.

For letting us help you with customs clearance, we need your authorization. Please find attached authorization letter POA, please fill part 4 and 5(company legal name, import busines number, company address and phone number), sign it and send it back to us. You may also find a template in the attachment.

Pls note all the information for customs clearance must be provided 48 hours before the shipment arrives. Also, pls make sure all the information you provided matches your company's record on CRA. If you have any questions for the correct name of importer name and import business number, please call CRA 1-800-959-5525 to confirm. Reject from CBSA due to information error will lead to an extra $100 charge.

(1)CARM is mandatory by Oct. 21, 2024 !! All importers must be registered in the CBSA CARM Portal https://ccp-pcc.cbsa-asfc.cloud-nuage.canada.ca/en/auth/login
(2)Pls register CARM, all cargo released after Oct 4th need to pay via CARM portal. CBSA need customers to pay duty&gst by CARM by themselves.'''


    beginning = '''Dear %s

Please note you has a new shipment from %s to %s is on the way to Canada. ETA to %s is to be advised.

''' % (consignee, departure, destination, destination)




    ending = '''

Please confirm if delivery address is the same as following:  **%s**

Is this a **Commercial** address or **residential** ? Is there a  **loading dock available**?

Attached document for your reference.

I'm looking forward for your reply. Thank you!

Best regards ''' % clientAddress

    content = beginning + content_for_customs_clearance + ending

    receiverList = [(clientEmail)]
    attachment = []
    ActionItems = '确认地址'

    return render_template('mail.html', subtitle = subtitle ,  content = content, receiverList = receiverList, attachment = attachment , ActionItems = ActionItems, ID = ID , fileList = fileList, operator = operator)



#添加项目重要通知
@app.route('/addItemCompanyNews/', methods = ["GET","POST"])

@login_required

def addItemCompanyNews():


    if request.method == 'POST':

        sender = request.form.get('sender')
        subtitle = request.form.get('subtitle')
        content = request.form.get('content')
        current_time = datetime.datetime.now()
        date = current_time.strftime('%Y-%m-%d %H:%M:%S')



        sql = "INSERT INTO companyNews (id, sender, subtitle, content, date ) VALUES (NULL, ?, ?, ?, ?)"


        conn = sqlite3.connect("/home/KTRANS/mysite/KTRANS.db")
        cur = conn.cursor()
        cur.execute(sql, (sender, subtitle, content, date))
        conn.commit()

        #cur.close()
        #conn.close()

        flash('New item is added!', category='success')


        return render_template('addItemCompanyNews.html')


    return render_template('addItemCompanyNews.html')


#派送价格查询
@app.route('/inquiry/<area>/', methods = ["GET","POST"])


def inquiry(area):

    if area == "toronto":
        area = "TORONTO"

    if area == "vancouver":
        area = "VANCOUVER"

    if request.method == 'POST':

        number_of_pallets = request.form.get('number_of_pallets')

        cargo_size = request.form.get('cargo_size')
        delivery_address = request.form.get('delivery_address')
        postcode = request.form.get('postcode')
        postcode = postcode.replace(" ","")
        tailgate = request.form.get('tailgate')
        city = request.form.get('city')
        city = city.upper()
        weight = request.form.get('weight')
        residential = request.form.get('residential')


        tailgateFee = 0
        residentialFee = 0

        if tailgate == "需要尾板":
            tailgate = "tailgate"
            tailgateFee = 50

        else :
            tailgate = "DOCK TO DOCK"

        if residential == "居民区":

            residentialFee = 15

        result = tools.LTLPrice(number_of_pallets , postcode)

        if result:

            price,area, zone,cityFound = result

            list = [number_of_pallets,weight, cargo_size,delivery_address, postcode,tailgate,residential, city, zone, area,  price, tailgateFee, residentialFee, cityFound]

            return render_template('inquiryResult.html' , list = list)

        else:
            return "<h3>您提供的城市和邮政编码有误，请重新确认之后再查询！</h3?"


    sql = "select `city` from LTL_Zone where area = '{area}' ORDER BY city ASC".format(area = area)

    cityList = tools.queryMysql(sql)

    return render_template('inquiry.html', area = area ,cityList = cityList)


#首页操作界面
@app.route('/serviceinquiry/', methods=['GET','POST'])

def home():

    return render_template('/home/home.html' )



#首页操作界面
@app.route('/lvsInput/<status>/', methods=['GET','POST'])

def lvsinput(status):

    if request.method == 'POST':


        Client_Number = request.form.get('Client_Number')
        MOT = request.form.get('MOT')
        Port_of_Clearance = request.form.get('Port_of_Clearance')
        Sublocation_Code = request.form.get('Sublocation_Code')
        Port_of_Exit = request.form.get('Port_of_Exit')
        PARS_Number = request.form.get('PARS_Number')
        Number_of_Expected_Invoices = request.form.get('Number_of_Expected_Invoices')
        Total_Package_Quantity = request.form.get('Total_Package_Quantity')
        Package_Quantity_Unit_of_Measure_ = request.form.get('Package_Quantity_Unit_of_Measure_')
        CCI_Number = request.form.get('CCI_Number')
        Purchase_Order_Number = request.form.get('Purchase_Order_Number')
        Shipment_Date = request.form.get('Shipment_Date')
        Invoice_Total_Amount = request.form.get('Invoice_Total_Amount')
        Invoice_Currency_Code = request.form.get('Invoice_Currency_Code')
        Other_References = request.form.get('Other_References')
        CCI_Package_Quantity = request.form.get('CCI_Package_Quantity')
        CCI_Package_Quantity_Unit_of_Measure_ = request.form.get('CCI_Package_Quantity_Unit_of_Measure_')
        Net_Weight = request.form.get('Net_Weight')
        Net_Weight_unit_of_measure = request.form.get('Net_Weight_unit_of_measure')
        Gross_Weight_for_invoice = request.form.get('Gross_Weight_for_invoice')
        Gross_Weight_unit_of_measure = request.form.get('Gross_Weight_unit_of_measure')
        Consignee_Qualifier = request.form.get('Consignee_Qualifier')
        Consignee_Name = request.form.get('Consignee_Name')
        Consignee_Address = request.form.get('Consignee_Address')
        Consignee_City = request.form.get('Consignee_City')
        Consignee_Province_Terr = request.form.get('Consignee_Province_Terr')
        Consignee_Zip_Postal_Code = request.form.get('Consignee_Zip_Postal_Code')
        Consignee_Country = request.form.get('Consignee_Country')
        Consignee_Address_2 = request.form.get('Consignee_Address_2')

        Vendor_Qualifier = request.form.get('Vendor_Qualifier')
        Vendor_Name = request.form.get('Vendor_Name')
        Vendor_Address = request.form.get('Vendor_Address')
        Vendor_City = request.form.get('Vendor_City')
        Vendor_State = request.form.get('Vendor_State')
        Vendor_Zip_Postal_Code = request.form.get('Vendor_Zip_Postal_Code')
        Vendor_Country = request.form.get('Vendor_Country')
        Vendor_Address_2 = request.form.get('Vendor_Address_2')

        '''Exporter_Qualifier = request.form.get('Exporter_Qualifier')
        Exporter_Name = request.form.get('Exporter_Name')
        Exporter_Address = request.form.get('Exporter_Address')
        Exporter_City = request.form.get('Exporter_City')
        Exporter_State = request.form.get('Exporter_State')
        Exporter_Zip_Postal_Code = request.form.get('Exporter_Zip_Postal_Code')
        Exporter_Country = request.form.get('Exporter_Country')
        Exporter_Address_2 = request.form.get('Exporter_Address_2')'''

        Item_Quantity_ = request.form.get('Item_Quantity_')
        Item_Quantity_Unit_of_Measure = request.form.get('Item_Quantity_Unit_of_Measure')
        Unit_Price = request.form.get('Unit_Price')
        Country_of_Origin = request.form.get('Country_of_Origin')
        Part_Number = request.form.get('Part_Number')
        Part_Description_1 = request.form.get('Part_Description_1')
        Part_Description_2 = request.form.get('Part_Description_2')
        Part_Description_3 = request.form.get('Part_Description_3')
        HS_Classification_Number_for_Line_Item = request.form.get('HS_Classification_Number_for_Line_Item')
        Tariff_Qty = request.form.get('Tariff_Qty')
        Tariff_UOM = request.form.get('Tariff_UOM')
        Extended_Price = request.form.get('Extended_Price')


        CC01list = [Client_Number ,
        MOT ,
        Port_of_Clearance ,
        Sublocation_Code ,
        Port_of_Exit,
        PARS_Number,
        Number_of_Expected_Invoices,
        Total_Package_Quantity ,
        Package_Quantity_Unit_of_Measure_ ]


        CC01listStart = [6, 14, 15, 20, 32, 54, 173, 178, 182]

        CC01listlength = [6, 1, 3, 4, 4, 25, 5, 4, 3]

        CC01 = "CC01"

        for i in range(0,9):
            item = addSpace(CC01list[i],CC01listlength[i])
            CC01 = addSpace(CC01,(CC01listStart[i]-1)) +  item

        CC01 += "\n"


        CC02listStart = [5, 27, 49, 57, 69, 115, 240, 244, 251, 259, 262, 270]

        CC02listlength = [22, 22, 8, 12, 3, 26, 4, 3, 8, 3, 8, 3]

        CC02 = "CC02"

        CC02list = [CCI_Number,
        Purchase_Order_Number,
        Shipment_Date ,
        Invoice_Total_Amount ,
        Invoice_Currency_Code ,
        Other_References ,
        CCI_Package_Quantity ,
        CCI_Package_Quantity_Unit_of_Measure_ ,
        Net_Weight ,
        Net_Weight_unit_of_measure ,
        Gross_Weight_for_invoice ,
        Gross_Weight_unit_of_measure ]

        for i in range(0,12):
            item = addSpace(CC02list[i],CC02listlength[i])
            CC02 = addSpace(CC02,(CC02listStart[i]-1)) +  item\

        CC02 += "\n"



        CC03AlistStart = [13, 25, 60, 95, 120, 122, 132, 134]

        CC03Alistlength = [2, 35, 35, 25, 2, 10, 2, 35]

        CC03A = "CC03"

        CC03Alist = [Consignee_Qualifier,
        Consignee_Name,
        Consignee_Address ,
        Consignee_City ,
        Consignee_Province_Terr ,
        Consignee_Zip_Postal_Code ,
        Consignee_Country,
        Consignee_Address_2 ]

        for i in range(0,8):
            item = addSpace(CC03Alist[i],CC03Alistlength[i])
            CC03A = addSpace(CC03A,(CC03AlistStart[i]-1)) +  item

        CC03A += "\n"



        CC03BlistStart = [13, 25, 60, 95, 120, 122, 132, 134]

        CC03Blistlength = [2, 35,  35, 25, 2, 10, 2, 35]

        CC03B = "CC03"

        CC03Blist = [Vendor_Qualifier ,
        Vendor_Name ,
        Vendor_Address ,
        Vendor_City ,
        Vendor_State ,
        Vendor_Zip_Postal_Code ,
        Vendor_Country ,
        Vendor_Address_2  ]

        for i in range(0,8):
            item = addSpace(CC03Blist[i],CC03Blistlength[i])
            CC03B = addSpace(CC03B,(CC03BlistStart[i]-1)) +  item

        CC03B += "\n"



        CC04list = [Item_Quantity_ ,
        Item_Quantity_Unit_of_Measure ,
        Unit_Price ,
        Country_of_Origin ,
        Part_Number ,
        Part_Description_1 ,
        Part_Description_2 ,
        Part_Description_3 ,
        HS_Classification_Number_for_Line_Item ,
        Tariff_Qty ,
        Tariff_UOM ,
        Extended_Price]


        CC04listStart = [5, 14, 17, 63, 66, 91, 121, 151, 171, 183, 197, 200]

        CC04listlength = [9, 3, 14, 3, 25, 30, 30, 20, 10, 14, 3, 14]

        CC04 = "CC04"

        for i in range(0,12):
            item = addSpace(CC04list[i],CC04listlength[i])
            CC04 = addSpace(CC04,(CC04listStart[i]-1)) +  item

        CC04 += "\n"

        l = [CC01, CC02, CC03A, CC03B, CC04 ]

        if status == "first":
            f = open("/home/KTRANS/mysite/static/files/LVS/LVS-EDI.txt", "w")
            f.writelines(l)
            f.close()
        elif status == "add":
            f = open("/home/KTRANS/mysite/static/files/LVS/LVS-EDI.txt", "a")
            f.writelines(l)
            f.close()




        flash('*此前信息已经录入。如没有新HS Code条目录入，请点击下方文件预览和下载。如需新增条目，请填写下方信息并提交*')





        return render_template('HSCodeInput.html')


    return render_template('lvsInput.html' )


#下载LVS-EDI文件
@app.route('/LVS-EDI-DOWNLOAD/')



def download_LVS_EDI():

    filePath = '/home/KTRANS/mysite/static/files/LVS/'
    fileName = 'LVS-EDI.txt'





    return send_from_directory(filePath, fileName, as_attachment=True)


#新增HS Code条目
@app.route('/addHSitems/', methods=['GET','POST'])



def addHSitems():

    if request.method == 'POST':
        Item_Quantity_ = request.form.get('Item_Quantity_')
        Item_Quantity_Unit_of_Measure = request.form.get('Item_Quantity_Unit_of_Measure')
        Unit_Price = request.form.get('Unit_Price')
        Country_of_Origin = request.form.get('Country_of_Origin')
        Part_Number = request.form.get('Part_Number')
        Part_Description_1 = request.form.get('Part_Description_1')
        Part_Description_2 = request.form.get('Part_Description_2')
        Part_Description_3 = request.form.get('Part_Description_3')
        HS_Classification_Number_for_Line_Item = request.form.get('HS_Classification_Number_for_Line_Item')
        Tariff_Qty = request.form.get('Tariff_Qty')
        Tariff_UOM = request.form.get('Tariff_UOM')
        Extended_Price = request.form.get('Extended_Price')

        CC04list = [Item_Quantity_ ,
        Item_Quantity_Unit_of_Measure ,
        Unit_Price ,
        Country_of_Origin ,
        Part_Number ,
        Part_Description_1 ,
        Part_Description_2 ,
        Part_Description_3 ,
        HS_Classification_Number_for_Line_Item ,
        Tariff_Qty ,
        Tariff_UOM ,
        Extended_Price]


        CC04listStart = [5, 14, 17, 63, 66, 91, 121, 151, 171, 183, 197, 200]

        CC04listlength = [9, 3, 14, 3, 25, 30, 30, 20, 10, 14, 3, 14]

        CC04 = "CC04"

        for i in range(0,12):
            item = addSpace(CC04list[i],CC04listlength[i])
            CC04 = addSpace(CC04,(CC04listStart[i]-1)) +  item

        CC04 += "\n"




        f = open("/home/KTRANS/mysite/static/files/LVS/LVS-EDI.txt", "a")
        f.writelines(CC04)
        f.close()

        flash('*此前信息已经录入。如没有新HS Code条目录入，请点击下方文件预览和下载。如需新增条目，请填写下方信息并提交*')



        return render_template('HSCodeInput.html')





    return render_template('HSCodeInput.html')



#制式转换工具
@app.route('/conversionTools/' , methods=['GET'] )
def conversionTools():

     return render_template('conversionTools.html')


#下载文件
'''@app.route('/download/<ID>/')

@login_required

def dpsd(ID):

    filePath = '/home/KTRANS/mysite/static/files/Ronnie/deliveryOrder/'
    fileName = 'Delivery_Order_%s.docx' %(ID)
    exists = os.path.isfile(filePath)

    if not exists:

        deliveryOrder.deliveryorder(ID)


    return send_from_directory(filePath, fileName, as_attachment=True)'''





#清关代理信息
@app.route('/brokerInfo/', methods = ["GET","POST"])

@login_required

def brokerInfo():
    if request.method == 'POST':

        company = request.form.get('company')
        email = request.form.get('email')
        cell = request.form.get('cell')
        city = request.form.get('city')
        contact = request.form.get('contact')
        country = request.form.get('country')
        remark = request.form.get('remark')
        star = request.form.get('star')




        sql = "INSERT INTO 清关公司联系人表 (公司名称, 公司邮件, 电话,城市, 姓名,业务范围,备注,星级 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"


        conn = sqlite3.connect("/home/KTRANS/mysite/KTRANS.db")
        cur = conn.cursor()
        cur.execute(sql, (company,email, cell, city, contact, country,remark,star))
        conn.commit()

        cur.close()
        conn.close()

        flash('New item is added!', category='success')


        return redirect(url_for('brokerInfo'))



    sql = "SELECT  *  FROM 清关公司联系人表"


    myresult = connectDB.connectDB(sql)




    return render_template('brokerInfo.html',  myresult =   myresult )


#发送邮件
@app.route('/sendEmail/', methods=['POST'])

def sendEmail():

    if request.method == 'POST':


        subtitle = request.form.get('subtitle')
        content = request.form.get('content')
        Port_of_Clearance = request.form.get('Port_of_Clearance')
        Sublocation_Code = request.form.get('Sublocation_Code')


    return 'Email is sent!'


#aboutus
@app.route('/aboutus/', methods=['GET'])
def aboutUs():

     return render_template('/home/aboutUs.html')


#solutions
@app.route('/solutions/', methods=['GET'])
def solutions():

     return render_template('/home/solutions.html')

#aboutus中文
@app.route('/aboutus-zh-cn/', methods=['GET'])
def aboutUsChinese():

     return render_template('/home/aboutUs-zh-cn.html')

#solutions中文
@app.route('/', methods=['GET'])
def solutionsChinese():

     return render_template('/home/solutions-zh-cn.html')


#国内散货邮件询价
@app.route('/overseaInquiryLTL/', methods=['GET','POST'])
def overseaInquiryLTL():
    if request.method == 'POST':

        #用当前时间生成id号
        toronto_tz = pytz.timezone('America/Toronto')
        toronto_time = datetime.datetime.now(toronto_tz)
        create_date = datetime.date.today()
        id = str(toronto_time)
        id = id.replace("-","")
        id = id.replace(" ","")
        id = id.replace(":","")
        id = id[0:14]


        company = request.form.get('company')
        email = request.form.get('email')


        originCountry = request.form.get('originCountry')
        originState = request.form.get('originState')

        originCity = request.form.get('originCity')


        destCountry = request.form.get('destCountry')



        destCity = request.form.get('destCity')

        destCity = destCity.strip()

        destCity = destCity.upper()

        item = request.form.get('item')

        dangerousGoods = request.form.get('dangerousGoods')




        stackable = request.form.get('stackable')


        deliveryTypeCH = request.form.get('deliveryType')

        deliveryType = ''

        if deliveryTypeCH == "普通散货":
            deliveryType = "LCL"
        if deliveryTypeCH == "搬运入户":
            deliveryType = "MOVING"
        if deliveryTypeCH == "需平板车":
            deliveryType = "FLATBED"







        number_of_pallets = int(request.form.get('number_of_pallets'))
        number_of_oversized = int(request.form.get('number_of_oversized'))
        number_of_overweight = int(request.form.get('number_of_overweight'))

        delivery_address = request.form.get('delivery_address')
        postcode = request.form.get('postcode')
        postcode = postcode.replace(" ","")
        if "-" in postcode:
                postcode = postcode[0:5]
        weight = request.form.get('weight')



        sql = f"select `city`, `state`,`country` from ZipCode where zipcode = '{postcode}';" #找到邮编对应城市和所属州/省
        resultTuple = tools.queryMysql(sql)


        if resultTuple is None:
            return "<h3>您提供的城市和邮政编码有误，请重新确认之后再查询！</h3?"

        if (destCountry !=  resultTuple[0][2]) or (destCity not in  resultTuple[0][0]):
            return f'''<p>您提供的信息有误，请重新核对之后再录入！</p>
<p>贵司提供的目的地国家和城市分别为{destCountry}，{destCity}</p>
</p>根据邮政编码查询的实际国家和城市分别为{resultTuple[0][2]}，{resultTuple[0][0]}</p> '''


        destState = resultTuple[0][1]


        sizeList = request.form.getlist('size[]')
        sizeInch =''' '''
        sizeCm =''' '''

        for i in sizeList:
            if i :
                inStr = tools.cmToInch(i)
                sizeInch += inStr + ";" +  " \n"
                sizeCm +=  i + ";" + " \n"


        weightUnit = request.form.get('weightUnit')


        volume = request.form.get('volume')
        volume =float(volume)


        tailgate = request.form.get('tailgate')

        residential = request.form.get('residential')


        if dangerousGoods == "是":
            dangerousGoods = "DANGEROUS GOODS"
        else:
            dangerousGoods = "Not dangerous Goods"


        if stackable == "是":
            stackable = "STACKABLE"
        else:
            stackable = "UNSTACKABLE"



        if weightUnit == "KGS":
            lbs = round(int(weight)*2.2046)
        else:
            lbs = weight


        tailgateFee = 0
        residentialFee = 0


        if tailgate == "有DOCK":
            tailgateEN = "DOCK TO DOCK"


        if tailgate == "需要尾板":

            tailgateEN = "CURBSIDE WITH TAILGATE NEEDED"

            tailgateFee =50


        if residential == "商业地址":
            residentialEN = "commercial"

        if residential == "居民区":
            residentialEN = "residential"
            residentialFee = 15



        if (deliveryType == "LCL") and ((originCity == "TORONTO" and number_of_pallets <= 10) or (originCity ==  "VANCOUVER" and number_of_pallets <= 12)):
            sql = f"select `zone` from LTLZone where city = '{destCity}';" #找到邮编对应城市和所属州/省
            resultTuple = tools.queryMysql(sql)

            if resultTuple :
                zone = resultTuple[0][0]

                sql = f"select `{zone}` from LTLPrice where (area = '{originCity}') AND (number_of_pallets = '{number_of_pallets}');" #找到邮编对应城市和所属州/省

                price = tools.queryMysql(sql)[0][0]


                totalPrice = tailgateFee + residentialFee + price

                list = [number_of_pallets,weight, '略',delivery_address, postcode,tailgate,residential, destCity, zone, originCity,  price, tailgateFee, residentialFee]

                info=(id, company, email, originCountry,originState,originCity, destCountry, destState, destCity, item,dangerousGoods, stackable, number_of_pallets,number_of_oversized,number_of_overweight,sizeCm,sizeInch,delivery_address,postcode,lbs,volume,tailgateEN,residentialEN,price,deliveryType,'已发送')
                sql= "INSERT INTO OverseaEmailinquiryLTL (id, company, email, originCountry,originState,originCity, destCountry, destState, destCity, item,dangerousGoods, stackable, number_of_pallets,number_of_oversized,number_of_overweight,cargo_size_cm,cargo_size_in,delivery_address,postcode,lbs,volume,tailgate,residential,price,deliveryType,mail) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); "

                tools.insertMysql(sql,info)

                #发确认邮件

                createTime = datetime.date.today()

                subtitle = f"""{company}贵司的这票{number_of_pallets}板货送至{destCountry}  {destState}  {destCity}的确认邮件，查询号：{id}"""


                content = f"""

                <h3>测试邮件</h3>

                <p>Dear&nbsp; {company}</p>



                <p>贵司刚刚查询的这票货，原始信息如下：</p>
                <p>从{originCountry}&nbsp;{originState}&nbsp;{originCity} 送至{destCountry}&nbsp;{destState}&nbsp;{destCity}&nbsp;{delivery_address}&nbsp;{postcode} 服务类型为：LCL</p>
                <p>品名：{item}&nbsp;{dangerousGoods}&nbsp;&nbsp{stackable}&nbsp&nbsp总重量为{weight}{weightUnit}。总体积为{volume}立方米</p>
                <p>总共{number_of_pallets}个板。其中超尺寸板数为：{number_of_oversized}&nbsp;超重板数为：{number_of_overweight}</p>

                <p>长宽高具体数据如下：</p>

                <p style="white-space: pre-line;">
                 {sizeCm}
                </p>

                <p>最终报价结果如下：</p>
                <p><strong>派送费：{price}; 尾板费：{ tailgateFee}; 住宅派送费：{residentialFee}; 总计：CAD{totalPrice};</strong></p>
                <p>请尽快确认，盼复</p>
                <p>多谢！</p>
                <p>Ktrans&nbsp;{createTime}</p>




                EmailSender.tor2Email(['tor2@ktranslogistics.com','kathie@ktranslogistics.com','anna@ktranslogistics.com','kevin@ktranslogistics.com','import@ktranslogistics.com','tor1@ktranslogistics.com'],subtitle,content)
                sql= f"UPDATE OverseaEmailinquiryLTL SET mail = '已发送' WHERE id = '{id}' ; "
                tools.updateMysql(sql)"""

                return render_template('inquiryResult.html' , list = list)


        createTime = datetime.date.today()

        subtitle = f"""{company}贵司的这票{number_of_pallets}板货送至{destCountry}  {destState} {destCity}的确认邮件，查询号：{id}"""


        content = f"""

        <h3>测试邮件</h3>

        <p>Dear&nbsp; {company}</p>



        <p>贵司刚刚查询的这票货，原始信息如下：</p>
        <p>从{originCountry}&nbsp;{originState}&nbsp;{originCity} 送至{destCountry}&nbsp;{destState}&nbsp;{destCity}&nbsp;{delivery_address}&nbsp;{postcode} 服务类型为：LCL</p>
        <p>品名：{item}&nbsp;{dangerousGoods}&nbsp;&nbsp{stackable}&nbsp&nbsp总重量为{weight}公斤。总体积为{volume}立方米</p>
        <p>总共{number_of_pallets}个板。其中超尺寸板数为：{number_of_oversized}&nbsp;超重板数为：{number_of_overweight}</p>

        <p>长宽高具体数据如下：</p>
        <p style="white-space: pre-line;">
        {sizeCm}
        </p>

        <p>我们会尽快提供报价信息。</p>

        <p>多谢！</p>
        <p>Ktrans&nbsp;{createTime}</p>




        EmailSender.tor2Email(['tor2@ktranslogistics.com','kathie@ktranslogistics.com','anna@ktranslogistics.com','kevin@ktranslogistics.com','import@ktranslogistics.com','tor1@ktranslogistics.com'],subtitle,content)

        info=(id, company, email, originCountry,originState,originCity, destCountry, destState, destCity, item,dangerousGoods, stackable, number_of_pallets,number_of_oversized,number_of_overweight,sizeCm,sizeInch,delivery_address,postcode,lbs,volume,tailgateEN,residentialEN,deliveryType,create_date)

        sql= "INSERT INTO OverseaEmailinquiryLTL (id, company, email, originCountry,originState,originCity, destCountry, destState, destCity, item,dangerousGoods, stackable, number_of_pallets,number_of_oversized,number_of_overweight,cargo_size_cm,cargo_size_in,delivery_address,postcode,lbs,volume,tailgate,residential,deliveryType,create_date) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); "

        tools.insertMysql(sql,info)"""


        return '''<p>查询确认邮件已发送至贵司邮箱，我司会尽快回复给贵司价格，多谢合作！</p>
                    <p>如在查询过程中有任何疑问，可以随时发邮件至我司邮箱，以便我司提供更优质的服务。再次感谢！</p>'''

    return render_template('overseaInquiryLTL.html')



#国内整柜邮件询价
@app.route('/overseaInquiryFCL/', methods=['GET','POST'])
def overseaInquiryFCL():
    #return render_template('overseaInquiryFCL.html')
    if request.method == 'POST':

        #用当前时间生成id号
        toronto_tz = pytz.timezone('America/Toronto')
        toronto_time = datetime.datetime.now(toronto_tz)
        create_date = datetime.date.today()
        id = str(toronto_time)
        id = id.replace("-","")
        id = id.replace(" ","")
        id = id.replace(":","")
        id = id[0:14]


        company = request.form.get('company')
        email = request.form.get('email')


        originCountry = request.form.get('originCountry')
        originState = request.form.get('originState')

        originCity = request.form.get('originCity')


        destCountry = request.form.get('destCountry')



        destCity = request.form.get('destCity')

        destCity = destCity.strip()

        destCity = destCity.upper()

        item = request.form.get('item')

        dangerousGoods = request.form.get('dangerousGoods')
        if dangerousGoods == "是":
            dangerousGoods = "DANGEROUS GOODS"
        else:
            dangerousGoods = "Not dangerous Goods"

        delivery_address = request.form.get('delivery_address')
        postcode = request.form.get('postcode')
        postcode = postcode.replace(" ","")
        if "-" in postcode:
                postcode = postcode[0:5]
        weight = request.form.get('weight')
        weightUnit = request.form.get('weightUnit')


        #试着提取数字，以区分是加拿大或者美国邮编。
        postcodeUSA = re.match(r'^\d{5}',postcode)

        if  postcodeUSA:
            postcode = postcodeUSA[0]

        sql = f"select `city`, `state`,`country` from ZipCode where zipcode = '{postcode}';" #找到邮编对应城市和所属州/省
        resultTuple = tools.queryMysql(sql)


        if resultTuple is None:
            return "<h3>您提供的城市和邮政编码有误，请重新确认之后再查询！</h3?"

        if (destCountry !=  resultTuple[0][2]) or (destCity not in  resultTuple[0][0]):
            return f'''<p>您提供的信息有误，请重新核对之后再录入！</p>
<p>贵司提供的目的地国家和城市分别为{destCountry}，{destCity}</p>
</p>根据邮政编码查询的实际国家和城市分别为{resultTuple[0][2]}，{resultTuple[0][0]}</p> '''


        destState = resultTuple[0][1]

        volume = request.form.get('volume')
        volume =float(volume)

        containerType = request.form.get('containerType')

        residential = request.form.get('residential')

        special_request = request.form.get('special_request')

        if special_request :
            special_requesthtml = f"<p>特殊要求为：{special_request}</p>"
        else:
            special_request = 'No'



        createTime = datetime.date.today()

        subtitle = f"""{company}贵司的这票{containerType}从{originCountry}  {originCity} 送至{destCountry}  {destState} {destCity}的确认邮件，查询号：{id}"""


        content = f"""

        <h3>测试邮件</h3>

        <p>Dear&nbsp; {company}</p>


        <p>贵司刚刚查询的这票货，原始信息如下：</p>
        <p>从{originCountry}&nbsp;{originState}&nbsp;{originCity} 送至{destCountry}&nbsp;{destState}&nbsp;{destCity}&nbsp;{delivery_address}&nbsp;{postcode} 服务类型为：{containerType}整柜</p>
        <p>品名：{item}&nbsp;{dangerousGoods}&nbsp;&nbsp总重量为{weight}{weightUnit}。总体积为{volume}立方米</p>
        {special_requesthtml}
        <p>我们会尽快提供报价信息。</p>

        <p>多谢！</p>
        <p>Ktrans&nbsp;{createTime}</p>


        """

        EmailSender.tor2Email(['tor2@ktranslogistics.com','kathie@ktranslogistics.com','anna@ktranslogistics.com','kevin@ktranslogistics.com','import@ktranslogistics.com','tor1@ktranslogistics.com'],subtitle,content)

        if weightUnit == "KGS":
            lbs = round(int(weight)*2.2046)
        else:
            lbs = weight



        if residential == "商业地址":
            residentialEN = "commercial"

        if residential == "居民区":
            residentialEN = "residential"

        if containerType == "20尺普通柜":
            containerType = "20FT"
        if containerType == "40尺普通柜":
            containerType = "40FT"
        if containerType == "40尺超高柜":
            containerType = "40HQ"
        if containerType == "40尺开顶柜":
            containerType = "40OT"
        if containerType == "40尺超限柜":
            containerType = "40FR"
        if containerType == "40尺冷冻柜":
            containerType = "40RF"




        info=(id, company, email, originCountry,originState,originCity, destCountry, destState, destCity, item,dangerousGoods,delivery_address,postcode,containerType,lbs,volume,residentialEN,create_date,special_request)

        sql= "INSERT INTO OverseaEmailinquiryFCL (id, company, email, originCountry,originState,originCity, destCountry, destState, destCity, item,dangerousGoods, delivery_address,postcode,containerType,lbs,volume,residential,create_date,special_request) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); "

        tools.insertMysql(sql,info)


        #,'kathie@ktranslogistics.com','anna@ktranslogistics.com','kevin@ktranslogistics.com','import@ktranslogistics.com','tor1@ktranslogistics.com'


        return '''<p>查询确认邮件已发送至贵司邮箱，我司会尽快回复给贵司价格，多谢合作！</p>
                    <p>如在查询过程中有任何疑问，可以随时发邮件至我司邮箱，以便我司提供更优质的服务。再次感谢！</p>'''



    return render_template('overseaInquiryFCL.html')

#国内邮件询价记录
@app.route('/overseaInquiryRecords/', methods=['GET','POST'])
@login_required
def overseaInquiryRecords():

    if request.method == 'POST':
        shipping_type = request.form.get('shipping_type')
        sql = f"SELECT * FROM OverseaEmailinquiry{shipping_type} WHERE "

        And_ = ''

        id = request.form.get('id')
        if id:
            sql += f"{And_}id = '{id}' "
            And_ = 'AND'

        company = request.form.get('company')
        if company and company != " ":
            sql += f"{And_} company = '{company}' "
            And_ = 'AND'



        originCountry = request.form.get('originCountry')
        if originCountry:
            sql += f"{And_} originCountry = '{originCountry}' "
            And_ = 'AND'



        originCity = request.form.get('originCity')
        originCity = originCity.strip()

        if originCity:
            sql += f"{And_} originCity = '{originCity}' "
            And_ = 'AND'


        mail = request.form.get('mail')
        if mail:
            sql += f"{And_} mail = '{mail}' "
            And_ = 'AND'


        dataStart = request.form.get('dataStart')
        if dataStart:
            sql += f"{And_} create_date >= '{dataStart}' "
            And_ = 'AND'

        dataEnd = request.form.get('dataEnd')
        if dataEnd:
            sql += f"{And_} create_date <= '{dataEnd} 23:59:59' "
            And_ = 'AND'


        delivery_address = request.form.get('delivery_address')
        if delivery_address:
            sql += f"{And_} delivery_address LIKE '%{delivery_address}%' "
            And_ = 'AND'


        postcode = request.form.get('postcode')
        if postcode:
            if "-" in postcode:
                postcode = postcode[0:5]
            postcode = postcode.replace(" ","")

            sql += f"{And_} postcode = '{postcode}' "
            And_ = 'AND'


        if And_ == '':
            return "您没有选择任何查询信息，请确认输入选项，再重新查询"
        sql += "ORDER BY create_date DESC;"
        myreslut = tools.queryMysql(sql)
        if not myreslut:
            return "很抱歉，根据您输入的查询信息，系统中没有找到任何匹配的记录。请试着更改查询条件，再进行查询操作。多谢！"
        else:
            return render_template('overseaInquiryRecordsSearchResult.html', myreslut = myreslut, shipping_type=shipping_type)


    sql = "select * from OverseaEmailinquiryFCL where mail = '未发送' order by id desc;"
    FCLInfoTupleNo = tools.queryMysql(sql)
    sql = "select * from OverseaEmailinquiryFCL where mail = '已发送' order by id desc LIMIT 15;"
    FCLInfoTupleYes = tools.queryMysql(sql)
    sql = "select * from OverseaEmailinquiryLTL where mail = '未发送' order by id desc;"
    LTLInfoTupleNo = tools.queryMysql(sql)
    sql = "select * from OverseaEmailinquiryLTL where mail = '已发送' order by id desc LIMIT 15;"
    LTLInfoTupleYes = tools.queryMysql(sql)

    fclOverseaInfoString = " "

    sql = "SELECT DISTINCT `company` FROM OverseaEmailinquiryFCL order by company;"
    FCLOverseaInfoTuple = tools.queryMysql(sql)
    FCLOverseaInfoList = [oversea[0] for oversea in FCLOverseaInfoTuple]
    for oversea in FCLOverseaInfoTuple:

        fclOverseaInfoString += ',' + oversea[0]


    ltlOverseaInfoString = " "
    sql = "SELECT DISTINCT `company` FROM OverseaEmailinquiryLTL order by company;"
    LTLOverseaInfoTuple = tools.queryMysql(sql)
    for oversea in LTLOverseaInfoTuple:

        ltlOverseaInfoString += ',' + oversea[0]



    return render_template('overseaInquiryRecords.html', FCLInfoTupleNo = FCLInfoTupleNo ,FCLInfoTupleYes = FCLInfoTupleYes ,LTLInfoTupleNo = LTLInfoTupleNo ,LTLInfoTupleYes = LTLInfoTupleYes , fclOverseaInfoString= fclOverseaInfoString, ltlOverseaInfoString =ltlOverseaInfoString, FCLOverseaInfoList = FCLOverseaInfoList )

#国内整柜邮件询价
@app.route('/inquiryMailToTruckersFCL/<id>/', methods=['GET','POST'])
@login_required
def inquiryMailToTruckersFCL(id):


        sql= f"SELECT *  FROM OverseaEmailinquiryFCL WHERE id = '{id}';"

        result = tools.queryMysql(sql)

        sql = f"select `company`, `email`,`remark` from Trucker where (city LIKE '%{result[0][5]}%' OR city = 'ALL ') and (country = '{result[0][3]}') and (state LIKE '%{result[0][4]}%' or state = 'ALL') and (field in ('FCL','ALL ')) and (Zone = 'ALL ' or Zone like '%{result[0][7]}%') ;" #找到符合条件Trucker邮箱
        receiverList = tools.queryMysql(sql)






        subtitle = "Please kindly quote us delivery fee for this FCL shipment with FILE#  " + id


        content = f"""

        <p>Good&nbsp;Day,</p>

<p>Please&nbsp;kindly&nbsp;quote&nbsp;us&nbsp;delivery&nbsp;fee&nbsp;for&nbsp;this&nbsp;Full container. Cargo info:<strong> {result[0][9]}&nbsp;&nbsp;{result[0][10]}&nbsp;&nbsp; {result[0][13]}&nbsp;{result[0][16]}</strong></p>

<p>Ship&nbsp;From:&nbsp;<strong>{result[0][5]}&nbsp;railway&nbsp;termianl&nbsp;{result[0][4]}&nbsp;{result[0][3]}</strong></p>

<p>Ship&nbsp;To:&nbsp;<strong>{result[0][11]}&nbsp;{result[0][8]}&nbsp;{result[0][7]}&nbsp;{result[0][6]}&nbsp;ZipCode:&nbsp;{result[0][12]}</strong></p>

<p><strong>{result[0][13]}&nbsp; {result[0][14]}&nbsp;POUNDS&nbsp;{result[0][15]}cbm</strong></p>

<p><strong>special request:{result[0][23]}</strong></p>

<p><strong>{result[0][16]}&nbsp; address</strong></p>

<p><strong>BOOK&nbsp;APPOINTMENT&nbsp;WITH&nbsp;CONSIGNEE&nbsp;AHEAD</strong></p>

<p>I&#39;m&nbsp;looking&nbsp;forward&nbsp;for&nbsp;your&nbsp;reply.&nbsp;Thank&nbsp;you!</p>

<p>Best&nbsp;regards</p>


<br>"""

        ActionItems = "整柜邮件群发询价"

        contentMarkdown = html2text.html2text(content)



        return render_template('inquiryMail.html', subtitle =  subtitle ,  contentMarkdown = contentMarkdown, receiverList = receiverList,ActionItems = ActionItems, ID = id )

#国内散货邮件询价
@app.route('/inquiryMailToTruckersLTL/<id>/', methods=['GET','POST'])
@login_required
def inquiryMailToTruckersLTL(id):

    sql= f"SELECT *  FROM OverseaEmailinquiryLTL WHERE id = '{id}';"

    result = tools.queryMysql(sql)

    sql = f"select `company`, `email`,`remark` from Trucker where (city LIKE '%{result[0][5]}%' OR city = 'ALL ') and (country = '{result[0][3]}') and (state LIKE '%{result[0][4]}%' or state = 'ALL') and (field in ('{result[0][27]}','ALL ')) and (Zone = 'ALL ' or Zone like '%{result[0][7]}%') ;" #找到符合条件Trucker邮箱
    receiverList = tools.queryMysql(sql)

    subtitle = "Please kindly quote us delivery fee for this shipment with FILE#  " + id


    content = f"""

        <p>Good&nbsp;Day,</p>

<p>Please&nbsp;kindly&nbsp;quote&nbsp;us&nbsp;delivery&nbsp;fee&nbsp;for&nbsp;this&nbsp;shipment. Cargo info:<strong> {result[0][9]}&nbsp;&nbsp;{result[0][10]}&nbsp;&nbsp;{result[0][11]}&nbsp;&nbsp;{result[0][27]}&nbsp;service</strong></p>

<p>Ship&nbsp;From:&nbsp;<strong>{result[0][5]}&nbsp;warehouse&nbsp;{result[0][4]}&nbsp;{result[0][3]}</strong></p>

<p>Ship&nbsp;To:&nbsp;<strong>{result[0][17]}&nbsp;&nbsp;{result[0][8]}&nbsp;{result[0][7]}&nbsp;{result[0][6]}&nbsp;ZipCode:&nbsp;{result[0][18]}</strong></p>

<p><strong>{result[0][12]}&nbsp;SKIDS&nbsp;{result[0][19]}&nbsp;POUNDS&nbsp;{result[0][20]}cbm</strong></p>


<p style="white-space: pre-line;">
       {result[0][16]}
</p>


<p><strong>Oversized pallets is : {result[0][13]}&nbsp;&nbsp; Overweighted pallets is : {result[0][14]}</strong></p>


<p><strong>{result[0][21]}</strong></p>

<p><strong>{result[0][22]}&nbsp; address</strong></p>

<p><strong>BOOK&nbsp;APPOINTMENT&nbsp;WITH&nbsp;CONSIGNEE&nbsp;AHEAD</strong></p>

<p>I&#39;m&nbsp;looking&nbsp;forward&nbsp;for&nbsp;your&nbsp;reply.&nbsp;Thank&nbsp;you!</p>

<p>Best&nbsp;regards</p>


<br>"""

    ActionItems = "散货邮件群发询价"

    contentMarkdown = html2text.html2text(content)
    return render_template('inquiryMail.html', subtitle =  subtitle ,  contentMarkdown = contentMarkdown, receiverList = receiverList,ActionItems = ActionItems, ID = id )


#国内询价记录局部修改
@app.route('/overseaInquiryRecordchange/<ID>/', methods = ["GET","POST"])

@login_required

def overseaInquiryRecordchange(ID):
    id = ID[:-3]
    shipping_type = ID[-3:]

    sql = f"SELECT `basePrice` ,`price` ,`dealDate` ,`remark` FROM OverseaEmailinquiry{shipping_type} WHERE id = '{id}' ;"
    myresult = tools.queryMysql(sql)

    basePrice = myresult[0][0]
    price = myresult[0][1]
    dealDate = myresult[0][2]
    remark = myresult[0][3]



    if request.method == 'POST':
        id = ID[:-3]
        shipping_type = ID[-3:]


        basePrice = request.form.get('basePrice')
        if basePrice :
            basePrice = int(basePrice)
        price = request.form.get('price')
        if price :
            price = int(price)
        dealDate = request.form.get('dealDate')
        remark = request.form.get('remark')


        sql = f"update OverseaEmailinquiry{shipping_type}  SET `basePrice` = {basePrice} ,`price`  = {price}  ,`dealDate` = '{dealDate}' ,`remark` = '{remark}' WHERE id = '{id}' "

        tools.updateMysql(sql)

        flash('Modification completed!', category='success')


        return redirect(url_for('overseaInquiryRecordchange', ID = ID))


    return render_template('overseaInquiryRecordchange.html', basePrice = basePrice ,price  = price  ,dealDate = dealDate ,remark = remark )


#综合状态查询
@app.route('/status/')

@login_required

def status():

    if current_user.job_id in ['kathie','ronnie','david','tina','anna', 'acountant']:
        condition = ''
    else:

        operatorid = current_user.id
        condition = f"and operator = {operatorid}"


    sql = f"select order_id, Orders.remark, create_date, vessel_name,ssl_info, shipping_type, service_type, dest_city , eta,  Oversea.company, Broker.company, User.name , SSLInfo.website, container_number FROM Orders JOIN SSLInfo ON Orders.ssl_info = SSLInfo.company  JOIN User ON User.user_id = Orders.operator JOIN Broker ON Orders.broker = Broker.broker_id   JOIN Oversea ON Orders.oversea = Oversea.oversea_id WHERE status = 'AT SEA' {condition} ORDER BY create_date ASC , User.name ASC"
    atSeaList = tools.queryMysql(sql)


    sql = f"select order_id, Orders.remark, hold, create_date, shipping_type, service_type, dest_city ,client , Orders.company , Orders.phone , Orders.address , delivery_type , ccn , lfdwarehouse , payment_methods ,  trucker , readyForDeliver, Oversea.company, Broker.company, Warehouse.company, Warehouse.website, amount, weight, volume, size , User.name FROM Orders JOIN User ON User.user_id = Orders.operator  JOIN Broker ON Orders.broker = Broker.broker_id  JOIN Oversea ON Orders.oversea = Oversea.oversea_id JOIN Warehouse ON Orders.warehouse = Warehouse.warehouse_id where status = 'IN PORT' {condition} ORDER BY order_id ASC , User.name ASC"
    inPortList = tools.queryMysql(sql)


    sql = f"select order_id, Orders.remark, hold,  train_company , shipping_type, service_type, dest_city ,CASE  WHEN LEFT(eta, 1) IN ('2','0') THEN SUBSTRING(eta, 6) ELSE eta END, client , Orders.phone , Orders.address , delivery_type , ccn , lfdwarehouse , payment_methods ,  trucker , readyForDeliver, Oversea.company, Broker.company, Warehouse.company, Warehouse.website, amount, weight, volume, size  , User.name, container_number FROM Orders JOIN User ON User.user_id = Orders.operator  JOIN Broker ON Orders.broker = Broker.broker_id  JOIN Oversea ON Orders.oversea = Oversea.oversea_id JOIN Warehouse ON Orders.warehouse = Warehouse.warehouse_id where status = 'ON RAIL' {condition} ORDER BY eta ASC , User.name ASC"
    onRailList = tools.queryMysql(sql)

    sql = f"select order_id, Orders.remark, hold, create_date, shipping_type, service_type, dest_city ,client , Orders.company , Orders.phone , Orders.address , delivery_type , ccn , lfdwarehouse , payment_methods ,  trucker , readyForDeliver, Oversea.company, Broker.company, Warehouse.company, Warehouse.website, amount, weight, volume, size  , User.name FROM Orders JOIN User ON User.user_id = Orders.operator  JOIN Broker ON Orders.broker = Broker.broker_id  JOIN Oversea ON Orders.oversea = Oversea.oversea_id JOIN Warehouse ON Orders.warehouse = Warehouse.warehouse_id where status = 'ON FLOOR' {condition} ORDER BY lfdwarehouse ASC , User.name ASC"
    onFloorList = tools.queryMysql(sql)

    sql = f"select order_id, Orders.remark, hold, create_date, shipping_type, service_type, dest_city ,client , Orders.company , Orders.phone , Orders.address , delivery_type , ccn , lfdwarehouse , payment_methods ,  trucker , readyForDeliver, Oversea.company, Broker.company, Warehouse.company, Warehouse.website, amount, weight, volume, size  , User.name FROM Orders JOIN User ON User.user_id = Orders.operator   JOIN Broker ON Orders.broker = Broker.broker_id JOIN Oversea ON Orders.oversea = Oversea.oversea_id JOIN Warehouse ON Orders.warehouse = Warehouse.warehouse_id where status = 'PICKEDUP' {condition} ORDER BY lfdwarehouse ASC , User.name ASC"
    pickedUpList = tools.queryMysql(sql)

    sql = f"select order_id, Orders.remark, hold, create_date, shipping_type, service_type, dest_city ,client , Orders.company , Orders.phone , Orders.address , delivery_type , ccn , lfdwarehouse , payment_methods ,  trucker , readyForDeliver, Oversea.company, Broker.company, Warehouse.company, Warehouse.website, amount, weight, volume, size  , User.name FROM Orders JOIN User ON User.user_id = Orders.operator   JOIN Broker ON Orders.broker = Broker.broker_id JOIN Oversea ON Orders.oversea = Oversea.oversea_id JOIN Warehouse ON Orders.warehouse = Warehouse.warehouse_id where status = 'BOOKED' {condition} ORDER BY lfdwarehouse ASC , User.name ASC"
    bookedList = tools.queryMysql(sql)


    return render_template('status.html', atSeaList = atSeaList , inPortList = inPortList, onRailList = onRailList , onFloorList = onFloorList, pickedUpList = pickedUpList, bookedList = bookedList)



@app.route('/accountant/', methods=['GET'])
@login_required
def accountant():


    return render_template('accountant.html')


#多伦多进仓货物查询
@app.route('/torontowarehouse/')



def torontowarehouse():


    sql = "select order_id, Orders.remark, hold,  train_company , shipping_type, service_type, dest_city , eta , client , Orders.phone , Orders.address , delivery_type , ccn , lfdwarehouse , payment_methods ,  trucker , readyForDeliver, Oversea.company, Broker.company, Warehouse.company, Warehouse.website, amount, weight, volume, size  , User.name FROM Orders JOIN User ON User.user_id = Orders.operator  JOIN Broker ON Orders.broker = Broker.broker_id  JOIN Oversea ON Orders.oversea = Oversea.oversea_id JOIN Warehouse ON Orders.warehouse = Warehouse.warehouse_id WHERE status = 'ON RAIL'  AND dest_city = 'TORONTO'  AND delivery_type <> '自提' ORDER BY eta ASC , User.name ASC"
    onRailList = tools.queryMysql(sql)

    sql = "select order_id, Orders.remark, hold, create_date, shipping_type, service_type, dest_city ,client , Orders.company , Orders.phone , Orders.address , delivery_type , ccn , lfdwarehouse , payment_methods ,  trucker , readyForDeliver, Oversea.company, Broker.company, Warehouse.company, Warehouse.website, amount, weight, volume, size  , User.name FROM Orders JOIN User ON User.user_id = Orders.operator  JOIN Broker ON Orders.broker = Broker.broker_id  JOIN Oversea ON Orders.oversea = Oversea.oversea_id JOIN Warehouse ON Orders.warehouse = Warehouse.warehouse_id where status = 'ON FLOOR'  AND dest_city = 'TORONTO' AND shipping_type = 'LCL' AND delivery_type <> '自提' ORDER BY lfdwarehouse ASC , User.name ASC"
    onFloorList = tools.queryMysql(sql)

    sql = "select order_id, Orders.remark, hold, create_date, shipping_type, service_type, dest_city ,client , Orders.company , Orders.phone , Orders.address , delivery_type , ccn , lfdwarehouse , payment_methods ,  trucker , readyForDeliver, Oversea.company, Broker.company, Warehouse.company, Warehouse.website, amount, weight, volume, size  , User.name FROM Orders JOIN User ON User.user_id = Orders.operator   JOIN Broker ON Orders.broker = Broker.broker_id JOIN Oversea ON Orders.oversea = Oversea.oversea_id JOIN Warehouse ON Orders.warehouse = Warehouse.warehouse_id where status = 'PICKEDUP'  AND dest_city = 'TORONTO' AND shipping_type = 'LCL' AND delivery_type <> '自提' ORDER BY lfdwarehouse ASC , User.name ASC"
    pickedUpList = tools.queryMysql(sql)

    sql = "select order_id, Orders.remark, hold, create_date, shipping_type, service_type, dest_city ,client , Orders.company , Orders.phone , Orders.address , delivery_type , ccn , lfdwarehouse , payment_methods ,  trucker , readyForDeliver, Oversea.company, Broker.company, Warehouse.company, Warehouse.website, amount, weight, volume, size  , User.name FROM Orders JOIN User ON User.user_id = Orders.operator   JOIN Broker ON Orders.broker = Broker.broker_id JOIN Oversea ON Orders.oversea = Oversea.oversea_id JOIN Warehouse ON Orders.warehouse = Warehouse.warehouse_id where status = 'BOOKED'  AND dest_city = 'TORONTO' AND shipping_type = 'LCL' AND delivery_type <> '自提' ORDER BY lfdwarehouse ASC , User.name ASC"
    bookedList = tools.queryMysql(sql)


    return render_template('torontowarehouse.html', onRailList = onRailList , onFloorList = onFloorList, pickedUpList = pickedUpList, bookedList = bookedList)


@app.route('/selfClearance/', methods=['GET'])
@login_required
def selfClearance():


    return render_template('selfClearance.html')



@app.route('/overseaOrderStatus/', methods=['GET', 'POST'])
def overseaOrderStatus():
    if request.method == 'POST':


        oversea = request.form.get('overseaID')
        overseaID = int(oversea)

        password = request.form.get('password')
        sql = f"select password  FROM Oversea where oversea_id = {overseaID}"
        result = tools.queryMysql(sql)
        passwordCorrect = result[0][0]

        if passwordCorrect == password:
            sql = f"select order_id, status, container_number, vessel_name, shipping_type, service_type, origin_city, dest_city , eta,lfdwarehouse, amount, weight, volume,Oversea.company,  User.name  FROM Orders  JOIN User ON User.user_id = Orders.operator   JOIN Oversea ON Orders.oversea = Oversea.oversea_id WHERE  Orders.oversea = {overseaID} and  status NOT IN ('DELIVERED','CANCELLED')  ORDER BY status ASC , order_id ASC"
            cargoList = tools.queryMysql(sql)

            return render_template('overseaCargoList.html', cargoList = cargoList )





        else:
            return '用户名和密码不正确，请返回原页面重新填写！'



    oversea = tools.fillComboBox('oversea_id','company', 'Oversea')


    overseaList = list(oversea)
    overseaList.remove((20,'未知'))
    overseaList.remove((40,'自揽货'))

    return render_template('oversealogin.html', overseaList = overseaList )



@app.route('/uploadexcel/', methods=['GET', 'POST'])
def upload_excel():
    folder_path = "/home/KTRANS/mysite/static/cache/"
    # 清理旧文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    if request.method == 'POST':
        entry_type = request.form.get('entry_type')  # 返回字符串，例如 "乐业excel录入"
        cargo_id = request.form.get('cargo_id')  # 用户输入的货柜号

        file = request.files['file']
        if file:
            filename = file.filename
            current_path = os.path.join(folder_path, filename)
            file.save(current_path)
            if entry_type == "恒好达":
                return excelreader.linkupreadexcel(current_path,cargo_id, filename)


    return render_template('excelUpload.html')





@app.route('/fba_order/', methods=['GET', 'POST'])
def fba_order():
    result = {}

    # 第一层查询 DISTINCT cargo_id
    sql_titles = """
    SELECT DISTINCT
        f.cargo_id,
        o.container_number,
        o.status
    FROM FBA_orders f
    LEFT JOIN Orders o
        ON f.cargo_id = o.order_id
    WHERE f.status IN ('即将入仓','在仓库')
    ORDER BY f.cargo_id;
    """

    titles = tools.queryMysql(sql_titles)  # [(cargo_id, container_number, status), ...]

    for cargo_id, container_number, status in titles:
        # 第二层查询明细
        sql_details = f"""
        SELECT
            shipment_id,
            mark,
            pallets,
            pieces,
            po_list,
            FBA_warehouse
        FROM FBA_orders
        WHERE cargo_id = '{cargo_id}'
          AND status <> '已派送'
        ORDER BY FBA_warehouse,FIELD(status, '在仓库', '即将入仓'), shipment_id;
        """

        details = tools.queryMysql(sql_details)

        # 存入字典
        result[cargo_id] = {
            "container_number": container_number,
            "status": status,
            "details": details
        }

    if request.method == 'POST':
        warehouse = 'YXU1'
        cargo_id = 'T304114&T304127&T304117&T304142'
        pallets = '14'
        date = '20260223'
        cargo_list = [	 ('SDCU1217863','T304114','4','641','17ZT8L2Y'),
    	 ('SDCU1217863','T304114','1','174','3PHSYHHR'),
    	 ('SMCU1273490','T304127',1,175,'8WJPDTJD'),
    	 ('KOCU4004464','T304117',3,228,'8LBRW5TB'),
    	 ('HMMU7122187','T304142',5,400,'7ALP3ONX')
    ]
        filePath = '/home/KTRANS/mysite/static/files/FBA/'

        for filename in os.listdir(filePath):
            file_full_path = os.path.join(filePath, filename)

            if os.path.isfile(file_full_path):
                os.remove(file_full_path)

        return deliveryOrder.FBA_deliveryorder(warehouse,cargo_id,pallets, date,cargo_list)

    # 传给模板
    return render_template("FBA_Order.html", cargo_data=result)



@app.route('/ktranslikupfba20260228/', methods=['GET', 'POST'])
def fba_edit():
    # 如果是 POST 提交，先处理表单
    if request.method == 'POST':
        for key, value in request.form.items():
            try:


                if key.startswith("remark_"):
                    _, cargo_id, shipment_id = key.split("_")
                    sql = "UPDATE FBA_orders SET remark = %s WHERE cargo_id = %s AND shipment_id = %s"
                    tools.queryMysql(sql, (value, cargo_id, shipment_id))

                # 新增：处理上火车货柜备注
                elif key.startswith("onrail_remark_"):
                    # key = "onrail_remark_123456" -> order_id = 123456
                    order_id = key[len("onrail_remark_"):]  # 取 name 中 15 位之后的部分
                    sql = "UPDATE Orders SET remark = %s WHERE order_id = %s"
                    tools.queryMysql(sql, (value, order_id))


            except Exception as e:
                print("更新出错:", key, value, e)

        # POST 后刷新页面
        return redirect(url_for('fba_edit'))

    # GET 请求，生成页面数据

    #查询 Orders 表中 status = 'ON RAIL' 且 oversea = 72 的记录


    sql = """
        SELECT Order_id, container_number, eta, remark
        FROM Orders
        WHERE oversea = %s AND status = %s order by eta
    """
    onrailList = tools.queryMysql(sql, (72, 'ON RAIL'))



    result = {}

    # 第一层查询 DISTINCT cargo_id
    sql_titles = """
    SELECT DISTINCT
        f.cargo_id,
        o.container_number,
        SUBSTRING(DATE_ADD(o.eta, INTERVAL 2 DAY), 6, 5) AS eta,
        o.status
    FROM FBA_orders f
    LEFT JOIN Orders o
        ON f.cargo_id = o.order_id
    WHERE f.status IN ('即将入仓','在仓库')
    ORDER BY o.eta DESC;
    """
    titles = tools.queryMysql(sql_titles)

    for cargo_id, container_number,eta, status in titles:
        # 第二层查询明细
        sql_details = f"""
        SELECT
            shipment_id,
            mark,
            pallets,
            pieces,
            po_list,
            FBA_warehouse,
            Inbound_date,
            remark,
            book_date

        FROM FBA_orders
        WHERE cargo_id = '{cargo_id}'
          AND status <> '已派送'
        ORDER BY FBA_warehouse, FIELD(status, '在仓库', '即将入仓'), shipment_id;
        """
        details = tools.queryMysql(sql_details)

        result[cargo_id] = {
            "container_number": container_number,
            "status": status,
            "eta": eta,
            "details": details
        }

    return render_template("FBA_Edit.html", cargo_data=result, onrailList =onrailList )



#编辑拼柜货明细表
@app.route('/GroupageOrder_manage/', methods=['GET','POST'])
def GroupageOrder_manage():

    if request.method == 'POST':
        def clean_int(value):
            return int(value) if value and value.strip() != "" else None

        def clean_decimal(value):
            return float(value) if value and value.strip() != "" else None

        for key in request.form:
            if key.startswith("pieces_"):
                sub_id = key.split("_")[1]

                sql = """
                UPDATE GroupageOrders
                SET pieces=%s,
                    weight=%s,
                    volumn=%s,
                    pallets_number=%s,
                    cargo=%s,
                    client=%s,
                    phone=%s,
                    email=%s,
                    address=%s,
                    delivery_type=%s,
                    hold=%s,
                    remark=%s,
                    status=%s
                WHERE sub_id=%s
                """

                params = (
                    clean_int(request.form.get(f"pieces_{sub_id}")),
                    clean_int(request.form.get(f"weight_{sub_id}")),
                    clean_decimal(request.form.get(f"volumn_{sub_id}")),
                    clean_int(request.form.get(f"pallets_number_{sub_id}")),
                    request.form.get(f"cargo_{sub_id}") or None,
                    request.form.get(f"client_{sub_id}") or None,
                    request.form.get(f"phone_{sub_id}") or None,
                    request.form.get(f"email_{sub_id}") or None,
                    request.form.get(f"address_{sub_id}") or None,
                    request.form.get(f"delivery_type_{sub_id}") or None,
                    request.form.get(f"hold_{sub_id}") or None,
                    request.form.get(f"remark_{sub_id}") or None,
                    request.form.get(f"status_{sub_id}"),
                    sub_id
                )

                tools.updateMysql(sql, params)

        return redirect(url_for('GroupageOrder_manage'))

    # ====== GET 部分改成字典游标 ======

    conn = pymysql.connect(
        host='KTRANS.mysql.pythonanywhere-services.com',
        user='KTRANS',
        password='ktrans6477021238',
        database='KTRANS$ktrans',
        charset='utf8mb4',


        cursorclass=DictCursor   # ⭐ 关键在这里
    )

    cursor = conn.cursor()

    sql = "SELECT * FROM GroupageOrders ORDER BY main_order"
    cursor.execute(sql)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    # 分组
    grouped = {}
    for row in data:
        grouped.setdefault(row['main_order'], []).append(row)

    return render_template("Groupage_manage.html", grouped=grouped)


@app.route('/fba_generate/', methods=['GET', 'POST'])
def fba_generate():

    # ------------------------
    # 连接数据库
    # ------------------------
    conn = pymysql.connect(
        host='KTRANS.mysql.pythonanywhere-services.com',
        user='KTRANS',
        password='ktrans6477021238',
        database='KTRANS$ktrans',
        charset='utf8mb4',
        cursorclass=DictCursor
    )

    cursor = conn.cursor()

    # =========================
    # POST：批量更新入仓时间
    # =========================
    if request.method == 'POST':
        selected_ids = request.form.getlist('selected_items')
        inbound_date = request.form.get('inbound_date')

        if selected_ids and inbound_date:
            format_strings = ','.join(['%s'] * len(selected_ids))
            sql = f"""
                UPDATE FBA_orders
                SET inbound_date = %s
                WHERE shipment_id IN ({format_strings})
            """
            cursor.execute(sql, [inbound_date] + selected_ids)
            conn.commit()
            flash("入仓时间更新成功！")

        cursor.close()
        conn.close()
        return redirect(url_for('fba_generate'))

    # =========================
    # GET：加载页面数据
    # =========================
    sql = """
    SELECT
        f.shipment_id,
        f.cargo_id,
        f.FBA_warehouse,
        f.mark,
        f.pallets,
        f.cartons,
        f.pieces,
        f.po_list,
        f.status,
        f.book_date,
        f.inbound_date,
        o.status AS order_status,
        s.pallets AS total_pallets,
        s.remark,
        s.cn_instruction
    FROM FBA_orders f
    JOIN Orders o ON o.order_id = f.cargo_id
    LEFT JOIN FBA_orders_summary s
        ON s.cargo_id = f.cargo_id
        AND s.FBA_warehouse = f.FBA_warehouse
    WHERE o.status IN ('ON RAIL', 'PICKEDUP')
    ORDER BY
        FIELD(o.status, 'PICKEDUP','ON RAIL'),
        f.FBA_warehouse,
        f.cargo_id
    """

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # =========================
    # 数据整理：按仓库分组 + 每 cargo 生成唯一 group_id
    # =========================
    warehouse_data = defaultdict(lambda: defaultdict(list))
    for r in rows:
        warehouse = r['FBA_warehouse']
        cargo = r['cargo_id']
        warehouse_data[warehouse][cargo].append(r)

    structured_data = {}
    for warehouse, cargos in warehouse_data.items():
        structured_data[warehouse] = []
        for cargo_id, shipments in cargos.items():
            group_id = str(uuid.uuid4()).replace("-", "")
            structured_data[warehouse].append({
                "cargo_id": cargo_id,
                "group_id": group_id,
                "shipments": shipments
            })

    return render_template('fba_generate.html', warehouse_data=structured_data)

#手机拍照上传POD
@app.route('/phone_upload_pod/<cargo_id>/', methods=['GET','POST'])
def phone_upload_pod(cargo_id):

    # 基础上传目录
    base_folder = "static/pod"

    # 每个单号一个文件夹
    upload_folder = os.path.join(base_folder, cargo_id)

    # 如果文件夹不存在就创建
    os.makedirs(upload_folder, exist_ok=True)

    # =================
    # GET：打开页面
    # =================
    if request.method == "GET":
        return render_template("phone_upload_pod.html",
                               cargo_id=cargo_id)

    # =================
    # POST：保存文件
    # =================

    # 从前端获取文件
    file = request.files.get('pod_photo')

    if not file:
        return "没有文件"

    # 获取扩展名
    ext = file.filename.split('.')[-1].lower()

    # 支持 jpg, jpeg, png, pdf
    if ext not in ['jpg', 'jpeg', 'png', 'pdf']:
        return "只允许上传图片或 PDF 文件"

    # 如果是图片，统一保存为 jpg
    if ext in ['jpeg', 'png']:
        ext = "jpg"

    # 构造基础文件名
    base_filename = f"{cargo_id}_pod"
    filename = f"{base_filename}.{ext}"
    save_path = os.path.join(upload_folder, filename)

    # 如果重名，自动编号
    counter = 1
    while os.path.exists(save_path):
        filename = f"{base_filename}_{counter}.{ext}"
        save_path = os.path.join(upload_folder, filename)
        counter += 1

    # 保存文件
    file.save(save_path)

    # 生成访问URL
    image_url = url_for('static', filename=f"pod/{cargo_id}/{filename}")

    # 前端显示
    if ext == "pdf":
        return f"""
        <h3>上传成功 ✅</h3>
        <a href="{image_url}" target="_blank">点击查看 PDF 文件</a>
        """
    else:
        return f"""
        <h3>上传成功 ✅</h3>
        <img src="{image_url}" style="max-width:100%;height:auto;">
        """

@app.route('/view_pod/<cargo_id>/')
def view_pod(cargo_id):
    # 基础上传目录
    base_folder = "static/pod"

    # 每个单号一个文件夹
    folder = os.path.join(base_folder, cargo_id)

    if not os.path.exists(folder):
        return f"没有找到 POD 文件夹: {cargo_id}"

    files = os.listdir(folder)
    # 只保留常用文件类型
    files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf'))]

    file_urls = [url_for('static', filename=f'pod/{cargo_id}/{f}') for f in files]

    return render_template('view_pod.html', files=file_urls)




if __name__=='__main__':

    app.run(host='0.0.0.0', debug=True , port='5001')