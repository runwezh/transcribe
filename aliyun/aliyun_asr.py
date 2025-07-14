"""
阿里云语音识别统一客户端
支持真实API调用和模拟调用两种模式
使用阿里云官方SDK (aliyun-python-sdk-core)
"""
import json
import time
import logging
import os
from typing import Dict, List, Any

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException

from config import config
from utils import upload_to_oss

class AliyunASRClient:
    """阿里云语音识别客户端（SDK版本）"""
    
    def __init__(self, use_mock=False):
        """
        初始化客户端
        
        Args:
            use_mock (bool): 是否使用模拟模式。True=模拟调用，False=真实API调用
        """
        self.config = config
        self.use_mock = use_mock
        self.logger = self._setup_logger()
        
        if use_mock:
            self.logger.info("使用模拟模式，将生成示例识别结果")
        else:
            self.logger.info("使用真实API模式（基于aliyun-python-sdk-core）")
            if not self.config.validate_config():
                raise ValueError("真实API模式下，必须配置阿里云AK/SK")
            if not self.config.appkey or self.config.appkey == 'default':
                raise ValueError("真实API模式下，必须配置有效的ALIYUN_APPKEY")
            
            self.client = AcsClient(
                self.config.access_key_id,
                self.config.access_key_secret,
                self.config.region
            )

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('AliyunASR_SDK')
        logger.setLevel(getattr(logging, self.config.log_config['level']))
        
        if not logger.handlers:
            file_handler = logging.FileHandler(self.config.log_config['file'], encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(self.config.log_config['format']))
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger

    def _generate_mock_result(self, audio_file_path: str) -> List[Dict[str, Any]]:
        """生成模拟识别结果"""
        filename = os.path.basename(audio_file_path).lower()
        
        if 'club' in filename:
            text = 'Tonight we are going to the club, the music there is great.'
            words_data = [
                ('Tonight', 0.0, 0.5), ('we', 0.5, 0.7), ('are', 0.7, 0.9), ('going', 0.9, 1.3),
                ('to', 1.3, 1.4), ('the', 1.4, 1.6), ('club', 1.6, 2.1), (',', 2.1, 2.2),
                ('the', 2.2, 2.4), ('music', 2.4, 2.8), ('there', 2.8, 3.0), ('is', 3.0, 3.2),
                ('great', 3.2, 3.7), ('.', 3.7, 3.8)
            ]
        else:
            text = 'This is a successful test of Aliyun speech recognition.'
            words_data = [
                ('This', 0.0, 0.3), ('is', 0.3, 0.5), ('a', 0.5, 0.6), ('successful', 0.6, 1.2),
                ('test', 1.2, 1.6), ('of', 1.6, 1.8), ('Aliyun', 1.8, 2.3), ('speech', 2.3, 2.7),
                ('recognition', 2.7, 3.5), ('.', 3.5, 3.6)
            ]
        
        words = [{'text': w, 'start_time': s, 'end_time': e, 'confidence': 0.95} for w, s, e in words_data]
        
        return [{'text': text, 'confidence': 0.94, 'words': words, 'start_time': 0.0, 'end_time': 3.8}]

    def recognize_sentence(self, audio_file_path: str) -> Dict[str, Any]:
        """一句话识别（适合60秒以内的短音频）"""
        if self.use_mock:
            time.sleep(0.5)
            # _generate_mock_result returns a list, get the first element for sentence recognition
            result = self._generate_mock_result(audio_file_path)[0]
            self.logger.info(f'模拟一句话识别完成: {result["text"]}')
            return result
        
        return self._real_api_recognize_sentence(audio_file_path)

    def _real_api_recognize_sentence(self, audio_file_path: str) -> Dict[str, Any]:
        """真实的一句话识别API调用（当前版本未完全实现）"""
        self.logger.error("真实API的'一句话识别'功能需要不同的API实现，当前版本暂未支持。")
        raise NotImplementedError("真实'一句话识别'API调用功能待实现。")

    def recognize_file(self, audio_file_path: str) -> List[Dict[str, Any]]:
        """录音文件识别（适合长音频）"""
        if self.use_mock:
            time.sleep(1)
            segments = self._generate_mock_result(audio_file_path)
            self.logger.info(f'模拟文件识别完成，共 {len(segments)} 段')
            return segments
            
        return self._real_api_recognize_file(audio_file_path)

    def _real_api_recognize_file(self, audio_file_path: str) -> List[Dict[str, Any]]:
        """真实的文件识别API调用（使用官方SDK）"""
        self.logger.info(f'开始真实文件识别: {audio_file_path}')
        
        # API常量，根据官方文档
        PRODUCT = "nls-filetrans"
        DOMAIN = f"filetrans.{self.config.region}.aliyuncs.com"
        API_VERSION = "2018-08-17"
        POST_REQUEST_ACTION = "SubmitTask"
        GET_REQUEST_ACTION = "GetTaskResult"

        try:
            file_link = upload_to_oss(audio_file_path)
        except Exception as e:
            self.logger.error(f"上传文件到OSS失败: {e}")
            return []

        # 1. 提交任务
        post_request = CommonRequest()
        post_request.set_domain(DOMAIN)
        post_request.set_version(API_VERSION)
        post_request.set_product(PRODUCT)
        post_request.set_action_name(POST_REQUEST_ACTION)
        post_request.set_method('POST')

        task_payload = {
            'appkey': self.config.appkey,
            'file_link': file_link,
            'version': '4.0',
            'enable_words': self.config.file_recognition_config.get('enable_words', False),
            'enable_sample_rate_adaptive': True, # 自动适配采样率
        }
        task_json = json.dumps(task_payload)
        post_request.add_body_params("Task", task_json)

        task_id = ""
        try:
            post_response = self.client.do_action_with_exception(post_request)
            post_response_data = json.loads(post_response)
            self.logger.debug(f"提交任务响应: {post_response_data}")
            
            if post_response_data.get('StatusText') == 'SUCCESS':
                task_id = post_response_data.get('TaskId')
                self.logger.info(f"任务提交成功, TaskId: {task_id}")
            else:
                raise Exception(f"提交任务失败: {post_response_data}")
        except (ClientException, ServerException) as e:
            self.logger.error(f"提交任务时发生SDK异常: {e}")
            return []

        if not task_id:
            return []

        # 2. 轮询结果
        get_request = CommonRequest()
        get_request.set_domain(DOMAIN)
        get_request.set_version(API_VERSION)
        get_request.set_product(PRODUCT)
        get_request.set_action_name(GET_REQUEST_ACTION)
        get_request.set_method('GET')
        get_request.add_query_param("TaskId", task_id)

        while True:
            try:
                self.logger.info("等待10秒后查询任务状态...")
                time.sleep(10)
                get_response = self.client.do_action_with_exception(get_request)
                get_response_data = json.loads(get_response)
                self.logger.debug(f"查询任务响应: {get_response_data}")

                status_text = get_response_data.get('StatusText')
                if status_text in ['RUNNING', 'QUEUEING']:
                    self.logger.info(f"任务仍在处理中... (状态: {status_text})")
                    continue
                
                if status_text == 'SUCCESS':
                    self.logger.info("任务处理成功")
                    result = get_response_data.get('Result', {})
                    return self._format_file_result(result)
                
                raise Exception(f"任务处理失败，状态: {status_text}, 响应: {get_response_data}")

            except (ClientException, ServerException) as e:
                self.logger.error(f"查询任务时发生SDK异常: {e}")
                break
        
        return []

    def _format_file_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化文件识别的API返回结果"""
        sentences = result.get('Sentences', [])
        if not sentences:
            return []
            
        formatted_segments = []
        all_words = result.get('Words', [])

        for sentence in sentences:
            words_list = []
            if all_words:
                # 根据文档，词信息和句子是分开的，需要自己匹配
                for word_info in all_words:
                     if sentence.get('BeginTime') <= word_info.get('BeginTime') and word_info.get('EndTime') <= sentence.get('EndTime'):
                        words_list.append({
                            'text': word_info.get('Word'),
                            'start_time': word_info.get('BeginTime') / 1000.0,
                            'end_time': word_info.get('EndTime') / 1000.0,
                            'confidence': -1
                        })
            
            formatted_segments.append({
                'text': sentence.get('Text'),
                'start_time': sentence.get('BeginTime') / 1000.0,
                'end_time': sentence.get('EndTime') / 1000.0,
                'confidence': sentence.get('Confidence', -1) if 'Confidence' in sentence else -1,
                'words': words_list,
            })
            
        return formatted_segments
