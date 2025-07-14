#!/usr/bin/env python3
"""
阿里云语音识别配置检查工具
"""
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_env_file():
    """检查 .env 文件"""
    env_file = Path('.env')
    
    print("📁 检查 .env 文件...")
    
    if not env_file.exists():
        print("❌ .env 文件不存在")
        print("💡 请运行: python setup_env.py 创建配置文件")
        return False
    
    print("✅ .env 文件存在")
    
    # 读取并检查内容
    required_keys = ['ALIYUN_ACCESS_KEY_ID', 'ALIYUN_ACCESS_KEY_SECRET', 'ALIYUN_APPKEY', 'ALIYUN_OSS_BUCKET']
    found_keys = []
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key in required_keys:
                        found_keys.append(key)
                        
                        # 检查值是否为默认模板值
                        if value in ['your_access_key_id', 'your_access_key_secret', 'your_app_key', 'your_oss_bucket_name']:
                            print(f"⚠️  第{line_num}行: {key} 仍为默认值，请填入真实的值")
                        elif 'SECRET' not in key:
                             print(f"✅ {key}: {value}")
                        else:
                            print(f"✅ {key}: 已设置")
    
    except Exception as e:
        print(f"❌ 读取 .env 文件失败: {e}")
        return False
    
    # 检查必需的键是否都存在
    missing_keys = set(required_keys) - set(found_keys)
    if missing_keys:
        print(f"❌ 缺少必需的配置项: {', '.join(missing_keys)}")
        return False
    
    return True

def check_config_loading():
    """检查配置加载"""
    print("\n🔧 检查配置加载...")
    
    try:
        from config import config
        
        print(f"✅ 配置模块加载成功")
        print(f"   Access Key ID: {config.access_key_id[:8] + '...' if config.access_key_id else '未设置'}")
        print(f"   Access Key Secret: {'已设置' if config.access_key_secret else '未设置'}")
        print(f"   Region: {config.region}")
        print(f"   AppKey: {config.appkey}")
        print(f"   OSS Bucket: {config.oss_bucket}")
        
        # 验证配置
        if config.validate_config():
            print("✅ 配置验证通过")
            return True
        else:
            print("❌ 配置验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def check_network():
    """检查网络连接"""
    print("\n🌐 检查网络连接...")
    
    try:
        import requests
        
        # 测试阿里云域名解析
        test_url = 'https://www.aliyun.com'
        response = requests.get(test_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ 网络连接正常")
            return True
        else:
            print(f"⚠️  网络连接异常，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 网络连接失败: {e}")
        print("💡 请检查网络连接或防火墙设置")
        return False

def main():
    """主函数"""
    print("🔍 阿里云语音识别配置检查")
    print("=" * 50)
    
    checks = [
        ("环境文件", check_env_file),
        ("配置加载", check_config_loading),
        ("网络连接", check_network),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}检查时出错: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 检查结果总结:")
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有检查都通过了！您可以开始使用阿里云语音识别服务。")
        print("\n🚀 快速开始:")
        print("   python demo.py")
        print("   python aliyun_transcribe.py --mode sentence your_audio.wav")
    else:
        print("\n⚠️  部分检查未通过，请根据上述提示进行修复。")
        print("\n🔧 常见解决方案:")
        print("   1. 运行 python setup_env.py 重新配置环境")
        print("   2. 编辑 .env 文件，填入正确的阿里云访问凭证")
        print("   3. 检查网络连接和防火墙设置")

if __name__ == '__main__':
    main()
