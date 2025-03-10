import os
import json
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

MODEL_PATH = "./model/vosk-model-cn-0.22"
AUDIO_FILE = "test.mp4"

def load_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    return audio.raw_data, 16000

raw_data, sample_rate = load_audio(AUDIO_FILE)

model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, sample_rate)
rec.SetWords(True)

timestamps = []
words = []
chunk_size = 4000

def process_result(res):
    data = json.loads(res)
    if 'result' not in data:
        return
    for word_info in data['result']:
        timestamps.append(round(word_info['start'], 3))
        words.append(word_info['word'])

# 分段处理
for i in range(0, len(raw_data), chunk_size):
    chunk = raw_data[i:i+chunk_size]
    if rec.AcceptWaveform(chunk):
        process_result(rec.Result())

# 最后一段
process_result(rec.FinalResult())

print("时间戳数组：")
print(json.dumps(timestamps, ensure_ascii=False))
print("\n文字数组：")
print(json.dumps(words, ensure_ascii=False, indent=2))
