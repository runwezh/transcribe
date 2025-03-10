import os
import sys
import subprocess
import tempfile
import datetime
import whisper
import warnings
import json
import concurrent.futures

# 判断文件是否为视频文件
def is_video_file(file_path: str) -> bool:
    # 支持的视频格式
    video_exts = ['.mp4', '.mkv', '.avi', '.mov', '.flv']
    _, ext = os.path.splitext(file_path.lower())
    return ext in video_exts

# 提取视频文件的音频并保存为临时文件
def extract_audio(video_path: str) -> str:
    # 创建一个临时文件保存音频
    temp_audio_fd, temp_audio_path = tempfile.mkstemp(suffix=".wav")
    os.close(temp_audio_fd)
    # 使用 ffmpeg 提取音频
    cmd = [
        "ffmpeg",
        "-y",                # 覆盖输出文件
        "-i", video_path,    # 输入视频文件
        "-vn",               # 不处理视频
        "-acodec", "pcm_s16le",  # 使用 PCM 编码
        "-ar", "16000",      # 设置音频采样率为 16kHz
        "-ac", "1",          # 单声道
        temp_audio_path      # 输出音频文件路径
    ]
    print(f"提取音频: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 如果音频提取失败，则输出错误信息并退出程序
    if result.returncode != 0:
        print("音频提取失败！")
        print(result.stderr.decode())
        sys.exit(1)
    return temp_audio_path

# 格式化时间戳为 SRT 格式
def format_timestamp_for_srt(seconds: float) -> str:
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds)
    return f"{str(datetime.timedelta(seconds=s))},{ms:03d}"

# 格式化时间戳为 VTT 格式
def format_timestamp_for_vtt(seconds: float) -> str:
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds)
    return f"{str(datetime.timedelta(seconds=s))}.{ms:03d}"

# 格式化时间戳为 LRC 格式
def format_timestamp_for_lrc(seconds: float) -> str:
    minutes = int(seconds // 60)
    sec = seconds - minutes * 60
    return f"[{minutes:02d}:{sec:05.2f}]"

# 生成 SRT 字幕文件内容
def generate_srt(segments):
    srt_output = ""
    for i, segment in enumerate(segments, 1):
        start = format_timestamp_for_srt(segment["start"])
        end = format_timestamp_for_srt(segment["end"])
        text = segment["text"].strip()
        srt_output += f"{i}\n{start} --> {end}\n{text}\n\n"
    return srt_output

# 生成 VTT 字幕文件内容
def generate_vtt(segments):
    vtt_output = "WEBVTT\n\n"
    for i, segment in enumerate(segments, 1):
        start = format_timestamp_for_vtt(segment["start"])
        end = format_timestamp_for_vtt(segment["end"])
        text = segment["text"].strip()
        vtt_output += f"{i}\n{start} --> {end}\n{text}\n\n"
    return vtt_output

# 生成 LRC 字幕文件内容
def generate_lrc(segments):
    lrc_output = ""
    for segment in segments:
        timestamp = format_timestamp_for_lrc(segment["start"])
        text = segment["text"].strip()
        lrc_output += f"{timestamp}{text}\n"
    return lrc_output

# 生成按语序排列的 JSON 文件，时间戳合并为一个列表，文字合并为一个字符串
def generate_json(segments):
    timestamp_list = []
    text_string = []
    
    # 原始的 timestamp 和 str 对应的 JSON
    for segment in segments:
        timestamp_list.append(round(segment["start"], 1))  # 保留一位小数
        # 文字拆分并用空格连接
        text_string.append(" ".join(segment["text"].strip()))

    # 合成结果，生成原始 JSON
    json_output = {
        "timestamp": timestamp_list,
        "str": " ".join(text_string)  # 将所有文字合并成一个字符串
    }

    return json_output

def generate_combined_json(segments):
    # 合并后的按语序排列的 JSON
    timestamp_list = []
    text_string = ""

    for segment in segments:
        timestamp_list.append(round(segment["start"], 1))  # 保留一位小数
        text_string += " " + segment["text"].strip()

    # 合成结果，生成按语序排列的 JSON
    combined_json_output = {
        "timestamp": timestamp_list,
        "str": text_string.strip()  # 将所有文字合并成一个字符串
    }

    return combined_json_output

def process_single_file(input_path: str, output_dir: str, model) -> None:
    print(f"\n处理文件: {input_path}")
    
    # 如果文件为视频，则先分离音频
    if is_video_file(input_path):
        audio_path = extract_audio(input_path)
        delete_audio_after = True
    else:
        audio_path = input_path
        delete_audio_after = False

    print("转录处理中，请稍候……")
    result = model.transcribe(audio_path)
    segments = result["segments"]

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成字幕文件
    output_files = {
        ".srt": generate_srt,
        ".vtt": generate_vtt,
        ".lrc": generate_lrc
    }
    
    for ext, generator in output_files.items():
        output_path = get_output_path(input_path, output_dir, ext)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(generator(segments))

    # 生成原始 JSON 文件
    json_output = generate_json(segments)
    json_file_path = get_output_path(input_path, output_dir, ".json")
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(json_output, json_file, ensure_ascii=False, indent=4)

    # 生成合并后的 JSON 文件
    combined_json_output = generate_combined_json(segments)
    combined_json_file_path = get_output_path(input_path, output_dir, "_combined.json")
    with open(combined_json_file_path, "w", encoding="utf-8") as combined_json_file:
        json.dump(combined_json_output, combined_json_file, ensure_ascii=False, indent=4)

    print(f"字幕文件和 JSON 文件生成成功，保存在目录: {output_dir}")

    if delete_audio_after:
        audio_output_path = get_output_path(input_path, output_dir, ".wav")
        os.rename(audio_path, audio_output_path)
        print(f"音频文件保存在: {audio_output_path}")


# 获取输出文件的路径
def get_output_path(input_path: str, output_dir: str, ext: str) -> str:
    basename = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join(output_dir, f"{basename}{ext}")


# 主函数：处理多个文件
def main(input_paths, output_dir="output"):
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

    # 按日期生成子目录
    date_subdir = datetime.datetime.now().strftime("%Y%m%d")
    output_dir = os.path.join(output_dir, date_subdir)
    
    # 加载 Whisper 模型
    custom_model_path = os.path.join(os.getcwd(), "model/whisper-large-v2-ct2-32/")
    print("正在加载 Whisper 模型……")
    model = whisper.load_model("base", download_root=custom_model_path)
    
    total_files = len(input_paths)
    print(f"\n共发现 {total_files} 个文件待处理")
    print(f"输出目录: {output_dir}")
    
    # 使用 ThreadPoolExecutor 并行处理文件
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i, input_path in enumerate(input_paths, 1):
            print(f"\n[{i}/{total_files}] 开始处理文件...")
            futures.append(executor.submit(process_single_file, input_path, output_dir, model))

        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            future.result()  # 捕获异常

    print("\n所有文件处理完成！")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python transcribe.py <音频或视频文件路径1> [文件路径2 ...]")
        sys.exit(1)
    
    input_paths = sys.argv[1:]
    main(input_paths)
