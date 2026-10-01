"""Hashtag GitHub Direct Cloud Web IDE & Development Studio.

Allows developers to build, edit, preview, and commit projects directly to GitHub
without ever needing local PC setup, git installations, or cloning.
"""

STUDIO_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Hashtag GitHub Cloud Studio</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #070b14;
      --panel: #0d1424;
      --panel2: #121c32;
      --border: rgba(120, 169, 255, 0.14);
      --border-focus: rgba(120, 169, 255, 0.4);
      --text: #eaf1fb;
      --muted: #8294ad;
      --accent: #78a9ff;
      --accent-glow: rgba(120, 169, 255, 0.35);
      --good: #52e396;
      --good-glow: rgba(82, 227, 150, 0.35);
      --warning: #f2c76d;
      --danger: #ff6b7e;
      --editor-bg: #090e1a;
    }
    * { box-sizing: border-box; }
    html, body {
      width: 100%;
      height: 100%;
      margin: 0;
      padding: 0;
      overflow: hidden;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif;
    }
    .studio-app {
      display: grid;
      grid-template-rows: 54px minmax(0, 1fr) 26px;
      height: 100vh;
      width: 100vw;
      overflow: hidden;
    }
    /* TOP NAVBAR */
    .studio-nav {
      background: rgba(10, 16, 29, 0.96);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      backdrop-filter: blur(12px);
      z-index: 100;
    }
    .nav-left, .nav-center, .nav-right {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .brand-title {
      font-weight: 850;
      font-size: 15px;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 7px;
      color: #fff;
    }
    .brand-title .badge {
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 6px;
      background: linear-gradient(135deg, rgba(120,169,255,0.2), rgba(82,227,150,0.2));
      border: 1px solid var(--border);
      color: var(--accent);
    }
    .repo-select-wrap {
      display: flex;
      align-items: center;
      background: var(--panel2);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 2px 6px;
      gap: 6px;
    }
    .repo-select-wrap select {
      background: transparent;
      border: none;
      color: var(--text);
      font-size: 12px;
      font-weight: 600;
      outline: none;
      cursor: pointer;
      padding: 4px 6px;
      max-width: 200px;
    }
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 7px;
      font-size: 12px;
      font-weight: 650;
      border: 1px solid var(--border);
      background: var(--panel2);
      color: var(--text);
      cursor: pointer;
      transition: all 0.18s ease;
      text-decoration: none;
      white-space: nowrap;
    }
    .btn:hover {
      background: rgba(120, 169, 255, 0.15);
      border-color: var(--accent);
      color: #fff;
    }
    .btn-primary {
      background: linear-gradient(135deg, #78a9ff, #4784f4);
      color: #040914;
      border: 1px solid rgba(255,255,255,0.25);
      font-weight: 750;
      box-shadow: 0 4px 14px var(--accent-glow);
    }
    .btn-primary:hover {
      background: linear-gradient(135deg, #8cb5ff, #5b92f7);
      box-shadow: 0 6px 18px var(--accent-glow);
      color: #000;
      transform: translateY(-1px);
    }
    .btn-commit {
      background: linear-gradient(135deg, #52e396, #29b86d);
      color: #041208;
      font-weight: 800;
      border: 1px solid rgba(255,255,255,0.25);
      box-shadow: 0 4px 14px var(--good-glow);
    }
    .btn-commit:hover {
      background: linear-gradient(135deg, #6bf2ab, #31cc7b);
      color: #000;
      transform: translateY(-1px);
    }
    .btn-danger {
      background: rgba(255, 107, 126, 0.12);
      border-color: rgba(255, 107, 126, 0.3);
      color: var(--danger);
    }
    .btn-danger:hover {
      background: rgba(255, 107, 126, 0.25);
      border-color: var(--danger);
      color: #fff;
    }
    /* MAIN WORKSPACE */
    .studio-workspace {
      display: grid;
      grid-template-columns: 260px 1fr 340px;
      height: 100%;
      min-height: 0;
      overflow: hidden;
      transition: grid-template-columns 0.2s ease;
    }
    .studio-workspace.preview-closed {
      grid-template-columns: 260px 1fr 0px;
    }
    .studio-workspace.preview-maximized {
      grid-template-columns: 0px 1fr 1fr;
    }
    /* LEFT PANEL: FILE EXPLORER */
    .sidebar-panel {
      background: var(--panel);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
    }
    .sidebar-head {
      padding: 10px 12px;
      font-size: 11px;
      font-weight: 750;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
    }
    .search-filter {
      padding: 8px 10px;
      border-bottom: 1px solid var(--border);
    }
    .search-filter input {
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text);
      padding: 5px 8px;
      font-size: 11px;
      outline: none;
    }
    .file-tree {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 6px 4px;
    }
    .tree-item {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 5px 8px;
      font-size: 12px;
      border-radius: 6px;
      cursor: pointer;
      color: #c9d7ec;
      user-select: none;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .tree-item:hover {
      background: rgba(120, 169, 255, 0.08);
      color: #fff;
    }
    .tree-item.active {
      background: rgba(120, 169, 255, 0.18);
      color: #fff;
      font-weight: 600;
      border-left: 2px solid var(--accent);
    }
    .tree-item .icon {
      font-size: 13px;
      flex-shrink: 0;
    }
    .tree-folder-group {
      margin-left: 12px;
      border-left: 1px solid rgba(120, 169, 255, 0.08);
      padding-left: 4px;
    }
    /* CENTER PANEL: EDITOR */
    .editor-panel {
      background: var(--editor-bg);
      display: flex;
      flex-direction: column;
      height: 100%;
      min-width: 0;
      overflow: hidden;
    }
    .editor-tabs {
      background: var(--panel);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      padding: 0 4px;
      height: 38px;
      overflow-x: auto;
      gap: 3px;
    }
    .editor-tab {
      background: rgba(18, 28, 50, 0.6);
      border: 1px solid var(--border);
      border-bottom: none;
      border-radius: 6px 6px 0 0;
      padding: 7px 12px;
      font-size: 12px;
      color: var(--muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      white-space: nowrap;
    }
    .editor-tab.active {
      background: var(--editor-bg);
      color: #fff;
      font-weight: 600;
      border-color: rgba(120, 169, 255, 0.3);
      border-top: 2px solid var(--accent);
    }
    .editor-tab .close-tab {
      border-radius: 50%;
      padding: 1px 4px;
      font-size: 11px;
    }
    .editor-tab .close-tab:hover {
      background: rgba(255,255,255,0.15);
      color: #fff;
    }
    .editor-body-wrap {
      flex: 1;
      display: flex;
      min-height: 0;
      position: relative;
    }
    .line-numbers {
      background: rgba(7, 11, 20, 0.7);
      border-right: 1px solid var(--border);
      padding: 12px 8px;
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 13px;
      line-height: 1.55;
      color: #4f637e;
      text-align: right;
      user-select: none;
      min-width: 44px;
      overflow: hidden;
    }
    .code-textarea {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      resize: none;
      padding: 12px;
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 13px;
      line-height: 1.55;
      color: var(--text);
      white-space: pre;
      tab-size: 2;
      overflow: auto;
    }
    /* RIGHT PANEL: LIVE PREVIEW & AI ASSISTANT */
    .aux-panel {
      background: var(--panel);
      border-left: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      height: 100%;
      min-width: 0;
      overflow: hidden;
    }
    .aux-tabs {
      background: var(--panel2);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      height: 38px;
    }
    .aux-tab {
      flex: 1;
      text-align: center;
      padding: 9px;
      font-size: 12px;
      font-weight: 650;
      color: var(--muted);
      cursor: pointer;
      border-bottom: 2px solid transparent;
    }
    .aux-tab.active {
      color: var(--accent);
      border-bottom-color: var(--accent);
      background: rgba(120, 169, 255, 0.05);
    }
    .preview-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
      background: #fff;
    }
    .preview-frame {
      width: 100%;
      height: 100%;
      border: none;
      background: #fff;
    }
    .ai-assistant-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
      padding: 12px;
    }
    .ai-chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 6px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      font-size: 12px;
    }
    .ai-msg {
      padding: 10px 12px;
      border-radius: 10px;
      line-height: 1.5;
    }
    .ai-msg.user {
      background: rgba(120, 169, 255, 0.15);
      border: 1px solid rgba(120, 169, 255, 0.25);
      align-self: flex-end;
      color: #fff;
    }
    .ai-msg.assistant {
      background: var(--panel2);
      border: 1px solid var(--border);
      align-self: flex-start;
      color: var(--text);
    }
    .ai-composer {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-top: 10px;
    }
    .ai-composer textarea {
      width: 100%;
      height: 60px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text);
      padding: 8px;
      font-size: 12px;
      outline: none;
      resize: none;
    }
    /* STATUS BAR */
    .studio-statusbar {
      background: rgba(5, 8, 16, 0.98);
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 14px;
      font-size: 11px;
      color: var(--muted);
    }
    .status-item {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .status-indicator {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--good);
    }
    .status-indicator.modified {
      background: var(--warning);
      box-shadow: 0 0 6px rgba(242, 199, 109, 0.6);
    }
    /* MODALS */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(6px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .modal-backdrop.open { display: flex; }
    .modal {
      background: var(--panel);
      border: 1px solid var(--border-focus);
      border-radius: 14px;
      width: min(480px, 92vw);
      padding: 22px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .modal h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 800;
      color: #fff;
    }
    .modal input, .modal textarea {
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: #fff;
      padding: 8px 10px;
      font-size: 12px;
      outline: none;
    }
    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 6px;
    }
    .spinner {
      display: inline-block;
      width: 12px;
      height: 12px;
      border: 2px solid rgba(255,255,255,0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>

<div class="studio-app">
  <!-- TOP BAR -->
  <header class="studio-nav">
    <div class="nav-left">
      <div class="brand-title">
        <span># Hashtag</span>
        <span class="badge">Cloud Studio</span>
      </div>
      <div class="repo-select-wrap">
        <span style="font-size:12px">📦</span>
        <select id="repo-select" title="Target GitHub Repository">
          <option value="">Loading repos...</option>
        </select>
        <button id="refresh-repo-btn" class="btn" style="padding:2px 6px;font-size:11px" title="Refresh files">↻</button>
      </div>
      <button id="new-repo-btn" class="btn" title="Create New Repository in GitHub">+ New Repo</button>
    </div>

    <div class="nav-center">
      <div id="active-file-title" style="font-size:12px;font-weight:700;color:var(--text);display:flex;align-items:center;gap:6px">
        <span>📄 Select a file from the explorer</span>
      </div>
    </div>

    <div class="nav-right">
      <button id="new-file-btn" class="btn" title="Create New File directly in GitHub">➕ New File</button>
      <button id="commit-btn" class="btn btn-commit" title="Commit and Push changes directly to GitHub (Ctrl+S)">
        <span>💾 Commit to GitHub</span>
      </button>
      <button id="delete-btn" class="btn btn-danger" style="display:none" title="Delete file from GitHub">🗑️ Delete</button>
      <button id="toggle-preview-btn" class="btn" title="Toggle Live Web Preview">👁️ Preview</button>
      <button id="toggle-ai-btn" class="btn" style="color:var(--accent)" title="Hashtag AI Co-Pilot">🤖 AI Co-Pilot</button>
      <a href="/console" class="btn" target="_blank" title="Open Hashtag Console">💬 Console ↗</a>
    </div>
  </header>

  <!-- WORKSPACE -->
  <main id="workspace" class="studio-workspace">
    <!-- SIDEBAR: FILES -->
    <aside class="sidebar-panel">
      <div class="sidebar-head">
        <span>Project Explorer</span>
        <span id="file-count" style="font-weight:600;color:var(--accent)">0 files</span>
      </div>
      <div class="search-filter">
        <input type="text" id="file-search" placeholder="Search files in repository...">
      </div>
      <div id="file-tree" class="file-tree">
        <div style="padding:20px;text-align:center;color:var(--muted);font-size:12px">
          Connecting to GitHub repository...
        </div>
      </div>
    </aside>

    <!-- CENTER: CODE EDITOR -->
    <section class="editor-panel">
      <div id="editor-tabs" class="editor-tabs">
        <div class="editor-tab active" id="tab-primary">
          <span id="tab-name">untitled</span>
          <span id="tab-dirty" style="display:none;color:var(--warning)">●</span>
        </div>
      </div>
      <div class="editor-body-wrap">
        <div id="line-numbers" class="line-numbers">1</div>
        <textarea id="code-editor" class="code-textarea" spellcheck="false" placeholder="// Click any file from the explorer to open and edit directly on GitHub..."></textarea>
      </div>
    </section>

    <!-- RIGHT: LIVE PREVIEW & AI ASSISTANT -->
    <aside id="aux-panel" class="aux-panel">
      <div class="aux-tabs">
        <div id="tab-btn-preview" class="aux-tab active">👁️ Live Web Preview</div>
        <div id="tab-btn-ai" class="aux-tab">🤖 Hashtag AI Co-Pilot</div>
      </div>

      <!-- PREVIEW TAB -->
      <div id="view-preview" class="preview-container">
        <div style="background:var(--panel2);padding:6px 10px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">
          <span style="font-size:11px;color:var(--muted);font-weight:600">Local In-Browser DOM Sandbox</span>
          <button id="refresh-preview-btn" class="btn" style="padding:2px 8px;font-size:10px">↻ Re-render</button>
        </div>
        <iframe id="preview-frame" class="preview-frame" sandbox="allow-scripts allow-modals allow-same-origin"></iframe>
      </div>

      <!-- AI ASSISTANT TAB -->
      <div id="view-ai" class="ai-assistant-container" style="display:none">
        <div id="ai-chat" class="ai-chat-messages">
          <div class="ai-msg assistant">
            👋 <b>Hashtag AI Cloud Co-Pilot</b> ready! I can write code, generate pages, fix errors, or refactor components directly in your GitHub project without touching your local PC.
          </div>
        </div>
        <div class="ai-composer">
          <textarea id="ai-prompt" placeholder="Ask Hashtag to build something in this repo (e.g. 'Create a modern landing page in index.html')..."></textarea>
          <button id="ai-send-btn" class="btn btn-primary" style="align-self:flex-end">
            <span>Ask Hashtag</span> <span>➜</span>
          </button>
        </div>
      </div>
    </aside>
  </main>

  <!-- STATUSBAR -->
  <footer class="studio-statusbar">
    <div class="status-item">
      <span id="sync-dot" class="status-indicator"></span>
      <span id="sync-status">Ready</span>
    </div>
    <div class="status-item">
      <span id="editor-meta">Lines: 1 · Chars: 0</span>
      <span>|</span>
      <span id="active-branch">Branch: main</span>
      <span>|</span>
      <span style="color:var(--accent)">Hashtag Cloud Runtime</span>
    </div>
  </footer>
</div>

<!-- COMMIT MODAL -->
<div id="commit-modal" class="modal-backdrop">
  <div class="modal">
    <h3>Commit Directly to GitHub</h3>
    <p style="font-size:12px;color:var(--muted);margin:0">
      Commit changes to <b id="commit-target-path" style="color:#fff"></b> on GitHub branch <b style="color:var(--accent)">main</b>.
    </p>
    <div>
      <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:4px">Commit Message:</label>
      <input type="text" id="commit-message-input" value="Update file via Hashtag Cloud Studio">
    </div>
    <div class="modal-actions">
      <button id="cancel-commit-btn" class="btn">Cancel</button>
      <button id="confirm-commit-btn" class="btn btn-commit">
        <span>Confirm & Push Commit</span>
      </button>
    </div>
  </div>
</div>

<!-- NEW FILE MODAL -->
<div id="new-file-modal" class="modal-backdrop">
  <div class="modal">
    <h3>Create New File in GitHub</h3>
    <p style="font-size:12px;color:var(--muted);margin:0">
      The file will be created immediately in your GitHub repository cloud workspace.
    </p>
    <div>
      <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:4px">File Path / Name:</label>
      <input type="text" id="new-file-path-input" placeholder="e.g. index.html or components/Navbar.js">
    </div>
    <div class="modal-actions">
      <button id="cancel-new-file-btn" class="btn">Cancel</button>
      <button id="confirm-new-file-btn" class="btn btn-primary">
        <span>Create on GitHub</span>
      </button>
    </div>
  </div>
</div>

<!-- NEW REPO MODAL -->
<div id="new-repo-modal" class="modal-backdrop">
  <div class="modal">
    <h3>Create New GitHub Repository</h3>
    <p style="font-size:12px;color:var(--muted);margin:0">
      Instantly creates a new repository on your GitHub account so you can start developing.
    </p>
    <div>
      <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:4px">Repository Name:</label>
      <input type="text" id="new-repo-name-input" placeholder="my-awesome-project">
    </div>
    <div>
      <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:4px">Description (optional):</label>
      <input type="text" id="new-repo-desc-input" placeholder="Web project built directly with Hashtag AI">
    </div>
    <div style="display:flex;align-items:center;gap:8px;font-size:12px">
      <input type="checkbox" id="new-repo-private" style="width:auto">
      <label for="new-repo-private">Private Repository</label>
    </div>
    <div class="modal-actions">
      <button id="cancel-new-repo-btn" class="btn">Cancel</button>
      <button id="confirm-new-repo-btn" class="btn btn-primary">
        <span>Create Repository</span>
      </button>
    </div>
  </div>
</div>

<script>
(function() {
  "use strict";

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    var d = String(s || "");
    return d.replace(/[&<>"']/g, function(c) {
      return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];
    });
  }

  var state = {
    repo: "",
    branch: "main",
    activePath: "",
    fileSha: null,
    initialContent: "",
    tree: [],
    isDirty: false,
    previewMode: "preview" // 'preview' or 'ai'
  };

  function api(url, options) {
    options = options || {};
    var headers = options.headers || {};
    headers["Content-Type"] = "application/json";
    return fetch(url, {
      method: options.method || "GET",
      headers: headers,
      body: options.body ? JSON.stringify(options.body) : undefined
    }).then(function(r) {
      return r.json().then(function(d) {
        if (!r.ok) throw new Error(d.detail || d.error || ("HTTP " + r.status));
        return d;
      });
    });
  }

  // 1. Load User's GitHub Repositories
  function loadRepositories() {
    var select = $("repo-select");
    api("/v1/github/repositories").then(function(res) {
      if (res.repositories && res.repositories.length) {
        var html = "";
        var current = res.current || res.repositories[0].full_name;
        res.repositories.forEach(function(r) {
          var sel = (r.full_name === current) ? "selected" : "";
          html += '<option value="' + esc(r.full_name) + '" ' + sel + '>' + esc(r.full_name) + (r.private ? " 🔒" : "") + '</option>';
        });
        select.innerHTML = html;
        state.repo = select.value;
        loadProjectTree();
      } else {
        select.innerHTML = '<option value="">No repositories found</option>';
      }
    }).catch(function(err) {
      select.innerHTML = '<option value="">Error loading repos</option>';
    });
  }

  // 2. Load Recursive Project Tree
  function loadProjectTree() {
    var treeEl = $("file-tree");
    treeEl.innerHTML = '<div style="padding:20px;text-align:center;color:var(--muted);font-size:12px"><span class="spinner"></span> Loading GitHub files...</div>';
    $("sync-status").textContent = "Fetching tree...";

    api("/v1/github/project/tree?repo=" + encodeURIComponent(state.repo)).then(function(res) {
      state.tree = res.tree || [];
      $("file-count").textContent = state.tree.filter(function(x){ return x.type === "blob"; }).length + " files";
      renderFileTree(state.tree);
      $("sync-status").textContent = "Synced with GitHub";

      // If active file is set, ensure it's loaded; otherwise open index.html or first file
      if (!state.activePath && state.tree.length) {
        var indexFile = state.tree.find(function(x) { return x.path.toLowerCase() === "index.html" || x.path.toLowerCase() === "readme.md"; });
        var firstFile = indexFile || state.tree.find(function(x) { return x.type === "blob"; });
        if (firstFile) {
          openFile(firstFile.path);
        }
      }
    }).catch(function(err) {
      treeEl.innerHTML = '<div style="padding:15px;color:var(--danger);font-size:12px">Failed to load repository tree: ' + esc(err.message) + '</div>';
      $("sync-status").textContent = "Error loading tree";
    });
  }

  // 3. Render Hierarchical File Tree
  function renderFileTree(items) {
    var treeEl = $("file-tree");
    var filter = ($("file-search").value || "").toLowerCase().trim();
    if (!items || !items.length) {
      treeEl.innerHTML = '<div style="padding:20px;text-align:center;color:var(--muted);font-size:12px">Repository is empty. Click "+ New File" to start!</div>';
      return;
    }

    var html = "";
    items.forEach(function(item) {
      if (filter && !item.path.toLowerCase().includes(filter)) return;
      if (item.type === "tree") return; // Flat list of file paths works reliably for all depths

      var isAct = (item.path === state.activePath) ? "active" : "";
      var icon = getFileIcon(item.path);
      html += '<div class="tree-item ' + isAct + '" data-path="' + esc(item.path) + '">'
            + '<span class="icon">' + icon + '</span>'
            + '<span style="flex:1;overflow:hidden;text-overflow:ellipsis">' + esc(item.path) + '</span>'
            + '</div>';
    });
    treeEl.innerHTML = html;

    // Attach click handlers
    treeEl.querySelectorAll(".tree-item").forEach(function(el) {
      el.onclick = function() {
        var p = el.getAttribute("data-path");
        if (p) openFile(p);
      };
    });
  }

  function getFileIcon(path) {
    var ext = path.split('.').pop().toLowerCase();
    if (["html", "htm"].includes(ext)) return "🌐";
    if (["js", "jsx", "ts", "tsx"].includes(ext)) return "📜";
    if (["css", "scss", "sass"].includes(ext)) return "🎨";
    if (["py"].includes(ext)) return "🐍";
    if (["json"].includes(ext)) return "📦";
    if (["md", "markdown", "txt"].includes(ext)) return "📝";
    if (["jpg", "jpeg", "png", "gif", "svg", "webp"].includes(ext)) return "🖼️";
    return "📄";
  }

  // 4. Open File directly from GitHub
  function openFile(path) {
    if (state.isDirty) {
      if (!confirm("You have unsaved changes in " + state.activePath + ". Discard and switch file?")) {
        return;
      }
    }
    state.activePath = path;
    $("active-file-title").innerHTML = '<span>' + getFileIcon(path) + '</span> <span>' + esc(path) + '</span>';
    $("tab-name").textContent = path.split('/').pop();
    $("delete-btn").style.display = "inline-flex";
    $("sync-status").textContent = "Opening " + path + "...";

    // Highlight in tree
    document.querySelectorAll(".tree-item").forEach(function(el) {
      el.classList.toggle("active", el.getAttribute("data-path") === path);
    });

    api("/v1/github/project/file?repo=" + encodeURIComponent(state.repo) + "&path=" + encodeURIComponent(path)).then(function(res) {
      var content = res.text !== undefined ? res.text : (res.content || "");
      state.initialContent = content;
      state.fileSha = res.sha;
      $("code-editor").value = content;
      markClean();
      updateLineNumbers();
      updatePreview();
      $("sync-status").textContent = "Synced with GitHub";
    }).catch(function(err) {
      alert("Error opening file: " + err.message);
      $("sync-status").textContent = "Error opening file";
    });
  }

  // 5. Line numbers and editor change tracking
  function updateLineNumbers() {
    var val = $("code-editor").value;
    var lines = val.split("\n").length;
    var numHtml = "";
    for (var i = 1; i <= lines; i++) {
      numHtml += i + "<br>";
    }
    $("line-numbers").innerHTML = numHtml;
    $("editor-meta").textContent = "Lines: " + lines + " · Chars: " + val.length;
  }

  function markDirty() {
    state.isDirty = true;
    $("tab-dirty").style.display = "inline";
    $("sync-dot").className = "status-indicator modified";
    $("sync-status").textContent = "● Unsaved changes (Press Ctrl+S to commit)";
  }

  function markClean() {
    state.isDirty = false;
    $("tab-dirty").style.display = "none";
    $("sync-dot").className = "status-indicator";
    $("sync-status").textContent = "✓ Synced with GitHub";
  }

  $("code-editor").addEventListener("input", function() {
    markDirty();
    updateLineNumbers();
    if (state.activePath.endsWith(".html") || state.activePath.endsWith(".htm")) {
      updatePreviewDebounced();
    }
  });

  $("code-editor").addEventListener("keydown", function(e) {
    // Ctrl+S or Cmd+S commits directly to GitHub
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
      e.preventDefault();
      triggerCommitModal();
    }
    // Tab key inserts 2 spaces
    if (e.key === "Tab") {
      e.preventDefault();
      var start = this.selectionStart, end = this.selectionEnd;
      this.value = this.value.substring(0, start) + "  " + this.value.substring(end);
      this.selectionStart = this.selectionEnd = start + 2;
      markDirty();
    }
  });

  // Synchronize line numbers scroll with textarea
  $("code-editor").addEventListener("scroll", function() {
    $("line-numbers").scrollTop = this.scrollTop;
  });

  // 6. Live Web Preview
  var previewTimer = null;
  function updatePreviewDebounced() {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(updatePreview, 400);
  }

  function updatePreview() {
    if (!state.activePath) return;
    var frame = $("preview-frame");
    var content = $("code-editor").value;

    if (state.activePath.endsWith(".html") || state.activePath.endsWith(".htm")) {
      frame.srcdoc = content;
    } else {
      frame.srcdoc = '<!doctype html><html><body style="font-family:sans-serif;background:#0d1424;color:#edf4ff;padding:24px;">'
                   + '<h3>📄 Preview for ' + esc(state.activePath) + '</h3>'
                   + '<pre style="background:#070b14;padding:14px;border-radius:8px;overflow:auto;color:#78a9ff">' + esc(content) + '</pre>'
                   + '</body></html>';
    }
  }

  // 7. Commit & Push Directly to GitHub
  function triggerCommitModal() {
    if (!state.activePath) {
      alert("Please open or create a file to commit.");
      return;
    }
    $("commit-target-path").textContent = state.activePath;
    $("commit-message-input").value = "Update " + state.activePath + " via Hashtag Cloud Studio";
    $("commit-modal").classList.add("open");
    $("commit-message-input").focus();
  }

  $("commit-btn").onclick = triggerCommitModal;
  $("cancel-commit-btn").onclick = function() { $("commit-modal").classList.remove("open"); };

  $("confirm-commit-btn").onclick = function() {
    var btn = $("confirm-commit-btn");
    var msg = $("commit-message-input").value.trim() || ("Update " + state.activePath);
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Committing to GitHub...';

    api("/v1/github/project/file", {
      method: "POST",
      body: {
        repo: state.repo,
        path: state.activePath,
        content: $("code-editor").value,
        message: msg,
        branch: state.branch
      }
    }).then(function(res) {
      $("commit-modal").classList.remove("open");
      markClean();
      alert("✓ Successfully committed to GitHub!\n\nCommit SHA: " + (res.commit ? res.commit.sha.substring(0, 8) : "ok"));
      btn.disabled = false;
      btn.innerHTML = '<span>Confirm & Push Commit</span>';
      loadProjectTree();
    }).catch(function(err) {
      alert("Commit failed: " + err.message);
      btn.disabled = false;
      btn.innerHTML = '<span>Confirm & Push Commit</span>';
    });
  };

  // 8. Create New File
  $("new-file-btn").onclick = function() {
    $("new-file-path-input").value = "";
    $("new-file-modal").classList.add("open");
    $("new-file-path-input").focus();
  };
  $("cancel-new-file-btn").onclick = function() { $("new-file-modal").classList.remove("open"); };

  $("confirm-new-file-btn").onclick = function() {
    var p = $("new-file-path-input").value.trim();
    if (!p) { alert("Enter a filename or path (e.g. index.html or app.py)"); return; }

    var initialCode = "";
    if (p.endsWith(".html") || p.endsWith(".htm")) {
      initialCode = "<!doctype html>\\n<html>\\n<head>\\n  <meta charset=\\\"utf-8\\\">\\n  <title>New Page</title>\\n</head>\\n<body>\\n  <h1>Hello from Hashtag Cloud Studio!</h1>\\n</body>\\n</html>\\n";
    } else if (p.endsWith(".py")) {
      initialCode = "#!/usr/bin/env python3\\n\\ndef main():\\n    print(\\\"Hello from Hashtag Cloud Studio!\\\")\\n\\nif __name__ == \\\"__main__\\\":\\n    main()\\n";
    } else if (p.endsWith(".js")) {
      initialCode = "// Built directly in GitHub with Hashtag Cloud Studio\\nconsole.log(\\\"Ready!\\\");\\n";
    }

    api("/v1/github/project/file", {
      method: "POST",
      body: {
        repo: state.repo,
        path: p,
        content: initialCode,
        message: "Create " + p + " via Hashtag Cloud Studio",
        branch: state.branch
      }
    }).then(function() {
      $("new-file-modal").classList.remove("open");
      loadProjectTree();
      openFile(p);
    }).catch(function(err) {
      alert("Failed creating file: " + err.message);
    });
  };

  // 9. Delete File
  $("delete-btn").onclick = function() {
    if (!state.activePath) return;
    if (!confirm("Are you sure you want to permanently delete '" + state.activePath + "' from GitHub?")) return;

    api("/v1/github/project/file", {
      method: "DELETE",
      body: {
        repo: state.repo,
        path: state.activePath,
        message: "Delete " + state.activePath + " via Hashtag Cloud Studio",
        branch: state.branch
      }
    }).then(function() {
      alert("✓ File deleted from GitHub!");
      state.activePath = "";
      $("code-editor").value = "";
      markClean();
      $("delete-btn").style.display = "none";
      loadProjectTree();
    }).catch(function(err) {
      alert("Delete failed: " + err.message);
    });
  };

  // 10. Create New Repo Modal
  $("new-repo-btn").onclick = function() {
    $("new-repo-modal").classList.add("open");
    $("new-repo-name-input").focus();
  };
  $("cancel-new-repo-btn").onclick = function() { $("new-repo-modal").classList.remove("open"); };

  $("confirm-new-repo-btn").onclick = function() {
    var name = $("new-repo-name-input").value.trim();
    var desc = $("new-repo-desc-input").value.trim();
    var isPriv = $("new-repo-private").checked;
    if (!name) { alert("Please provide a repository name."); return; }

    var btn = $("confirm-new-repo-btn");
    btn.disabled = true;
    btn.textContent = "Creating on GitHub...";

    api("/v1/github/project/create-repo", {
      method: "POST",
      body: { name: name, description: desc, private: isPriv, auto_init: true }
    }).then(function(res) {
      $("new-repo-modal").classList.remove("open");
      btn.disabled = false;
      btn.textContent = "Create Repository";
      alert("✓ Repository '" + name + "' created successfully on GitHub!");
      loadRepositories();
    }).catch(function(err) {
      alert("Failed creating repository: " + err.message);
      btn.disabled = false;
      btn.textContent = "Create Repository";
    });
  };

  // 11. Switch Repository
  $("repo-select").onchange = function() {
    state.repo = this.value;
    state.activePath = "";
    $("delete-btn").style.display = "none";
    $("code-editor").value = "";
    markClean();
    api("/v1/github/target_repo", { method: "POST", body: { target_repo: state.repo } }).catch(function(){});
    loadProjectTree();
  };
  $("refresh-repo-btn").onclick = loadProjectTree;

  // 12. Aux Tabs: Preview vs AI Assistant
  $("tab-btn-preview").onclick = function() {
    $("tab-btn-preview").classList.add("active");
    $("tab-btn-ai").classList.remove("active");
    $("view-preview").style.display = "flex";
    $("view-ai").style.display = "none";
  };
  $("tab-btn-ai").onclick = function() {
    $("tab-btn-ai").classList.add("active");
    $("tab-btn-preview").classList.remove("active");
    $("view-preview").style.display = "none";
    $("view-ai").style.display = "flex";
  };

  $("toggle-preview-btn").onclick = function() {
    var ws = $("workspace");
    ws.classList.toggle("preview-closed");
  };
  $("refresh-preview-btn").onclick = updatePreview;

  // 13. Hashtag AI Co-Pilot integration
  $("ai-send-btn").onclick = sendAiPrompt;
  $("ai-prompt").onkeydown = function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendAiPrompt();
    }
  };

  function sendAiPrompt() {
    var promptEl = $("ai-prompt");
    var txt = promptEl.value.trim();
    if (!txt) return;
    promptEl.value = "";

    var chat = $("ai-chat");
    var userBubble = document.createElement("div");
    userBubble.className = "ai-msg user";
    userBubble.textContent = txt;
    chat.appendChild(userBubble);

    var botBubble = document.createElement("div");
    botBubble.className = "ai-msg assistant";
    botBubble.innerHTML = '<span class="spinner"></span> Hashtag is planning & coding in GitHub...';
    chat.appendChild(botBubble);
    chat.scrollTop = chat.scrollHeight;

    api("/v1/console/request", {
      method: "POST",
      body: {
        request: txt,
        body_id: "hashtag-executor",
        context: { target_repo: state.repo, repository: state.repo }
      }
    }).then(function(res) {
      var summary = "✓ Done! Hashtag processed the request.";
      if (res.plan && res.plan.message) summary = res.plan.message;
      if (res.execution && res.execution.result) {
        var r = res.execution.result;
        if (typeof r.text === "string") summary = r.text;
        else if (r.message) summary = r.message;
      }
      botBubble.innerHTML = '<b>Hashtag Brain:</b><br>' + esc(summary);
      chat.scrollTop = chat.scrollHeight;
      // Reload tree in case files were created or modified
      loadProjectTree();
      if (state.activePath) openFile(state.activePath);
    }).catch(function(err) {
      botBubble.innerHTML = '<span style="color:var(--danger)">Error: ' + esc(err.message) + '</span>';
      chat.scrollTop = chat.scrollHeight;
    });
  }

  // File filter input
  $("file-search").oninput = function() {
    renderFileTree(state.tree);
  };

  // Init
  loadRepositories();
})();
</script>
</body>
</html>
"""
