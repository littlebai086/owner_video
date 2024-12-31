# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 10:24:30 2024

@author: peter
"""

### 自己的資料
from datasets import Dataset

new_data = [
    {"audio": "part_1.wav", "text": "之前我們討論過這個案例 在桃園有一個男子 他繳了大半輩子勞保費"},
    {"audio": "part_2.wav", "text": "後來 家屬要請你勞保年輕"},
    {"audio": "part_3.wav", "text": "其實他周邊的朋友也有人繳了大半輩子勞保費"},
    {"audio": "part_4.wav", "text": "或者是在過去付了大半輩子勞保金"},
    {"audio": "part_5.wav", "text": "然後順便就退了這個勞保"},
    {"audio": "part_6.wav", "text": "其實用最高級距去投保這個勞保"},
    {"audio": "part_7.wav", "text": "但是最後他去申請勞保局的時候"},
]

for idx, new_array in enumerate(new_data):
    new_data[idx]["audio"] = "wav/"+new_array["audio"]
    

dataset = Dataset.from_list(new_data)

# 預覽數據
print(dataset)

# 預處理音檔
import librosa
import soundfile as sf

def preprocess_audio(audio_path):
    # 載入音檔，重新採樣為 16kHz
    audio, sr = librosa.load(audio_path, sr=16000)
    # 保存音檔
    sf.write(audio_path, audio, sr)

# 遍歷處理所有音檔
for item in new_data:
    preprocess_audio(item["audio"])
    
from datasets import Audio

# 添加音頻欄位
dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))

# 預處理數據
def preprocess(example):
    audio = example["audio"]
    text = example["text"]
    return {"audio": audio, "text": text}

# 應用預處理
dataset = dataset.map(preprocess)
# dataset[0]["sentence"]
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# 載入模型與處理器
processor = WhisperProcessor.from_pretrained("openai/whisper-small")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")


# def prepare_data(batch):
#     inputs = processor(batch["audio"]["array"], sampling_rate=16000, return_tensors="pt").input_features
#     labels = processor.tokenizer(batch["text"], return_tensors="pt").input_ids
#     batch["input_features"] = inputs
#     batch["labels"] = labels
#     # batch["sentence"] = batch["text"]
#     return batch

def prepare_data(batch):
    # 处理音频，生成模型输入特征
    inputs = processor(batch["audio"]["array"], sampling_rate=16000, return_tensors="pt").input_features[0]
    
    # 处理文本，生成标签（input_ids）
    labels = processor.tokenizer(
         batch["text"],
         truncation=True,               # 启用截断
         padding="max_length",          # 启用填充
         max_length=448,                # 最大长度设置为 448
         return_tensors="pt"
     ).input_ids[0]
    
    batch["input_features"] = inputs
    batch["labels"] = labels
    return batch

dataset = dataset.map(prepare_data, remove_columns=["audio", "text"])


train_test_split = dataset.train_test_split(test_size=0.1)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]

from transformers import TrainingArguments, Trainer
# 創建數據填充器
from transformers import DataCollatorWithPadding

# data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

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
data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)


def compute_metrics(pred):
    pred_ids = pred.predictions
    label_ids = pred.label_ids

    # replace -100 with the pad_token_id
    label_ids[label_ids == -100] = tokenizer.pad_token_id

    # we do not want to group tokens when computing the metrics
    pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    cer = 100 * metric.compute(predictions=pred_str, references=label_str)

    return {"cer": cer}
# 設定訓練參數
# training_args = TrainingArguments(
#     output_dir="./whisper-finetune",
#     per_device_train_batch_size=4,
#     evaluation_strategy="epoch",
#     num_train_epochs=3,
#     save_steps=500,
#     logging_dir="./logs",
#     learning_rate=1e-5,
#     save_total_limit=2,
#     fp16=False,
# )

from transformers import Seq2SeqTrainingArguments

training_args = Seq2SeqTrainingArguments(
    output_dir="./whisper-small-chinese",  # change to a repo name of your choice
    per_device_train_batch_size=16,
    gradient_accumulation_steps=1,  # increase by 2x for every 2x decrease in batch size
    learning_rate=1e-5,
    warmup_steps=500,
    max_steps=5000,
    gradient_checkpointing=True, # 开启梯度检查点
    fp16=False,
    eval_strategy="steps",
    per_device_eval_batch_size=8,
    predict_with_generate=True,
    generation_max_length=225,
    save_steps=500,
    eval_steps=500,
    logging_steps=25,
    report_to=["tensorboard"],
    load_best_model_at_end=True,
    metric_for_best_model="wer",
    greater_is_better=False,
    push_to_hub=False,
    # use_cache=False,              # 必须禁用
)


# 定義 Trainer
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=eval_dataset,
#     tokenizer=processor.feature_extractor,
#     data_collator=data_collator,
# )


from transformers import Seq2SeqTrainer

trainer = Seq2SeqTrainer(
    args=training_args,
    model=model,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    tokenizer=processor.feature_extractor,
)


# 開始訓練
trainer.train()


#### 網路的資料

from datasets import load_dataset, DatasetDict

common_voice = DatasetDict()

common_voice["train"] = load_dataset(
    "mozilla-foundation/common_voice_11_0", 
    "zh-TW", 
    split="train+validation"
    )
common_voice["test"] = load_dataset(
    "mozilla-foundation/common_voice_11_0", 
    "zh-TW",
    split="test")

print(common_voice)

common_voice = common_voice.remove_columns(["accent", "age", "client_id", "down_votes", "gender", "locale", "path", "segment", "up_votes"])

from transformers import WhisperFeatureExtractor

feature_extractor = WhisperFeatureExtractor.from_pretrained("openai/whisper-small")

from transformers import WhisperTokenizer

tokenizer = WhisperTokenizer.from_pretrained(
    "openai/whisper-small", 
    language="chinese", 
    task="transcribe"
    )

from transformers import WhisperProcessor

processor = WhisperProcessor.from_pretrained("openai/whisper-small", language="chinese", task="transcribe")

input_str = common_voice["train"][0]["sentence"]
labels = tokenizer(input_str).input_ids
decoded_with_special = tokenizer.decode(labels, skip_special_tokens=False)
decoded_str = tokenizer.decode(labels, skip_special_tokens=True)

print(f"Input:                 {input_str}")
print(f"Decoded w/ special:    {decoded_with_special}")
print(f"Decoded w/out special: {decoded_str}")
print(f"Are equal:             {input_str == decoded_str}")

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

data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

import evaluate

metric = evaluate.load("cer")

def compute_metrics(pred):
    pred_ids = pred.predictions
    label_ids = pred.label_ids

    # replace -100 with the pad_token_id
    label_ids[label_ids == -100] = tokenizer.pad_token_id

    # we do not want to group tokens when computing the metrics
    pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    cer = 100 * metric.compute(predictions=pred_str, references=label_str)

    return {"cer": cer}

from transformers import WhisperForConditionalGeneration

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

# 後面一樣記得改成自己的模型

model.config.forced_decoder_ids = None
model.config.suppress_tokens = []

from transformers import Seq2SeqTrainingArguments

training_args = Seq2SeqTrainingArguments(
    output_dir="./whisper-small-chinese",  # change to a repo name of your choice
    per_device_train_batch_size=16,
    gradient_accumulation_steps=1,  # increase by 2x for every 2x decrease in batch size
    learning_rate=1e-5,
    warmup_steps=500,
    max_steps=5000,
    gradient_checkpointing=True, # 开启梯度检查点
    fp16=False,
    eval_strategy="steps",
    per_device_eval_batch_size=8,
    predict_with_generate=True,
    generation_max_length=225,
    save_steps=500,
    eval_steps=500,
    logging_steps=25,
    report_to=["tensorboard"],
    load_best_model_at_end=True,
    metric_for_best_model="wer",
    greater_is_better=False,
    push_to_hub=False,
    # use_cache=False,              # 必须禁用
)


from transformers import TrainerCallback
import time

class TimeLoggerCallback(TrainerCallback):
    def __init__(self):
        self.start_time = None

    def on_train_begin(self, args, state, control, **kwargs):
        self.start_time = time.time()
        print("Training started...")

    def on_step_end(self, args, state, control, **kwargs):
        elapsed_time = time.time() - self.start_time
        steps_completed = state.global_step
        total_steps = state.max_steps
        estimated_total_time = (elapsed_time / steps_completed) * total_steps if steps_completed > 0 else 0
        remaining_time = estimated_total_time - elapsed_time

        print(f"Step {steps_completed}/{total_steps} - Elapsed time: {elapsed_time:.2f}s - Estimated remaining time: {remaining_time:.2f}s")

    def on_train_end(self, args, state, control, **kwargs):
        total_time = time.time() - self.start_time
        print(f"Training completed in {total_time:.2f} seconds.")


from transformers import Seq2SeqTrainer

trainer = Seq2SeqTrainer(
    args=training_args,
    model=model,
    train_dataset=common_voice["train"],
    eval_dataset=common_voice["test"],
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    tokenizer=processor.feature_extractor,
    callbacks=[TimeLoggerCallback()],  # 添加回调
)

trainer.train()
