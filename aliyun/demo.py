#!/usr/bin/env python3
"""
阿里云语音识别统一演示程序
"""
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aliyun_asr import AliyunASRClient
from output_formatter import OutputFormatter
from utils import get_audio_info, format_duration, estimate_cost

class AliyunTranscriber:
    """阿里云转录器"""
    
    def __init__(self, use_mock=True):
        """
        初始化转录器
        
        Args:
            use_mock (bool): 是否使用模拟模式
        """
        self.asr_client = AliyunASRClient(use_mock=use_mock)
        self.formatter = OutputFormatter()
        self.use_mock = use_mock
    
    def process_file(self, input_path: str, mode: str, output_dir: str, 
                    formats: list) -> bool:
        """处理单个文件"""
        try:
            print(f"🚀 开始处理文件: {os.path.basename(input_path)} (模式: {mode})")
            
            if not os.path.exists(input_path):
                print(f"❌ 文件不存在: {input_path}")
                return False
            
            # 显示文件信息
            audio_info = get_audio_info(input_path)
            if audio_info:
                print(f"📊 音频信息: 时长 {format_duration(audio_info['duration'])}, "
                      f"采样率 {audio_info['sample_rate']}Hz")
                
                # 成本估算
                cost_info = estimate_cost(audio_info['duration'], mode)
                print(f"💰 预估成本: {cost_info['estimated_cost']:.4f} 元 "
                      f"({cost_info['service_type']} 模式)")
            
            # 根据模式选择识别方法
            if mode == 'sentence':
                segment = self.asr_client.recognize_sentence(input_path)
                segments = [segment] if segment else []
            elif mode == 'file':
                segments = self.asr_client.recognize_file(input_path)
            else:
                print(f"❌ 不支持的识别模式: {mode}")
                return False
            
            if not segments:
                print(f"⚠️  未识别到任何内容: {input_path}")
                return False
            
            # 显示识别结果
            print(f"✅ 识别完成，共 {len(segments)} 段内容:")
            for i, segment in enumerate(segments, 1):
                text = segment.get('text', '')
                confidence = segment.get('confidence', 0)
                print(f"   {i}. {text} (置信度: {confidence:.2f})")
            
            # 保存输出文件
            print("📄 生成输出文件...")
            saved_files = self.formatter.save_output(
                segments, input_path, output_dir, formats
            )
            
            print("✅ 文件处理完成！生成的文件:")
            for format_name, file_path in saved_files.items():
                print(f"   {format_name.upper()}: {file_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ 处理文件时出错 {input_path}: {str(e)}")
            return False

