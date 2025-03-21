import os
import re
import json
import jieba
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制

# 确保上传和输出目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 读取 LRC 文件
# 在文件顶部添加日志模块
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 修改read_lrc函数，添加错误处理
def read_lrc(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            logger.error(f"LRC文件为空: {file_path}")
            return []
        
        logger.info(f"成功读取LRC文件，共{len(lines)}行")
        return lines
    except Exception as e:
        logger.error(f"读取LRC文件出错: {str(e)}")
        return []

# 修改parse_lrc函数，添加错误处理和调试信息
# 添加一个更智能的标点符号处理函数
def add_smart_punctuation(text_list):
    """根据jieba分词结果智能添加标点符号"""
    if not text_list:
        return text_list
    
    # 句子结束标志词
    sentence_end_words = ['吗', '呢', '啊', '呀', '吧', '了', '的', '呐', '哦', '哈', '嘛']
    # 可能需要加逗号的词
    comma_words = ['但是', '然后', '所以', '因为', '而且', '如果', '虽然', '不过', '其实', '当然', 
                  '首先', '其次', '最后', '总之', '另外', '同时', '比如', '例如', '就是', '这样',
                  '并且', '或者', '要么', '不仅', '况且', '不但', '尽管', '无论', '只要', '只有',
                  '除了', '以及', '不管', '即使', '假如', '假使', '假若', '倘若', '要是', '譬如']
    
    # 标点符号添加规则
    result = text_list.copy()
    sentence_length = 0
    last_punctuation_idx = -1
    
    for i in range(len(result)):
        word = result[i]
        sentence_length += len(word)
        
        # 检查是否需要添加标点
        add_punctuation = False
        punctuation_type = None
        
        # 1. 句子长度超过15个字符，考虑添加逗号
        if sentence_length > 15 and i - last_punctuation_idx > 5:
            # 检查当前词是否适合加逗号
            if any(cw in word for cw in comma_words):
                add_punctuation = True
                punctuation_type = '，'
        
        # 2. 句子长度超过30个字符，强制添加逗号或句号
        if sentence_length > 30 and i - last_punctuation_idx > 8:
            add_punctuation = True
            punctuation_type = '，'
        
        # 3. 句子结束词，添加句号或问号
        if word[-1] in sentence_end_words and sentence_length > 10:
            add_punctuation = True
            # 如果包含疑问词，添加问号
            if '什么' in ''.join(result[last_punctuation_idx+1:i+1]) or '为何' in ''.join(result[last_punctuation_idx+1:i+1]) or '怎么' in ''.join(result[last_punctuation_idx+1:i+1]):
                punctuation_type = '？'
            else:
                punctuation_type = '。'
        
        # 应用标点符号
        if add_punctuation and punctuation_type:
            result[i] = word + punctuation_type
            last_punctuation_idx = i
            sentence_length = 0
    
    # 确保最后一个词有句号
    if result and not any(p in result[-1] for p in ['。', '！', '？']):
        result[-1] = result[-1] + '。'
    
    return result

# 删除嵌套的函数定义，修复标点符号处理逻辑

def parse_lrc(lines, config):
    pattern = re.compile(r'\[(\d+):(\d+\.\d+)\](.*)')
    raw_entries = []
    
    logger.info(f"开始解析LRC，配置: {config}")
    
    # 解析LRC行
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            minutes, seconds, text = match.groups()
            timestamp = round(float(minutes) * 60 + float(seconds), 1)  # 精确到小数点后一位
            if text.strip():
                raw_entries.append((timestamp, text.strip()))
    
    if not raw_entries:
        logger.error("未能从LRC文件中提取有效内容")
        return {"timestamp": [], "text": [], "full_text": ""}
    
    logger.info(f"成功提取{len(raw_entries)}个时间戳和文本")
    
    # 从配置中获取特殊词的时间调整
    special_words_adjustment = config.get('special_words_adjustment', {})
    global_time_shift = float(config.get('global_time_shift', -1.0))
    add_line_breaks = config.get('add_line_breaks', True)
    add_punctuation_enabled = config.get('add_punctuation', True)
    
    # 计算每个时间段内每个词的时间戳
    entries = []
    
    try:
        for i in range(len(raw_entries)):
            current_timestamp = raw_entries[i][0]
            current_text = raw_entries[i][1]
            
            logger.debug(f"处理文本: {current_text}, 时间戳: {current_timestamp}")
            
            # 使用jieba分词
            words = list(jieba.cut(current_text))
            logger.debug(f"分词结果: {words}")
            
            # 计算下一个时间戳（如果有的话）
            next_timestamp = None
            if i < len(raw_entries) - 1:
                next_timestamp = raw_entries[i+1][0]
            
            # 为每个词分配时间戳
            for j, word in enumerate(words):
                if word.strip():  # 忽略空白词
                    # 基础时间戳计算
                    if next_timestamp is not None:
                        # 在当前时间戳和下一个时间戳之间均匀分布
                        word_timestamp = current_timestamp + (next_timestamp - current_timestamp) * (j / len(words))
                    else:
                        # 如果没有下一个时间戳，则在当前时间戳基础上增加一个小值
                        word_timestamp = current_timestamp + j * 0.1
                    
                    # 全局时间调整
                    word_timestamp += global_time_shift
                    
                    # 针对特定词应用特殊调整
                    for special_word, adjustment in special_words_adjustment.items():
                        if special_word == word or special_word in word:
                            word_timestamp += float(adjustment)
                            break
                    
                    # 检查是否需要添加换行符
                    is_line_end = False
                    if j == len(words) - 1 and add_line_breaks:  # 如果是当前行的最后一个词
                        is_line_end = True
                    
                    # 添加词条，如果是行尾则添加换行符
                    if is_line_end:
                        entries.append((round(word_timestamp, 1), word.strip() + "\n"))
                    else:
                        entries.append((round(word_timestamp, 1), word.strip()))
        
        logger.info(f"成功处理所有词语，共{len(entries)}个词")
        
        # 再次按时间戳排序（以防万一）
        entries.sort(key=lambda x: x[0])
        
        # 获取所有文本
        all_text = "".join(entry[1] for entry in entries)
        
        # 如果启用了标点符号添加功能，处理标点符号
        if add_punctuation_enabled:
            # 将文本分成句子
            processed_text = add_smart_punctuation(all_text)
            full_text = processed_text
        else:
            full_text = all_text
        
        result = {
            "timestamp": [entry[0] for entry in entries],
            "text": [entry[1] for entry in entries],
            "full_text": full_text  # 使用处理过的文本
        }
        
        logger.info(f"生成结果: {len(result['timestamp'])}个时间戳, {len(result['text'])}个文本片段")
        return result
    except Exception as e:
        logger.error(f"处理LRC时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"timestamp": [], "text": [], "full_text": ""}

# 修改upload_file函数中的文件写入部分
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and file.filename.endswith('.lrc'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 获取配置参数
        config = {
            'global_time_shift': request.form.get('global_time_shift', '-1.0'),
            'add_line_breaks': request.form.get('add_line_breaks', 'true') == 'true',
            'add_punctuation': request.form.get('add_punctuation', 'true') == 'true',
            'special_words_adjustment': {}
        }
        
        # 解析特殊词调整
        special_words = request.form.get('special_words', '')
        if special_words:
            for item in special_words.split(','):
                if ':' in item:
                    word, value = item.split(':')
                    config['special_words_adjustment'][word.strip()] = float(value.strip())
        
        # 处理文件
        lrc_lines = read_lrc(file_path)
        if not lrc_lines:
            return jsonify({'error': 'LRC文件为空或读取失败'}), 400
        
        parsed_data = parse_lrc(lrc_lines, config)
        if not parsed_data['text']:
            return jsonify({'error': 'LRC解析失败，未能提取文本'}), 400
        
        # 生成输出文件路径
        current_date = datetime.now().strftime("%Y%m%d")
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], current_date)
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = os.path.splitext(filename)[0] + '.json'
        output_file = os.path.join(output_dir, output_filename)
        
        # 写入 JSON 文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"成功写入JSON文件: {output_file}")
            
            # 验证文件是否正确写入
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                with open(output_file, 'r', encoding='utf-8') as f:
                    check_data = json.load(f)
                if not check_data.get('text'):
                    logger.error(f"写入的JSON文件内容为空: {output_file}")
                    return jsonify({'error': '生成的JSON文件内容为空'}), 500
            else:
                logger.error(f"JSON文件写入失败或为空: {output_file}")
                return jsonify({'error': '文件写入失败'}), 500
            
            return jsonify({
                'success': True,
                'message': f'文件已处理并保存为 {output_file}',
                'download_url': f'/download/{current_date}/{output_filename}',
                'edit_url': f'/edit/{current_date}/{output_filename}'
            })
        except Exception as e:
            logger.error(f"写入JSON文件时出错: {str(e)}")
            return jsonify({'error': f'保存文件时出错: {str(e)}'}), 500

# 添加首页路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/<date>/<filename>')
def download_file(date, filename):
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], date)
    return send_file(os.path.join(output_dir, filename), as_attachment=True)

