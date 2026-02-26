

import os
import re
import pandas as pd
import math
import openpyxl
import json
from flask import jsonify,Response
import pymysql
from decimal import Decimal, ROUND_CEILING, getcontext, InvalidOperation



from datetime import datetime


def get_column(row, keywords):
    """
    从 row 中找到包含 keywords 的列名（忽略空格和大小写）
    """
    for col in row.index:
        col_clean = col.replace(' ', '').replace('\xa0','').lower()
        if keywords.replace(' ', '').lower() in col_clean:
            return row[col]
    # 找不到就返回 0 或 None
    return 0

def read_excel_safe(
    path,
    sheet_name=0,              # 默认第一页（等同于不传）
    keep_default_na=False
):
    """
    安全读取 Excel，自动识别 xls / xlsx

    参数：
    - path: 文件路径
    - sheet_name:
        0 / "Sheet1"        -> 单个 sheet
        [0, 1] / ["A","B"]  -> 多个 sheet
        None                -> 所有 sheet（返回 dict）
    """

    ext = os.path.splitext(path)[1].lower()

    if ext == ".xls":
        engine = "xlrd"
    elif ext == ".xlsx":
        engine = "openpyxl"
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return pd.read_excel(
        path,
        engine=engine,
        sheet_name=sheet_name,
        keep_default_na=keep_default_na
    )

def get_db():
    return pymysql.connect(
        host="KTRANS.mysql.pythonanywhere-services.com",
        user="KTRANS",
        password="ktrans6477021238",
        database="KTRANS$ktrans",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor  # ✅ 返回字典
    )




def clean_value(v):
    if pd.isna(v) or (isinstance(v, float) and math.isnan(v)):
        return None
    return v

def to_number(value, as_int=False, default=0):
    """
    将Excel单元格内容安全转换为数值（整数或小数）

    参数:
        value    - Excel单元格的原始值
        as_int   - True: 输出整数(int)，False: 输出小数(float)
        default  - 无法转换时的默认值
    """
    if pd.isna(value):
        return default

    # 如果本身就是 int 或 float
    if isinstance(value, (int, float)):
        return int(value) if as_int else float(value)

    # 如果是字符串
    if isinstance(value, str):
        val_str = value.strip().replace(",", "")
        if val_str == "":
            return default
        try:
            # 转换
            return int(float(val_str)) if as_int else float(val_str)
        except ValueError:
            return default

    # 其他类型（比如公式对象），尝试强制转字符串再解析
    try:
        val_str = str(value).strip().replace(",", "")
        return int(float(val_str)) if as_int else float(val_str)
    except Exception:
        return default

def linkupreadexcel(path, cargo_id, filename):
    conn = get_db()
    conn.autocommit(False)


    # 读取第一个 sheet（默认）
    df = pd.read_excel(path, sheet_name=0, header=None)  # 0 表示第一个 sheet
    batch = filename
    if '-' in filename:
        batch = filename.split('-', 1)[1].strip()
    if '.xlsx' in filename:
        batch = batch.replace('.xlsx', '')


    mark = ''
    FBA_warehouse = ''
    delivery_type = ''
    errors = []
    info_count = 0

    with conn.cursor() as cur:

        for _, row in df.iterrows():
            # 基本过滤

            if pd.notna(row[2]) and 'FBA' in str(row[2]):
                shipment_id = row[2]
                mark = row[3] if pd.notna(row[3]) else mark
                cartons = int(to_number(row[6]))
                pieces = int(to_number(row[7]))
                po_list = row[8]
                FBA_warehouse = row[9] if pd.notna(row[9]) else FBA_warehouse
                volume = to_number(row[10])
                weight = to_number(row[11])
                delivery_type = row[12] if pd.notna(row[12]) else delivery_type



                info = (
                    batch,cargo_id, shipment_id, mark,cartons,pieces,po_list, FBA_warehouse,  volume, weight , delivery_type
                )

                insert_sql = """
                    INSERT INTO FBA_orders (
                        batch,cargo_id, shipment_id, mark,cartons,pieces,po_list, FBA_warehouse,  volume, weight , delivery_type
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s
                    );
                """
                try:
                    cur.execute("SAVEPOINT sp;")

                    # 1️⃣ 插入 cargoInfo
                    print(info)
                    cur.execute(insert_sql, info)
                    info_count += 1



                except Exception as e:
                    msg = str(e)
                    if "Duplicate entry" in msg:
                        errors.append({...})
                    else:
                        errors.append({...})

                    cur.execute("ROLLBACK TO SAVEPOINT sp;")




    conn.commit()  # 循环完成后统一提交


    # 打印或返回错误（按需，你现在选择打印）
    if errors:
        print("⚠️ Some records failed to insert:")
        for err in errors:
            print(err)

    return f"success，cargoInfo 成功 {info_count} 条 "


