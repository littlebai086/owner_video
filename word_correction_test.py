# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 15:46:52 2024

@author: peter
"""

import jieba
from pypinyin import pinyin, Style
from difflib import SequenceMatcher

# 股票列表
stock_names = ["聯發科", "台達電"]

# 转换拼音
def get_pinyin(word):
    return ''.join([item[0] for item in pinyin(word, style=Style.NORMAL)])

# 计算相似度
def calculate_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 匹配单个词
def match_word_to_stock(word, stock_list):
    input_pinyin = get_pinyin(word)
    best_match = None
    highest_score = 0

    for stock in stock_list:
        stock_pinyin = get_pinyin(stock)
        
        # 拼音相似度
        pinyin_similarity = calculate_similarity(input_pinyin, stock_pinyin)
        
        # 字符相似度
        text_similarity = calculate_similarity(word, stock)
        
        # 综合相似度
        total_score = 0.6 * pinyin_similarity + 0.4 * text_similarity
        
        if total_score > highest_score:
            highest_score = total_score
            best_match = stock

    return best_match, highest_score

# 从句子中匹配多个股票名称
def find_stocks_in_sentence(sentence, stock_list, threshold=0.7):
    # 分词
    words = jieba.lcut(sentence)
    results = []

    for word in words:
        match, score = match_word_to_stock(word, stock_list)
        if score >= threshold:  # 只保留匹配度高的结果
            results.append((word, match, score))

    return results

# 测试输入
sentence = input_stock_name = "派了連發科派了台打電"  # 输入错误的股票名称
matches  = find_stocks_in_sentence(input_stock_name, stock_names)
for word, match, score in matches:
    print(f"输入词: {word}, 匹配股票: {match}, 相似度: {score:.2f}")
