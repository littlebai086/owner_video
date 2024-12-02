# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 09:26:43 2024

@author: peter
"""

import whisper
import torch

def list_available_devices():
    devices = {}

    # 检查 CPU
    devices["CPU"] = "Available"

    # 检查 XPU
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        devices["XPU"] = torch.xpu.get_device_name()
    else:
        devices["XPU"] = "Not available"

    # 检查 GPU
    if torch.cuda.is_available():
        gpu_devices = []
        for i in range(torch.cuda.device_count()):
            gpu_devices.append(torch.cuda.get_device_name(i))
        devices["GPU"] = gpu_devices
    else:
        devices["GPU"] = "Not available"

    return devices

# 列出所有可用设备
available_devices = list_available_devices()
for device_type, status in available_devices.items():
    print(f"{device_type}: {status}")

list_devices = []
model = whisper.load_model("small", device="xpu")
next(model.parameters()).device
for device_type, status in available_devices.items():
    if isinstance(status, list):  # 处理多个 GPU 的情况
        for i, gpu_name in enumerate(status):
            list_devices.append(f"{device_type} {i}: {gpu_name}")
    else:
        list_devices.append(f"{device_type}: {status}")
                
torch.xpu.is_available()
device = "Intel(R) UHD Graphics 750"
# 加载模型
device = torch.device("xpu" if torch.xpu.is_available() else "cpu")
model = whisper.load_model("small", device="cpu")  # 先用 CPU 加载
model.to("xpu")
if device.type == "xpu":
    model.to(device)  # 手动迁移到 XPU
    
device = "cuda" if torch.cuda.is_available() else "cpu"
# torch.cuda.current_device()
print(device)
print("PyTorch version:", torch.__version__)
print(torch.cuda.is_available())
if torch.xpu.is_available():
    xpu_name = torch.xpu.get_device_name()
    print(f"XPU device name: {xpu_name}")
else:
    print("XPU is not available.")
    
model = whisper.load_model("small", device="cuda")
torch.xpu.is_available()
print(torch.cuda.device_count())
if torch.cuda.is_available():
    print("GPU is available!")
else:
    print("GPU is not available.")
    
import tensorflow as tf
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))


model = whisper.load_model("small", device="cuda")
