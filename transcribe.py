import os
import sys
import subprocess
import tempfile
import datetime
import whisper
import warnings  # 新增导入

def is_video_file(file_path: str) -> bool:
    # 简单判断是否为视频文件，可根据需求扩展支持的格式
    video_exts = ['.mp4', '.mkv', '.avi', '.mov', '.flv']
    _, ext = os.path.splitext(file_path.lower())
    return ext in video_exts

def extract_audio(video_path: str) -> str:
    # 使用 ffmpeg 提取音频，保存为临时 WAV 文件
    temp_audio_fd, temp_audio_path = tempfile.mkstemp(suffix=".wav")
    os.close(temp_audio_fd)  # 关闭文件描述符
    cmd = [
        "ffmpeg",
        "-y",  # 覆盖输出文件
        "-i", video_path,
        "-vn",  # 不处理视频流
        "-acodec", "pcm_s16le",
        "-ar", "16000",  # 将采样率转为 16000 Hz，Whisper 性能较佳
        "-ac", "1",  # 单通道
        temp_audio_path
    ]
    print(f"提取音频: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("音频提取失败！")
        print(result.stderr.decode())
        sys.exit(1)
    return temp_audio_path

def format_timestamp_for_srt(seconds: float) -> str:
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds)
    return f"{str(datetime.timedelta(seconds=s))},{ms:03d}"

def format_timestamp_for_vtt(seconds: float) -> str:
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds)
    return f"{str(datetime.timedelta(seconds=s))}.{ms:03d}"

def format_timestamp_for_lrc(seconds: float) -> str:
    minutes = int(seconds // 60)
    sec = seconds - minutes * 60
    return f"[{minutes:02d}:{sec:05.2f}]"

def generate_srt(segments):
    srt_output = ""
    for i, segment in enumerate(segments, 1):
        start = format_timestamp_for_srt(segment["start"])
        end = format_timestamp_for_srt(segment["end"])
        text = segment["text"].strip()
        srt_output += f"{i}\n{start} --> {end}\n{text}\n\n"
    return srt_output

def generate_vtt(segments):
    vtt_output = "WEBVTT\n\n"
    for i, segment in enumerate(segments, 1):
        start = format_timestamp_for_vtt(segment["start"])
        end = format_timestamp_for_vtt(segment["end"])
        text = segment["text"].strip()
        vtt_output += f"{i}\n{start} --> {end}\n{text}\n\n"
    return vtt_output

def generate_lrc(segments):
    lrc_output = ""
    for segment in segments:
        timestamp = format_timestamp_for_lrc(segment["start"])
        text = segment["text"].strip()
        lrc_output += f"{timestamp}{text}\n"
    return lrc_output

def generate_smi(segments, lang="ENCC"):
    smi_output = """<SAMI>
<Head>
 <STYLE TYPE="text/css">
  <!--
   P { margin-left: 2pt; margin-right: 2pt; margin-bottom: 1pt; margin-top: 1pt;
       font-size: 10pt; text-align: center; font-family: Arial; font-weight: normal; color: white; }
  -->
 </STYLE>
</Head>
<BODY>
"""
    for segment in segments:
        start_ms = int(segment["start"] * 1000)
        text = segment["text"].strip()
        smi_output += f'<SYNC Start={start_ms}><P Class={lang}>{text}<br>\n'
    smi_output += "</BODY>\n</SAMI>"
    return smi_output

def get_output_path(input_path: str, output_dir: str, ext: str) -> str:
    """为输出文件生成合适的路径"""
    basename = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join(output_dir, f"{basename}{ext}")

def process_single_file(input_path: str, output_dir: str, model) -> None:
    """处理单个文件的转录"""
    print(f"\n处理文件: {input_path}")
    
    # 如果文件为视频，则先分离音频
    if is_video_file(input_path):
        print("检测到视频文件，正在提取音频...")
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
        ".lrc": generate_lrc,
        ".smi": generate_smi
    }
    
    for ext, generator in output_files.items():
        output_path = get_output_path(input_path, output_dir, ext)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(generator(segments))
    
    print(f"字幕文件生成成功，保存在目录: {output_dir}")

    # 如果创建了临时音频文件，保存音频文件到output目录
    if delete_audio_after:
        audio_output_path = get_output_path(input_path, output_dir, ".wav")
        os.rename(audio_path, audio_output_path)
        print(f"音频文件保存在: {audio_output_path}")
    

def main(input_paths, output_dir="output"):
    # 忽略 FP16 警告
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

    # 创建带日期的输出子目录
    date_subdir = datetime.datetime.now().strftime("%Y%m%d")
    output_dir = os.path.join(output_dir, date_subdir)
    
    print("正在加载 Whisper 模型……选base模型速度快，但是如果效果太差选large 是多语言的")
    model = whisper.load_model("base")
    
    total_files = len(input_paths)
    print(f"\n共发现 {total_files} 个文件待处理")
    print(f"输出目录: {output_dir}")
    
    for i, input_path in enumerate(input_paths, 1):
        print(f"\n[{i}/{total_files}] 开始处理文件...")
        try:
            process_single_file(input_path, output_dir, model)
            print(f"文件处理完成: {input_path}")
        except Exception as e:
            print(f"处理文件时出错 {input_path}: {str(e)}")
            continue

    print("\n所有文件处理完成！")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python transcribe.py <音频或视频文件路径1> [文件路径2 ...]")
        sys.exit(1)
    
    # 获取所有输入文件路径
    input_paths = sys.argv[1:]
    main(input_paths)