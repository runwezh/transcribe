#!/usr/bin/env python3
"""
阿里云语音识别测试脚本
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from aliyun_asr import AliyunASRClient
from output_formatter import OutputFormatter
from utils import validate_audio_file, format_duration, estimate_cost

class TestAliyunASRConfig(unittest.TestCase):
    """测试配置类"""
    
    def test_config_validation(self):
        """测试配置验证"""
        # 保存原始配置
        original_key_id = config.access_key_id
        original_key_secret = config.access_key_secret
        
        try:
            # 测试空配置
            config.access_key_id = ''
            config.access_key_secret = ''
            self.assertFalse(config.validate_config())
            
            # 测试有效配置
            config.access_key_id = 'test_key_id'
            config.access_key_secret = 'test_key_secret'
            self.assertTrue(config.validate_config())
            
        finally:
            # 恢复原始配置
            config.access_key_id = original_key_id
            config.access_key_secret = original_key_secret
    
    def test_service_config(self):
        """测试服务配置获取"""
        file_config = config.get_service_config('file')
        self.assertIn('format', file_config)
        self.assertIn('sample_rate', file_config)
        self.assertIn('enable_words', file_config)
        
        realtime_config = config.get_service_config('realtime')
        self.assertIn('format', realtime_config)
        self.assertIn('enable_intermediate_result', realtime_config)

class TestOutputFormatter(unittest.TestCase):
    """测试输出格式化器"""
    
    def setUp(self):
        self.formatter = OutputFormatter()
        self.sample_segments = [
            {
                'text': '你好，欢迎使用阿里云语音识别',
                'start_time': 0.0,
                'end_time': 2.5,
                'confidence': 0.95,
                'words': [
                    {'text': '你', 'start_time': 0.0, 'end_time': 0.2, 'confidence': 0.98},
                    {'text': '好', 'start_time': 0.2, 'end_time': 0.4, 'confidence': 0.97},
                    {'text': '，', 'start_time': 0.4, 'end_time': 0.5, 'confidence': 0.90},
                    {'text': '欢', 'start_time': 0.5, 'end_time': 0.7, 'confidence': 0.96},
                    {'text': '迎', 'start_time': 0.7, 'end_time': 0.9, 'confidence': 0.95},
                ]
            },
            {
                'text': '这是一个测试音频文件',
                'start_time': 2.5,
                'end_time': 5.0,
                'confidence': 0.92,
                'words': [
                    {'text': '这', 'start_time': 2.5, 'end_time': 2.7, 'confidence': 0.94},
                    {'text': '是', 'start_time': 2.7, 'end_time': 2.9, 'confidence': 0.93},
                    {'text': '一', 'start_time': 2.9, 'end_time': 3.1, 'confidence': 0.91},
                    {'text': '个', 'start_time': 3.1, 'end_time': 3.3, 'confidence': 0.92},
                ]
            }
        ]
    
    def test_srt_generation(self):
        """测试SRT格式生成"""
        srt_content = self.formatter.generate_srt(self.sample_segments)
        
        self.assertIn('1\n00:00:00,000 --> 00:00:02,500', srt_content)
        self.assertIn('你好，欢迎使用阿里云语音识别', srt_content)
        self.assertIn('2\n00:00:02,500 --> 00:00:05,000', srt_content)
        self.assertIn('这是一个测试音频文件', srt_content)
    
    def test_vtt_generation(self):
        """测试VTT格式生成"""
        vtt_content = self.formatter.generate_vtt(self.sample_segments)
        
        self.assertTrue(vtt_content.startswith('WEBVTT'))
        self.assertIn('00:00:00.000 --> 00:00:02.500', vtt_content)
        self.assertIn('你好，欢迎使用阿里云语音识别', vtt_content)
    
    def test_lrc_generation(self):
        """测试LRC格式生成"""
        lrc_content = self.formatter.generate_lrc(self.sample_segments)
        
        self.assertIn('[ti:语音转录结果]', lrc_content)
        self.assertIn('[00:00.00]你好，欢迎使用阿里云语音识别', lrc_content)
        self.assertIn('[00:02.50]这是一个测试音频文件', lrc_content)
    
    def test_json_generation(self):
        """测试JSON格式生成"""
        import json
        
        json_content = self.formatter.generate_json(self.sample_segments)
        data = json.loads(json_content)
        
        self.assertIn('segments', data)
        self.assertIn('metadata', data)
        self.assertEqual(len(data['segments']), 2)
        self.assertEqual(data['metadata']['total_segments'], 2)
    
    def test_txt_generation(self):
        """测试TXT格式生成"""
        txt_content = self.formatter.generate_txt(self.sample_segments)
        
        self.assertIn('你好，欢迎使用阿里云语音识别', txt_content)
        self.assertIn('这是一个测试音频文件', txt_content)

class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_validate_audio_file(self):
        """测试音频文件验证"""
        # 测试不存在的文件
        valid, message = validate_audio_file('nonexistent.wav')
        self.assertFalse(valid)
        self.assertIn('不存在', message)
        
        # 创建临时文件测试
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(b'fake audio data')
            tmp_path = tmp.name
        
        try:
            valid, message = validate_audio_file(tmp_path)
            self.assertTrue(valid)
            self.assertEqual(message, '文件验证通过')
        finally:
            os.unlink(tmp_path)
        
        # 测试不支持的格式
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'not audio')
            tmp_path = tmp.name
        
        try:
            valid, message = validate_audio_file(tmp_path)
            self.assertFalse(valid)
            self.assertIn('不支持的文件格式', message)
        finally:
            os.unlink(tmp_path)
    
    def test_format_duration(self):
        """测试时长格式化"""
        self.assertEqual(format_duration(30), '30.0秒')
        self.assertEqual(format_duration(90), '1分30.0秒')
        self.assertEqual(format_duration(3661), '1小时1分1.0秒')
    
    def test_estimate_cost(self):
        """测试成本估算"""
        cost_info = estimate_cost(3600, 'file')  # 1小时
        
        self.assertEqual(cost_info['duration_hours'], 1.0)
        self.assertEqual(cost_info['service_type'], 'file')
        self.assertEqual(cost_info['estimated_cost'], 2.50)
        self.assertEqual(cost_info['currency'], 'CNY')

class TestAliyunASRClient(unittest.TestCase):
    """测试阿里云ASR客户端"""
    
    def setUp(self):
        self.client = AliyunASRClient()
    
    @patch('aliyun_asr.requests.post')
    def test_make_request(self, mock_post):
        """测试API请求"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.json.return_value = {'Code': '20000000', 'Data': {'TaskId': 'test_task_id'}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 设置测试配置
        self.client.config.access_key_id = 'test_key_id'
        self.client.config.access_key_secret = 'test_key_secret'
        
        result = self.client._make_request('CreateTask', {'test': 'param'})
        
        self.assertEqual(result['Code'], '20000000')
        self.assertEqual(result['Data']['TaskId'], 'test_task_id')
    
    def test_parse_recognition_result(self):
        """测试识别结果解析"""
        mock_result_data = {
            'Result': '{"Sentences": [{"Text": "测试文本", "BeginTime": 0, "EndTime": 2000, "Words": [{"Word": "测", "BeginTime": 0, "EndTime": 500, "Score": 0.95}]}]}'
        }
        
        segments = self.client.parse_recognition_result(mock_result_data)
        
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0]['text'], '测试文本')
        self.assertEqual(segments[0]['start_time'], 0.0)
        self.assertEqual(segments[0]['end_time'], 2.0)
        self.assertEqual(len(segments[0]['words']), 1)
        self.assertEqual(segments[0]['words'][0]['text'], '测')

