# 阿里云语音识别 - 快速开始指南

## 🚀 5分钟快速上手

### 第一步：安装依赖
```bash
cd aliyun
make install
```

### 第二步：配置访问凭证
编辑 `.env` 文件，填入您的阿里云访问凭证：
```bash
nano .env
```

将以下内容替换为您的真实凭证和配置：
```
# 阿里云访问凭证
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_REGION=cn-shanghai

# 智能语音交互服务配置 (必需)
ALIYUN_APPKEY=your_app_key

# 对象存储OSS配置 (必需)
ALIYUN_OSS_BUCKET=your_oss_bucket_name
```

### 第三步：检查配置
```bash
make check
```

如果看到 "🎉 所有检查都通过了！"，说明配置成功。

### 第四步：开始使用
```bash
# 运行交互式演示（推荐）
python demo.py

# 或使用命令行工具
python aliyun_transcribe.py --mode sentence your_audio.wav

# 或使用make命令
make demo
```

## 📋 获取阿里云访问凭证

1. 登录 [阿里云控制台](https://ram.console.aliyun.com/)
2. 在[智能语音交互控制台](https://nls-portal.console.aliyun.com/applist)创建一个项目，获取**AppKey**。
3. 创建一个用于存放音频文件的[OSS Bucket](https://oss.console.aliyun.com/bucket)，并记录其名称。
4. 进入 "访问控制 RAM" → "用户"，创建新用户。
5. 为用户添加权限：`AliyunNLSFullAccess` 和 `AliyunOSSFullAccess`。
6. 为该用户创建 AccessKey，获得 AccessKey ID 和 AccessKey Secret。

## 🎯 使用场景

### 场景1：短音频识别（≤60秒）
```bash
python aliyun_transcribe.py --mode sentence short_audio.wav
```
- **成本**：按次计费，适合少量短音频
- **速度**：最快，通常几秒内完成
- **适用**：语音命令、短消息、语音备忘录

### 场景2：长音频识别
```bash
python aliyun_transcribe.py --mode file long_audio.mp3
```
- **成本**：1元/小时起（闲时版）
- **速度**：较慢，需要等待处理
- **适用**：会议录音、讲座、访谈

### 场景3：批量处理
```bash
python aliyun_transcribe.py --mode file *.wav *.mp3
```
- **成本**：按总时长计费
- **速度**：并发处理，效率高
- **适用**：大量音频文件处理

## 📄 输出格式

### 基本格式
```bash
# 生成字幕文件
python aliyun_transcribe.py --formats srt,vtt audio.wav

# 生成文本文件
python aliyun_transcribe.py --formats txt,json audio.wav

# 生成所有格式
python aliyun_transcribe.py --formats srt,vtt,lrc,txt,json audio.wav
```

### 输出文件说明
- **SRT**: 视频字幕格式，支持大多数播放器
- **VTT**: 网页字幕格式，适用于HTML5视频
- **LRC**: 歌词格式，适用于音乐播放器
- **TXT**: 纯文本，便于阅读和编辑
- **JSON**: 结构化数据，包含详细时间戳和置信度

## 💰 成本优化建议

### 大批量处理
```bash
# 使用闲时版，成本最低
python aliyun_transcribe.py --mode file --service-type idle *.wav
```

### 测试和开发
```bash
# 使用一句话识别，按次计费
python aliyun_transcribe.py --mode sentence test_audio.wav
```

### 生产环境
```bash
# 使用Paraformer模型，性价比最高
python aliyun_transcribe.py --mode file --service-type paraformer *.mp3
```

## 🔧 常见问题

### Q: 提示"配置验证失败"
**A**: 检查 `.env` 文件中的访问凭证是否正确
```bash
make check  # 运行配置检查
```

### Q: 网络连接失败
**A**: 检查网络连接和防火墙设置
```bash
ping nls.cn-shanghai.aliyuncs.com
```

### Q: 音频格式不支持
**A**: 转换为支持的格式
```bash
# 支持的格式：WAV, MP3, AAC, M4A, WMA, FLAC
ffmpeg -i input.mp4 -acodec pcm_s16le -ar 16000 -ac 1 output.wav
```

### Q: 识别准确率低
**A**: 优化音频质量
- 使用16kHz采样率
- 单声道音频
- 减少背景噪音
- 考虑使用热词功能

## 📚 更多资源

- [完整文档](README.md)
- [API参考](https://help.aliyun.com/document_detail/84435.html)
- [阿里云控制台](https://nls.console.aliyun.com/)
- [定价说明](https://www.aliyun.com/price/product#/nls/detail)

## 🆘 获取帮助

如果遇到问题：

1. 运行 `make check` 检查配置
2. 查看日志文件 `aliyun_asr.log`
3. 运行 `make test` 进行诊断
4. 参考 [阿里云文档](https://help.aliyun.com/product/30413.html)

---

**🎉 现在您已经可以开始使用阿里云语音识别服务了！**
