# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 15:30:35 2024

@author: peter
"""

# 合併語音檔案

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
    else:
        new_stock_array.append(stock)
        
import os

def create_silence(output_file, duration=1):
    """
    生成指定長度的靜音檔案。
    :param output_file: str, 靜音檔案名稱
    :param duration: int, 靜音的秒數
    """
    command = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", f"anullsrc=channel_layout=mono:sample_rate=44100",
        "-t", str(duration),
        output_file
    ]
    result = os.system(' '.join(command))
    if result == 0:
        print(f"靜音檔案已生成: {output_file}")
    else:
        print("靜音檔案生成失敗。")

# def format_time(seconds):
#     # 将秒数转换为 SRT 的时间格式
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds = seconds % 60
#     milliseconds = int((seconds - int(seconds)) * 1000)
#     return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

def format_time(seconds):
    # 将秒数四舍五入到最近的毫秒，避免误差
    milliseconds = round(seconds * 1000)  # 转换为毫秒并四舍五入
    hours = milliseconds // (3600 * 1000)
    minutes = (milliseconds % (3600 * 1000)) // (60 * 1000)
    seconds = (milliseconds % (60 * 1000)) // 1000
    milliseconds = milliseconds % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
        
def generate_srt(subtitles, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, subtitle in enumerate(subtitles, start=1):
            # 写入序号
            f.write(f"{idx}\n")
            # 写入时间戳
            start_time = subtitle['start_time']
            end_time = subtitle['end_time']
            f.write(f"{start_time} --> {end_time}\n")
            # 写入字幕内容
            text = subtitle.get("text", "")
            f.write(f"{text}\n\n")

def merge_srt_subtitle(file,stock_array):
    subtitle = []
    total_time = 0.0
    for stock in stock_array:
        print(file+stock+"_fixed.wav")
        duration = get_audio_duration(file+stock+"_fixed.wav")
        
        data_dict = {
            "start_time" : format_time(total_time),
            "end_time" : format_time(total_time+duration+1),
            "text" : stock
        }
        total_time += duration + 1
        subtitle.append(data_dict)
    return subtitle

# def merge_srt_files(stock_array, output_srt, silence_duration=1):
#     """
#     合併多個 .srt 檔案，並根據靜音間隔調整時間戳。
#     :param srt_files: list, 要合併的 SRT 檔案列表
#     :param output_srt: str, 合併後的 SRT 檔案名稱
#     :param silence_duration: int, 靜音的秒數
#     """
#     total_time = 0.0  # 累積時間
#     with open(output_srt, "w", encoding="utf-8") as output:
#         subtitle_index = 1
#         for srt_file in srt_files:
#             if not os.path.exists(srt_file):
#                 print(f"SRT 檔案不存在: {srt_file}")
#                 continue

#             with open(srt_file, "r", encoding="utf-8") as f:
#                 for stock in stock_array:
#                     duration = get_audio_duration(stock+"_fixed.wav")
                    
#                     # 写入序号
#                     f.write(f"{subtitle_index}\n")
#                     # 写入时间戳
#                     start_time = format_time(subtitle['start'])
#                     end_time = format_time(subtitle['end'])
#                     f.write(f"{start_time} --> {end_time}\n")
#                     # 写入字幕内容
#                     text = subtitle.get(text_field, "")
#                     f.write(f"{text}\n\n")
                    
#                     subtitle_index +=1
#                         output.write(line)

#             # 累加音訊時長與靜音間隔
#             audio_duration = get_audio_duration(srt_file.replace(".srt", ".wav"))
#             total_time += audio_duration + silence_duration

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


def convert_to_seconds(srt_time):
    """
    將 SRT 時間格式轉換為秒數。
    支持格式: 
    - "00:01:23,456" (標準格式)
    - "00:01:23.456" (小數點格式)
    - "00:01:23" (無毫秒)
    :param srt_time: str, SRT 時間格式
    :return: float, 時間（秒）
    """
    hours, minutes, seconds = srt_time.strip().split(":")
    if "," in seconds:
        seconds, milliseconds = map(int, seconds.split(","))
        return int(hours) * 3600 + int(minutes) * 60 + seconds + milliseconds / 1000.0
    elif "." in seconds:
        seconds, milliseconds = map(float, seconds.split("."))
        return int(hours) * 3600 + int(minutes) * 60 + seconds + milliseconds / 1000.0
    else:
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

def convert_to_srt_time(seconds):
    """
    將秒數轉換為 SRT 時間格式。
    :param seconds: float, 時間（秒）
    :return: str, SRT 時間格式 (e.g., "00:01:23,456")
    """
    milliseconds = int((seconds % 1) * 1000)
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def merge_wav_with_silence(input_files, output_file, silence_duration=1):
    """
    將多個 .wav 檔案合併，並在每個音訊之間加入靜音。
    :param input_files: list, 要合併的 .wav 檔案列表
    :param output_file: str, 合併後的 .wav 檔案名稱
    :param silence_duration: int, 靜音的秒數
    """
    # 確保檔案存在
    valid_files = [f for f in input_files if os.path.exists(f)]
    if not valid_files:
        print("沒有有效的 .wav 檔案可用於合併。")
        return

    # 建立靜音檔案
    silence_file = "silence.wav"
    create_silence(silence_file, duration=silence_duration)

    # 建立合併清單檔案
    list_file = "file_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for wav_file in valid_files:
            f.write(f"file '{wav_file}'\n")
            f.write(f"file '{silence_file}'\n")  # 在每個音檔後加入靜音

    # 使用 ffmpeg 合併檔案
    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_file
    ]
    result = os.system(' '.join(command))

    # 清理暫存檔案
    os.remove(list_file)
    if os.path.exists(silence_file):
        os.remove(silence_file)

    if result == 0:
        print(f"檔案已成功合併到: {output_file}")
    else:
        print("合併檔案時發生錯誤。")


# 使用示例
# new_stock_array = ["台積電*", "元大台灣50*", "佳龍*", "世紀鋼*"]  # 假設這是股票陣列
input_files = [f"股票語音/{stock.replace('*', '')}_fixed.wav" for stock in new_stock_array]
srt_files = [f"{stock.replace('*', '')}" for stock in new_stock_array]
output_file = "股票語音/merged_stock_with_silence.wav"
output_srt = "股票語音/merged_stock_with_silence.srt"

stock_subtittle = merge_srt_subtitle("股票語音/",new_stock_array)
generate_srt(stock_subtittle, "股票語音/merged_stock_with_silence.srt")
merge_wav_with_silence(input_files, output_file, silence_duration=0.5)
merge_srt_files(srt_files, output_srt, silence_duration=1)
