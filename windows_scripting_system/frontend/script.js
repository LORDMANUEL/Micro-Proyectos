document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://127.0.0.1:5008/api';

    // Elements
    const generateScriptForm = document.getElementById('generate-script-form');
    const generatedScriptOutput = document.getElementById('generated-script-output');
    const saveGeneratedScriptBtn = document.getElementById('save-generated-script-btn');
    const scriptList = document.getElementById('script-list');
    const showAddScriptFormBtn = document.getElementById('show-add-script-form-btn');
    const addScriptModal = document.getElementById('add-script-modal');
    const addScriptForm = document.getElementById('add-script-form');
    const closeModalBtn = document.querySelector('.close-btn');

    let lastGeneratedScript = {};

    // --- Core Functions ---
    async function fetchData(endpoint) {
        try {
            const response = await fetch(`${apiUrl}${endpoint}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    async function postData(endpoint, data) {
        try {
            const response = await fetch(`${apiUrl}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            return await response.json();
        } catch (error) {
            console.error('Error posting data:', error);
        }
    }

    // --- Render Functions ---
    async function renderScripts() {
        const scripts = await fetchData('/scripts');
        scriptList.innerHTML = '';
        if (!scripts) return;
        scripts.forEach(script => {
            const item = document.createElement('div');
            item.className = 'script-item';
            item.innerHTML = `
                <h4>${script.title} (${script.script_type})</h4>
                <p>${script.description}</p>
                <pre><code>${script.content}</code></pre>
                <button class="btn delete-btn" data-id="${script.id}">Eliminar</button>
            `;
            scriptList.appendChild(item);
        });
    }

    // --- Event Listeners ---
    generateScriptForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = document.getElementById('ai-prompt').value;
        const script_type = document.getElementById('ai-script-type').value;

        generatedScriptOutput.textContent = 'Generando...';
        saveGeneratedScriptBtn.style.display = 'none';

        const response = await postData('/generate-script', { prompt, script_type });

        generatedScriptOutput.textContent = response.generated_script;
        lastGeneratedScript = {
            title: prompt.substring(0, 30), // Short title from prompt
            description: prompt,
            script_type: script_type,
            content: response.generated_script,
        };
        saveGeneratedScriptBtn.style.display = 'block';
    });

    saveGeneratedScriptBtn.addEventListener('click', async () => {
        if (lastGeneratedScript.content) {
            await postData('/scripts', lastGeneratedScript);
            alert('¡Script guardado en tu repositorio!');
            renderScripts();
            saveGeneratedScriptBtn.style.display = 'none';
        }
    });

    showAddScriptFormBtn.addEventListener('click', () => {
        addScriptModal.style.display = 'block';
    });

    closeModalBtn.addEventListener('click', () => {
        addScriptModal.style.display = 'none';
    });

    addScriptForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            title: document.getElementById('script-title').value,
            description: document.getElementById('script-description').value,
            script_type: document.getElementById('script-type').value,
            content: document.getElementById('script-content').value,
        };
        await postData('/scripts', data);
        addScriptForm.reset();
        addScriptModal.style.display = 'none';
        renderScripts();
    });

    scriptList.addEventListener('click', async (e) => {
        if (e.target.classList.contains('delete-btn')) {
            const scriptId = e.target.dataset.id;
            if (confirm('¿Seguro que quieres eliminar este script?')) {
                await fetch(`${apiUrl}/scripts/${scriptId}`, { method: 'DELETE' });
                renderScripts();
            }
        }
    });

    // --- Initial Load ---
    renderScripts();
});
