"""
通用工具模块
"""
import os
import logging
from typing import Optional
import oss2
from config import config

def upload_to_oss(local_file_path: str) -> str:
    """
    将本地文件上传到阿里云OSS

    Args:
        local_file_path (str): 本地文件的完整路径

    Returns:
        str: 上传成功后文件的OSS URL

    Raises:
        Exception: 如果上传失败
    """
    logger = logging.getLogger('OSS_Uploader')
    
    # 从配置中获取OSS信息
    access_key_id = config.access_key_id
    access_key_secret = config.access_key_secret
    bucket_name = config.oss_bucket
    region = config.region
    
    if not all([access_key_id, access_key_secret, bucket_name, region]):
        raise ValueError("OSS配置不完整 (AK, SK, Bucket, Region都需要)")

    # OSS endpoint 通常是 oss-cn-beijing.aliyuncs.com 格式
    endpoint = f'oss-{region}.aliyuncs.com'
    
    # 创建Bucket实例
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    
    # 定义上传后的对象名
    object_name = os.path.basename(local_file_path)
    
    logger.info(f"准备上传文件 '{local_file_path}' 到OSS Bucket '{bucket_name}'...")
    
    try:
        # 执行上传
        result = bucket.put_object_from_file(object_name, local_file_path)
        
        if result.status != 200:
            raise Exception(f"上传失败，HTTP状态码: {result.status}")
            
        # 构建文件URL
        # 注意：这里的URL格式需要根据你的Bucket权限设置（公开/私有）
        # 这里我们构建一个标准的https地址
        file_url = f"https://{bucket_name}.{endpoint}/{object_name}"
        
        logger.info(f"文件上传成功！URL: {file_url}")
        return file_url

    except oss2.exceptions.OssError as e:
        logger.error(f"上传到OSS时发生错误: {e}")
        raise
    except Exception as e:
        logger.error(f"上传过程中发生未知错误: {e}")
        raise

def get_audio_info(file_path: str) -> Optional[dict]:
    """
    使用pydub获取音频文件的基本信息
    """
    try:
        from pydub import AudioSegment
        from pydub.utils import mediainfo

        info = mediainfo(file_path)
        audio = AudioSegment.from_file(file_path)
        
        return {
            'duration': audio.duration_seconds,
            'sample_rate': int(info.get('sample_rate', 0)),
            'channels': int(info.get('channels', 0)),
            'codec': info.get('codec_name'),
        }
    except Exception as e:
        logging.getLogger('AudioInfo').error(f"获取音频信息失败: {e}")
        return None
