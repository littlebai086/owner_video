# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 12:03:58 2024

@author: peter
"""

# srt檔案內容批次翻譯

from googletrans import Translator

# 示例函数：翻译每 30 行
def translate_srt(file_path):
    translator = Translator()
    
    # 打开 SRT 文件并读取所有行
    with open(file_path, 'r', encoding='utf-8') as file:
        srt_lines = file.readlines()

    # 存储翻译后的 SRT 内容
    translated_srt = []
    
    # 原本文字
    oringinal_srts = []
    new_translated_srt = []
    # 每 30 行翻译一次
    for i in range(0, len(srt_lines), 4):  # 每次处理3行（编号、时间戳、字幕）
        subtitle_lines = srt_lines[i:i+4]  # 获取当前字幕的3行（编号、时间、字幕文本）
        
        subtitle_text = subtitle_lines[2]
        oringinal_srts.append(subtitle_text)
    len(oringinal_srts)
    for i in range(0, len(oringinal_srts), 300):  # 每次处理3行（编号、时间戳、字幕）
        part_srts = oringinal_srts[i:i+300]  # 获取当前字幕的3行（编号、时间、字幕文本）
        merged_subtitles = '\n\n'.join(part_srts)
        translated_text = translator.translate(merged_subtitles, src='auto', dest='zh-TW').text
        
        new_part_srts = translated_text.split('\n\n\n')
        new_translated_srt[i:i+300] = new_part_srts
    j=0
    for i in range(0, len(srt_lines), 4):  # 每次处理3行（编号、时间戳、字幕）
        subtitle_lines = srt_lines[i:i+4]  # 获取当前字幕的3行（编号、时间、字幕文本）
        
        srt_lines[i+2] = new_translated_srt[j]+"\n"
        j = j+1

    

        # 保存翻译后的 SRT 文件
    with open('translated_output1.srt', 'w', encoding='utf-8') as output_file:
        output_file.writelines(srt_lines)

    print("翻译完成并保存为 translated_output.srt")

file_path="20241210_112915【錢線百分百】20241209完整版(上集)《台積除息日.台股攻高時？ 蹲低股上演逆襲？ 財報進入空窗期 IC設計迎吹牛行情!》│非凡財經新聞│_翻譯.srt"
# 调用函数进行翻译
translate_srt("20241210_112915【錢線百分百】20241209完整版(上集)《台積除息日.台股攻高時？ 蹲低股上演逆襲？ 財報進入空窗期 IC設計迎吹牛行情!》│非凡財經新聞│_翻譯.srt")
