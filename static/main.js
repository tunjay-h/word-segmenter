document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyze-form');
    const apiKeyInput = document.getElementById('api-key');
    const wordInput = document.getElementById('word');
    const wordsInput = document.getElementById('words');
    const fileInput = document.getElementById('file');
    const outputDiv = document.getElementById('output');
    const tabSingle = document.getElementById('tab-single');
    const tabBatch = document.getElementById('tab-batch');
    const tabFile = document.getElementById('tab-file');
    const singleInput = document.getElementById('single-input');
    const batchInput = document.getElementById('batch-input');
    const fileInputDiv = document.getElementById('file-input');
    let mode = 'single';

    function switchTab(newMode) {
        mode = newMode;
        tabSingle.classList.toggle('active', mode === 'single');
        tabBatch.classList.toggle('active', mode === 'batch');
        tabFile.classList.toggle('active', mode === 'file');
        singleInput.style.display = mode === 'single' ? '' : 'none';
        batchInput.style.display = mode === 'batch' ? '' : 'none';
        fileInputDiv.style.display = mode === 'file' ? '' : 'none';
    }
    tabSingle.onclick = () => switchTab('single');
    tabBatch.onclick = () => switchTab('batch');
    tabFile.onclick = () => switchTab('file');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        outputDiv.innerHTML = '<span style="color:#888">Analyzing...</span>';
        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            outputDiv.innerHTML = '<span style="color:red">Please provide your API key.</span>';
            return;
        }
        if (mode === 'single') {
            const word = wordInput.value.trim();
            if (!word) {
                outputDiv.innerHTML = '<span style="color:red">Please enter a word.</span>';
                return;
            }
            try {
                const response = await fetch('/analyze/single', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'api-key': apiKey
                    },
                    body: JSON.stringify({ word })
                });
                const result = await response.json();
                if (response.ok) {
                    outputDiv.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
                } else {
                    outputDiv.innerHTML = '<span style="color:red">Error: ' + (result.detail || 'Unknown error') + '</span>';
                }
            } catch (err) {
                outputDiv.innerHTML = '<span style="color:red">Network error: ' + err.message + '</span>';
            }
        } else if (mode === 'batch') {
            const words = wordsInput.value.split('\n').map(w => w.trim()).filter(Boolean);
            if (!words.length) {
                outputDiv.innerHTML = '<span style="color:red">Please enter one or more words.</span>';
                return;
            }
            try {
                const response = await fetch('/analyze/batch', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'api-key': apiKey
                    },
                    body: JSON.stringify({ words })
                });
                const result = await response.json();
                if (response.ok) {
                    outputDiv.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
                } else {
                    outputDiv.innerHTML = '<span style="color:red">Error: ' + (result.detail || 'Unknown error') + '</span>';
                }
            } catch (err) {
                outputDiv.innerHTML = '<span style="color:red">Network error: ' + err.message + '</span>';
            }
        } else if (mode === 'file') {
            const file = fileInput.files[0];
            if (!file) {
                outputDiv.innerHTML = '<span style="color:red">Please upload a .txt file.</span>';
                return;
            }
            const formData = new FormData();
            formData.append('file', file);
            try {
                const response = await fetch('/analyze/upload', {
                    method: 'POST',
                    headers: {
                        'api-key': apiKey
                    },
                    body: formData
                });
                const result = await response.json();
                if (response.ok) {
                    outputDiv.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
                } else {
                    outputDiv.innerHTML = '<span style="color:red">Error: ' + (result.detail || 'Unknown error') + '</span>';
                }
            } catch (err) {
                outputDiv.innerHTML = '<span style="color:red">Network error: ' + err.message + '</span>';
            }
        }
    });
});
