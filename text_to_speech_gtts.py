# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 15:28:47 2024

@author: peter
"""

from gtts import gTTS

# Import pygame for playing the converted audio
import pygame

# The text that you want to convert to audio
mytext = '台積電'

# Language in which you want to convert
language = 'zh-TW'

# Passing the text and language to the engine, 
# here we have marked slow=False. Which tells 
# the module that the converted audio should 
# have a high speed
myobj = gTTS(text=mytext, lang=language, slow=False)

# Saving the converted audio in a mp3 file named
# welcome 
myobj.save("welcome.wav")

# Initialize the mixer module
pygame.mixer.init()

# Load the mp3 file
pygame.mixer.music.load("welcome.mp3")

# Play the loaded mp3 file
pygame.mixer.music.play()
