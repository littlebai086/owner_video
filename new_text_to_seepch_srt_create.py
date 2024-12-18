# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 18:13:05 2024

@author: peter
"""

def split_srt_to_array(srt_file):
    with open(srt_file, "r", encoding="utf-8") as f:
        lines = f.readlines()  # 读取所有行
    
    # 去掉每行的换行符
    lines = [line.strip() for line in lines]  # 去掉空行和多余的换行
    
    # 每 4 行切割成子数组
    result = []
    for i in range(0, len(lines), 4):
        index = lines[i]          # 第一行为索引
        time = lines[i + 1]       # 第二行为时间
        text = lines[i + 2]       # 第三行为文本
        data_dict = {
            "index" : index,
            "time" : time,
            "text" : text,
        }
        result.append(data_dict)  # 将索引、时间和文本存入子数组
    
    return result

# 示例使用
srt_file = "error_srt_text_right_time.srt"
srt_array = split_srt_to_array(srt_file)

len(new_stock_array)
# 输出结果
for idx,segment in enumerate(srt_array):
    srt_array[idx]["text_1"] = new_stock_array[idx]
    print(segment)
    print("---")

    
    output_file = "merged_stock_with_silence_right.srt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, array in enumerate(srt_array, start=1):
            index = array["index"]
            time = array["time"]
            text = array["text_1"]
            # 写入序号
            f.write(f"{index}\n")
            # 写入时间戳
            f.write(f"{time}\n")
            # 写入字幕内容
            f.write(f"{text}\n\n")