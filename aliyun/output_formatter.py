"""
阿里云语音识别结果输出格式化模块
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from config import config

class OutputFormatter:
    """输出格式化器"""
    
    def __init__(self):
        self.config = config
    
    def format_timestamp_for_srt(self, seconds: float) -> str:
        """格式化SRT时间戳"""
        ms = int((seconds - int(seconds)) * 1000)
        td = timedelta(seconds=int(seconds))
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"
    
    def format_timestamp_for_vtt(self, seconds: float) -> str:
        """格式化VTT时间戳"""
        ms = int((seconds - int(seconds)) * 1000)
        td = timedelta(seconds=int(seconds))
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"
    
    def format_timestamp_for_lrc(self, seconds: float) -> str:
        """格式化LRC时间戳"""
        minutes = int(seconds // 60)
        sec = seconds - minutes * 60
        return f"[{minutes:02d}:{sec:05.2f}]"
    
    def generate_srt(self, segments: List[Dict[str, Any]]) -> str:
        """生成SRT格式字幕"""
        srt_output = ""
        
        for i, segment in enumerate(segments, 1):
            text = segment.get('text', '').strip()
            if not text:
                continue
                
            # 使用句子级时间戳
            start_time = segment.get('start_time', 0)
            end_time = segment.get('end_time', start_time + 2)
            
            start_str = self.format_timestamp_for_srt(start_time)
            end_str = self.format_timestamp_for_srt(end_time)
            
            srt_output += f"{i}\n{start_str} --> {end_str}\n{text}\n\n"
        
        return srt_output
    
    def generate_word_level_srt(self, segments: List[Dict[str, Any]]) -> str:
        """生成逐字级SRT格式字幕"""
        srt_output = ""
        subtitle_index = 1
        
        for segment in segments:
            words = segment.get('words', [])
            if not words:
                continue
            
            # 将词语按时间分组，每组3-5个词
            word_groups = []
            current_group = []
            
            for word in words:
                current_group.append(word)
                if len(current_group) >= 4:  # 每组4个词
                    word_groups.append(current_group)
                    current_group = []
            
            if current_group:  # 添加剩余的词
                word_groups.append(current_group)
            
            # 为每组生成字幕
            for group in word_groups:
                if not group:
                    continue
                
                text = ''.join([w.get('text', '') for w in group])
                start_time = group[0].get('start_time', 0)
                end_time = group[-1].get('end_time', start_time + 1)
                
                start_str = self.format_timestamp_for_srt(start_time)
                end_str = self.format_timestamp_for_srt(end_time)
                
                srt_output += f"{subtitle_index}\n{start_str} --> {end_str}\n{text}\n\n"
                subtitle_index += 1
        
        return srt_output
    
    def generate_vtt(self, segments: List[Dict[str, Any]]) -> str:
        """生成VTT格式字幕"""
        vtt_output = "WEBVTT\n\n"
        
        for i, segment in enumerate(segments, 1):
            text = segment.get('text', '').strip()
            if not text:
                continue
                
            start_time = segment.get('start_time', 0)
            end_time = segment.get('end_time', start_time + 2)
            
            start_str = self.format_timestamp_for_vtt(start_time)
            end_str = self.format_timestamp_for_vtt(end_time)
            
            vtt_output += f"{i}\n{start_str} --> {end_str}\n{text}\n\n"
        
        return vtt_output
    
    def generate_lrc(self, segments: List[Dict[str, Any]]) -> str:
        """生成LRC格式歌词"""
        lrc_output = ""
        
        # 添加LRC头信息
        lrc_output += "[ti:语音转录结果]\n"
        lrc_output += f"[ar:阿里云语音识别]\n"
        lrc_output += f"[al:转录文件]\n"
        lrc_output += f"[by:阿里云ASR]\n"
        lrc_output += f"[offset:0]\n\n"
        
        for segment in segments:
            text = segment.get('text', '').strip()
            if not text:
                continue
                
            start_time = segment.get('start_time', 0)
            timestamp = self.format_timestamp_for_lrc(start_time)
            lrc_output += f"{timestamp}{text}\n"
        
        return lrc_output
    
    def generate_word_level_lrc(self, segments: List[Dict[str, Any]]) -> str:
        """生成逐字级LRC格式"""
        lrc_output = ""
        
        # 添加LRC头信息
        lrc_output += "[ti:语音转录结果(逐字)]\n"
        lrc_output += f"[ar:阿里云语音识别]\n"
        lrc_output += f"[al:转录文件]\n"
        lrc_output += f"[by:阿里云ASR]\n"
        lrc_output += f"[offset:0]\n\n"
        
        for segment in segments:
            words = segment.get('words', [])
            for word in words:
                text = word.get('text', '').strip()
                if not text:
                    continue
                    
                start_time = word.get('start_time', 0)
                timestamp = self.format_timestamp_for_lrc(start_time)
                lrc_output += f"{timestamp}{text}\n"
        
        return lrc_output
    
    def generate_txt(self, segments: List[Dict[str, Any]]) -> str:
        """生成纯文本格式"""
        txt_output = ""
        
        for segment in segments:
            text = segment.get('text', '').strip()
            if text:
                txt_output += text + "\n"
        
        return txt_output
    
    def generate_json(self, segments: List[Dict[str, Any]], include_metadata: bool = True) -> str:
        """生成JSON格式"""
        output_data = {
            'segments': segments
        }
        
        if include_metadata:
            output_data['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'total_segments': len(segments),
                'total_duration': max([s.get('end_time', 0) for s in segments]) if segments else 0,
                'service': 'aliyun_asr',
                'version': '1.0'
            }
        
        return json.dumps(output_data, ensure_ascii=False, indent=2)
    
    def save_output(self, segments: List[Dict[str, Any]], input_filename: str, 
                   output_dir: str, formats: List[str] = None) -> Dict[str, str]:
        """保存输出文件"""
        if formats is None:
            formats = self.config.output_config['supported_formats']
        
        # 创建输出目录
        if self.config.output_config['create_date_subdir']:
            date_subdir = datetime.now().strftime("%Y%m%d")
            output_dir = os.path.join(output_dir, date_subdir)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取基础文件名
        base_name = os.path.splitext(os.path.basename(input_filename))[0]
        
        saved_files = {}
        
        # 生成各种格式
        format_generators = {
            'srt': self.generate_srt,
            'vtt': self.generate_vtt,
            'lrc': self.generate_lrc,
            'txt': self.generate_txt,
            'json': self.generate_json,
        }
        
        for format_name in formats:
            if format_name not in format_generators:
                continue
            
            generator = format_generators[format_name]
            content = generator(segments)
            
            output_path = os.path.join(output_dir, f"{base_name}.{format_name}")
            
            try:
                with open(output_path, 'w', encoding=self.config.output_config['default_encoding']) as f:
                    f.write(content)
                saved_files[format_name] = output_path
            except Exception as e:
                print(f"保存{format_name}文件失败: {e}")
        
        # 生成逐字级格式（如果支持）
        if 'srt_words' in formats:
            content = self.generate_word_level_srt(segments)
            output_path = os.path.join(output_dir, f"{base_name}_words.srt")
            try:
                with open(output_path, 'w', encoding=self.config.output_config['default_encoding']) as f:
                    f.write(content)
                saved_files['srt_words'] = output_path
            except Exception as e:
                print(f"保存逐字SRT文件失败: {e}")
        
        if 'lrc_words' in formats:
            content = self.generate_word_level_lrc(segments)
            output_path = os.path.join(output_dir, f"{base_name}_words.lrc")
            try:
                with open(output_path, 'w', encoding=self.config.output_config['default_encoding']) as f:
                    f.write(content)
                saved_files['lrc_words'] = output_path
            except Exception as e:
                print(f"保存逐字LRC文件失败: {e}")
        
        return saved_files
