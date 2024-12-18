# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 10:53:07 2024

@author: peter
"""


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
        
import edge_tts
import asyncio
import re


value_to_find = "矽力*-KY"
new_stock_array = []
filtered_stocks = []
stock_name_array[1002] = stock_name_array[1002].replace("*","")
for stock in stock_name_array:
    stock = stock.replace("*","")
    if "原簡稱" in stock:
        cleaned_name = re.sub(r"\(.*?\)", "", stock).strip()  # 移除括號及內容，並去掉多餘的空格
        filtered_stocks.append(cleaned_name)
        new_stock_array.append(cleaned_name)
    else:
        new_stock_array.append(stock)


len(new_stock_array)
stock_name_array[728:]
try:
    index = new_stock_array.index(value_to_find)
    print(f"'{value_to_find}' 位於索引位置: {index}")
except ValueError:
    print(f"'{value_to_find}' 不在陣列中")
# stock_name_array = ["台積電","台達電"]
# new_stock_array = ["台積電","台達電"]
text = '。'.join(new_stock_array)
text += '。'

async def text_to_speech(text, voice, output_file):
    # 初始化 Edge-TTS 物件
    communicator = edge_tts.Communicate(text=text, voice=voice)
    print(f"正在生成語音: {text}")
    # 保存語音到檔案
    await communicator.save(output_file)
    print(f"語音檔案已儲存為 {output_file}")

# 主程式
async def main(folder,text):
    # 要轉換的文字（繁體中文）
    # text = "台積電。台達電。"
    # 使用的語音模型（繁體中文）
    # voice = "zh-TW-HsiaoYuNeural"  # 女性語音
    # voice = "zh-TW-HsiaoChenNeural"  # 女性語音
    voice = "zh-TW-YunJheNeural"  # 女性語音
    # 輸出的檔案名稱
    # output_file = f"股票語音/stock_all.wav"
    
    output_file = f"{folder}/{text}.wav"
    await text_to_speech(text, voice, output_file)

folder = "股票語音-edge-tts-YunJheNeural"
if __name__ == "__main__":
    try:
        for stock in new_stock_array:
            asyncio.run(main(folder,stock.replace("*","")))
        # asyncio.run(main(text))
    except RuntimeError:  # 如果在 Jupyter Notebook 或其他異步環境中
        import nest_asyncio
        nest_asyncio.apply()
        
# aconda cmd 執行 列出清單 edge-tts --list-voices
import asyncio
from edge_tts import VoicesManager
import nest_asyncio
nest_asyncio.apply()

async def list_voices():
    voices_manager = await VoicesManager.create()
    voices = await voices_manager.get_voice_list()
    for voice in voices:
        print(f"Name: {voice['Name']}, Locale: {voice['Locale']}, Gender: {voice['Gender']}")

asyncio.run(list_voices())




import pyttsx3

def get_available_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    return voices

# 获取所有可用语音
voices = get_available_voices()

for voice in voices:
    print(f"ID: {voice.id}, Name: {voice.name}, Languages: {voice.languages}, Gender: {voice.gender}")
    
def get_chinese_voice(engine):
    """Get a Chinese voice"""
    voices = engine.getProperty("voices")
    for voice in voices:
        if "zh-CN" in voice.languages:
            return voice
        if "Chinese" in voice.name or "Mandarin" in voice.name.title():
            return voice

    raise KeyError(f"No Chinese voice found among {voices}")


engine = pyttsx3.init()

chinese_voice = get_chinese_voice(engine)

engine.setProperty("voice", chinese_voice.id)
# 设置输出为 wav 文件
folder = "股票語音-pyttsx3"
for stock in new_stock_array:
    new_stock = stock.replace("*","")
    # Set output file name dynamically
    output_file = f"{folder}/{new_stock}.wav"
    engine.save_to_file(new_stock, output_file)
    engine.runAndWait()  # Ensure each file is generated before moving to the next
    print(f"生成 {output_file}")

        # asyncio.run(main(text))
# 用於保存字幕內容
# srt_lines = []

# async def text_to_speech_with_metadata(text, voice, output_file, srt_file):
#     global srt_lines
#     # 初始化 Edge-TTS 物件
#     communicator = edge_tts.Communicate(text=text, voice=voice)
#     print(f"正在生成語音: {text}")

#     # 保存語音並生成 Metadata
#     metadata = await communicator.save(output_file, write_to_stdout=False)

#     print(f"語音檔案已儲存為 {output_file}")

#     # 解析 Metadata 生成 SRT 文件
#     for index, item in enumerate(metadata, start=1):
#         if item["type"] != "WordBoundary":
#             continue  # 只處理文字邊界的數據
        
#         # 起始時間與結束時間
#         start_time = item["offset"] / 10000  # 將 100ns 單位轉為秒
#         end_time = start_time + 1.0  # 假設每個單詞播放時間為 1 秒

#         # 將時間轉換為 SRT 格式
#         def format_time(seconds):
#             milliseconds = int((seconds % 1) * 1000)
#             seconds = int(seconds)
#             minutes = seconds // 60
#             hours = minutes // 60
#             minutes = minutes % 60
#             seconds = seconds % 60
#             return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

#         # 添加字幕內容
#         srt_lines.append(f"{index}")
#         srt_lines.append(f"{format_time(start_time)} --> {format_time(end_time)}")
#         srt_lines.append(item["text"])  # 單字內容
#         srt_lines.append("")  # 空行分隔

#     # 保存 SRT 文件
#     with open(srt_file, "w", encoding="utf-8") as f:
#         f.write("\n".join(srt_lines))
#     print(f"字幕檔案已儲存為 {srt_file}")


# 主程式
# async def main(new_stock_array):
#     # 要轉換的文字（繁體中文）
#     text = '。'.join(new_stock_array)
#     text += '。'
#     text = "台積電。台達電。中鋼。"
#     # 使用的語音模型（繁體中文）
#     voice = "zh-TW-HsiaoYuNeural"  # 女性語音
#     # 輸出的語音檔案和 SRT 檔案
#     output_file = "股票語音/stock_all.wav"
#     srt_file = "股票語音/stock_all.srt"

#     await text_to_speech_with_metadata(text, voice, output_file, srt_file)
    
# 檢查是否有事件循環正在運行
# if __name__ == "__main__":
#     try:
#         # for stock in new_stock_array[728:]:
#             # asyncio.run(main(stock))
#         asyncio.run(main(new_stock_array))
#     except RuntimeError:  # 如果在 Jupyter Notebook 或其他異步環境中
#         import nest_asyncio
#         nest_asyncio.apply()
#         # asyncio.run(main(text))
