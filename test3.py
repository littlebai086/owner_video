# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 09:25:42 2024

@author: peter
"""
from datasets import Dataset, concatenate_datasets,load_dataset, DatasetDict

common_voice = DatasetDict()

common_voice["train"] = load_dataset(
    "mozilla-foundation/common_voice_11_0", 
    "zh-TW", 
    split="train+validation", 
    # use_auth_token=token, 
    trust_remote_code=True
)
common_voice["test"] = load_dataset(
    "mozilla-foundation/common_voice_11_0", 
    "zh-TW", 
    split="test", 
    # use_auth_token=token, 
    trust_remote_code=True
)
# Remove useless columns
common_voice = common_voice.remove_columns([
    "accent", "age", "client_id", "down_votes", 
    "gender", "locale", "path", "segment", "up_votes"
])

from transformers import WhisperFeatureExtractor

feature_extractor = WhisperFeatureExtractor.from_pretrained("openai/whisper-small")

from transformers import WhisperTokenizer

tokenizer = WhisperTokenizer.from_pretrained("openai/whisper-small", language="chinese", task="transcribe")

from transformers import WhisperProcessor

processor = WhisperProcessor.from_pretrained("openai/whisper-small", language="chinese", task="transcribe")

from datasets import Audio

common_voice = common_voice.cast_column("audio", Audio(sampling_rate=16000))

print(common_voice["train"][0])

def prepare_dataset(batch):
    # load and resample audio data from 48 to 16kHz
    audio = batch["audio"]

    # compute log-Mel input features from input audio array 
    batch["input_features"] = feature_extractor(audio["array"], sampling_rate=audio["sampling_rate"]).input_features[0]

    # encode target text to label ids 
    batch["labels"] = tokenizer(batch["sentence"]).input_ids
    return batch

common_voice = common_voice.map(prepare_dataset, remove_columns=common_voice.column_names["train"], num_proc=1)

import torch

from dataclasses import dataclass
from typing import Any, Dict, List, Union

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # split inputs and labels since they have to be of different lengths and need different padding methods
        # first treat the audio inputs by simply returning torch tensors
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        # get the tokenized label sequences
        label_features = [{"input_ids": feature["labels"]} for feature in features]
        # pad the labels to max length
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        # replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        # if bos token is appended in previous tokenization step,
        # cut bos token here as it's append later anyways
        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels

        return batch
