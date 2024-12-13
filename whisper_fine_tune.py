# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 13:41:18 2024

@author: peter
"""

from transformers import pipeline

classifier = pipeline("sentiment-analysis") #使用情感分析
classifier(
    [
        "寶寶覺得苦，但寶寶不說",
        "我愛寶寶"
    ]
)

from huggingface_hub import notebook_login
notebook_login()

from datasets import Dataset, concatenate_datasets,load_dataset, DatasetDict
token = "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"
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

print(common_voice)

print(common_voice['train'][1])

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

new_data
# 创建新的 Dataset
new_dataset = Dataset.from_dict(new_data)
new_dataset = new_dataset.cast_column("audio", Audio(sampling_rate=48000))
print(common_voice["train"].features)
print(new_dataset.features)
# 将新数据追加到 common_voice 的 train 数据集中
common_voice["train"] = concatenate_datasets([common_voice["train"], new_dataset])

# 查看新的数据集长度
print(len(common_voice["train"]))


from datasets import load_dataset

# 切分訓練集與驗證集
train_dataset = common_voice["train"].train_test_split(test_size=0.2, seed=42)["train"]
val_dataset = common_voice["train"].train_test_split(test_size=0.2, seed=42)["test"]

# 查看數據集長度
print("Train dataset length:", len(train_dataset))
print("Validation dataset length:", len(val_dataset))

from transformers import WhisperFeatureExtractor

feature_extractor = WhisperFeatureExtractor.from_pretrained("openai/whisper-small")

from transformers import WhisperForConditionalGeneration, WhisperTokenizer, Trainer, TrainingArguments

# 加載 tokenizer 和模型
model_checkpoint = "openai/small"  # 你訓練使用的模型
tokenizer = WhisperTokenizer.from_pretrained(model_checkpoint)
model = WhisperForConditionalGeneration.from_pretrained(model_checkpoint)

# 訓練參數
training_args = TrainingArguments(
    output_dir="./results",              # 訓練結果儲存目錄
    per_device_train_batch_size=8,       # 訓練時每個 GPU 上的批次大小
    per_device_eval_batch_size=8,        # 驗證時每個 GPU 上的批次大小
    warmup_steps=500,                    # 預熱步數
    num_train_epochs=3,                  # 訓練的 epoch 數
    logging_dir="./logs",                # 日誌儲存目錄
    logging_steps=10,                    # 訓練過程中輸出訓練狀態間隔
    evaluation_strategy="steps",         # 驗證間隔
    save_steps=1000,                     # 儲存間隔
    eval_steps=100,                      # 每次驗證間隔
    save_total_limit=2,                  # 保留最好的模型
    learning_rate=5e-5,                  # 學習率
    weight_decay=0.01,                   # 過擴參數
    report_to="tensorboard",             # 用於儲存訓練狀態到 TensorBoard
    push_to_hub=False,
    load_best_model_at_end=True,        # 加載最好的模型
)

# 定義 Trainer
trainer = Trainer(
    model=model,                         # 訓練的模型
    args=training_args,                  # 訓練參數
    train_dataset=train_dataset,          # 訓練數據集
    eval_dataset=val_dataset,             # 驗證數據集
    tokenizer=tokenizer                   # 訓練所用的 tokenizer
)

# 開始訓練
trainer.train()