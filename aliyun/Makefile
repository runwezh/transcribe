# 阿里云语音识别项目 Makefile

.PHONY: help install setup test demo clean

# 默认目标
help:
	@echo "阿里云语音识别项目"
	@echo "===================="
	@echo ""
	@echo "可用命令:"
	@echo "  install    - 安装依赖包"
	@echo "  setup      - 配置环境"
	@echo "  check      - 检查配置"
	@echo "  test       - 运行测试"
	@echo "  demo       - 运行演示"
	@echo "  clean      - 清理临时文件"
	@echo "  example    - 运行示例"
	@echo ""
	@echo "使用示例:"
	@echo "  make install"
	@echo "  make setup"
	@echo "  make demo"

# 安装依赖
install:
	@echo "📦 安装依赖包..."
	pip install -r requirements.txt
	@echo "✅ 依赖安装完成"

# 环境配置
setup:
	@echo "🔧 配置环境..."
	python setup_env.py

# 检查配置
check:
	@echo "🔍 检查配置..."
	python check_config.py

# 运行测试
test:
	@echo "🧪 运行测试..."
	python test_aliyun_asr.py

# 运行演示
demo:
	@echo "🚀 启动演示..."
	python demo.py

# 运行示例
example:
	@echo "📝 运行示例..."
	@if [ -f example.py ]; then \
		python example.py; \
	else \
		echo "❌ example.py 不存在，请先运行 make setup"; \
	fi

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.log" -delete
	rm -rf demo_output/
	rm -rf test_output/
	@echo "✅ 清理完成"

# 检查代码风格
lint:
	@echo "🔍 检查代码风格..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 *.py --max-line-length=100 --ignore=E501,W503; \
	else \
		echo "⚠️  flake8 未安装，跳过代码风格检查"; \
	fi

# 格式化代码
format:
	@echo "🎨 格式化代码..."
	@if command -v black >/dev/null 2>&1; then \
		black *.py --line-length=100; \
	else \
		echo "⚠️  black 未安装，跳过代码格式化"; \
	fi

# 生成文档
docs:
	@echo "📚 生成文档..."
	@if command -v pydoc >/dev/null 2>&1; then \
		pydoc -w aliyun_asr; \
		pydoc -w output_formatter; \
		pydoc -w config; \
		echo "✅ 文档生成完成"; \
	else \
		echo "⚠️  pydoc 未找到"; \
	fi

# 打包项目
package:
	@echo "📦 打包项目..."
	tar -czf aliyun_asr.tar.gz *.py requirements.txt README.md Makefile
	@echo "✅ 打包完成: aliyun_asr.tar.gz"

# 显示项目信息
info:
	@echo "项目信息"
	@echo "========"
	@echo "名称: 阿里云语音识别"
	@echo "版本: 1.0.0"
	@echo "作者: AI Assistant"
	@echo "描述: 基于阿里云智能语音交互服务的语音转文字解决方案"
	@echo ""
	@echo "文件列表:"
	@ls -la *.py | awk '{print "  " $$9 " (" $$5 " bytes)"}'
	@echo ""
	@echo "Python版本: $(shell python --version)"
	@echo "当前目录: $(shell pwd)"
