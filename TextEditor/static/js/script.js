document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const resultDiv = document.getElementById('result');
    const resultMessage = document.getElementById('result-message');
    const downloadLink = document.getElementById('download-link');
    const editLink = document.getElementById('edit-link');  // 添加编辑链接元素
    const processAnother = document.getElementById('process-another');
    const loading = document.getElementById('loading');
    const addWordBtn = document.getElementById('add-word-btn');
    const specialWordsContainer = document.getElementById('special-words-container');
    
    // 确保页面加载时隐藏加载动画
    loading.classList.add('hidden');
    
    // 添加特殊词
    addWordBtn.addEventListener('click', function() {
        const newItem = document.createElement('div');
        newItem.className = 'special-word-item';
        newItem.innerHTML = `
            <input type="text" placeholder="词语" class="word-input">
            <input type="number" placeholder="调整值(秒)" step="0.1" class="time-input">
            <button type="button" class="remove-btn">删除</button>
        `;
        specialWordsContainer.appendChild(newItem);
        
        // 为新添加的删除按钮添加事件监听
        newItem.querySelector('.remove-btn').addEventListener('click', function() {
            specialWordsContainer.removeChild(newItem);
        });
    });
    
    // 为初始的删除按钮添加事件监听
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const item = btn.closest('.special-word-item');
            specialWordsContainer.removeChild(item);
        });
    });
    
    // 处理表单提交
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 收集特殊词调整
        const specialWords = [];
        document.querySelectorAll('.special-word-item').forEach(item => {
            const word = item.querySelector('.word-input').value.trim();
            const time = item.querySelector('.time-input').value.trim();
            if (word && time) {
                specialWords.push(`${word}:${time}`);
            }
        });
        
        const formData = new FormData(form);
        formData.append('special_words', specialWords.join(','));
        
        // 显示加载动画
        loading.classList.remove('hidden');
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loading.classList.add('hidden');
            
            if (data.success) {
                resultMessage.textContent = data.message;
                downloadLink.href = data.download_url;
                editLink.href = data.edit_url;  // 设置编辑链接
                form.classList.add('hidden');
                resultDiv.classList.remove('hidden');
            } else {
                alert('错误: ' + data.error);
            }
        })
        .catch(error => {
            loading.classList.add('hidden');
            alert('发生错误: ' + error);
        });
    });
    
    // 处理"处理另一个文件"按钮
    processAnother.addEventListener('click', function() {
        form.reset();
        form.classList.remove('hidden');
        resultDiv.classList.add('hidden');
    });
});