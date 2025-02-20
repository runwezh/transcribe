# 视频/音频转录工具

## 功能概述
该工具可以将视频或音频文件转换为多种格式的字幕文件，支持批量处理。使用 OpenAI 的 Whisper 模型进行语音识别转录。

## 主要功能
- 支持多种视频格式（mp4, mkv, avi, mov, flv）
- 支持音频直接转录
- 批量处理多个文件
- 自动提取视频中的音频
- 生成多种字幕格式：
  - SRT（通用字幕格式）
  - VTT（网页字幕格式）
  - LRC（歌词格式）
  - SMI（SAMI 字幕格式）
- 按日期自动归类输出文件

## 系统要求
- Python 3.7+
- FFmpeg（用于视频音频处理）
- 依赖包：
  - openai-whisper
  - ffmpeg-python

## 安装步骤
1. 安装 FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

2. 安装 Python 依赖
```bash
pip install openai-whisper
```

## 使用方法
### 基本用法
```bash
python transcribe.py <文件路径1> [文件路径2 ...]
```

### 示例
```bash
# 处理单个文件
python transcribe.py video.mp4

# 处理多个文件
python transcribe.py video1.mp4 audio.mp3 video2.mkv
```

## 输出说明
- 所有输出文件会保存在 `output/YYYYMMDD/` 目录下
- 对于每个输入文件，会生成以下格式的字幕：
  - .srt 文件
  - .vtt 文件
  - .lrc 文件
  - .smi 文件
- 如果输入是视频文件，会同时保存提取出的音频文件（.wav 格式）

## 注意事项
1. 确保系统已正确安装 FFmpeg
2. 首次运行时会下载 Whisper 模型，需要网络连接
3. 处理大文件时可能需要较长时间
4. 默认使用 Whisper 的 base 模型，可以根据需要修改为其他模型