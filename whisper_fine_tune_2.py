# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 16:01:19 2024

@author: peter
"""

from datasets import load_dataset

dataset = load_dataset("path/to/dataset")

from transformers import WhisperForConditionalGeneration, WhisperProcessor

model_name = "openai/whisper-small"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name)

import torch
from datasets import Audio


new_data = {
    "audio": [
        "part_1.wav", 
        "part_2.wav",
        "part_3.wav",
        "part_4.wav",
        "part_5.wav",
        "part_6.wav",
        "part_7.wav"
    ],
    "sentence": [
        "之前我們討論過這個案例 在桃園有一個男子 他繳了大半輩子勞保費", 
        "後來 家屬要請你勞保年輕", 
        "其實他周邊的朋友也有人繳了大半輩子勞保費", 
        "或者是在過去付了大半輩子勞保金", 
        "然後順便就退了這個勞保", 
        "其實用最高級距去投保這個勞保", 
        "但是最後他去申請勞保局的時候"
    ],
}


for idx, audio in enumerate(new_data["audio"]):
    new_data["audio"][idx] = "wav/"+audio

from datasets import Audio
from datasets import Dataset, concatenate_datasets,load_dataset, DatasetDict

import uuid

random_id = uuid.uuid4().hex

new_data
# 创建新的 Dataset
new_dataset = Dataset.from_dict(new_data)
new_dataset = new_dataset.cast_column("audio", Audio(sampling_rate=16000))

# 將數據集中的音頻加載為特徵
# dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))


def preprocess_function(batch):
    audio = batch["audio"]
    input_features = processor(audio["array"], sampling_rate=audio["sampling_rate"], return_tensors="pt").input_features
    # batch["input_ids"] = uuid.uuid4().hex
    batch["input_features"] = input_features[0]
    batch["labels"] = processor.tokenizer(batch["sentence"], return_tensors="pt").input_ids[0]
    return batch

processed_dataset = new_dataset.map(preprocess_function, remove_columns=["audio", "sentence"])

# processed_dataset = new_dataset.map(preprocess_function, remove_columns=["audio", "sentence"])

print(processed_dataset)

train_test_split = processed_dataset.train_test_split(test_size=0.2)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]


from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./whisper-finetuned",
    per_device_train_batch_size=8,
    evaluation_strategy="steps",
    num_train_epochs=3,
    save_steps=500,
    save_total_limit=2,
    learning_rate=1e-5,
    fp16=False,         # 禁用半精度，因为只有 GPU 支持
    no_cuda=True,       # 明确禁用 GPU
    logging_dir="./logs"
)

from transformers import DataCollatorWithPadding
import torch

class DataCollatorSpeechSeq2Seq:
    def __init__(self, processor):
        self.processor = processor

    def __call__(self, features):
        input_features = [torch.tensor(feature["input_features"]) for feature in features]  # 转换为 Tensor
        labels = [feature["labels"] for feature in features]

        # 将 input_features 堆叠成批次张量
        input_features = torch.stack(input_features)

        # 使用 processor.tokenizer.pad 来填充 labels
        labels = self.processor.tokenizer.pad(
            {"input_ids": labels}, padding=True, return_tensors="pt"
        )["input_ids"]

        batch = {
            "input_features": input_features,
            "labels": labels,
        }
        return batch
    
data_collator = DataCollatorSpeechSeq2Seq(processor)


# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=eval_dataset,
#     tokenizer=processor.tokenizer
# )

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,  # 使用自定义 DataCollator
    tokenizer=processor.feature_extractor,  # 使用音频特征提取器
)

trainer.train()

# 自定義 PyTorch 訓練循環

from torch.utils.data import DataLoader
from torch.optim import AdamW

# 創建數據加載器
train_loader = DataLoader(processed_dataset["train"], batch_size=8, shuffle=True)

# 定義優化器
optimizer = AdamW(model.parameters(), lr=1e-5)

model.train()
for epoch in range(3):
    for batch in train_loader:
        optimizer.zero_grad()
        input_features = batch["input_features"].to("cuda")
        labels = batch["labels"].to("cuda")
        outputs = model(input_features=input_features, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch} completed.")
    
# 保存模型

model.save_pretrained("./whisper-finetuned")
processor.save_pretrained("./whisper-finetuned")

# 測試模型

from transformers import pipeline

fine_tuned_model = WhisperForConditionalGeneration.from_pretrained("./whisper-finetuned")
fine_tuned_processor = WhisperProcessor.from_pretrained("./whisper-finetuned")

asr = pipeline("automatic-speech-recognition", model=fine_tuned_model, processor=fine_tuned_processor)
result = asr("path/to/audio.wav")
print(result["text"])