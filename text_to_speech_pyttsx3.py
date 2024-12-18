# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 11:25:02 2024

@author: peter
"""

        

import pyttsx3


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
output_file = "output.wav"
engine.save_to_file("台積電", output_file)

# 运行并生成文件
engine.runAndWait()