# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 18:17:37 2024

@author: peter
"""

from pytube import YouTube

# YouTube 视频 URL
video_url = "https://www.youtube.com/watch?v=gd38-X3HpbM"

try:
    # 初始化 YouTube 对象
    yt = YouTube(video_url)

    # 打印视频信息
    print(f"标题: {yt.title}")
    print(f"作者: {yt.author}")
    print(f"视频时长: {yt.length} 秒")

    # 选择最高分辨率的视频流
    stream = yt.streams.get_highest_resolution()

    # 下载视频
    print("下载中...")
    stream.download(output_path=".", filename="downloaded_video.mp4")
    print("下载完成！")
except Exception as e:
    print(f"下载失败: {e}")


try:
    yt = YouTube(video_url)

    # 列出所有可用流
    print("可用流：")
    for stream in yt.streams.filter(progressive=True):
        print(stream)

    # 下载指定流（比如选择最高分辨率）
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if stream:
        print(f"下载流：{stream}")
        stream.download(output_path=".", filename="downloaded_video.mp4")
        print("下载完成！")
    else:
        print("未找到可用流")
except Exception as e:
    print(f"下载失败: {e}")