const chat = document.getElementById('chat');
const input = document.getElementById('input');
const send = document.getElementById('send');
const useWebSearch = document.getElementById('use_web_search');
const typing = document.getElementById('typing');
// Feature bar buttons
const btnWeb = document.getElementById('btn_web_search');
const btnCopy = document.getElementById('btn_copy');
const btnClear = document.getElementById('btn_clear');
const btnAbout = document.getElementById('btn_about');
const aboutModal = document.getElementById('about_modal');
const aboutClose = document.getElementById('about_close');
const btnTheme = document.getElementById('btn_theme');

// Apply saved theme early (also mirrored in DOMContentLoaded safeguard)
try {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') document.documentElement.classList.add('light');
} catch { }

function addMessage(text, role) {
    const row = document.createElement('div');
    row.className = `msg-row ${role}`;

    const avatar = document.createElement('div');
    avatar.className = `avatar ${role}`;
    avatar.textContent = role === 'user' ? '🧑' : '🤖';

    const bubble = document.createElement('div');
    bubble.className = `bubble ${role}`;
    bubble.textContent = text;

    row.appendChild(avatar);
    row.appendChild(bubble);
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
    return bubble;
}

function showTyping() {
    typing.innerHTML = '';
    const row = document.createElement('div');
    row.className = 'typing-row';
    const avatar = document.createElement('div');
    avatar.className = 'avatar assistant';
    avatar.textContent = '🤖';
    const bubble = document.createElement('div');
    bubble.className = 'typing-bubble';
    bubble.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    row.appendChild(avatar);
    row.appendChild(bubble);
    typing.appendChild(row);
    typing.style.display = 'block';
}

function hideTyping() {
    typing.style.display = 'none';
    typing.innerHTML = '';
}

async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    send.disabled = true;

    addMessage(text, 'user');
    showTyping();
    const assistantBubble = addMessage('', 'assistant');

    const messages = [
        { role: 'system', content: 'You are a helpful assistant.' },
        { role: 'user', content: text }
    ];

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages, use_web_search: useWebSearch.checked })
        });

        if (!res.ok || !res.body) {
            hideTyping();
            const errText = await res.text().catch(() => 'Unknown error');
            assistantBubble.textContent = 'Error: ' + errText;
            send.disabled = false;
            return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
        while (!done) {
            const { value, done: doneReading } = await reader.read();
            if (value) assistantBubble.textContent += decoder.decode(value);
            done = doneReading;
        }
    } catch (e) {
        assistantBubble.textContent = 'Network error. Is the server running on this port?';
    } finally {
        hideTyping();
        send.disabled = false;
    }
}

send.addEventListener('click', sendMessage);
input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// --- Feature bar actions ---
if (btnWeb) btnWeb.onclick = () => { useWebSearch.checked = !useWebSearch.checked; };
if (btnCopy) btnCopy.onclick = async () => {
    // Collect visible transcript text
    const parts = Array.from(chat.querySelectorAll('.bubble')).map(el => el.textContent);
    try { await navigator.clipboard.writeText(parts.join('\n\n')); btnCopy.textContent = '✅ Copied'; setTimeout(() => btnCopy.textContent = '📋 Copy Transcript', 1500); } catch { }
};
if (btnClear) btnClear.onclick = () => { chat.innerHTML = ''; typing.innerHTML = ''; typing.style.display = 'none'; };
if (btnAbout) btnAbout.onclick = () => { if (aboutModal) { aboutModal.style.display = 'flex'; } };
if (aboutClose) aboutClose.onclick = () => { if (aboutModal) { aboutModal.style.display = 'none'; } };

// Theme toggle
if (btnTheme) btnTheme.onclick = () => {
    const root = document.documentElement;
    const isLight = root.classList.toggle('light');
    try { localStorage.setItem('theme', isLight ? 'light' : 'dark'); } catch { }
};

// Ensure theme on first paint
document.addEventListener('DOMContentLoaded', () => {
    try {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') document.documentElement.classList.add('light');
    } catch { }
});
