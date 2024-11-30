# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 15:56:46 2024

@author: peter
"""

file_path = "example.srt"

# 要写入 .str 文件的内容
srt_content = """1
00:00:01,000 --> 00:00:04,000
您好，這是一個範例 .srt 檔案。

2
00:00:05,000 --> 00:00:08,000
它包含一些文字行。

3
00:00:09,000 --> 00:00:12,000
敏捷的棕色狐狸跳過了那隻懶狗。

4
00:00:13,000 --> 00:00:16,000
關鍵字：範例、測是、測試中、測是中、測是中1

5
00:00:17,000 --> 00:00:20,000
文件結束。
"""

# 将内容写入 .str 文件
with open(file_path, "w", encoding="utf-8") as file:
    file.write(srt_content)

print(f"成功生成 .srt 文件: {file_path}")

file_path = "20241122_155546_原文.srt"  # 替换为您的 .str 文件路径
file_path = "C:\\Users\\peter\\Desktop\\20241127_110348WIZ KHALIFA (FEAT. CHARLIE PUTH) -  See You Again 當我們再相見 (華納official 高畫質 HD 官方完整版MV)_480p_翻譯.srt"  # 替换为您的 .str 文件路径
# 读取文件内容
try:
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    print("文件内容：")
    print(file_content)
except FileNotFoundError:
    print(f"文件 {file_path} 不存在！")