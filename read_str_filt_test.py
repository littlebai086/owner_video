# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 15:59:07 2024

@author: peter
"""


import mysql.connector
from mysql.connector import Error
from fuzzywuzzy import fuzz, process
# 数据库连接配置
config = {
    'user': 'admin',      # 替换为你的用户名
    'password': 'ustvweb',   # 替换为你的密码
    'host': '192.168.20.152',           # 替换为你的主机地址，通常是 'localhost'
    'database': 'ustvmedia'    # 替换为你的数据库名
}

stock_name_array = []
try:
    # 连接到数据库
    connection = mysql.connector.connect(**config)

    if connection.is_connected():
        print("成功连接到数据库")
        cursor = connection.cursor(dictionary=True)
        
        # 执行查询
        query = f"SELECT name  FROM stock"  # 替换为你的查询语句
        cursor.execute(query)
        
        # 获取结果
        result = cursor.fetchall()
        for item in result:
            stock_name_array.append(item["name"])
except Error as e:
    print(f"连接数据库时发生错误: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("数据库连接已关闭")
       
        
from fuzzywuzzy import fuzz, process

def is_stock_name_fuzzy_ratio(input_name, stock_names, threshold=80):
    """
    使用模糊比率判斷股票名稱是否匹配。

    :param input_name: 輸入的字串
    :param stock_names: 股票名稱列表
    :param threshold: 匹配比例的閾值
    :return: 匹配的股票名稱（若存在），否則返回 None
    """
    best_match = process.extractOne(input_name, stock_names)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return None


if result:
    print(f"輸入的字串匹配了股票名稱: {result}")
else:
    print("輸入的字串未匹配任何股票名稱")

        
def read_srt_file(file_path):
    """
    讀取 .srt 檔案並解析成結構化資料。
    
    :param file_path: .srt 檔案路徑
    :return: 字幕列表，每個元素為字典 {'index': 索引, 'timestamp': 時間戳, 'text': 字幕文本}
    """
    subtitles = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 分割每一段字幕
    segments = content.strip().split("\n\n")
    text = ""
    for segment in segments:
        lines = segment.split("\n")
        if len(lines) >= 3:
            subtitle = {
                'index': lines[0],  # 字幕索引
                'timestamp': lines[1],  # 時間戳
                'text': "\n".join(lines[2:])  # 字幕文本（可能多行）
            }
            text += "\n".join(lines[2:]) + "\n"
            subtitles.append(subtitle)
    return text,subtitles

def is_stock_name_fuzzy_ratio(input_name, stock_names, threshold=80):
    """
    使用模糊比率判斷股票名稱是否匹配。

    :param input_name: 輸入的字串
    :param stock_names: 股票名稱列表
    :param threshold: 匹配比例的閾值
    :return: 匹配的股票名稱（若存在），否則返回 None
    """
    best_match = process.extractOne(input_name, stock_names)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return None

all_text,subtitles = read_srt_file("test_錢線百分百_翻譯.srt")

test_name = "派了連發科派了台打電"

from pycorrector import Corrector
m=Corrector()
corrected_sent = m.correct(test_name)
print(corrected_sent)
# 測試
result = is_stock_name_fuzzy_ratio(test_name, stock_name_array)
