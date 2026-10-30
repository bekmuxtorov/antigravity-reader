/**
 * Antigravity Reader — Client Application Logic
 * Real-time SSE streaming, Markdown rendering, Reading controls.
 */

(function () {
  'use strict';

  // State
  let currentConvId = null;
  let conversations = [];
  let currentTurns = [];
  let eventSource = null;
  let fontScale = parseFloat(localStorage.getItem('ag_reader_font_scale')) || 1.0;
  let isWideMode = localStorage.getItem('ag_reader_wide_mode') === 'true';
  let currentTheme = localStorage.getItem('ag_reader_theme') || 'book'; // Default to warm book mode
  let searchQuery = '';

  // DOM Elements
  const convSelect = document.getElementById('conv-select');
  const liveIndicator = document.getElementById('live-indicator');
  const liveText = document.getElementById('live-text');
  const turnsFeed = document.getElementById('turns-feed');
  const loadingState = document.getElementById('loading-state');
  const quickJumpChips = document.getElementById('quick-jump-chips');
  const statTotalTurns = document.getElementById('stat-total-turns');
  const statLastTime = document.getElementById('stat-last-time');
  const filterInput = document.getElementById('filter-input');
  const clearSearchBtn = document.getElementById('clear-search');
  const themeBtnDark = document.getElementById('theme-btn-dark');
  const themeBtnBook = document.getElementById('theme-btn-book');
  const themeBtnLight = document.getElementById('theme-btn-light');
  const btnFontDec = document.getElementById('btn-font-dec');
  const btnFontInc = document.getElementById('btn-font-inc');
  const fontSizeLabel = document.getElementById('font-size-label');
  const btnToggleWidth = document.getElementById('btn-toggle-width');
  const readerContainer = document.getElementById('reader-container');
  const btnExportMd = document.getElementById('btn-export-md');
  const btnHideNavbar = document.getElementById('btn-hide-navbar');
  const btnShowNavbar = document.getElementById('btn-show-navbar');
  const toast = document.getElementById('toast');



  // Configure Marked Markdown Renderer
  if (typeof marked !== 'undefined') {
    const renderer = new marked.Renderer();

    // Custom code block rendering with Copy button & language tag
    renderer.code = function (arg1, arg2) {
      // Modern marked (v12+) passes a token object: { text, lang, raw, type }
      // Older versions pass (code, lang)
      let code = '';
      let lang = '';
      if (typeof arg1 === 'object' && arg1 !== null) {
        code = arg1.text || '';
        lang = arg1.lang || '';
      } else {
        code = String(arg1 || '');
        lang = String(arg2 || '');
      }

      const validLang = lang && typeof hljs !== 'undefined' && hljs.getLanguage(lang) ? lang : '';
      let highlighted = '';
      if (typeof hljs !== 'undefined') {
        try {
          highlighted = validLang 
            ? hljs.highlight(code, { language: validLang }).value 
            : hljs.highlightAuto(code).value;
        } catch (e) {
          highlighted = escapeHtml(code);
        }
      } else {
        highlighted = escapeHtml(code);
      }

      const displayLang = (lang || 'code').toUpperCase();
      const escapedCode = encodeURIComponent(code);

      return `
        <div class="code-block-wrapper">
          <div class="code-header">
            <span class="code-lang">${displayLang}</span>
            <button class="btn-copy-code" data-code="${escapedCode}" title="Kodni nusxalash">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              <span>Nusxa olish</span>
            </button>
          </div>
          <pre><code class="hljs ${validLang}">${highlighted}</code></pre>
        </div>
      `;
    };


    marked.setOptions({
      renderer: renderer,
      breaks: true,
      gfm: true
    });
  }

  // Toast notification
  function showToast(message) {
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2200);
  }

  // Apply Font Scaling
  function updateFontScale(scale) {
    fontScale = Math.max(0.8, Math.min(1.4, scale));
    document.documentElement.style.setProperty('--font-scale', fontScale);
    fontSizeLabel.textContent = `${Math.round(fontScale * 100)}%`;
    localStorage.setItem('ag_reader_font_scale', fontScale);
  }

  // Apply Width Mode
  function updateWidthMode(wide) {
    isWideMode = wide;
    if (isWideMode) {
      readerContainer.classList.add('wide-mode');
    } else {
      readerContainer.classList.remove('wide-mode');
    }
    localStorage.setItem('ag_reader_wide_mode', isWideMode);
  }

  // Apply Theme Mode (dark, book, light)
  function setTheme(themeName, showNotification = false) {
    currentTheme = themeName;
    if (themeName === 'book') {
      document.body.setAttribute('data-theme', 'book');
      if (showNotification) showToast("📖 Kitob rejimi yoqildi (Iliq sariq qog'oz)");
    } else if (themeName === 'light') {
      document.body.setAttribute('data-theme', 'light');
      if (showNotification) showToast("☀️ Yorug' rejim yoqildi");
    } else {
      document.body.removeAttribute('data-theme');
      if (showNotification) showToast("🌙 Qorong'i rejim yoqildi");
    }

    [themeBtnDark, themeBtnBook, themeBtnLight].forEach(btn => {
      if (btn) {
        btn.classList.toggle('active', btn.getAttribute('data-theme') === themeName);
      }
    });

    localStorage.setItem('ag_reader_theme', themeName);
  }


  // Copy text helper
  function copyToClipboard(text, successMsg = "Nusxa olindi!") {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(() => showToast(successMsg));
    } else {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        showToast(successMsg);
      } catch (err) {
        showToast("Nusxalashda xatolik");
      }
      document.body.removeChild(textarea);
    }
  }

  // Render Jump Chips
  function renderJumpChips(turns) {
    quickJumpChips.innerHTML = '<span class="jump-title">Navbat:</span>';
    turns.forEach(turn => {
      const chip = document.createElement('a');
      chip.className = 'chip-btn';
      chip.href = `#turn-${turn.id}`;
      chip.textContent = `#${turn.id}`;
      chip.title = `Savol #${turn.id}: ${turn.prompt.slice(0, 40)}...`;
      quickJumpChips.appendChild(chip);
    });
  }

  // Render Turns List
  function renderTurns(turns) {
    if (!turns || turns.length === 0) {
      loadingState.style.display = 'block';
      loadingState.innerHTML = '<p>Ushbu suhbatda hali javoblar mavjud emas.</p>';
      turnsFeed.innerHTML = '';
      statTotalTurns.textContent = '0 ta javob';
      return;
    }

    loadingState.style.display = 'none';

    // Filter by search query if any
    const filtered = !searchQuery.trim() ? turns : turns.filter(t => {
      const q = searchQuery.toLowerCase();
      return (t.prompt && t.prompt.toLowerCase().includes(q)) ||
             (t.response && t.response.toLowerCase().includes(q));
    });

    statTotalTurns.textContent = `${turns.length} ta javob${filtered.length !== turns.length ? ` (${filtered.length} ta mos keldi)` : ''}`;
    if (turns.length > 0) {
      statLastTime.textContent = turns[turns.length - 1].response_time || '';
    }

    renderJumpChips(turns);

    turnsFeed.innerHTML = '';

    filtered.forEach(turn => {
      const card = document.createElement('article');
      card.className = 'turn-card';
      card.id = `turn-${turn.id}`;

      // User prompt section
      const promptSec = document.createElement('div');
      promptSec.className = 'turn-prompt-section';
      promptSec.innerHTML = `
        <div class="user-avatar-badge" title="Foydalanuvchi so'rovi">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        </div>
        <div class="prompt-details">
          <div class="prompt-meta">
            <span class="turn-badge">#${turn.id}</span>
            <span class="prompt-timestamp">${turn.user_time || ''}</span>
          </div>
          <div class="prompt-text">${escapeHtml(turn.prompt)}</div>
        </div>
      `;

      // AI Response section
      const responseSec = document.createElement('div');
      responseSec.className = 'turn-response-section';

      const markdownHtml = typeof marked !== 'undefined' 
        ? marked.parse(turn.response) 
        : `<pre>${escapeHtml(turn.response)}</pre>`;

      responseSec.innerHTML = `
        <div class="response-toolbar">
          <div class="ai-meta-indicator">
            <svg class="ai-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
              <polyline points="2 17 12 22 22 17"></polyline>
              <polyline points="2 12 12 17 22 12"></polyline>
            </svg>
            <span>Antigravity Javobi</span>
          </div>
          <div class="response-actions">
            <button class="btn-icon-subtle btn-copy-response" title="Butun javobni nusxalash">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              <span>Nusxa olish</span>
            </button>
          </div>
        </div>
        <div class="markdown-body">
          ${markdownHtml}
        </div>
      `;

      // Wire up copy response button
      const copyBtn = responseSec.querySelector('.btn-copy-response');
      copyBtn.addEventListener('click', () => {
        copyToClipboard(turn.response, `#${turn.id} javobi nusxalandi!`);
      });

      card.appendChild(promptSec);
      card.appendChild(responseSec);
      turnsFeed.appendChild(card);
    });

    // Wire up code block copy buttons
    document.querySelectorAll('.btn-copy-code').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const rawCode = decodeURIComponent(btn.getAttribute('data-code'));
        copyToClipboard(rawCode, "Kod nusxalandi!");
      });
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Connect Server-Sent Events (SSE)
  function connectStream(convId) {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }

    liveIndicator.className = 'live-pill connected';
    liveText.textContent = "Jonli ulanmoqda...";

    eventSource = new EventSource(`/api/stream?id=${encodeURIComponent(convId)}`);

    eventSource.onopen = function () {
      liveIndicator.className = 'live-pill connected';
      liveText.textContent = "Jonli bog'langan";
    };

    eventSource.onmessage = function (event) {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'init' || data.type === 'update') {
          const prevLength = currentTurns.length;
          currentTurns = data.turns || [];
          renderTurns(currentTurns);

          // If a new turn was added, smoothly scroll to it
          if (data.type === 'update' && currentTurns.length > prevLength && prevLength > 0) {
            const lastTurn = currentTurns[currentTurns.length - 1];
            const elem = document.getElementById(`turn-${lastTurn.id}`);
            if (elem) {
              elem.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            showToast(`Yangi javob keldi: #${lastTurn.id}!`);
          }
        }
      } catch (err) {
        console.error('SSE data parse error:', err);
      }
    };

    eventSource.onerror = function () {
      liveIndicator.className = 'live-pill';
      liveIndicator.style.background = 'rgba(239, 68, 68, 0.15)';
      liveIndicator.style.borderColor = 'rgba(239, 68, 68, 0.3)';
      liveIndicator.style.color = '#f87171';
      liveText.textContent = "Qayta ulanmoqda...";
    };
  }

  // Load Specific Conversation
  async function loadConversation(convId) {
    currentConvId = convId;
    btnExportMd.href = `/api/export?id=${encodeURIComponent(convId)}`;

    loadingState.style.display = 'block';
    loadingState.innerHTML = '<div class="spinner"></div><p>Suhbat yuklanmoqda...</p>';
    turnsFeed.innerHTML = '';

    try {
      const res = await fetch(`/api/conversation?id=${encodeURIComponent(convId)}`);
      const data = await res.json();
      currentTurns = data.turns || [];
      renderTurns(currentTurns);
      connectStream(convId);
    } catch (err) {
      loadingState.style.display = 'block';
      loadingState.innerHTML = `<p style="color: #ef4444;">Yuklashda xatolik: ${err.message}</p>`;
    }
  }

  // Fetch conversations list
  async function fetchConversations() {
    try {
      const res = await fetch('/api/conversations');
      conversations = await res.json();

      convSelect.innerHTML = '';
      if (!conversations || conversations.length === 0) {
        convSelect.innerHTML = '<option value="">Hech qanday suhbat topilmadi</option>';
        return;
      }

      conversations.forEach((conv, index) => {
        const opt = document.createElement('option');
        opt.value = conv.id;
        const tag = index === 0 ? ' [FAOL]' : '';
        opt.textContent = `${conv.updated_at.slice(5, 16)} — ${conv.title}${tag} (${conv.turns_count} ta)`;
        convSelect.appendChild(opt);
      });

      // Default to the first (latest) conversation
      const activeId = conversations[0].id;
      convSelect.value = activeId;
      loadConversation(activeId);
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
      convSelect.innerHTML = '<option value="">Xatolik yuz berdi</option>';
    }
  }

  // Event Listeners
  convSelect.addEventListener('change', (e) => {
    if (e.target.value) {
      loadConversation(e.target.value);
    }
  });

  // Font adjustments
  btnFontDec.addEventListener('click', () => updateFontScale(fontScale - 0.08));
  btnFontInc.addEventListener('click', () => updateFontScale(fontScale + 0.08));

  // Width toggle
  btnToggleWidth.addEventListener('click', () => updateWidthMode(!isWideMode));

  // Search filter
  filterInput.addEventListener('input', (e) => {
    searchQuery = e.target.value;
    clearSearchBtn.style.display = searchQuery ? 'block' : 'none';
    renderTurns(currentTurns);
  });

  clearSearchBtn.addEventListener('click', () => {
    filterInput.value = '';
    searchQuery = '';
    clearSearchBtn.style.display = 'none';
    renderTurns(currentTurns);
  });

  // Navbar Hide / Show Toggle Logic
  function hideNavbar() {
    document.body.classList.add('is-navbar-hidden');
    showToast("Navbar yashirildi (Fokus rejimi)");
  }

  function showNavbar() {
    document.body.classList.remove('is-navbar-hidden');
    showToast("Navbar ko'rsatildi");
  }

  if (btnHideNavbar) btnHideNavbar.addEventListener('click', hideNavbar);
  if (btnShowNavbar) btnShowNavbar.addEventListener('click', showNavbar);

  // Keyboard shortcuts: Ctrl+K to search, Esc to restore navbar
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      filterInput.focus();
    } else if (e.key === 'Escape') {
      if (document.body.classList.contains('is-navbar-hidden')) {
        showNavbar();
      }
    }
  });

  // Theme switcher listeners
  if (themeBtnDark) themeBtnDark.addEventListener('click', () => setTheme('dark', true));
  if (themeBtnBook) themeBtnBook.addEventListener('click', () => setTheme('book', true));
  if (themeBtnLight) themeBtnLight.addEventListener('click', () => setTheme('light', true));

  // Initialize
  setTheme(currentTheme, false);
  updateFontScale(fontScale);
  updateWidthMode(isWideMode);
  fetchConversations();



})();
