document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const fileInput = document.getElementById('file-input');
    const userTopics = document.getElementById('user-topics');
    const apiKeyInput = document.getElementById('api-key');
    const modelSelect = document.getElementById('model-select'); // New
    const generateTopicsBtn = document.getElementById('generate-topics-btn');
    const topicSelectionStatus = document.getElementById('topic-selection-status');
    const refinementControls = document.getElementById('refinement-controls');
    const selectedTopicsOutput = document.getElementById('selected-topics-output');
    const critiqueBtn = document.getElementById('critique-btn');
    const acceptTopicsBtn = document.getElementById('accept-topics-btn');
    const chunkingStep = document.getElementById('chunking-step');
    const tokenLimitInput = document.getElementById('token-limit');
    const chunkContentBtn = document.getElementById('chunk-content-btn');
    const chunkingStatus = document.getElementById('chunking-status');
    const flashcardStep = document.getElementById('flashcard-step');
    const ankiDeckInput = document.getElementById('anki-deck');
    const ankiConnectUrlInput = document.getElementById('anki-connect-url');
    const generateFlashcardsBtn = document.getElementById('generate-flashcards-btn');
    const flashcardStatus = document.getElementById('flashcard-status');

    // --- State Management ---
    let markdownFiles = {};
    let allHeadings = [];
    let selectedTopics = [];
    let contentChunks = [];

    const API_URL = 'http://localhost:5001/api';

    // --- Helper Functions ---
    function showStatus(element, message, isError = false) {
        element.classList.remove('hidden');
        element.textContent = message;
        element.style.color = isError ? '#dc3545' : '#1c1e21';
    }

    function toggleButtons(disabled) {
        generateTopicsBtn.disabled = disabled;
        critiqueBtn.disabled = disabled;
        acceptTopicsBtn.disabled = disabled;
        chunkContentBtn.disabled = disabled;
        generateFlashcardsBtn.disabled = disabled;
    }

    // --- Event Listeners ---

    fileInput.addEventListener('change', async (event) => {
        const files = event.target.files;
        markdownFiles = {};
        showStatus(topicSelectionStatus, `Reading ${files.length} file(s)...`);
        await Promise.all(Array.from(files).map(async (file) => {
            if (file.name.endsWith('.md')) {
                markdownFiles[file.name] = await file.text();
            }
        }));
        showStatus(topicSelectionStatus, `Successfully loaded ${Object.keys(markdownFiles).length} markdown files.`);
    });

    generateTopicsBtn.addEventListener('click', async () => {
        if (Object.keys(markdownFiles).length === 0 || !userTopics.value.trim() || !apiKeyInput.value.trim()) {
            showStatus(topicSelectionStatus, 'Error: Please select files, provide topics, and enter an API key.', true);
            return;
        }
        showStatus(topicSelectionStatus, 'Sending data to AI for topic selection...');
        toggleButtons(true);

        try {
            const response = await fetch(`${API_URL}/generate-topics`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    files: markdownFiles,
                    user_topics: userTopics.value,
                    api_key: apiKeyInput.value,
                    model_name: modelSelect.value // New
                })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Unknown error');

            allHeadings = data.all_headings;
            selectedTopics = data.selected_topics;

            selectedTopicsOutput.textContent = JSON.stringify(selectedTopics, null, 2);
            refinementControls.classList.remove('hidden');
            showStatus(topicSelectionStatus, 'Initial topic list generated. Please review.');
        } catch (error) {
            showStatus(topicSelectionStatus, `Error: ${error.message}`, true);
        } finally {
            toggleButtons(false);
        }
    });

    critiqueBtn.addEventListener('click', async () => {
        showStatus(topicSelectionStatus, 'Asking Critic AI to review and refine the selection...');
        toggleButtons(true);

        try {
            const response = await fetch(`${API_URL}/refine-topics`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    all_headings: allHeadings,
                    user_topics: userTopics.value,
                    selected_topics: selectedTopics,
                    api_key: apiKeyInput.value,
                    model_name: modelSelect.value // New
                })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Unknown error');

            selectedTopics = data.refined_topics;
            const critiqueReport = JSON.stringify(data.critique, null, 2);
            selectedTopicsOutput.textContent = JSON.stringify(selectedTopics, null, 2);
            showStatus(topicSelectionStatus, `Critique complete and list refined:\n${critiqueReport}`);

        } catch (error) {
            showStatus(topicSelectionStatus, `Error: ${error.message}`, true);
        } finally {
            toggleButtons(false);
        }
    });

    acceptTopicsBtn.addEventListener('click', () => {
        showStatus(topicSelectionStatus, 'Topics accepted. Proceeding to Step 3.');
        chunkingStep.classList.remove('hidden');
        showStatus(chunkingStatus, 'Ready to chunk content.');
    });

    chunkContentBtn.addEventListener('click', async () => {
        showStatus(chunkingStatus, 'Reconstructing and chunking content...');
        toggleButtons(true);

        try {
            const response = await fetch(`${API_URL}/chunk-content`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    all_headings: allHeadings,
                    selected_topics: selectedTopics,
                    token_limit: parseInt(tokenLimitInput.value, 10)
                })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Unknown error');

            contentChunks = data.chunks;
            const summary = `${contentChunks.length} chunks created.\n` + contentChunks.map((c, i) => `Chunk ${i+1}: ${c.warning || 'OK'}`).join('\n');
            showStatus(chunkingStatus, summary);
            flashcardStep.classList.remove('hidden');

        } catch (error) {
            showStatus(chunkingStatus, `Error: ${error.message}`, true);
        } finally {
            toggleButtons(false);
        }
    });

    generateFlashcardsBtn.addEventListener('click', async () => {
        if (!ankiDeckInput.value.trim()) {
            showStatus(flashcardStatus, 'Error: Please provide a main Anki deck name.', true);
            return;
        }
        showStatus(flashcardStatus, `Generating flashcards for ${contentChunks.length} chunks and adding to Anki... This may take a while.`);
        toggleButtons(true);

        try {
            const response = await fetch(`${API_URL}/generate-flashcards`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chunks: contentChunks,
                    api_key: apiKeyInput.value,
                    model_name: modelSelect.value, // New
                    anki_deck: ankiDeckInput.value,
                    anki_connect_url: ankiConnectUrlInput.value
                })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Unknown error');

            showStatus(flashcardStatus, data.message);

        } catch (error) {
            showStatus(flashcardStatus, `Error: ${error.message}`, true);
        } finally {
            toggleButtons(false);
        }
    });
});