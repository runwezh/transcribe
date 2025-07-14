#!/usr/bin/env python3
"""
阿里云语音识别主程序
"""
import os
import sys
import argparse
import logging
from typing import List
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aliyun_asr import AliyunASRClient
from output_formatter import OutputFormatter
from config import config

class AliyunTranscriber:
    """阿里云转录器主类"""

    def __init__(self, use_mock=True):
        """
        初始化转录器

        Args:
            use_mock (bool): 是否使用模拟模式
        """
        self.asr_client = AliyunASRClient(use_mock=use_mock)
        self.formatter = OutputFormatter()
        self.logger = logging.getLogger('AliyunTranscriber')
    
    def is_audio_file(self, file_path: str) -> bool:
        """检查是否为支持的音频文件"""
        audio_extensions = ['.wav', '.mp3', '.aac', '.m4a', '.wma', '.flac', '.pcm']
        return Path(file_path).suffix.lower() in audio_extensions
    
    def process_file(self, input_path: str, mode: str, output_dir: str, 
                    formats: List[str]) -> bool:
        """处理单个文件"""
        try:
            self.logger.info(f"开始处理文件: {input_path} (模式: {mode})")
            
            if not os.path.exists(input_path):
                self.logger.error(f"文件不存在: {input_path}")
                return False
            
            if not self.is_audio_file(input_path):
                self.logger.error(f"不支持的文件格式: {input_path}")
                return False
            
            # 根据模式选择识别方法
            if mode == 'file':
                segments = self.asr_client.recognize_file(input_path)
            elif mode == 'sentence':
                segment = self.asr_client.recognize_sentence(input_path)
                segments = [segment] if segment else []
            else:
                self.logger.error(f"不支持的识别模式: {mode}")
                return False
            
            if not segments:
                self.logger.warning(f"未识别到任何内容: {input_path}")
                return False
            
            # 保存输出文件
            saved_files = self.formatter.save_output(
                segments, input_path, output_dir, formats
            )
            
            self.logger.info(f"文件处理完成: {input_path}")
            for format_name, file_path in saved_files.items():
                self.logger.info(f"  {format_name.upper()}: {file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"处理文件时出错 {input_path}: {str(e)}")
            return False
    
    def process_files(self, input_paths: List[str], mode: str, output_dir: str, 
                     formats: List[str]) -> None:
        """批量处理文件"""
        if not config.validate_config():
            self.logger.error("配置验证失败，请检查环境变量设置")
            return
        
        total_files = len(input_paths)
        success_count = 0
        
        self.logger.info(f"开始批量处理，共 {total_files} 个文件")
        self.logger.info(f"识别模式: {mode}")
        self.logger.info(f"输出目录: {output_dir}")
        self.logger.info(f"输出格式: {', '.join(formats)}")
        
        for i, input_path in enumerate(input_paths, 1):
            self.logger.info(f"\n[{i}/{total_files}] 处理文件: {input_path}")
            
            if self.process_file(input_path, mode, output_dir, formats):
                success_count += 1
            
            # 显示进度
            progress = (i / total_files) * 100
            self.logger.info(f"进度: {progress:.1f}% ({i}/{total_files})")
        
        self.logger.info(f"\n批量处理完成！")
        self.logger.info(f"成功: {success_count}/{total_files}")
        if success_count < total_files:
            self.logger.warning(f"失败: {total_files - success_count}/{total_files}")


def setup_logging(log_level: str = 'INFO'):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('aliyun_transcribe.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='阿里云语音识别工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 录音文件识别
  python aliyun_transcribe.py --mode file audio.wav
  
  # 一句话识别
  python aliyun_transcribe.py --mode sentence short_audio.wav
  
  # 批量处理
  python aliyun_transcribe.py --mode file audio1.wav audio2.mp3
  
  # 指定输出格式
  python aliyun_transcribe.py --mode file --formats srt,vtt,json audio.wav
  
  # 指定输出目录
  python aliyun_transcribe.py --mode file --output-dir /path/to/output audio.wav

环境变量设置:
  export ALIYUN_ACCESS_KEY_ID="your_access_key_id"
  export ALIYUN_ACCESS_KEY_SECRET="your_access_key_secret"
  export ALIYUN_REGION="cn-shanghai"
        """
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        help='输入音频文件路径'
    )
    
    parser.add_argument(
        '--mode',
        choices=['file', 'sentence'],
        default='file',
        help='识别模式 (默认: file)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='output',
        help='输出目录 (默认: output)'
    )
    
    parser.add_argument(
        '--formats',
        default='srt,vtt,txt,json',
        help='输出格式，用逗号分隔 (默认: srt,vtt,txt,json)'
    )
    
    parser.add_argument(
        '--sample-rate',
        type=int,
        choices=[8000, 16000],
        default=16000,
        help='音频采样率 (默认: 16000)'
    )

    parser.add_argument(
        '--lang',
        default='zh-CN',
        help='识别语言 (例如: zh-CN, en-US) (默认: zh-CN)'
    )
    
    parser.add_argument(
        '--use-mock',
        action='store_true',
        help='使用模拟模式，不调用真实API'
    )

    parser.add_argument(
        '--oss-bucket',
        help='用于存储音频文件的阿里云OSS Bucket名称'
    )
    
    parser.add_argument(
        '--vocabulary-id',
        help='热词表ID'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='阿里云语音识别工具 v1.0.0'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    
    # 解析输出格式
    formats = [f.strip() for f in args.formats.split(',')]
    
    # 更新配置
    file_config_updates = {
        'sample_rate': args.sample_rate,
        'language': args.lang,
        'vocabulary_id': args.vocabulary_id,
    }
    if args.oss_bucket:
        file_config_updates['oss_bucket'] = args.oss_bucket
    
    config.update_config('file', **file_config_updates)
    
    config.update_config('sentence', 
        sample_rate=args.sample_rate,
        language=args.lang,
        vocabulary_id=args.vocabulary_id
    )
    
    # 创建转录器并处理文件
    transcriber = AliyunTranscriber(use_mock=args.use_mock)
    transcriber.process_files(args.input_files, args.mode, args.output_dir, formats)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        logging.error(f"程序异常退出: {e}")
        sys.exit(1)