def print_banner():
    """打印横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    阿里云语音识别演示                          ║
║                                                              ║
║  基于阿里云智能语音交互服务的语音转文字解决方案                ║
║  支持录音文件识别、一句话识别和逐字时间戳                      ║
║  提供多种输出格式：SRT、VTT、LRC、TXT、JSON                   ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def find_audio_files():
    """查找音频文件"""
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    
    audio_files = []
    for pattern in ['*.wav', '*.mp3', '*.m4a', '*.aac', '*.flac']:
        audio_files.extend(parent_dir.glob(pattern))
    
    return audio_files

def demo_sentence_recognition(transcriber):
    """演示一句话识别"""
    print("\n🗣️  一句话识别演示")
    print("-" * 40)
    print("适用于60秒以内的短音频，识别速度快，成本低")
    
    audio_files = find_audio_files()
    
    if not audio_files:
        print("❌ 未找到音频文件")
        print("请将音频文件放在项目根目录下")
        return
    
    print(f"📁 找到 {len(audio_files)} 个音频文件:")
    for i, file_path in enumerate(audio_files, 1):
        print(f"   {i}. {file_path.name}")
    
    try:
        choice = input(f"\n请选择要识别的文件编号 (1-{len(audio_files)}): ")
        file_index = int(choice) - 1
        
        if 0 <= file_index < len(audio_files):
            selected_file = audio_files[file_index]
            
            success = transcriber.process_file(
                str(selected_file),
                mode='sentence',
                output_dir='output',
                formats=['srt', 'vtt', 'txt', 'json']
            )
            
            if success:
                print("\n🎉 一句话识别演示完成！")
            else:
                print("\n❌ 识别失败")
        else:
            print("❌ 无效的选择")
            
    except ValueError:
        print("❌ 请输入有效的数字")
    except KeyboardInterrupt:
        print("\n⚠️  用户取消操作")

def demo_file_recognition(transcriber):
    """演示文件识别"""
    print("\n🎵 文件识别演示")
    print("-" * 40)
    print("适用于长音频文件，支持多段识别和详细时间戳")
    
    audio_files = find_audio_files()
    
    if not audio_files:
        print("❌ 未找到音频文件")
        return
    
    print(f"📁 找到 {len(audio_files)} 个音频文件:")
    for i, file_path in enumerate(audio_files, 1):
        print(f"   {i}. {file_path.name}")
    
    try:
        choice = input(f"\n请选择要识别的文件编号 (1-{len(audio_files)}): ")
        file_index = int(choice) - 1
        
        if 0 <= file_index < len(audio_files):
            selected_file = audio_files[file_index]
            
            success = transcriber.process_file(
                str(selected_file),
                mode='file',
                output_dir='output',
                formats=['srt', 'vtt', 'lrc', 'txt', 'json', 'srt_words']
            )
            
            if success:
                print("\n🎉 文件识别演示完成！")
            else:
                print("\n❌ 识别失败")
        else:
            print("❌ 无效的选择")
            
    except ValueError:
        print("❌ 请输入有效的数字")
    except KeyboardInterrupt:
        print("\n⚠️  用户取消操作")

def demo_batch_processing(transcriber):
    """演示批量处理"""
    print("\n🔄 批量处理演示")
    print("-" * 40)
    
    audio_files = find_audio_files()
    
    if not audio_files:
        print("❌ 未找到音频文件")
        return
    
    print(f"📁 找到 {len(audio_files)} 个音频文件，将全部处理")
    
    confirm = input("确认开始批量处理？(y/N): ")
    if confirm.lower() != 'y':
        print("⚠️  用户取消操作")
        return
    
    success_count = 0
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] 处理: {audio_file.name}")
        success = transcriber.process_file(
            str(audio_file),
            mode='file',
            output_dir='output',
            formats=['srt', 'txt', 'json']
        )
        if success:
            success_count += 1
    
    print(f"\n🎉 批量处理完成！成功: {success_count}/{len(audio_files)}")

def show_pricing_info():
    """显示定价信息"""
    print("\n💰 阿里云语音识别定价信息")
    print("-" * 40)
    
    pricing_table = [
        ("录音文件识别", "2.50元/小时", "标准价格"),
        ("录音文件识别(闲时版)", "1.00元/小时", "性价比最高"),
        ("Paraformer语音模型", "0.288元/小时", "最便宜"),
        ("实时语音识别", "3.50元/小时", "实时处理"),
        ("一句话识别", "按次计费", "短音频"),
    ]
    
    for service, price, note in pricing_table:
        print(f"  {service:<20} {price:<15} {note}")

def main():
    """主函数"""
    print_banner()
    
    # 检查配置
    from config import config
    if not config.validate_config():
        print("❌ 配置验证失败，请先配置环境变量")
        print("运行: python setup_env.py")
        return
    
    print(f"✅ 配置正常 (区域: {config.region})")
    print("💡 当前使用模拟模式，演示完整的识别流程")
    
    # 创建转录器（使用模拟模式）
    transcriber = AliyunTranscriber(use_mock=True)
    
    while True:
        print("\n" + "=" * 60)
        print("📋 请选择功能:")
        print("  1. 一句话识别演示")
        print("  2. 文件识别演示")
        print("  3. 批量处理演示")
        print("  4. 查看定价信息")
        print("  0. 退出")
        
        try:
            choice = input("\n请输入选项编号: ").strip()
            
            if choice == '1':
                demo_sentence_recognition(transcriber)
            elif choice == '2':
                demo_file_recognition(transcriber)
            elif choice == '3':
                demo_batch_processing(transcriber)
            elif choice == '4':
                show_pricing_info()
            elif choice == '0':
                print("\n👋 感谢使用阿里云语音识别演示！")
                break
            else:
                print("❌ 无效的选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用阿里云语音识别演示！")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

if __name__ == '__main__':
    main()