@app.route('/edit/<date>/<filename>')
def edit_file(date, filename):
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], date)
    file_path = os.path.join(output_dir, filename)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return render_template('edit.html', data=data, date=date, filename=filename)
    except Exception as e:
        return jsonify({'error': f'无法读取文件: {str(e)}'}), 400

@app.route('/save_edit', methods=['POST'])
def save_edit():
    try:
        data = request.json
        date = data.get('date')
        filename = data.get('filename')
        edited_data = data.get('data')
        
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], date)
        file_path = os.path.join(output_dir, filename)
        
        # 更新full_text
        edited_data['full_text'] = "".join(edited_data['text'])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(edited_data, f, ensure_ascii=False, indent=4)
        
        return jsonify({
            'success': True,
            'message': f'文件已保存: {file_path}',
            'download_url': f'/download/{date}/{filename}'
        })
    except Exception as e:
        return jsonify({'error': f'保存失败: {str(e)}'}), 400

# 添加404错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Changed port from 5000 to 5001

# 添加一个智能标点符号处理函数
def add_smart_punctuation(text):
    """根据文本内容智能添加标点符号"""
    if not text:
        return text
    
    # 将文本分成句子
    result = ""
    current_sentence = ""
    
    # 句子结束标志词
    sentence_end_words = ['吗', '呢', '啊', '呀', '吧', '了', '的', '呐', '哦', '哈', '嘛']
    # 可能需要加逗号的词
    comma_words = ['但是', '然后', '所以', '因为', '而且', '如果', '虽然', '不过', '其实', '当然', 
                  '首先', '其次', '最后', '总之', '另外', '同时', '比如', '例如', '就是', '这样',
                  '并且', '或者', '要么', '不仅', '况且', '不但', '尽管', '无论', '只要', '只有',
                  '除了', '以及', '不管', '即使', '假如', '假使', '假若', '倘若', '要是', '譬如']
    
    # 分词处理
    words = list(jieba.cut(text))
    
    # 标点符号添加规则
    sentence_length = 0
    last_punctuation_idx = -1
    processed_text = ""
    
    for i, word in enumerate(words):
        processed_text += word
        sentence_length += len(word)
        
        # 检查是否需要添加标点
        add_punctuation = False
        punctuation_type = None
        
        # 1. 句子长度超过15个字符，考虑添加逗号
        if sentence_length > 15 and i - last_punctuation_idx > 5:
            # 检查当前词是否适合加逗号
            if any(cw in word for cw in comma_words) or word in comma_words:
                add_punctuation = True
                punctuation_type = '，'
        
        # 2. 句子长度超过30个字符，强制添加逗号或句号
        if sentence_length > 30 and i - last_punctuation_idx > 8:
            add_punctuation = True
            punctuation_type = '，'
        
        # 3. 句子结束词，添加句号或问号
        if word and word[-1] in sentence_end_words and sentence_length > 10:
            add_punctuation = True
            # 如果包含疑问词，添加问号
            if '什么' in ''.join(words[last_punctuation_idx+1:i+1]) or '为何' in ''.join(words[last_punctuation_idx+1:i+1]) or '怎么' in ''.join(words[last_punctuation_idx+1:i+1]):
                punctuation_type = '？'
            else:
                punctuation_type = '。'
        
        # 应用标点符号
        if add_punctuation and punctuation_type:
            processed_text += punctuation_type
            last_punctuation_idx = i
            sentence_length = 0
    
    # 确保最后一个词有句号
    if processed_text and not any(p in processed_text[-1] for p in ['。', '！', '？']):
        processed_text += '。'
    
    return processed_text