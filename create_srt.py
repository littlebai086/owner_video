# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 15:56:46 2024

@author: peter
"""

file_path = "example.srt"

# 要写入 .str 文件的内容
content = """您好，這是一個範例 .srt 檔案。
它包含一些文字行。
敏捷的棕色狐狸跳過了那隻懶狗。
關鍵字： 範例、測是、測試中、測是中、測是中1
文件結束。"""

# 将内容写入 .str 文件
with open(file_path, "w", encoding="utf-8") as file:
    file.write(content)

print(f"成功生成 .str 文件: {file_path}")

file_path = "example.str"  # 替换为您的 .str 文件路径

# 读取文件内容
try:
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    print("文件内容：")
    print(file_content)
except FileNotFoundError:
    print(f"文件 {file_path} 不存在！")