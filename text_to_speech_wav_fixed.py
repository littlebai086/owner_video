# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 15:10:18 2024

@author: peter
"""

# wav檔案修正

import mysql.connector
from mysql.connector import Error
# from fuzzywuzzy import fuzz, process
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
        query = f"SELECT name  FROM stock WHERE type = '上市'"  # 替换为你的查询语句
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
        

import re


new_stock_array = []
filtered_stocks = []
for stock in stock_name_array:
    stock = stock.replace("*","")
    if "原簡稱" in stock:
        cleaned_name = re.sub(r"\(.*?\)", "", stock).strip()  # 移除括號及內容，並去掉多餘的空格
        filtered_stocks.append(cleaned_name)
        new_stock_array.append(cleaned_name)
    else:
        new_stock_array.append(stock)
        
import subprocess
import os
def convert_audio(input_file, output_file):
    try:
        command = [
            'ffmpeg',
            '-i', input_file,
            '-c:v', 'copy',
            '-c:a', 'pcm_s16le',
            output_file
        ]
        subprocess.run(command, check=True)
        print(f"已成功轉換檔案: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 錯誤: {e}")

# 使用示例
input_folder = "股票語音-google-cloud-Wavenet-C"
output_folder = "股票語音資料-google-cloud-Wavenet-C"
# new_stock = "元大中型100"
for stock in new_stock_array:
    new_stock = stock.replace("*","")
    input_file = f"{input_folder}/{new_stock}.wav"
    if os.path.exists(input_file):
        output_file = f"{output_folder}/{new_stock}_fixed.wav"
        if not os.path.exists(output_file):
            convert_audio(input_file, output_file)
    else:
        print(f"檔案 {input_file} 不存在")
        
        

def get_audio_duration(audio_file):
    """
    獲取音訊檔案的時長（秒）。
    :param audio_file: str, 音訊檔案名稱
    :return: float, 音訊時長
    """
    import subprocess
    try:
        result = subprocess.run(
            ["ffprobe", "-i", audio_file, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"無法獲取音訊時長: {audio_file}, 錯誤: {e}")
        return 0.0
    
def generate_srt(wav_file, output_file,stock):
    with open(output_file, 'w', encoding='utf-8') as f:
        end_time = get_audio_duration(wav_file)
        f.write("1\n")
        # 写入时间戳
        start_time = "00:00:00"
        end_time = format_time(end_time)
        f.write(f"{start_time} --> {end_time}\n")
        # 写入字幕内容
        f.write(f"{stock}\n\n")



def format_time(seconds):
    # 将秒数四舍五入到最近的毫秒，避免误差
    milliseconds = round(seconds * 1000)  # 转换为毫秒并四舍五入
    hours = milliseconds // (3600 * 1000)
    minutes = (milliseconds % (3600 * 1000)) // (60 * 1000)
    seconds = (milliseconds % (60 * 1000)) // 1000
    milliseconds = milliseconds % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

for stock in new_stock_array:
    new_stock = stock.replace("*","")
    wav_file = f"{output_folder}/{new_stock}_fixed.wav"
    output_file = f"{output_folder}/{new_stock}.srt"
    generate_srt(wav_file, output_file,stock)
    print(f"{output_file} srt生成完成")
    
