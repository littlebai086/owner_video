# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 15:52:47 2024

@author: peter
"""
import jieba
from difflib import SequenceMatcher
from pypinyin import lazy_pinyin
import numpy as np
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
        
# 股票名稱列表
stock_list = ["聯發科", "台達電"]

# 加載自定義詞典
for stock in stock_list:
    jieba.add_word(stock)

# 拼音轉換函數
def get_pinyin(text):
    return ''.join(lazy_pinyin(text))

# 相似度計算函數
def calculate_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 校正分詞結果
stock_list = stock_name_array
def correct_words(words, stock_list,skip_word_array):
    corrected_words = []
    best_matchs = []
    highest_scores = []
    combine_str_boolean = False
    max_combine_length = 2
    last_combined_index = 0
    for i in range(len(words)):
        find_match_boolean = False
        print("combine_str_boolean",combine_str_boolean)
        print("combine_比較",len(words[i]))
        print("combine_比較1",last_combined_index+1)
        if combine_str_boolean:
            if len(words[i])>last_combined_index+1:
                combined_word = words[i][last_combined_index+1:]
                print(words[i][last_combined_index+1:])
                print(words[i:])
                new_combine_word = ''.join(words[i:])
                new_sentence = new_combine_word[last_combined_index+1:]
                print("new_combine_word",new_combine_word)
                print("new_sentence",new_sentence)
                new_words = jieba.lcut(new_sentence)
    
                combine_best_matchs, combine_highest_scores, combine_corrected_words = correct_words(new_words, stock_list, skip_word_array)
                new_best_matchs = np.concatenate((best_matchs,combine_best_matchs))
                new_highest_scores = np.concatenate((highest_scores,combine_highest_scores))
                new_corrected_words = np.concatenate((corrected_words,combine_corrected_words))
                find_match_boolean = True
                return new_best_matchs, new_highest_scores, new_corrected_words
                continue  # 繼續處理下一個詞組
            else:
                continue
        else:
            combined_word = words[i]
        
        combine_str_boolean = False
        best_match = None
        highest_score = 0
        
        if words[i] in skip_word_array:
            corrected_words.append(words[i])
            best_matchs.append(best_match)
            highest_scores.append(highest_score)
            continue
        print("原本的詞:", combined_word)
        words_move_index=0
        words_move_index_2=0
        
        for j in range(0,max_combine_length):
            if len(words)-1 <= i:
                break
            # if j==0:
            #     match, score = find_best_match(combined_word, stock_list)
            #     best_matchs.append(match)
            #     highest_scores.append(score)
            #     find_match_boolean = True
            #     if score >=0.8:
            #         corrected_words.append(match)
            #         break
            #     else:
            #         corrected_words.append(words[i])
            print("start")
            # print("j",j)
            # if current_combine_length>max_combine_length:
            #     break
            # print(i)
            # print(len(words))
            combine_boolean = False
            if len(words)>(i+words_move_index):
                if len(words[i+words_move_index])>(words_move_index_2+1):
                    # print("第二次if",True)
                    # print(words[i+words_move_index])
                    # print("尚未加words_move_index",words_move_index)
                    # print("第二次判斷",words_move_index_2+1)
                    if j>0:
                        words_move_index_2 += 1
                    else:
                        words_move_index = 1
                        # if len(words)>=i+words_move_index:
                        #     break
                            
                    combine_boolean = True
                else:
                    # print("第二次if",False)
                    print(len(words[i:]))
                    print(words_move_index+1)
                    if len(words[i:]) > words_move_index+1:
                        words_move_index += 1
                        words_move_index_2 = 0
                        combine_boolean = True
                
                        
                print("words_move_index",words_move_index)
                print("words_move_index_2",words_move_index_2)
                if combine_boolean:
                    combined_word += words[i+words_move_index][words_move_index_2]    
                else:
                    break
                
                print("嘗試合併的詞:", combined_word)
                
                match, score = find_best_match(combined_word, stock_list)
                # print(score)
                # print(highest_score)
                if score > highest_score:  # 更新最佳匹配
                    best_match = match
                    highest_score = score
        
                # 如果分數超過閾值，立即選擇最佳結果
                if highest_score >= 0.8:
                    combine_str_boolean = True
                    last_combined_index = words_move_index_2
                    print(f"合併成功: {combined_word} → {best_match} (分數: {highest_score})")
                    corrected_words.append(best_match)
                    best_matchs.append(best_match)
                    highest_scores.append(highest_score)
                    find_match_boolean = True
                    break

                print("end")
                    # print("長度words i+current_combine_length:",len(words[i+current_combine_index]))
                    # print("j:",j)
                    # match, score = find_best_match(combined_word, stock_list)
            else:
                break

        # 如果沒有達到閾值，僅加入當前詞
        if not find_match_boolean:
            match, score = find_best_match(combined_word, stock_list)
            if score >=0.8:
                corrected_words.append(match)
            else:
                corrected_words.append(words[i])
            best_matchs.append(match)
            highest_scores.append(score)
    
    
    return best_matchs,highest_scores,corrected_words
# def correct_words(words, stock_list,skip_word_array):
#     corrected_words = []
#     best_matchs = []
#     highest_scores = []
#     skip_next = False
#     skip_count = 0
#     combine_str_boolean = False
#     max_combine_length = 2
#     last_combined_index = 0
#     for i in range(len(words)):
#         # if skip_count > 0:
#         #     skip_count -= 1
#         #     continue
#         if skip_next:
#             skip_next = False
#             continue
#         print("combine_str_boolean",combine_str_boolean)
#         print("combine_比較",len(words[i])>last_combined_index+1)
#         if combine_str_boolean:
#             if len(words[i])>last_combined_index+1:
#                 combined_word = words[i][last_combined_index+1:]
#                 print(words[i][last_combined_index+1:])
#                 print(words[i:])
#                 new_combine_word = ''.join(words[i:])
#                 new_sentence = new_combine_word[last_combined_index+1:]
#                 print("new_combine_word",new_combine_word)
#                 print("new_sentence",new_sentence)
#                 new_words = jieba.lcut(new_sentence)
    
#                 combine_best_matchs, combine_highest_scores, combine_corrected_words = correct_words(new_words, stock_list, skip_word_array)
#                 new_best_matchs = np.concatenate((best_matchs,combine_best_matchs))
#                 new_highest_scores = np.concatenate((highest_scores,combine_highest_scores))
#                 new_corrected_words = np.concatenate((corrected_words,combine_corrected_words))
#                 return new_best_matchs, new_highest_scores, new_corrected_words
#                 continue  # 繼續處理下一個詞組
#             else:
#                 continue
#         else:
#             combined_word = words[i]
        
#         combine_str_boolean = False
#         best_match = None
#         highest_score = 0
#         current_combine_length = 0
        
#         if words[i] in skip_word_array:
#             corrected_words.append(combined_word)
#             best_matchs.append(best_match)
#             highest_scores.append(highest_score)
#             continue
#         print("原本的詞:", combined_word)
#         for j in range(1,max_combine_length+1):
            
#             current_combine_length+=1
#             last_combined_index = index = j-1
#             if current_combine_length>max_combine_length:
#                 break
#             print(i)
#             print(len(words))
#             print(i+current_combine_length)
#             current_combine_index = current_combine_length
#             if len(words)>i+current_combine_index:
#                 if len(words[i+current_combine_index])>=j:
#                     combined_word += words[i+current_combine_index][index]
#                     print("嘗試合併的詞:", combined_word)
                
#                     match, score = find_best_match(combined_word, stock_list)
#                     print(score)
#                     if score > highest_score:  # 更新最佳匹配
#                         best_match = match
#                         highest_score = score
        
#                     # 如果分數超過閾值，立即選擇最佳結果
#                     if highest_score >= 0.8:
#                         combine_str_boolean = True
#                         print(f"合併成功: {combined_word} → {best_match} (分數: {highest_score})")
#                         corrected_words.append(best_match)
#                         best_matchs.append(best_match)
#                         highest_scores.append(highest_score)
                        
#                         # skip_count = j  # 跳過已合併的詞
#                         break
#             else:
#                 match, score = find_best_match(combined_word, stock_list)
#                 print("最後的字詞",combined_word)
#                 if score >= 0.8:
#                     corrected_words.append(match)
#                     best_matchs.append(match)
#                     highest_scores.append(score)
                    
#             # else:
#             #     break

#         # 如果沒有達到閾值，僅加入當前詞
#         if score<0.8:
#             corrected_words.append(words[i])
#             best_matchs.append(match)
#             highest_scores.append(score)
    
    
#     return best_matchs,highest_scores,corrected_words
        # for j in range(1, max_combine_length + 1):
        #     if i + j < len(words):
        #         combined_word += words[i + j][0]
        #         print("嘗試合併的詞:", combined_word)
        
        #         match, score = find_best_match(combined_word, stock_list)
        #         if score > highest_score:  # 更新最佳匹配
        #             best_match = match
        #             highest_score = score
        
        #         # 如果分數超過閾值，立即選擇最佳結果
        #         if highest_score > 0.8:
        #             print(f"合併成功: {combined_word} → {best_match} (分數: {highest_score})")
        #             corrected_words.append(best_match)
        #             best_matchs.append(best_match)
        #             highest_scores.append(highest_score)
        #             skip_count = j  # 跳過已合併的詞
        #             break
        #     else:
        #         break
    
        # 如果當前詞在跳過陣列中，直接加入結果並跳過計算
        # if words[i] in skip_word_array:
        #     corrected_words.append(words[i])
        #     best_matchs.append(best_match)
        #     highest_scores.append(highest_score)
        #     continue
        # # 嘗試合併當前詞與下一個詞
        # if i < len(words) - 1:
        #     combined_word = words[i] + words[i + 1]
        #     print("嘗試合併的詞",combined_word)
        #     best_match, highest_score = find_best_match(combined_word, stock_list)
        #     # print(best_match)
        #     # print(highest_score)
        #     if highest_score > 0.8:  # 閾值可調
        #         print("合併成功高於0.8")
        #         corrected_words.append(best_match)
        #         skip_next = True
        #         continue
        #     print("合併失敗低於0.8")
        
        # # 單詞匹配
        # best_match, highest_score = find_best_match(words[i], stock_list)
        # if highest_score > 0.8:
        #     corrected_words.append(best_match)
        # else:
        #     corrected_words.append(words[i])
    # return best_matchs,highest_scores,corrected_words

    # for word in words:
    #     best_match, highest_score = find_best_match(word, stock_list)
    #     print(word)
    #     print(best_match)
    #     print(highest_score)
    #     # 如果相似度高於某個閾值，替換為正確名稱
    #     if highest_score > 0.8:  # 可調整閾值
    #         corrected_words.append(best_match)
    #     else:
    #         corrected_words.append(word)
    # return corrected_words

# 找到最佳匹配
def find_best_match(input_name, stock_list):
    input_pinyin = get_pinyin(input_name)
    best_match = None
    highest_score = 0
    if len(input_name) == 1:
        return None, 0  # 沒有匹配結果，分數為 0
    for stock in stock_list:
        stock_pinyin = get_pinyin(stock)
        # 拼音相似度
        pinyin_similarity = calculate_similarity(input_pinyin, stock_pinyin)
        # 字符相似度
        text_similarity = calculate_similarity(input_name, stock)
        # 綜合相似度

        # total_score = 0.8 * pinyin_similarity + 0.2 * text_similarity
        # 原本的
        total_score = 0.6 * pinyin_similarity + 0.4 * text_similarity

        if total_score > highest_score:
            highest_score = total_score
            best_match = stock
    
    # if len(best_match)!=len(input_name):
    #     print("best_match",best_match)
    #     print("input_name",input_name)
    #     return None,0
    return best_match, highest_score

       
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

all_text,subtitles = read_srt_file("test_錢線百分百_翻譯 - 複製1.srt")

skip_word_array=[
    "妳","你","我","他",
    "妳們","你們","我們","他們",
    "錯","不錯",
    "現在","今天",
    "看","觀眾","上次","的",
    "等","都","又","喝","就","再","以外",
    "美國",
    "這","那",
    "這個","那個",
    "這樣","那樣",
    "不",
    "可以","不可以",
    "對","不對",
    "會","不會",
    "好","不好",
    "謝謝",
    "比較",
    "但是",
]
new_subtitles_result = []
for subtitle in subtitles:
    print(subtitle["text"])
    # 測試句子
    # sentence = "派了聯伐科派了台妲電"
    sentence = subtitle["text"]
    words = jieba.lcut(sentence)
    print("分詞結果:", words)

    # 校正後的結果
    best_matchs,highest_scores,corrected_words = correct_words(words, stock_name_array,skip_word_array)
    print("校正結果:", corrected_words)
    
    result_dict = {
        "timestamp": subtitle["timestamp"],
        "words" : words,
        "best_matchs" : best_matchs,
        "highest_scores" : highest_scores,
        "corrected_words" : corrected_words,
    }
    
    new_subtitles_result.append(result_dict)
    
for new_subtitle in new_subtitles_result:
    print("=====================================")
    print("words:", new_subtitle["words"])
    print("校正結果:", new_subtitle["corrected_words"])
    print("原本字詞  ",''.join(new_subtitle["words"]))
    print("校正完字詞",''.join(new_subtitle["corrected_words"]))
    print("best_matchs:", new_subtitle["best_matchs"])
    print("highest_scores:", new_subtitle["highest_scores"])
    print("=====================================")
    
input_name = "台基電扣瓦斯雜的產能了"
input_name = "0056新增了楊明"
input_name = "那我們來看一下台基電"
input_name = "現在連發科已經定好了"
input_name = "代表的台機電不要給你先用"
input_name = "我連連發科所就帶來了"
input_name = "派了連發科派了台打電"
sentence = input_name
file_path = "./userdict.txt"
jieba.load_userdict (file_path)
words = jieba.lcut(sentence)
print("分詞結果:", words)

# 校正後的結果
best_matchs,highest_scores,corrected_words = correct_words(words, stock_name_array,skip_word_array)
print("words:", words)
print("校正結果:", corrected_words)
print("原本字詞  ",''.join(words))
print("校正完字詞",''.join(corrected_words))
print("best_matchs:", best_matchs)
print("highest_scores:", highest_scores)
