# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 12:00:17 2024

@author: peter
"""

import sys
from faster_whisper import WhisperModel

def transcribe_audio(model, audio_path):
    """將音訊轉為文字"""
    print("將音訊轉為文字")
    try:
        # 加载音频文件并开始转录
        segments, info = model.transcribe(audio_path)
        
        total_duration = info.duration  # 总时长
        progress = 0
        text = ""
        all_text = ""
        new_segments = []
        original_srts = []

        for segment in segments:
            text += f"{segment.text}\r\n"
            all_text += f"Start: {segment.start}s, End: {segment.end}s, Text: {segment.text}\r\n"
            progress = int(segment.end / total_duration * 100)
            print("progress", progress)

            subtitle_dict = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
            }
            original_srts.append(segment.text)
            new_segments.append(subtitle_dict)

            print(f"[{segment.start} -> {segment.end}] {segment.text}")

        print("progress", 100)
        print("開始轉錄完成!")
        return [text, all_text, new_segments]

    except Exception as e:
        print(f"讀取音訊時出錯: {e}")
        return [None, None, None]
    
def format_time(seconds):
    # 将秒数转换为 SRT 的时间格式
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

def generate_srt(subtitles, output_file,text_field="text"):
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, subtitle in enumerate(subtitles, start=1):
            # 写入序号
            f.write(f"{idx}\n")
            # 写入时间戳
            start_time = format_time(subtitle['start'])
            end_time = format_time(subtitle['end'])
            f.write(f"{start_time} --> {end_time}\n")
            # 写入字幕内容
            text = subtitle.get(text_field, "")
            f.write(f"{text}\n\n")
class VideoProcessThread():

    def __init__(self, audio_path,model):
        super().__init__()
        self.audio_path = audio_path
        self.model = model
        # self.subtitles = None
        # self.model = WhisperModel.load_model("small", compute_type="float16")  # 选择 'base' 模型，适合快速测试

    def run(self):
        try:
            # 擷取音訊並轉為文字
            print("擷取音訊並轉為文字")
            transcribed_text,all_transcribed_text,subtitles = self.transcribe_audio(self.audio_path)
            return transcribed_text,all_transcribed_text,subtitles
        except Exception as e:
            print(e)


    def transcribe_audio(self, audio_path):
        """將音訊轉為文字"""
        print("將音訊轉為文字")
        try:
            # 設定進度回調函數
            # result = self.model.transcribe(audio_path, verbose=True)  # 支持 MP3, WAV, FLAC 格式
            segments, info = self.model.transcribe(audio_path)
            # 獲取總時長（用於進度條的總值）
            total_duration = info.duration
            progress = 0  # 初始化進度
            # 估算进度
            # total_segments = len(segments)
            text = ""
            all_text = ""
            new_segments = []
            oringinal_srts = []
            for segment in segments:
                text += f"{segment.text}\r\n"
                all_text += f"Start: {segment.start}s, End: {segment.end}s, Text: {segment.text}\r\n"
                progress = int(segment.end / total_duration * 100)
                print("progress",progress)
                subtitle_dict = {
                    "start" : segment.start,
                    "end" : segment.end,
                    "text" : segment.text,
                }
                oringinal_srts.append(segment.text)
                new_segments.append(subtitle_dict)
                print(f"[{segment.start} -> {segment.end}] {segment.text}")
            print("progress",100)
            
            
            # for  i, segment in enumerate(result["segments"]):
            #     text += f"{segment['text']}\r\n"
            #     all_text += f"Start: {segment['start']}s, End: {segment['end']}s, Text: {segment['text']}\r\n"
            #     progress = int((i + 1) / total_segments * 100)
            #     self.progress_signal.emit(progress)  # 发送信号更新进度条
            #     # time.sleep(0.1)  # 模拟处理时间
            #     print(f"Start: {segment['start']}s, End: {segment['end']}s, Text: {segment['text']}")
            print("開始轉錄...")
            return [text,all_text,new_segments]
        except Exception as e:
            print(f"讀取音訊時出錯: {e}")
            return [None,None,None]
        

class Main():
    def __init__(self):
        super().__init__()
        self.speech_recognition_text=""
        self.translate_text=""
        self.all_speech_recognition_text=""
        self.audio_path = "股票語音/stock_all.wav"
        self.processing_seconds = 0
        # 翻譯是否完成
        self.translation_complete = False
        self.selected_device_value = "gpu"
        # model_path = "D:/python/modal/ggml-small.bin"
        # print(os.path.exists(model_path))
        if self.selected_device_value=="cpu":
            self.model = WhisperModel('turbo', device=self.selected_device_value)
        else:
            self.model = WhisperModel('turbo', device="cuda", compute_type="float16")

    def start_speech_to_text_processing(self):
        """启动语音转文字"""
               
        self.video_thread = VideoProcessThread(self.audio_path,self.model)
        
        transcribed_text,all_transcribed_text,subtitles = self.video_thread.run()
        
        self.generate_srt(subtitles, "股票語音/stock_all.srt",text_field="text")

    def format_time(self,seconds):
        # 将秒数转换为 SRT 的时间格式
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

    def generate_srt(self,subtitles, output_file,text_field="text"):
        with open(output_file, 'w', encoding='utf-8') as f:
            for idx, subtitle in enumerate(subtitles, start=1):
                # 写入序号
                f.write(f"{idx}\n")
                # 写入时间戳
                start_time = self.format_time(subtitle['start'])
                end_time = self.format_time(subtitle['end'])
                f.write(f"{start_time} --> {end_time}\n")
                # 写入字幕内容
                text = subtitle.get(text_field, "")
                f.write(f"{text}\n\n")
                
          

if __name__ == "__main__":
    app = Main()
    app.start_speech_to_text_processing()

    sys.exit(app.exec())
len(new_stock_array)
len(new_segments)
audio_path = "股票語音/merged_stock_with_silence.wav"
model = WhisperModel('base', device="cuda", compute_type="float16")
text, all_text, new_segments = transcribe_audio(model,audio_path)
generate_srt(new_segments, "stock_all.srt")
index=68
new_segments[index]["text"]
new_stock_array[index]
new_stock_segments_stock = []
for idx, segments in enumerate(new_segments):
    new_stock_segments_stock.append(segments["text"])
    new_segments[idx]["oringinal_text"] = new_stock_array[1032]

new_stock_segments_stock.remove("齊元大美元指數")
for idx, stock1 in enumerate(new_stock_segments_stock):
    print("===========Start=============")
    print(idx)
    print("stock1:"+stock1)
    print("stock2:"+new_stock_array[idx])
    print("============End=============")
    if idx>200:
        break
    
output_file = "new_stock_array.txt"  # 输出的文件名

# 将数组写入到文本文件中
with open(output_file, "w", encoding="utf-8") as f:
    for stock in new_stock_array:
        f.write(stock + "\n")  # 每个元素写入一行
