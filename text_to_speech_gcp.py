# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 11:45:05 2024

@author: peter
"""

from typing import Sequence

import google.cloud.texttospeech as tts


def unique_languages_from_voices(voices: Sequence[tts.Voice]):
    language_set = set()
    for voice in voices:
        for language_code in voice.language_codes:
            language_set.add(language_code)
    return language_set


def list_languages():
    client = tts.TextToSpeechClient()
    response = client.list_voices()
    languages = unique_languages_from_voices(response.voices)

    print(f" Languages: {len(languages)} ".center(60, "-"))
    for i, language in enumerate(sorted(languages)):
        print(f"{language:>10}", end="\n" if i % 5 == 4 else "")
        
import google.cloud.texttospeech as tts
language_code = "cmn-TW"
def list_voices(language_code=None):
    client = tts.TextToSpeechClient()
    response = client.list_voices(language_code=language_code)
    voices = sorted(response.voices, key=lambda voice: voice.name)

    print(f" Voices: {len(voices)} ".center(60, "-"))
    for voice in voices:
        languages = ", ".join(voice.language_codes)
        name = voice.name
        gender = tts.SsmlVoiceGender(voice.ssml_gender).name
        rate = voice.natural_sample_rate_hertz
        print(f"{languages:<8} | {name:<24} | {gender:<8} | {rate:,} Hz")

list_voices(language_code)

from google.cloud import texttospeech
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "F:\cert\imgsortable-9c8c5ba46036.json"

def google_tts_speech(text,output_file, language="cmn-TW"):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        # name="cmn-TW-Standard-A"  # 可替换为其他声音引擎名称
        # name="cmn-TW-Standard-B"
        # name="cmn-TW-Standard-C"
        # name="cmn-TW-Wavenet-A"
        # name="cmn-TW-Wavenet-B"
        name="cmn-TW-Wavenet-C"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(output_file, "wb") as out:
        out.write(response.audio_content)

    print(f"Audio content written to file {output_file}")

# google_tts_speech("台積電", "cmn-TW")

def get_characters_count(s):
    # 繁体字等中文字符：每个字符视为 3 个字节
    # 英文字符：每个字符视为 1 个字节
    return sum(3 if '\u4e00' <= c <= '\u9fff' else 1 for c in s)

folder = "股票語音-google-cloud-Wavenet-C"
for stock in new_stock_array:
    new_stock = stock.replace("*","")
    output_file = f"{folder}/{new_stock}.wav"
    google_tts_speech(new_stock,output_file, language="cmn-TW")




    # total_characters += get_characters_count(new_stock)
# print(f"總共字串字符數：{total_characters}")

