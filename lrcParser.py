import re
import json
import jieba
import os
from datetime import datetime

# 读取 LRC 文件
def read_lrc(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

# 解析 LRC 并进行自然分割
def parse_lrc(lines):
    pattern = re.compile(r'\[(\d+):(\d+\.\d+)\](.*)')
    raw_entries = []
    
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            minutes, seconds, text = match.groups()
            timestamp = round(float(minutes) * 60 + float(seconds), 1)  # 精确到小数点后一位
            if text.strip():
                raw_entries.append((timestamp, text.strip()))
    
    # 按时间戳排序
    raw_entries.sort(key=lambda x: x[0])
    
    # 定义特殊词的时间调整（秒）
    special_words_adjustment = {
        "的": 3.0,  # "的"慢3秒
        "我": -2.0,  # "我"快2秒
        "是": 1.5,
        "和": 1.0,
        "了": 2.0,
    }
    
    # 计算每个时间段内每个词的时间戳
    entries = []
    
    # 记录原始 LRC 行的结束位置，用于添加换行符
    line_end_positions = []
    for i in range(len(raw_entries)):
        if i < len(raw_entries) - 1:
            line_end_positions.append(raw_entries[i+1][0] - 0.1)  # 每行结束前的时间点
    
    for i in range(len(raw_entries)):
        current_timestamp = raw_entries[i][0]
        current_text = raw_entries[i][1]
        
        # 添加标点符号
        current_text = add_punctuation(current_text)
        
        words = list(jieba.cut(current_text))
        
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
                
                # 全局加速1秒
                word_timestamp -= 1.0
                
                # 针对特定词应用特殊调整
                for special_word, adjustment in special_words_adjustment.items():
                    if special_word == word or special_word in word:
                        word_timestamp += adjustment
                        break
                
                # 检查是否需要添加换行符
                is_line_end = False
                if j == len(words) - 1:  # 如果是当前行的最后一个词
                    is_line_end = True
                
                # 添加词条，如果是行尾则添加换行符
                if is_line_end:
                    entries.append((round(word_timestamp, 1), word.strip() + "\n"))
                else:
                    entries.append((round(word_timestamp, 1), word.strip()))
    
    # 再次按时间戳排序（以防万一）
    entries.sort(key=lambda x: x[0])
    
    result = {
        "timestamp": [entry[0] for entry in entries],
        "text": [entry[1] for entry in entries],
        "full_text": "".join(entry[1] for entry in entries)  # 使用空字符串连接，保留换行符
    }
    return result

# 添加标点符号的函数
def add_punctuation(text):
    # 检查文本是否已经有标点符号
    if re.search(r'[，。！？；：]', text):
        return text  # 如果已有标点符号，则不做修改
    
    # 定义可能需要添加标点的词语列表（表示停顿或结束）
    pause_words = ['然后', '所以', '但是', '因为', '而且', '如果', '虽然', '不过', '其实', '当然', 
                  '首先', '其次', '最后', '总之', '另外', '同时', '比如', '例如', '就是', '这样']
    
    # 检查文本是否以这些词结尾，如果是则添加逗号
    for word in pause_words:
        if text.endswith(word):
            return text + '，'
    
    # 检查文本长度，较长的文本可能需要在末尾添加句号
    if len(text) > 10:  # 如果文本较长
        return text + '。'
    
    # 默认情况下不添加标点
    return text

# 运行解析
file_path = "./output/20250319/test_01.lrc"
lrc_lines = read_lrc(file_path)
parsed_data = parse_lrc(lrc_lines)

# 生成输出文件路径
current_date = datetime.now().strftime("%Y%m%d")
output_dir = f"output/{current_date}"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "test_01.json")

# 写入 JSON 文件
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=4)

print(f"JSON 数据已写入: {output_file}")
