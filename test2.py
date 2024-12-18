import ctranslate2
from faster_whisper import WhisperModel

# 检查 GPU 支持
print(ctranslate2.get_supported_compute_types("cuda"))  # 应输出 ['int8', 'float16', 'float32']

model_path = "openai/whisper-small"
WhisperModel.convert(
    model_path,
    output_dir="./converted_model",  # 保存转换后模型的目录
    device="cuda",                  # 指定设备 (cuda 或 cpu)
    compute_type="float16",         # 精度：fp16、int8 等
)

# 加载模型
# model = WhisperModel("small", device="cuda", compute_type="float16")
model = WhisperModel("./ggml-python-small", device="cuda", compute_type="float16")
# model = WhisperModel("small", device="cpu")
print("Model loaded successfully.")
segments, info = model.transcribe("《小心！勞保充公？這３種人辛苦繳一生 退休一毛都領不到？》【錢線百分百】20230711-7│非凡財經新聞│.wav", beam_size=5)
print(f"Detected language: {info.language}")
for segment in segments:
    print(f"[{segment.start} -> {segment.end}] {segment.text}")