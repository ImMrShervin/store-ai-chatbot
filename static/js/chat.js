
const API = {
  newSession: '/api/chat/session/new',
  message:    '/api/chat/message',
  clear:      (id) => `/api/chat/session/${id}/clear`,
  history:    (id) => `/api/chat/session/${id}/history`,
};

const els = {
  messages: document.getElementById('messages'),
  input:    document.getElementById('input'),
  send:     document.getElementById('sendBtn'),
  form:     document.getElementById('composer'),
  typing:   document.getElementById('typing'),
  clearBtn: document.getElementById('clearBtn'),
  themeBtn: document.getElementById('themeBtn'),
};

let sessionId = localStorage.getItem('chatbot_session_id') || null;

const time = () => new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' });

const isLTR = (text) => {
  const m = text.match(/[A-Za-z\u0590-\u05FF\u0600-\u06FF]/);
  return m ? /[A-Za-z]/.test(m[0]) : false;
};

const escapeHtml = (s) => s
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;');

const mdRender = (text) => {
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/(^|\s)\*([^*\n]+)\*(?=\s|$)/g, '$1<em>$2</em>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/(^|\n)[-•]\s+(.+)/g, '$1<li>$2</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m.replace(/\n/g,'')}</ul>`);
  return html;
};

const scrollBottom = () => {
  requestAnimationFrame(() => {
    els.messages.scrollTop = els.messages.scrollHeight;
  });
};

const appendMessage = (role, content) => {
  const wrap = document.createElement('div');
  wrap.className = `msg ${role === 'user' ? 'user' : 'bot'}`;
  if (isLTR(content)) wrap.classList.add('ltr');
  wrap.innerHTML = `${mdRender(content)}<span class="time">${time()}</span>`;
  els.messages.appendChild(wrap);
  scrollBottom();
};

const showTyping = (v) => els.typing.classList.toggle('hidden', !v);

async function startSession() {
  if (sessionId) {
    try {
      const res = await fetch(API.history(sessionId));
      if (res.ok) {
        const data = await res.json();
        if (data.messages && data.messages.length) {
          data.messages.forEach((m) => appendMessage(m.role, m.content));
          return;
        }
      }
    } catch (_) { }
  }
  const res = await fetch(API.newSession, { method: 'POST' });
  const data = await res.json();
  sessionId = data.session_id;
  localStorage.setItem('chatbot_session_id', sessionId);
  appendMessage('assistant', data.welcome_message);
}

async function sendMessage(text) {
  appendMessage('user', text);
  showTyping(true);
  els.send.disabled = true;

  try {
    const res = await fetch(API.message, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, session_id: sessionId }),
    });
    const data = await res.json();
    showTyping(false);

    if (!res.ok) {
      const err = data.message || data.error || 'خطا در ارتباط با سرور';
      appendMessage('assistant', `⚠️ ${err}`);
      return;
    }
    sessionId = data.session_id;
    localStorage.setItem('chatbot_session_id', sessionId);
    appendMessage('assistant', data.reply);
  } catch (e) {
    showTyping(false);
    appendMessage('assistant', `⚠️ خطا در برقراری ارتباط: ${e.message}`);
  } finally {
    els.send.disabled = false;
    els.input.focus();
  }
}

async function clearConversation() {
  if (!sessionId) return;
  if (!confirm('آیا از پاک کردن گفتگو مطمئن هستید؟ / Clear conversation?')) return;
  await fetch(API.clear(sessionId), { method: 'POST' });
  els.messages.innerHTML = '';
  localStorage.removeItem('chatbot_session_id');
  sessionId = null;
  await startSession();
}

function toggleTheme() {
  document.body.classList.toggle('dark');
  localStorage.setItem('chatbot_theme', document.body.classList.contains('dark') ? 'dark' : 'light');
}
if (localStorage.getItem('chatbot_theme') === 'dark') {
  document.body.classList.add('dark');
}

els.input.addEventListener('input', () => {
  els.input.style.height = 'auto';
  els.input.style.height = Math.min(els.input.scrollHeight, 140) + 'px';
});

els.input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    els.form.requestSubmit();
  }
});

els.form.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = els.input.value.trim();
  if (!text) return;
  els.input.value = '';
  els.input.style.height = 'auto';
  sendMessage(text);
});

els.clearBtn.addEventListener('click', clearConversation);
els.themeBtn.addEventListener('click', toggleTheme);

startSession();
