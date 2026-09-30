"""Hashtag Omniscient Knowledge & Body Evolution Dashboard (HTML/JS/CSS).

Comprehensive visual reports of:
1. Total knowledge acquired
2. Where knowledge was acquired (Wikipedia, Reddit, HackerNews, AI Federation)
3. What knowledge was acquired (Domain distribution & searchable concept explorer)
4. How learned knowledge was used (Execution & repair audit telemetry)
5. Autonomous body modification & evolution panel (Executor, Console, OCR Formatter)
"""

KNOWLEDGE_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hashtag Omniscient Knowledge & Intelligence Dashboard</title>
  <style>
    :root {
      --bg: #090d16;
      --card-bg: rgba(18, 26, 43, 0.75);
      --card-border: rgba(88, 166, 255, 0.18);
      --card-hover: rgba(88, 166, 255, 0.28);
      --text: #e6edf3;
      --muted: #8b949e;
      --accent: #58a6ff;
      --accent-glow: rgba(88, 166, 255, 0.35);
      --success: #3fb950;
      --purple: #bc8cff;
      --warning: #d29922;
      --gradient: linear-gradient(135deg, #1f6feb 0%, #a371f7 100%);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background-color: var(--bg); color: var(--text); min-height: 100vh; padding: 24px; background-image: radial-gradient(circle at 10% 20%, rgba(31, 111, 235, 0.08) 0%, transparent 40%), radial-gradient(circle at 90% 80%, rgba(163, 113, 247, 0.08) 0%, transparent 40%); }
    .container { max-width: 1280px; margin: 0 auto; }
    
    /* Header */
    header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 24px; border-bottom: 1px solid var(--card-border); margin-bottom: 28px; flex-wrap: wrap; gap: 16px; }
    .brand { display: flex; align-items: center; gap: 14px; }
    .logo-badge { width: 44px; height: 44px; border-radius: 12px; background: var(--gradient); display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 800; color: #fff; box-shadow: 0 0 20px var(--accent-glow); }
    .title-group h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.5px; display: flex; align-items: center; gap: 10px; }
    .title-group p { font-size: 13px; color: var(--muted); margin-top: 2px; }
    .nav-actions { display: flex; gap: 12px; align-items: center; }
    .btn { padding: 9px 16px; border-radius: 9px; font-size: 13px; font-weight: 600; text-decoration: none; cursor: pointer; border: 1px solid transparent; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 8px; }
    .btn-primary { background: #238636; color: #fff; }
    .btn-primary:hover { background: #2ea043; }
    .btn-outline { background: rgba(30, 41, 59, 0.6); color: var(--text); border-color: var(--card-border); }
    .btn-outline:hover { border-color: var(--accent); color: var(--accent); background: rgba(88, 166, 255, 0.1); }
    .status-pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; background: rgba(63, 185, 80, 0.15); color: var(--success); border: 1px solid rgba(63, 185, 80, 0.3); }
    .pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--success); animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.8); } 100% { opacity: 1; transform: scale(1); } }

    /* Metrics Grid */
    .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 28px; }
    .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 20px; backdrop-filter: blur(12px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35); transition: border-color 0.2s; }
    .card:hover { border-color: var(--card-hover); }
    .card-title { font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; display: flex; justify-content: space-between; align-items: center; }
    .card-num { font-size: 34px; font-weight: 800; margin: 12px 0 4px; letter-spacing: -1px; color: #fff; }
    .card-sub { font-size: 12px; color: var(--muted); }

    /* Layout Sections */
    .section-title { font-size: 18px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
    .section-title span { font-size: 13px; font-weight: 400; color: var(--muted); }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-bottom: 28px; }
    @media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }

    /* Source Bars */
    .source-row { margin-bottom: 14px; }
    .source-header { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; font-weight: 500; }
    .source-bar-bg { height: 9px; background: rgba(255, 255, 255, 0.08); border-radius: 6px; overflow: hidden; }
    .source-bar-fill { height: 100%; border-radius: 6px; transition: width 0.6s ease; }
    .fill-wiki { background: #58a6ff; }
    .fill-reddit { background: #ff4500; }
    .fill-hn { background: #ff6600; }
    .fill-ai { background: #a371f7; }

    /* Domain Badges */
    .domain-list { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
    .domain-badge { display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 10px; background: rgba(88, 166, 255, 0.1); border: 1px solid rgba(88, 166, 255, 0.25); font-size: 13px; font-weight: 600; color: #c9d1d9; cursor: pointer; transition: all 0.2s; }
    .domain-badge:hover, .domain-badge.active { background: rgba(88, 166, 255, 0.25); border-color: var(--accent); color: #fff; }
    .domain-count { font-size: 11px; padding: 2px 7px; border-radius: 12px; background: rgba(0, 0, 0, 0.35); color: var(--accent); }

    /* Usage Table */
    .usage-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px; }
    .usage-table th { text-align: left; padding: 10px 14px; color: var(--muted); font-size: 11px; text-transform: uppercase; border-bottom: 1px solid var(--card-border); }
    .usage-table td { padding: 12px 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.04); vertical-align: top; }
    .usage-tag { font-size: 11px; padding: 3px 8px; border-radius: 6px; background: rgba(163, 113, 247, 0.15); color: var(--purple); font-weight: 600; }
    .outcome-tag { font-size: 11px; padding: 3px 8px; border-radius: 6px; background: rgba(63, 185, 80, 0.15); color: var(--success); font-weight: 600; }

    /* Body Evolution Cards */
    .body-card { background: rgba(14, 21, 37, 0.8); border: 1px solid var(--card-border); border-radius: 12px; padding: 16px; margin-bottom: 14px; transition: transform 0.2s; }
    .body-card:hover { transform: translateY(-2px); border-color: var(--accent); }
    .body-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .body-name { font-size: 15px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px; }
    .body-desc { font-size: 12px; color: var(--muted); line-height: 1.5; margin-bottom: 10px; }
    .body-caps { display: flex; flex-wrap: wrap; gap: 6px; }
    .cap-tag { font-size: 11px; background: rgba(255, 255, 255, 0.05); padding: 2px 7px; border-radius: 5px; color: #8fa0bb; }

    /* Concept Stream */
    .stream-item { display: flex; justify-content: space-between; align-items: center; padding: 11px 14px; border-radius: 8px; background: rgba(255, 255, 255, 0.02); margin-bottom: 8px; border: 1px solid rgba(255, 255, 255, 0.04); font-size: 13px; }
    .stream-title { font-weight: 600; color: #c9d1d9; }
    .stream-meta { font-size: 11px; color: var(--muted); }

    /* Search & Controls */
    .search-box { display: flex; gap: 10px; margin-bottom: 16px; }
    .input-field { flex: 1; background: rgba(10, 16, 28, 0.9); border: 1px solid var(--card-border); border-radius: 9px; padding: 10px 16px; color: #fff; font-size: 13px; outline: none; transition: border-color 0.2s; }
    .input-field:focus { border-color: var(--accent); box-shadow: 0 0 10px var(--accent-glow); }
    .live-search-results { max-height: 380px; overflow-y: auto; margin-top: 12px; }
    .concept-card { background: rgba(10, 16, 28, 0.6); border: 1px solid rgba(88, 166, 255, 0.12); border-radius: 10px; padding: 14px; margin-bottom: 10px; cursor: pointer; transition: all 0.2s; }
    .concept-card:hover { border-color: var(--accent); background: rgba(88, 166, 255, 0.08); }
    .concept-head { display: flex; justify-content: space-between; font-weight: 700; font-size: 14px; margin-bottom: 4px; color: #58a6ff; }
    .concept-body { font-size: 12px; color: #8b949e; line-height: 1.5; }

    /* Modal */
    .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(6px); z-index: 999; justify-content: center; align-items: center; padding: 20px; }
    .modal-content { background: #0d1322; border: 1px solid var(--accent); border-radius: 16px; max-width: 650px; width: 100%; max-height: 85vh; overflow-y: auto; padding: 28px; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8); }
    .modal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .modal-close { font-size: 22px; cursor: pointer; color: var(--muted); border: none; background: none; }
    .modal-close:hover { color: #fff; }
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <header>
      <div class="brand">
        <div class="logo-badge">#</div>
        <div class="title-group">
          <h1>Hashtag Omniscient Intelligence <span class="status-pill"><span class="pulse-dot"></span> Live Continuous Learning</span></h1>
          <p>Autonomous Knowledge Ingestion, Reasoning Telemetry, and Body Evolution Engine</p>
        </div>
      </div>
      <div class="nav-actions">
        <button class="btn btn-outline" onclick="loadData()">⟳ Refresh Live Data</button>
        <a href="/console" class="btn btn-primary">➜ Back to Console</a>
      </div>
    </header>

    <!-- Metrics Cards -->
    <div class="metrics-grid">
      <div class="card">
        <div class="card-title"><span>Total Concepts Learned</span><span>🧠</span></div>
        <div class="card-num" id="metric-learned">--</div>
        <div class="card-sub" id="metric-harvest-rate">Harvesting Wikipedia, Reddit, HN, AI Mesh</div>
      </div>
      <div class="card">
        <div class="card-title"><span>Applied Knowledge Usages</span><span>⚡</span></div>
        <div class="card-num" id="metric-usages" style="color: var(--accent);">--</div>
        <div class="card-sub">Real-world tasks & repairs executed</div>
      </div>
      <div class="card">
        <div class="card-title"><span>Connected Knowledge Sources</span><span>🌐</span></div>
        <div class="card-num" id="metric-sources">4 Feeds</div>
        <div class="card-sub">Wikipedia, Reddit, HackerNews, AI Mesh</div>
      </div>
      <div class="card">
        <div class="card-title"><span>Connected Bodies Evolving</span><span>🧬</span></div>
        <div class="card-num" id="metric-bodies" style="color: var(--purple);">3 Active</div>
        <div class="card-sub">Executor, Web Console, OCR Formatter</div>
      </div>
    </div>

    <!-- Section: Knowledge Sources & Domain Breakdown -->
    <div class="grid-2">
      <!-- Sources Card -->
      <div class="card">
        <div class="section-title">Where Hashtag Gets Knowledge <span>(Source Ingestion Breakdown)</span></div>
        <p style="font-size: 12px; color: var(--muted); margin-bottom: 18px;">Continuous background harvesters query global encyclopedias, discussions, and AI federations.</p>
        
        <div class="source-row">
          <div class="source-header"><span>📚 Wikipedia Encyclopedic Knowledge</span><span id="wiki-stat">--</span></div>
          <div class="source-bar-bg"><div id="wiki-bar" class="source-bar-fill fill-wiki" style="width: 0%"></div></div>
        </div>
        <div class="source-row">
          <div class="source-header"><span>🔥 HackerNews Tech & Engineering</span><span id="hn-stat">--</span></div>
          <div class="source-bar-bg"><div id="hn-bar" class="source-bar-fill fill-hn" style="width: 0%"></div></div>
        </div>
        <div class="source-row">
          <div class="source-header"><span>💬 Reddit Developer Communities</span><span id="reddit-stat">--</span></div>
          <div class="source-bar-bg"><div id="reddit-bar" class="source-bar-fill fill-reddit" style="width: 0%"></div></div>
        </div>
        <div class="source-row">
          <div class="source-header"><span>🤖 AI Federation Mesh (Distilled AIs)</span><span id="ai-stat">--</span></div>
          <div class="source-bar-bg"><div id="ai-bar" class="source-bar-fill fill-ai" style="width: 0%"></div></div>
        </div>

        <!-- Harvest on demand -->
        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--card-border);">
          <div style="font-size: 13px; font-weight: 600; margin-bottom: 8px;">Trigger Immediate Topic Absorption:</div>
          <div style="display: flex; gap: 8px;">
            <input type="text" id="harvest-input" class="input-field" placeholder="e.g. Transformers, WebAssembly, Quantum...">
            <button class="btn btn-primary" onclick="triggerHarvest()">Learn Topic</button>
          </div>
          <div id="harvest-feedback" style="font-size: 12px; margin-top: 6px; color: var(--success);"></div>
        </div>
      </div>

      <!-- Domain Distribution Card -->
      <div class="card">
        <div class="section-title">What Hashtag Learned <span>(Domain Categorization)</span></div>
        <p style="font-size: 12px; color: var(--muted); margin-bottom: 14px;">Distilled concepts clustered into engineering domains and reasoning foundations:</p>
        <div class="domain-list" id="domain-badges">
          <div class="domain-badge active" onclick="filterDomain('all')">All Domains <span class="domain-count" id="dom-all-cnt">0</span></div>
        </div>

        <div style="margin-top: 20px;">
          <div style="font-size: 13px; font-weight: 600; margin-bottom: 10px;">Recent Knowledge Stream:</div>
          <div id="recent-stream-box" style="max-height: 220px; overflow-y: auto;">
            <!-- Live stream items inserted here -->
          </div>
        </div>
      </div>
    </div>

    <!-- Section: How Knowledge Is Used (Usage & Application Reports) -->
    <div class="card" style="margin-bottom: 28px;">
      <div class="section-title">How Hashtag Used Its Learned Knowledge <span>(Live Application Telemetry)</span></div>
      <p style="font-size: 13px; color: var(--muted); margin-bottom: 16px;">Hashtag doesn't just store knowledge—it applies learned patterns to solve coding tasks, synthesize missing functions, repair broken DOM trees, and guide execution pipelines.</p>
      
      <div style="overflow-x: auto;">
        <table class="usage-table">
          <thead>
            <tr>
              <th>Applied Concept / Topic</th>
              <th>Action Executed</th>
              <th>Target / Context</th>
              <th>Domain</th>
              <th>Outcome</th>
              <th>When</th>
            </tr>
          </thead>
          <tbody id="usage-tbody">
            <!-- Dynamic usage rows inserted here -->
          </tbody>
        </table>
      </div>
    </div>

    <!-- Section: Body Evolution Engine & Connected Bodies -->
    <div class="grid-2">
      <!-- Connected Bodies -->
      <div class="card">
        <div class="section-title">Connected Bodies <span>(Inspect & Modify Connected Systems)</span></div>
        <p style="font-size: 12px; color: var(--muted); margin-bottom: 16px;">Hashtag Core acts as the central brain controlling and modifying all attached bodies:</p>
        <div id="bodies-container">
          <!-- Body cards populated by JS -->
        </div>
      </div>

      <!-- Evolution & Feature Synthesizer -->
      <div class="card">
        <div class="section-title">Autonomous Body Evolution <span>(Synthesize New Features)</span></div>
        <p style="font-size: 12px; color: var(--muted); margin-bottom: 16px;">Core can synthesize new capabilities into connected bodies based on internet knowledge:</p>
        
        <div style="margin-bottom: 14px;">
          <label style="font-size: 12px; color: var(--muted); display: block; margin-bottom: 6px;">Target Body to Evolve:</label>
          <select id="evo-target" class="input-field" style="width: 100%;">
            <option value="executor">Hashtag the Executor (Runtime Body)</option>
            <option value="console">Hashtag Web Console (Interface Body)</option>
            <option value="ocr_formatter">OCR Record Formatter (Body 1)</option>
          </select>
        </div>

        <div style="margin-bottom: 14px;">
          <label style="font-size: 12px; color: var(--muted); display: block; margin-bottom: 6px;">Feature Name:</label>
          <input type="text" id="evo-feature" class="input-field" placeholder="e.g. WebSocket Live Log Streaming, Regex Auto-Sanitizer...">
        </div>

        <div style="margin-bottom: 14px;">
          <label style="font-size: 12px; color: var(--muted); display: block; margin-bottom: 6px;">Knowledge Source / Rationale:</label>
          <input type="text" id="evo-source" class="input-field" placeholder="e.g. Synthesized from Web Standards & AI Federation">
        </div>

        <div style="margin-bottom: 16px;">
          <label style="font-size: 12px; color: var(--muted); display: block; margin-bottom: 6px;">Summary of Feature Upgrade:</label>
          <textarea id="evo-summary" class="input-field" rows="3" style="width: 100%; resize: vertical;" placeholder="Describe the new capability Hashtag will inject into this body..."></textarea>
        </div>

        <button class="btn btn-primary" style="width: 100%; justify-content: center;" onclick="applyEvolution()">🧬 Apply Evolution to Body</button>
        <div id="evo-feedback" style="font-size: 12px; margin-top: 10px; color: var(--success); text-align: center;"></div>
      </div>
    </div>

    <!-- Section: Searchable Concept Explorer -->
    <div class="card" style="margin-bottom: 40px;">
      <div class="section-title">Knowledge Explorer <span>(Search & Inspect All Absorbed Knowledge)</span></div>
      <div class="search-box">
        <input type="text" id="search-input" class="input-field" placeholder="Search concepts (e.g. Python, Docker, HTML, Neural, REST)..." oninput="doSearch()">
      </div>
      <div id="search-results" class="live-search-results">
        <!-- Search concept cards -->
      </div>
    </div>
  </div>

  <!-- Detail Modal -->
  <div id="modal" class="modal-overlay" onclick="closeModal(event)">
    <div class="modal-content" onclick="event.stopPropagation()">
      <div class="modal-head">
        <h2 id="modal-title" style="color: var(--accent); font-size: 18px;">Concept Details</h2>
        <button class="modal-close" onclick="closeModal()">&times;</button>
      </div>
      <div id="modal-meta" style="font-size: 12px; color: var(--muted); margin-bottom: 14px;"></div>
      <div id="modal-summary" style="font-size: 14px; line-height: 1.6; color: #c9d1d9; margin-bottom: 16px;"></div>
      <div id="modal-tags" style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px;"></div>
      <div id="modal-url"></div>
    </div>
  </div>

  <script>
    var globalReport = null;
    var activeDomainFilter = 'all';

    function timeAgo(ts) {
      if (!ts) return "recently";
      var sec = Math.floor(Date.now() / 1000 - ts);
      if (sec < 60) return sec + "s ago";
      if (sec < 3600) return Math.floor(sec / 60) + "m ago";
      if (sec < 86400) return Math.floor(sec / 3600) + "h ago";
      return Math.floor(sec / 86400) + "d ago";
    }

    function loadData() {
      fetch('/v1/knowledge/status')
        .then(function(res) { return res.json(); })
        .then(function(data) {
          globalReport = data;
          renderMetrics(data);
          renderSources(data.sources);
          renderDomains(data.domains);
          renderStream(data.recent_stream);
          renderUsages(data.recent_usages);
          doSearch();
        })
        .catch(function(err) {
          console.error("Failed to load knowledge status:", err);
        });

      fetch('/v1/body/evolution/status')
        .then(function(res) { return res.json(); })
        .then(function(data) {
          renderBodies(data.bodies);
        })
        .catch(function(err) {
          console.error("Failed to load bodies status:", err);
        });
    }

    function renderMetrics(data) {
      document.getElementById('metric-learned').textContent = (data.total_learned || 0) + " Concepts";
      document.getElementById('metric-usages').textContent = (data.total_usages || 0) + " Applied";
    }

    function renderSources(sources) {
      if (!sources) return;
      var wiki = sources.wikipedia || { count: 0, percentage: 0 };
      var reddit = sources.reddit || { count: 0, percentage: 0 };
      var hn = sources.hackernews || { count: 0, percentage: 0 };
      var ai = sources.ai_federation || { count: 0, percentage: 0 };

      document.getElementById('wiki-stat').textContent = wiki.count + " concepts (" + wiki.percentage + "%)";
      document.getElementById('wiki-bar').style.width = Math.max(5, wiki.percentage) + "%";

      document.getElementById('hn-stat').textContent = hn.count + " discussions (" + hn.percentage + "%)";
      document.getElementById('hn-bar').style.width = Math.max(5, hn.percentage) + "%";

      document.getElementById('reddit-stat').textContent = reddit.count + " articles (" + reddit.percentage + "%)";
      document.getElementById('reddit-bar').style.width = Math.max(5, reddit.percentage) + "%";

      document.getElementById('ai-stat').textContent = ai.count + " syntheses (" + ai.percentage + "%)";
      document.getElementById('ai-bar').style.width = Math.max(5, ai.percentage) + "%";
    }

    function renderDomains(domains) {
      var container = document.getElementById('domain-badges');
      if (!domains) return;
      var total = globalReport ? globalReport.total_learned : 0;
      var html = '<div class="domain-badge ' + (activeDomainFilter === 'all' ? 'active' : '') + '" onclick="filterDomain(\\'all\\')">All Domains <span class="domain-count">' + total + '</span></div>';
      
      for (var d in domains) {
        var cnt = domains[d];
        var isAct = (activeDomainFilter === d) ? 'active' : '';
        html += '<div class="domain-badge ' + isAct + '" onclick="filterDomain(\\'' + d.replace(/'/g, "\\\\'") + '\\')">' + d + ' <span class="domain-count">' + cnt + '</span></div>';
      }
      container.innerHTML = html;
    }

    function filterDomain(d) {
      activeDomainFilter = d;
      renderDomains(globalReport ? globalReport.domains : {});
      doSearch();
    }

    function renderStream(stream) {
      var box = document.getElementById('recent-stream-box');
      if (!stream || !stream.length) {
        box.innerHTML = '<div style="color:var(--muted); font-size:12px;">Waiting for new harvest cycles...</div>';
        return;
      }
      var html = "";
      for (var i = 0; i < stream.length; i++) {
        var item = stream[i];
        html += '<div class="stream-item">';
        html += '  <div class="stream-title">' + (item.title || item.id) + '</div>';
        html += '  <div class="stream-meta"><span style="text-transform:capitalize; color:var(--accent);">' + item.source + '</span> • ' + timeAgo(item.time) + '</div>';
        html += '</div>';
      }
      box.innerHTML = html;
    }

    function renderUsages(usages) {
      var tbody = document.getElementById('usage-tbody');
      if (!usages || !usages.length) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--muted);">No usage records yet.</td></tr>';
        return;
      }
      var html = "";
      for (var i = 0; i < usages.length; i++) {
        var u = usages[i];
        html += '<tr>';
        html += '  <td><b>' + u.topic + '</b></td>';
        html += '  <td style="color:#c9d1d9;">' + u.action + '</td>';
        html += '  <td style="font-family:monospace; font-size:11px; color:var(--muted);">' + (u.context || '--') + '</td>';
        html += '  <td><span class="usage-tag">' + (u.domain || 'General') + '</span></td>';
        html += '  <td><span class="outcome-tag">✓ ' + (u.outcome || 'Success') + '</span></td>';
        html += '  <td style="color:var(--muted); font-size:11px;">' + timeAgo(u.timestamp) + '</td>';
        html += '</tr>';
      }
      tbody.innerHTML = html;
    }

    function renderBodies(bodies) {
      var box = document.getElementById('bodies-container');
      if (!bodies || !bodies.length) {
        box.innerHTML = '<div style="color:var(--muted); font-size:12px;">Loading connected bodies...</div>';
        return;
      }
      var html = "";
      for (var i = 0; i < bodies.length; i++) {
        var b = bodies[i];
        html += '<div class="body-card">';
        html += '  <div class="body-head">';
        html += '    <div class="body-name"><span>' + b.name + '</span> <span style="font-size:11px; color:var(--muted); font-weight:400;">v' + (b.version || '1.0') + '</span></div>';
        html += '    <span class="status-pill" style="font-size:10px;">' + (b.status || 'online') + '</span>';
        html += '  </div>';
        html += '  <div class="body-desc">' + b.description + '</div>';
        html += '  <div class="body-caps">';
        var caps = b.capabilities || [];
        for (var j = 0; j < Math.min(caps.length, 6); j++) {
          html += '    <span class="cap-tag">' + caps[j] + '</span>';
        }
        if (caps.length > 6) {
          html += '    <span class="cap-tag">+' + (caps.length - 6) + ' more</span>';
        }
        html += '  </div>';
        html += '</div>';
      }
      box.innerHTML = html;
    }

    function doSearch() {
      var q = document.getElementById('search-input').value.trim();
      var url = '/v1/knowledge/search?limit=25' + (q ? '&q=' + encodeURIComponent(q) : '');
      fetch(url)
        .then(function(res) { return res.json(); })
        .then(function(data) {
          var items = data.results || [];
          var container = document.getElementById('search-results');
          if (!items.length) {
            container.innerHTML = '<div style="color:var(--muted); font-size:13px; text-align:center; padding:20px;">No matching concepts found. Try another search.</div>';
            return;
          }
          var html = "";
          for (var i = 0; i < items.length; i++) {
            var c = items[i];
            var jsonStr = JSON.stringify(c).replace(/"/g, '&quot;');
            html += '<div class="concept-card" onclick="openModal(' + jsonStr + ')">';
            html += '  <div class="concept-head"><span>' + c.title + '</span><span style="font-size:11px; text-transform:uppercase; color:var(--muted);">' + c.source + '</span></div>';
            html += '  <div class="concept-body">' + (c.summary ? c.summary.substring(0, 160) + '...' : '') + '</div>';
            html += '</div>';
          }
          container.innerHTML = html;
        });
    }

    function openModal(concept) {
      document.getElementById('modal-title').textContent = concept.title;
      document.getElementById('modal-meta').textContent = "Source: " + concept.source + " • Absorbed " + timeAgo(concept.timestamp);
      document.getElementById('modal-summary').textContent = concept.summary;
      
      var tagsHtml = "";
      var tags = concept.tags || [];
      for (var i = 0; i < tags.length; i++) {
        tagsHtml += '<span class="cap-tag">' + tags[i] + '</span>';
      }
      document.getElementById('modal-tags').innerHTML = tagsHtml;

      var urlDiv = document.getElementById('modal-url');
      if (concept.details && concept.details.url) {
        urlDiv.innerHTML = '<a href="' + concept.details.url + '" target="_blank" class="btn btn-outline" style="font-size:12px;">🔗 View Original Knowledge Source</a>';
      } else {
        urlDiv.innerHTML = "";
      }

      document.getElementById('modal').style.display = 'flex';
    }

    function closeModal() {
      document.getElementById('modal').style.display = 'none';
    }

    function triggerHarvest() {
      var input = document.getElementById('harvest-input');
      var val = input.value.trim();
      if (!val) return;
      var fb = document.getElementById('harvest-feedback');
      fb.textContent = "Harvesting and synthesizing " + val + "...";
      fetch('/v1/knowledge/harvest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: val })
      })
      .then(function(res) { return res.json(); })
      .then(function(res) {
        input.value = "";
        fb.textContent = "✓ Successfully absorbed " + val + " into Omniscient Knowledge!";
        setTimeout(function() { fb.textContent = ""; }, 4000);
        loadData();
      })
      .catch(function(err) {
        fb.textContent = "Error: " + err.message;
      });
    }

    function applyEvolution() {
      var target = document.getElementById('evo-target').value;
      var feature = document.getElementById('evo-feature').value.trim();
      var source = document.getElementById('evo-source').value.trim();
      var summary = document.getElementById('evo-summary').value.trim();
      var fb = document.getElementById('evo-feedback');

      if (!feature || !summary) {
        fb.textContent = "Please fill in both Feature Name and Summary.";
        fb.style.color = "var(--warning)";
        return;
      }

      fb.textContent = "Core is evolving " + target + "...";
      fb.style.color = "var(--accent)";

      fetch('/v1/body/evolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_body: target,
          feature_name: feature,
          knowledge_source: source || "Synthesized from Internet & AI Federation",
          summary: summary
        })
      })
      .then(function(res) { return res.json(); })
      .then(function(res) {
        document.getElementById('evo-feature').value = "";
        document.getElementById('evo-source').value = "";
        document.getElementById('evo-summary').value = "";
        fb.textContent = "✓ Evolution applied! " + res.body_name + " upgraded with " + res.feature + ".";
        fb.style.color = "var(--success)";
        setTimeout(function() { fb.textContent = ""; }, 5000);
        loadData();
      })
      .catch(function(err) {
        fb.textContent = "Evolution error: " + err.message;
        fb.style.color = "red";
      });
    }

    // Initialize and start live polling every 10 seconds
    loadData();
    setInterval(loadData, 10000);
  </script>
</body>
</html>
"""
