# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 10:45:51 2024

@author: peter
"""

from pathlib import Path
from openai import OpenAI
client = OpenAI(api_key="")

speech_file_path = "speech.wav"
response = client.audio.speech.create(
model="tts-1",
voice="alloy",
input="台積電",
response_format="wav"
)

response.stream_to_file(speech_file_path)