def create_test_audio_file():
    """创建测试音频文件"""
    try:
        import numpy as np
        from scipy.io import wavfile
        
        # 生成1秒的正弦波
        sample_rate = 16000
        duration = 1.0
        frequency = 440  # A4音符
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        wavfile.write(temp_file.name, sample_rate, audio_data)
        
        return temp_file.name
    except ImportError:
        print("警告: scipy未安装，无法创建测试音频文件")
        return None

def run_integration_test():
    """运行集成测试"""
    print("🧪 运行集成测试...")
    
    # 检查配置
    if not config.validate_config():
        print("❌ 配置验证失败，跳过集成测试")
        return
    
    # 创建测试音频文件
    test_audio = create_test_audio_file()
    if not test_audio:
        print("⚠️  无法创建测试音频文件，跳过集成测试")
        return
    
    try:
        from aliyun_transcribe import AliyunTranscriber
        
        transcriber = AliyunTranscriber()
        
        # 测试一句话识别（使用较短的音频）
        print("测试一句话识别...")
        success = transcriber.process_file(
            test_audio, 'sentence', 'test_output', ['txt', 'json']
        )
        
        if success:
            print("✅ 集成测试通过")
        else:
            print("❌ 集成测试失败")
            
    except Exception as e:
        print(f"❌ 集成测试异常: {e}")
    finally:
        # 清理测试文件
        if test_audio and os.path.exists(test_audio):
            os.unlink(test_audio)

def main():
    """主函数"""
    print("🧪 阿里云语音识别测试套件")
    print("=" * 50)
    
    # 运行单元测试
    print("运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 50)
    
    # 运行集成测试
    run_integration_test()
    
    print("\n✅ 测试完成")

if __name__ == '__main__':
    main()
