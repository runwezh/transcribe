"""
阿里云语音识别配置文件
"""
import os
from typing import Dict, Any
from pathlib import Path

class AliyunConfig:
    """阿里云语音识别配置类"""

    def __init__(self):
        # 首先尝试加载 .env 文件
        self._load_env_file()

        # 阿里云访问凭证 - 从环境变量获取
        self.access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID', '')
        self.access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET', '')
        
        # 服务地址配置
        self.region = os.getenv('ALIYUN_REGION', 'cn-shanghai')
        self.endpoint = f'https://nls-meta.{self.region}.aliyuncs.com'
        
        # OSS 配置
        self.oss_bucket = os.getenv('ALIYUN_OSS_BUCKET', '')

        # 从环境变量获取AppKey，如果不存在则使用 'default' 作为后备
        self.appkey = os.getenv('ALIYUN_APPKEY', 'default')

        # 录音文件识别配置
        self.file_recognition_config = {
            'appkey': self.appkey, # 您项目的Appkey
            'format': 'wav',  # 支持格式: wav, mp3, aac, m4a, wma, flac
            'sample_rate': 16000,  # 采样率: 8000, 16000
            'language': 'zh-CN',  # 识别语言, zh-CN, en-US
            'enable_words': True,  # 开启逐字时间戳
            'enable_subtitle': True,  # 开启字幕功能
            'max_single_segment_time': 60000,  # 单段最大时长(毫秒)
            'vocabulary_id': '',  # 热词表ID(可选)
            'oss_bucket': self.oss_bucket, # 存储音频文件的OSS Bucket名称
        }
        
        # 实时语音识别配置
        self.realtime_config = {
            'format': 'pcm',
            'sample_rate': 16000,
            'enable_intermediate_result': True,  # 开启中间结果
            'enable_punctuation_prediction': True,  # 开启标点预测
            'enable_inverse_text_normalization': True,  # 开启ITN
            'enable_words': True,  # 开启逐字时间戳
            'max_sentence_silence': 800,  # 句子间最大静音时长(毫秒)
            'vocabulary_id': '',  # 热词表ID(可选)
        }
        
        # 一句话识别配置
        self.sentence_config = {
            'appkey': self.appkey, # 您项目的Appkey
            'format': 'wav',
            'sample_rate': 16000,
            'language': 'zh-CN',  # 识别语言, zh-CN, en-US
            'enable_punctuation_prediction': True,
            'enable_inverse_text_normalization': True,
            'enable_words': True,  # 开启逐字时间戳
        }
        
        # 输出配置
        self.output_config = {
            'output_dir': 'output',
            'create_date_subdir': True,
            'supported_formats': ['srt', 'vtt', 'lrc', 'txt', 'json'],
            'default_encoding': 'utf-8',
        }
        
        # 日志配置
        self.log_config = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'aliyun_asr.log',
        }
    
    def validate_config(self) -> bool:
        """验证配置是否完整"""
        if not self.access_key_id or not self.access_key_secret:
            print("错误: 请设置环境变量 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET")
            return False
        return True
    
    def get_service_config(self, service_type: str) -> Dict[str, Any]:
        """获取指定服务的配置"""
        config_map = {
            'file': self.file_recognition_config,
            'realtime': self.realtime_config,
            'sentence': self.sentence_config,
        }
        return config_map.get(service_type, {})
    
    def update_config(self, service_type: str, **kwargs):
        """更新指定服务的配置"""
        if service_type == 'file':
            self.file_recognition_config.update(kwargs)
        elif service_type == 'realtime':
            self.realtime_config.update(kwargs)
        elif service_type == 'sentence':
            self.sentence_config.update(kwargs)
        elif service_type == 'output':
            self.output_config.update(kwargs)
        elif service_type == 'log':
            self.log_config.update(kwargs)

    def _load_env_file(self):
        """加载 .env 文件中的环境变量"""
        env_file = Path(__file__).parent / '.env'

        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()

                            # 移除引号（如果有的话）
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]

                            # 只有当环境变量不存在时才设置
                            if not os.getenv(key):
                                os.environ[key] = value

            except Exception as e:
                print(f"警告: 读取 .env 文件失败: {e}")

# 全局配置实例
config = AliyunConfig()
