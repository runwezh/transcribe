document.addEventListener('DOMContentLoaded', () => {
    const mediaFileInput = document.getElementById('media-file');
    const subtitleFileInput = document.getElementById('subtitle-file');
    const mediaPlayer = document.getElementById('media-player');
    const subtitleContainer = document.getElementById('subtitle-container');

    let subtitles = [];
    let subtitleType = 'sentence'; // 'sentence' or 'word'

    mediaFileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const url = URL.createObjectURL(file);
            mediaPlayer.src = url;
        }
    });

    subtitleFileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const content = e.target.result;
                const extension = file.name.split('.').pop().toLowerCase();
                parseSubtitles(content, extension);
            };
            reader.readAsText(file);
        }
    });

    function parseSubtitles(content, format) {
        subtitleContainer.innerHTML = ''; // Clear previous subtitles
        if (format === 'vtt') {
            subtitles = parseVTT(content);
            subtitleType = 'sentence';
        } else if (format === 'srt') {
            subtitles = parseSRT(content);
            subtitleType = 'sentence';
        } else if (format === 'json') {
            subtitles = parseJSON(content);
            subtitleType = 'word';
        }
        renderSubtitles();
    }

    function timeToSeconds(timeStr) {
        const parts = timeStr.split(':');
        let seconds = 0;
        if (parts.length === 3) {
            seconds += Number.parseFloat(parts[0]) * 3600;
            seconds += Number.parseFloat(parts[1]) * 60;
            seconds += Number.parseFloat(parts[2].replace(',', '.'));
        } else {
            seconds += Number.parseFloat(parts[0]) * 60;
            seconds += Number.parseFloat(parts[1].replace(',', '.'));
        }
        return seconds;
    }

    function parseVTT(data) {
        const lines = data.trim().split('\n');
        const subs = [];
        let i = 0;
        while (i < lines.length) {
            if (lines[i].includes('-->')) {
                const [start, end] = lines[i].split(' --> ').map(s => s.trim());
                let text = '';
                i++;
                while (i < lines.length && lines[i].trim() !== '') {
                    text += `${lines[i].trim()} `;
                    i++;
                }
                subs.push({ start: timeToSeconds(start), end: timeToSeconds(end), text: text.trim() });
            }
            i++;
        }
        return subs;
    }

    function parseSRT(data) {
        const blocks = data.trim().split('\n\n');
        return blocks.map(block => {
            const lines = block.split('\n');
            if (lines.length >= 3) {
                const [start, end] = lines[1].split(' --> ').map(s => s.trim());
                const text = lines.slice(2).join(' ').trim();
                return { start: timeToSeconds(start), end: timeToSeconds(end), text };
            }
            return null;
        }).filter(Boolean);
    }

    function parseJSON(data) {
        const parsedData = JSON.parse(data);
        return parsedData.segments || [];
    }

    function renderSubtitles() {
        subtitleContainer.innerHTML = '';
        if (subtitleType === 'sentence') {
            for (const [index, sub] of subtitles.entries()) {
                const p = document.createElement('p');
                p.textContent = sub.text;
                p.dataset.index = index;
                p.classList.add('sentence');
                subtitleContainer.appendChild(p);
            }
        } else if (subtitleType === 'word') {
            for (const [segmentIndex, segment] of subtitles.entries()) {
                const p = document.createElement('p');
                p.classList.add('sentence');
                p.dataset.segmentIndex = segmentIndex;
                for (const [wordIndex, word] of segment.words.entries()) {
                    const span = document.createElement('span');
                    span.textContent = `${word.text} `;
                    span.dataset.wordIndex = wordIndex;
                    span.classList.add('word');
                    p.appendChild(span);
                }
                subtitleContainer.appendChild(p);
            }
        }
    }

    mediaPlayer.addEventListener('timeupdate', () => {
        const currentTime = mediaPlayer.currentTime;
        if (subtitleType === 'sentence') {
            updateSentenceHighlight(currentTime);
        } else if (subtitleType === 'word') {
            updateWordHighlight(currentTime);
        }
    });

    function updateSentenceHighlight(currentTime) {
        const activeSub = subtitles.find(sub => currentTime >= sub.start && currentTime <= sub.end);
        for (const p of document.querySelectorAll('#subtitle-container .sentence')) {
            p.classList.remove('active-sentence');
        }
        if (activeSub) {
            const activeP = document.querySelector(`#subtitle-container .sentence[data-index='${subtitles.indexOf(activeSub)}']`);
            if (activeP) {
                activeP.classList.add('active-sentence');
            }
        }
    }

    function updateWordHighlight(currentTime) {
        let activeSegment = null;
        let activeWord = null;

        for (const segment of subtitles) {
            if (currentTime >= segment.start_time && currentTime <= segment.end_time) {
                activeSegment = segment;
                for (const word of segment.words) {
                    if (currentTime >= word.start_time && currentTime <= word.end_time) {
                        activeWord = word;
                        break;
                    }
                }
                break;
            }
        }

        for (const span of document.querySelectorAll('#subtitle-container .word')) {
            span.classList.remove('active-word');
        }
        for (const p of document.querySelectorAll('#subtitle-container .sentence')) {
            p.classList.remove('active-sentence');
        }

        if (activeSegment) {
            const segmentIndex = subtitles.indexOf(activeSegment);
            const activeP = document.querySelector(`#subtitle-container .sentence[data-segment-index='${segmentIndex}']`);
            if (activeP) {
                activeP.classList.add('active-sentence');
                if (activeWord) {
                    const wordIndex = activeSegment.words.indexOf(activeWord);
                    const activeSpan = activeP.querySelector(`span[data-word-index='${wordIndex}']`);
                    if (activeSpan) {
                        activeSpan.classList.add('active-word');
                    }
                }
            }
        }
    }
});
