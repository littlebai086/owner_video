# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 17:36:37 2024

@author: peter
"""

import torch

def list_devices():
    """列出可用的設備 (GPU 和 CPU)。"""
    devices = []
        
    # 檢查 GPU 是否可用
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            devices.append(f"GPU:{i} ({torch.cuda.get_device_name(i)})")
        
    # 添加 CPU
    devices.append("CPU")
    return devices
    
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
    print(devices)
    return devices

list_available_devices()
