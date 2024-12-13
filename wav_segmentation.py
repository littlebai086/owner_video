# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 15:36:48 2024

@author: peter
"""

def time_to_milliseconds(time_str):
    # 將時間字串解析為毫秒
    h, m, s = time_str.split(":")
    s, ms = map(int, s.split(","))
    return (int(h) * 3600 + int(m) * 60 + s) * 1000 + ms

# 示例字幕時間
start_time = "00:01:16,640"
end_time = "00:01:18,920"

# 計算毫秒
start_ms = time_to_milliseconds(start_time)
end_ms = time_to_milliseconds(end_time)

print(f"Start time in milliseconds: {start_ms}")
print(f"End time in milliseconds: {end_ms}")

from pydub import AudioSegment

# 加载音频文件
audio = AudioSegment.from_wav("wav/勞保_all.wav")

wav_data = [
    {
        "start_time"  : 6000,
        "end_time"  : 11160,
        "wav_file" : "part_1.wav",
        "text" : "之前我們討論過這個案例 在桃園有一個男子 他繳了大半輩子老寶費"
    },
    {
        "start_time"  : 13920,
        "end_time"  : 16360,
        "wav_file" : "part_2.wav",
        "text" : "後來 家屬要請你老寶年輕"
    },
    {
        "start_time"  : 22400,
        "end_time"  : 25920,
        "wav_file" : "part_3.wav",
        "text" : "其實他周邊的朋友也有人繳了大半輩子老寶費"
    },
    {
        "start_time"  : 35320,
        "end_time"  : 38560,
        "wav_file" : "part_4.wav",
        "text" : "或者是在過去付了大半輩子老寶金"
    },
    {
        "start_time"  : 50160,
        "end_time"  : 52640,
        "wav_file" : "part_5.wav",
        "text" : "然後順便就退了這個老寶"
    },
    {
        "start_time"  : 56240,
        "end_time"  : 60000,
        "wav_file" : "part_6.wav",
        "text" : "其實用最高級距去投保這個老寶"
    },
    {
        "start_time"  : 76640,
        "end_time"  : 78920,
        "wav_file" : "part_7.wav",
        "text" : "但是最後他去申請老寶局的時候"
    },
]

for data in wav_data:
    start_time = data["start_time"]
    end_time = data["end_time"]
    wav_file = data["wav_file"]
    extracted_audio = audio[start_time:end_time]
    extracted_audio.export("wav/"+wav_file, format="wav")
    print(f"部分音频已保存到 wav/{wav_file}")
# 提取部分音频（单位是毫秒）
# start_time = 5000  # 起始时间（毫秒），这里是5秒
# end_time = 15000   # 结束时间（毫秒），这里是15秒
# extracted_audio = audio[start_time:end_time]

# # 保存结果到新文件
# extracted_audio.export("output.wav", format="wav")

# print("部分音频已保存到 output.wav")
