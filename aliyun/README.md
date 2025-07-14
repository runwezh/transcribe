# 阿里云语音识别方案

基于阿里云智能语音交互服务和官方Python SDK (`aliyun-python-sdk-core`) 的语音转文字解决方案，支持录音文件识别、实时语音识别和一句话识别，并提供逐字时间戳功能。

**核心优势**: 使用官方SDK替代手动API请求，显著提升了稳定性和后续可维护性。

## 功能特性

- **多种识别模式**：
  - 录音文件识别（支持长音频，成本低廉）
  - 实时语音识别（支持流式处理）
  - 一句话识别（适合短音频）

- **逐字时间戳**：精确到毫秒级的字级别时间戳信息

- **多格式支持**：
  - 输入：WAV, MP3, AAC, M4A, WMA, FLAC
  - 输出：SRT, VTT, LRC, TXT, JSON

- **成本优化**：
  - 录音文件识别闲时版：1元/小时起
  - Paraformer语音模型服务：0.288元/小时
  - 按秒计费，避免浪费

## 安装配置

### 1. 安装依赖

```bash
cd aliyun
pip install -r requirements.txt
```

### 2. 配置环境变量

**方法一：使用 .env 文件（推荐）**

编辑项目目录下的 `.env` 文件：

```bash
# 编辑 .env 文件
nano .env
```

填入您的阿里云访问凭证和项目配置：

```
# 阿里云访问凭证
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_REGION=cn-shanghai

# 智能语音交互服务配置
ALIYUN_APPKEY=your_app_key

# 对象存储OSS配置
ALIYUN_OSS_BUCKET=your_oss_bucket_name
```

**方法二：设置系统环境变量**

```bash
# 设置阿里云访问凭证
export ALIYUN_ACCESS_KEY_ID="your_access_key_id"
export ALIYUN_ACCESS_KEY_SECRET="your_access_key_secret"
export ALIYUN_REGION="cn-shanghai"  # 可选，默认为cn-shanghai
```

> 💡 **提示**: 程序会自动读取 `.env` 文件，无需手动设置环境变量。如果同时存在环境变量和 `.env` 文件，环境变量优先级更高。

### 3. 获取阿里云访问凭证

1. 登录[阿里云控制台](https://ram.console.aliyun.com/)
2. 在[智能语音交互控制台](https://nls-portal.console.aliyun.com/applist)创建一个项目，获取**AppKey**。
3. 创建一个用于存放音频文件的[OSS Bucket](https://oss.console.aliyun.com/bucket)，并记录其名称。
4. 创建RAM用户并授予其`AliyunNLSFullAccess`和`AliyunOSSFullAccess`权限。
5. 获取该RAM用户的AccessKey ID和AccessKey Secret。

## 使用方法

### 快速开始

```bash
# 交互式演示（推荐）
python demo.py

# 命令行使用
python aliyun_transcribe.py --mode sentence audio.wav
```

### 基本用法

```bash
# 一句话识别（适合短音频）
python aliyun_transcribe.py --mode sentence audio.wav

# 录音文件识别（适合长音频）
python aliyun_transcribe.py --mode file audio.wav

# 批量处理
python aliyun_transcribe.py --mode file audio1.wav audio2.mp3 audio3.m4a
```

### 高级选项

```bash
# 指定输出目录
python aliyun_transcribe.py --mode file --output-dir /path/to/output audio.wav

# 指定输出格式
python aliyun_transcribe.py --mode file --formats srt,vtt,json audio.wav

# 启用热词
python aliyun_transcribe.py --mode file --vocabulary-id vocab_123 audio.wav

# 调整采样率
python aliyun_transcribe.py --mode file --sample-rate 8000 audio.wav
```

## 输出格式说明

### SRT格式（字幕）
```
1
00:00:00,000 --> 00:00:02,500
你好，欢迎使用阿里云语音识别

2
00:00:02,500 --> 00:00:05,000
这是一个测试音频文件
```

### VTT格式（网页字幕）
```
WEBVTT

1
00:00:00.000 --> 00:00:02.500
你好，欢迎使用阿里云语音识别

2
00:00:02.500 --> 00:00:05.000
这是一个测试音频文件
```

### JSON格式（详细信息）
```json
{
  "text": "你好，欢迎使用阿里云语音识别",
  "words": [
    {"text": "你", "start_time": 0, "end_time": 200},
    {"text": "好", "start_time": 200, "end_time": 400}
  ],
  "confidence": 0.95
}
```

## 成本说明

根据阿里云官方定价（2024年数据）：

- **录音文件识别闲时版**：1元/小时起，50000小时以上0.6元/小时
- **Paraformer语音模型服务**：0.288元/小时，无梯度定价
- **实时语音识别**：3.50元/小时起，5000小时以上1.20元/小时
- **一句话识别**：按次计费，具体价格请参考阿里云官网

## 注意事项

1. 确保网络连接稳定，API调用需要访问阿里云服务
2. 音频文件建议采用16kHz采样率，单声道格式以获得最佳识别效果
3. 长音频文件会自动分段处理，确保识别质量
4. 逐字时间戳功能需要在配置中启用 `enable_words=True`
5. 热词功能可以提高特定领域词汇的识别准确率

## 故障排除

### 常见问题

1. **认证失败**：检查AccessKey配置是否正确
2. **网络超时**：检查网络连接，可能需要配置代理
3. **音频格式不支持**：转换为支持的格式（WAV推荐）
4. **识别准确率低**：尝试使用热词功能或调整音频质量

### 日志查看

程序运行时会生成详细日志文件 `aliyun_asr.log`，可以查看具体的错误信息和调试信息。

## 技术支持

- [阿里云智能语音交互文档](https://help.aliyun.com/product/30413.html)
- [API参考文档](https://help.aliyun.com/document_detail/84435.html)
- [SDK下载](https://help.aliyun.com/document_detail/120611.html)
