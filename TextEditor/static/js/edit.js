document.addEventListener('DOMContentLoaded', function() {
    const editor = document.getElementById('editor');
    const saveBtn = document.getElementById('save-btn');
    const previewBtn = document.getElementById('preview-btn');
    const showTimestampsBtn = document.getElementById('show-timestamps-btn');
    const autoAdjustBtn = document.getElementById('auto-adjust-btn');
    const mergeBtn = document.getElementById('merge-btn');
    const splitBtn = document.getElementById('split-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const timeIncreaseBtn = document.getElementById('time-increase-btn');
    const timeDecreaseBtn = document.getElementById('time-decrease-btn');
    const timeStepInput = document.getElementById('time-step');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const selectionInfo = document.getElementById('selection-info');
    const timelineRuler = document.getElementById('timeline-ruler');
    
    const previewModal = document.getElementById('preview-modal');
    const previewContent = document.getElementById('preview-content');
    const splitModal = document.getElementById('split-modal');
    const currentWordSpan = document.getElementById('current-word');
    const splitInput = document.getElementById('split-input');
    const confirmSplitBtn = document.getElementById('confirm-split');
    
    const closeBtns = document.querySelectorAll('.close-btn');
    const loading = document.getElementById('loading');
    
    // 确保加载动画隐藏
    loading.classList.add('hidden');
    
    // 当前数据
    let currentData = JSON.parse(JSON.stringify(initialData));
    let showTimestamps = false;
    let selectedIndices = [];
    let isMouseDown = false;  // 添加鼠标按下状态
    let startIndex = null;    // 添加滑动起始索引
    
    // 渲染时间轴
    function renderTimeline() {
        if (currentData.timestamp.length === 0) return;
        
        const minTime = Math.min(...currentData.timestamp);
        const maxTime = Math.max(...currentData.timestamp);
        
        // 创建时间轴容器
        timelineRuler.innerHTML = '';
        timelineRuler.style.position = 'relative';
        timelineRuler.style.height = '40px';
        timelineRuler.style.backgroundColor = '#2c3e50';
        timelineRuler.style.borderRadius = '4px';
        timelineRuler.style.marginBottom = '15px';
        timelineRuler.style.overflow = 'hidden';
        
        // 添加时间刻度
        const duration = maxTime - minTime;
        // 根据总时长确定刻度间隔
        let interval = 1; // 默认1秒
        if (duration > 60) interval = 5;
        if (duration > 300) interval = 15;
        if (duration > 900) interval = 30;
        if (duration > 1800) interval = 60;
        
        // 创建刻度容器
        const ticksContainer = document.createElement('div');
        ticksContainer.className = 'timeline-ticks';
        ticksContainer.style.position = 'absolute';
        ticksContainer.style.top = '0';
        ticksContainer.style.left = '0';
        ticksContainer.style.width = '100%';
        ticksContainer.style.height = '20px';
        ticksContainer.style.borderBottom = '1px solid #34495e';
        
        // 添加刻度和时间标签
        for (let i = 0; i <= Math.ceil(duration); i += interval) {
            const time = minTime + i;
            const percent = (i / duration) * 100;
            
            // 创建主刻度
            const tick = document.createElement('div');
            tick.className = 'timeline-tick';
            tick.style.position = 'absolute';
            tick.style.left = `${percent}%`;
            tick.style.height = '10px';
            tick.style.width = '1px';
            tick.style.backgroundColor = '#ecf0f1';
            tick.style.top = '10px';
            
            // 创建时间标签
            const label = document.createElement('div');
            label.className = 'timeline-label';
            label.textContent = formatTime(time);
            label.style.position = 'absolute';
            label.style.left = `${percent}%`;
            label.style.top = '22px';
            label.style.transform = 'translateX(-50%)';
            label.style.fontSize = '10px';
            label.style.color = '#ecf0f1';
            
            ticksContainer.appendChild(tick);
            timelineRuler.appendChild(label);
            
            // 添加次要刻度
            if (i < Math.ceil(duration) && interval > 1) {
                for (let j = 1; j < interval; j++) {
                    if (i + j <= duration) {
                        const minorPercent = ((i + j) / duration) * 100;
                        const minorTick = document.createElement('div');
                        minorTick.className = 'timeline-minor-tick';
                        minorTick.style.position = 'absolute';
                        minorTick.style.left = `${minorPercent}%`;
                        minorTick.style.height = '5px';
                        minorTick.style.width = '1px';
                        minorTick.style.backgroundColor = '#95a5a6';
                        minorTick.style.top = '15px';
                        ticksContainer.appendChild(minorTick);
                    }
                }
            }
        }
        
        timelineRuler.appendChild(ticksContainer);
        
        // 添加当前词语位置指示器
        if (selectedIndices.length > 0) {
            const index = selectedIndices[0];
            const time = currentData.timestamp[index];
            const percent = ((time - minTime) / duration) * 100;
            
            const indicator = document.createElement('div');
            indicator.className = 'timeline-indicator';
            indicator.style.position = 'absolute';
            indicator.style.left = `${percent}%`;
            indicator.style.top = '0';
            indicator.style.height = '40px';
            indicator.style.width = '2px';
            indicator.style.backgroundColor = '#e74c3c';
            indicator.style.zIndex = '10';
            
            const indicatorLabel = document.createElement('div');
            indicatorLabel.className = 'indicator-label';
            indicatorLabel.textContent = formatTime(time);
            indicatorLabel.style.position = 'absolute';
            indicatorLabel.style.left = '50%';
            indicatorLabel.style.bottom = '2px';
            indicatorLabel.style.transform = 'translateX(-50%)';
            indicatorLabel.style.backgroundColor = '#e74c3c';
            indicatorLabel.style.color = 'white';
            indicatorLabel.style.padding = '1px 4px';
            indicatorLabel.style.borderRadius = '2px';
            indicatorLabel.style.fontSize = '10px';
            
            indicator.appendChild(indicatorLabel);
            timelineRuler.appendChild(indicator);
        }
        
        // 添加词语位置标记
        const markersContainer = document.createElement('div');
        markersContainer.className = 'word-markers';
        markersContainer.style.position = 'absolute';
        markersContainer.style.bottom = '0';
        markersContainer.style.left = '0';
        markersContainer.style.width = '100%';
        markersContainer.style.height = '10px';
        
        currentData.timestamp.forEach((time, idx) => {
            const percent = ((time - minTime) / duration) * 100;
            
            const marker = document.createElement('div');
            marker.className = 'word-marker';
            marker.dataset.index = idx;
            marker.style.position = 'absolute';
            marker.style.left = `${percent}%`;
            marker.style.bottom = '0';
            marker.style.width = '3px';
            marker.style.height = '8px';
            marker.style.backgroundColor = selectedIndices.includes(idx) ? '#f39c12' : '#3498db';
            marker.style.borderRadius = '1px';
            marker.style.cursor = 'pointer';
            
            // 添加点击事件
            marker.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                selectedIndices = [index];
                renderEditor();
                
                // 滚动到对应词语
                const wordElement = document.querySelector(`.word-item[data-index="${index}"]`);
                if (wordElement) {
                    wordElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });
            
            markersContainer.appendChild(marker);
        });
        
        timelineRuler.appendChild(markersContainer);
    }
    
    // 格式化时间为分:秒.毫秒
    function formatTime(seconds) {
        const min = Math.floor(seconds / 60);
        const sec = Math.floor(seconds % 60);
        const ms = Math.floor((seconds % 1) * 10);
        
        return `${min}:${sec.toString().padStart(2, '0')}.${ms}`;
    }
    
    // 渲染编辑器
    function renderEditor() {
        editor.innerHTML = '';
        
        // 创建一个文档片段，提高性能
        const fragment = document.createDocumentFragment();
        
        // 计算每个词的平均长度，用于动态调整间距
        const avgLength = currentData.text.reduce((sum, word) => sum + word.length, 0) / currentData.text.length || 3;
        const spacing = Math.max(3, Math.min(8, 12 - avgLength)); // 根据平均长度动态调整间距
        
        for (let i = 0; i < currentData.text.length; i++) {
            const wordSpan = document.createElement('span');
            wordSpan.className = 'word-item';
            if (showTimestamps) {
                wordSpan.classList.add('show-timestamp');
            }
            if (selectedIndices.includes(i)) {
                wordSpan.classList.add('selected');
            }
            wordSpan.dataset.index = i;
            wordSpan.textContent = currentData.text[i];
            
            // 根据词语长度动态调整内边距
            const paddingH = Math.max(4, Math.min(8, 10 - currentData.text[i].length));
            wordSpan.style.padding = `4px ${paddingH}px`;
            wordSpan.style.margin = `3px ${spacing}px 3px 0`;
            
            // 添加时间戳提示
            const timestampSpan = document.createElement('span');
            timestampSpan.className = 'timestamp';
            timestampSpan.textContent = formatTime(currentData.timestamp[i]);
            wordSpan.appendChild(timestampSpan);
            
            // 为长词添加特殊样式
            if (currentData.text[i].length > 6) {
                wordSpan.classList.add('long-word');
            }
            
            fragment.appendChild(wordSpan);
            
            // 每10个词或句号后添加一个换行，改善可读性
            if ((i > 0 && i % 10 === 0) || 
                (currentData.text[i].endsWith('。') || 
                 currentData.text[i].endsWith('！') || 
                 currentData.text[i].endsWith('？'))) {
                const lineBreak = document.createElement('br');
                fragment.appendChild(lineBreak);
                
                // 在句子结束后添加额外的间距
                if (currentData.text[i].endsWith('。') || 
                    currentData.text[i].endsWith('！') || 
                    currentData.text[i].endsWith('？')) {
                    const spacer = document.createElement('span');
                    spacer.className = 'sentence-spacer';
                    spacer.style.display = 'inline-block';
                    spacer.style.width = '10px';
                    spacer.style.height = '1px';
                    fragment.appendChild(spacer);
                }
            }
        }
        
        editor.appendChild(fragment);
        
        // 添加事件监听
        addEventListeners();
        
        // 更新时间轴
        renderTimeline();
        
        // 更新按钮状态
        updateButtonStates();
        
        // 更新选中信息
        updateSelectionInfo();
    }
    
    // 格式化时间为分:秒.毫秒
    function formatTime(seconds) {
        const min = Math.floor(seconds / 60);
        const sec = Math.floor(seconds % 60);
        const ms = Math.floor((seconds % 1) * 10);
        
        return `${min}:${sec.toString().padStart(2, '0')}.${ms}`;
    }
    
    // 更新按钮状态
    function updateButtonStates() {
        if (selectedIndices.length === 0) {
            mergeBtn.disabled = true;
            splitBtn.disabled = true;
            deleteBtn.disabled = true;
            timeIncreaseBtn.disabled = true;
            timeDecreaseBtn.disabled = true;
        } else if (selectedIndices.length === 1) {
            mergeBtn.disabled = true;
            splitBtn.disabled = false;
            deleteBtn.disabled = false;
            timeIncreaseBtn.disabled = false;
            timeDecreaseBtn.disabled = false;
        } else {
            // 检查是否连续
            const isConsecutive = isConsecutiveIndices(selectedIndices);
            mergeBtn.disabled = !isConsecutive;
            splitBtn.disabled = true;
            deleteBtn.disabled = false;
            timeIncreaseBtn.disabled = false;
            timeDecreaseBtn.disabled = false;
        }
    }
    
    // 检查索引是否连续
    function isConsecutiveIndices(indices) {
        const sortedIndices = [...indices].sort((a, b) => a - b);
        for (let i = 1; i < sortedIndices.length; i++) {
            if (sortedIndices[i] !== sortedIndices[i-1] + 1) {
                return false;
            }
        }
        return true;
    }
    
    // 更新选中信息
    function updateSelectionInfo() {
        if (selectedIndices.length === 0) {
            selectionInfo.textContent = '未选中任何词语';
        } else if (selectedIndices.length === 1) {
            const index = selectedIndices[0];
            selectionInfo.textContent = `已选中: "${currentData.text[index]}" (${currentData.timestamp[index].toFixed(1)}s)`;
        } else {
            selectionInfo.textContent = `已选中 ${selectedIndices.length} 个词语`;
        }
    }
    
    // 添加事件监听
    function addEventListeners() {
        // 单击选择
        document.querySelectorAll('.word-item').forEach(item => {
            // 鼠标按下事件
            item.addEventListener('mousedown', function(e) {
                const index = parseInt(this.dataset.index);
                
                // 如果按住Ctrl键(Mac上是Command键)，则添加到多选
                if (e.ctrlKey || e.metaKey) {
                    const indexPos = selectedIndices.indexOf(index);
                    if (indexPos === -1) {
                        selectedIndices.push(index);
                    } else {
                        selectedIndices.splice(indexPos, 1);
                    }
                } else if (e.shiftKey && selectedIndices.length > 0) {
                    // 如果按住Shift键，则选择范围
                    const lastIndex = selectedIndices[selectedIndices.length - 1];
                    selectedIndices = [];
                    
                    const start = Math.min(lastIndex, index);
                    const end = Math.max(lastIndex, index);
                    
                    for (let i = start; i <= end; i++) {
                        selectedIndices.push(i);
                    }
                } else {
                    // 普通点击，清除其他选择
                    selectedIndices = [index];
                    
                    // 开始滑动选择
                    isMouseDown = true;
                    startIndex = index;
                }
                
                renderEditor();
            });
            
            // 鼠标进入事件 - 用于滑动选择
            item.addEventListener('mouseenter', function(e) {
                if (isMouseDown && startIndex !== null) {
                    const currentIndex = parseInt(this.dataset.index);
                    
                    // 清除之前的选择
                    selectedIndices = [];
                    
                    // 计算选择范围
                    const start = Math.min(startIndex, currentIndex);
                    const end = Math.max(startIndex, currentIndex);
                    
                    // 添加范围内的所有索引
                    for (let i = start; i <= end; i++) {
                        selectedIndices.push(i);
                    }
                    
                    renderEditor();
                }
            });
        });
        
        // 鼠标松开事件 - 结束滑动选择
        document.addEventListener('mouseup', function() {
            isMouseDown = false;
        });
        
        // 鼠标离开编辑器区域 - 结束滑动选择
        editor.addEventListener('mouseleave', function() {
            isMouseDown = false;
        });
    }
    
    // 合并选中的词语
    function mergeSelectedWords() {
        if (selectedIndices.length <= 1) {
            alert('请至少选择两个词语进行合并');
            return;
        }
        
        // 排序索引
        const indices = [...selectedIndices].sort((a, b) => a - b);
        
        // 检查是否连续
        if (!isConsecutiveIndices(indices)) {
            alert('只能合并连续的词语');
            return;
        }
        
        // 合并文本
        const mergedText = indices.map(i => currentData.text[i]).join('');
        
        // 使用第一个词的时间戳
        const timestamp = currentData.timestamp[indices[0]];
        
        // 更新数据
        indices.reverse().forEach(i => {
            currentData.text.splice(i, 1);
            currentData.timestamp.splice(i, 1);
        });
        
        currentData.text.splice(indices[indices.length - 1], 0, mergedText);
        currentData.timestamp.splice(indices[indices.length - 1], 0, timestamp);
        
        // 清除选择
        selectedIndices = [indices[indices.length - 1]];
        
        // 重新渲染
        renderEditor();
    }
    
    // 拆分选中的词语
    function splitSelectedWord() {
        if (selectedIndices.length !== 1) {
            alert('请选择一个词语进行拆分');
            return;
        }
        
        const index = selectedIndices[0];
        const text = currentData.text[index];
        
        if (text.length <= 1) {
            alert('单字无法拆分');
            return;
        }
        
        // 显示拆分对话框
        currentWordSpan.textContent = text;
        splitInput.value = text.split('').join(' ');
        splitModal.classList.remove('hidden');
        
        // 聚焦输入框
        splitInput.focus();
        splitInput.select();
    }
    
    // 确认拆分
    function confirmSplitWord() {
        const index = selectedIndices[0];
        const splitText = splitInput.value;
        
        if (!splitText) return;
        
        const parts = splitText.split(' ').filter(p => p.trim());
        if (parts.length <= 1) {
            alert('至少需要拆分成两部分');
            return;
        }
        
        // 计算新的时间戳
        const currentTime = currentData.timestamp[index];
        const timeStep = parseFloat(timeStepInput.value) || 0.1;
        
        // 更新数据
        currentData.text.splice(index, 1);
        currentData.timestamp.splice(index, 1);
        
        for (let i = 0; i < parts.length; i++) {
            currentData.text.splice(index + i, 0, parts[i]);
            currentData.timestamp.splice(index + i, 0, currentTime + i * timeStep);
        }
        
        // 隐藏对话框
        splitModal.classList.add('hidden');
        
        // 更新选择
        selectedIndices = [];
        for (let i = 0; i < parts.length; i++) {
            selectedIndices.push(index + i);
        }
        
        // 重新渲染
        renderEditor();
    }
    
    // 删除选中的词语
    function deleteSelectedWords() {
        if (selectedIndices.length === 0) {
            alert('请选择要删除的词语');
            return;
        }
        
        if (!confirm(`确定要删除选中的 ${selectedIndices.length} 个词语吗？`)) {
            return;
        }
        
        // 排序并反转索引，从后往前删除
        const indices = [...selectedIndices].sort((a, b) => b - a);
        
        indices.forEach(i => {
            currentData.text.splice(i, 1);
            currentData.timestamp.splice(i, 1);
        });
        
        // 清除选择
        selectedIndices = [];
        
        // 重新渲染
        renderEditor();
    }
    
    // 调整选中词语的时间
    function adjustSelectedWordsTime(delta) {
        if (selectedIndices.length === 0) return;
        
        const timeStep = parseFloat(timeStepInput.value) || 0.1;
        const adjustment = delta * timeStep;
        
        selectedIndices.forEach(i => {
            currentData.timestamp[i] += adjustment;
        });
        
        // 重新渲染
        renderEditor();
    }
    
    // 自动调整所有时间戳
    function autoAdjustTimestamps() {
        if (currentData.timestamp.length <= 1) return;
        
        if (!confirm('这将重新计算所有词语的时间间隔，确定继续吗？')) {
            return;
        }
        
        const firstTime = currentData.timestamp[0];
        const lastTime = currentData.timestamp[currentData.timestamp.length - 1];
        const totalDuration = lastTime - firstTime;
        const avgStep = totalDuration / (currentData.timestamp.length - 1);
        
        // 均匀分布时间戳
        for (let i = 0; i < currentData.timestamp.length; i++) {
            currentData.timestamp[i] = firstTime + i * avgStep;
        }
        
        // 重新渲染
        renderEditor();
    }
    
    // 搜索文本
    function searchText() {
        const searchTerm = searchInput.value.trim();
        if (!searchTerm) return;
        
        // 清除之前的高亮
        document.querySelectorAll('.highlight').forEach(el => {
            el.classList.remove('highlight');
        });
        
        // 查找匹配项
        let found = false;
        document.querySelectorAll('.word-item').forEach(item => {
            if (item.textContent.includes(searchTerm)) {
                item.classList.add('highlight');
                found = true;
                
                // 滚动到第一个匹配项
                if (!found) {
                    item.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
        
        if (!found) {
            alert('未找到匹配项');
        }
    }
    
    // 切换时间戳显示
    function toggleTimestamps() {
        showTimestamps = !showTimestamps;
        
        // 直接修改DOM元素的类，而不是重新渲染整个编辑器
        document.querySelectorAll('.word-item').forEach(item => {
            if (showTimestamps) {
                item.classList.add('show-timestamp');
            } else {
                item.classList.remove('show-timestamp');
            }
        });
        
        // 更新按钮文本以反映当前状态
        showTimestampsBtn.textContent = showTimestamps ? '隐藏时间戳' : '显示时间戳';
    }
    
    // 保存修改
    saveBtn.addEventListener('click', function() {
        loading.classList.remove('hidden');
        
        // 更新full_text
        currentData.full_text = currentData.text.join('');
        
        fetch('/save_edit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: date,
                filename: filename,
                data: currentData
            })
        })
        .then(response => response.json())
        .then(data => {
            loading.classList.add('hidden');
            
            if (data.success) {
                alert('保存成功!');
            } else {
                alert('错误: ' + data.error);
            }
        })
        .catch(error => {
            loading.classList.add('hidden');
            alert('发生错误: ' + error);
        });
    });
    
    // 预览
    previewBtn.addEventListener('click', function() {
        previewContent.textContent = currentData.text.join('');
        previewModal.classList.remove('hidden');
    });
    
    // 关闭预览
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            previewModal.classList.add('hidden');
            splitModal.classList.add('hidden');
        });
    });
    
    // 点击模态框外部关闭
    window.addEventListener('click', function(e) {
        if (e.target === previewModal) {
            previewModal.classList.add('hidden');
        }
        if (e.target === splitModal) {
            splitModal.classList.add('hidden');
        }
    });
    
    // 确认拆分按钮
    confirmSplitBtn.addEventListener('click', confirmSplitWord);
    
    // 合并按钮
    mergeBtn.addEventListener('click', mergeSelectedWords);
    
    // 拆分按钮
    splitBtn.addEventListener('click', splitSelectedWord);
    
    // 删除按钮
    deleteBtn.addEventListener('click', deleteSelectedWords);
    
    // 时间增加按钮
    timeIncreaseBtn.addEventListener('click', function() {
        adjustSelectedWordsTime(1);
    });
    
    // 时间减少按钮
    timeDecreaseBtn.addEventListener('click', function() {
        adjustSelectedWordsTime(-1);
    });
    
    // 显示/隐藏时间戳
    showTimestampsBtn.addEventListener('click', toggleTimestamps);
    
    // 自动调整时间戳
    autoAdjustBtn.addEventListener('click', autoAdjustTimestamps);
    
    // 搜索按钮
    searchBtn.addEventListener('click', searchText);
    
    // 搜索输入框回车事件
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchText();
        }
    });
    
    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        // 如果正在输入，不处理快捷键
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }
        
        // Ctrl+S 或 Command+S 保存
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveBtn.click();
        }
        
        // Delete 或 Backspace 删除选中词语
        if (e.key === 'Delete' || e.key === 'Backspace') {
            if (selectedIndices.length > 0) {
                e.preventDefault();
                deleteSelectedWords();
            }
        }
        
        // Ctrl+F 或 Command+F 搜索
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            searchInput.focus();
        }
        
        // Escape 取消选择
        if (e.key === 'Escape') {
            selectedIndices = [];
            renderEditor();
        }
    });
    
    // 初始渲染
    renderEditor();
});