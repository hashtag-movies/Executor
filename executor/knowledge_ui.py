"""Hashtag Omniscient Knowledge, Auto-Task Learning & Body Evolution Dashboard (HTML/JS/CSS).

Comprehensive visual reports of:
1. Total knowledge acquired across the internet
2. Where knowledge was acquired (Wikipedia, Reddit, HackerNews, AI Federation)
3. What knowledge was acquired (Domain distribution & searchable concept explorer)
4. How learned knowledge was used (Execution & repair audit telemetry)
5. Autonomous body modification & evolution panel (Executor, Console, OCR Formatter)
6. Autonomous Task Learning & Hot-Injection Pipeline (Detect Gap -> Harvest -> Sandbox Test -> Retain -> Hot-Inject -> Execute)
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
    .btn-accent { background: #1f6feb; color: #fff; }
    .btn-accent:hover { background: #388bfd; }
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

    /* Autonomous Task Learning Pipeline Section */
    .pipeline-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 18px 0; }
    .pipe-step-card { background: rgba(255, 255, 255, 0.03); border: 1px solid var(--card-border); border-radius: 10px; padding: 14px; position: relative; }
    .pipe-step-card.active { border-color: var(--accent); background: rgba(88, 166, 255, 0.1); }
    .pipe-step-card.completed { border-color: var(--success); background: rgba(63, 185, 80, 0.08); }
    .step-num { font-size: 11px; font-weight: 800; color: var(--accent); text-transform: uppercase; margin-bottom: 4px; }
    .pipe-step-card.completed .step-num { color: var(--success); }
    .step-title { font-size: 13px; font-weight: 700; color: #fff; margin-bottom: 4px; }
    .step-desc { font-size: 11px; color: var(--muted); line-height: 1.4; }
    .task-chip { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 16px; background: rgba(88, 166, 255, 0.1); border: 1px solid var(--card-border); font-size: 12px; color: #c9d1d9; cursor: pointer; margin-right: 8px; margin-bottom: 8px; transition: all 0.2s; }
    .task-chip:hover { border-color: var(--accent); background: rgba(88, 166, 255, 0.25); color: #fff; }
    .result-console { background: #06090f; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 14px; font-family: monospace; font-size: 12px; color: #3fb950; max-height: 220px; overflow-y: auto; white-space: pre-wrap; line-height: 1.5; margin-top: 12px; }

    /* Concept Stream */
    .stream-item { display: flex; justify-content: space-between; align-items: center; padding: 11px 14px; border-radius: 8px; background: rgba(255, 255, 255, 0.02); margin-bottom: 8px; border: 1px solid rgba(255, 255, 255, 0.04); font-size: 13px; }
    .stream-title { font-weight: 600; color: #c9d1d9; }
    .stream-meta { font-size: 11px; color: var(--muted); }

    /* Inputs */
    .input-field { background: rgba(0, 0, 0, 0.4); border: 1px solid var(--card-border); border-radius: 8px; padding: 10px 14px; color: #fff; font-size: 13px; outline: none; transition: border-color 0.2s; }
    .input-field:focus { border-color: var(--accent); }
    .search-box { margin-bottom: 16px; }
    .search-box input { width: 100%; }

    /* Concept Explorer Grid */
    .live-search-results { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; max-height: 440px; overflow-y: auto; padding-right: 6px; }
    .concept-card { background: rgba(18, 26, 43, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 14px; cursor: pointer; transition: all 0.2s; }
    .concept-card:hover { border-color: var(--accent); background: rgba(88, 166, 255, 0.06); }
    .concept-head { font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 6px; display: flex; justify-content: space-between; }
    .concept-body { font-size: 12px; color: var(--muted); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }

    /* Modal */
    .modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.75); display: none; align-items: center; justify-content: center; z-index: 1000; padding: 20px; backdrop-filter: blur(4px); }
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
          <p>Autonomous Knowledge Ingestion, Sandbox Verification, and Dynamic Body Hot-Evolution</p>
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
        <div class="card-title"><span>Knowledge Applications</span><span>⚡</span></div>
        <div class="card-num" id="metric-usages" style="color: var(--purple);">--</div>
        <div class="card-sub">Reasoning hits, repairs & plan executions</div>
      </div>
      <div class="card">
        <div class="card-title"><span>Active Knowledge Sources</span><span>🌐</span></div>
        <div class="card-num" id="metric-sources" style="color: var(--accent);">4 / 4</div>
        <div class="card-sub">Wikipedia • HackerNews • Reddit • AI Federation</div>
      </div>
      <div class="card">
        <div class="card-title"><span>Connected Bodies Evolving</span><span>🧬</span></div>
        <div class="card-num" id="metric-evolutions" style="color: var(--success);">--</div>
        <div class="card-sub">Executor, Console, OCR Formatter & Dynamic</div>
      </div>
    </div>

    <!-- Section: Autonomous Task Learning & Hot-Injection Pipeline -->
    <div class="card" style="margin-bottom: 28px; border-color: rgba(88, 166, 255, 0.4);">
      <div class="section-title">
        <span>⚡</span> Autonomous Self-Learning & Hot-Injection Pipeline
        <span>(Ask any task → Researched → Sandbox Tested → Learned → Injected into Body → Executed)</span>
      </div>
      <p style="font-size: 13px; color: var(--muted); margin-bottom: 16px;">
        When a user requests a task for any connected body that Hashtag does not yet know how to do, this entire 5-step loop runs <b>100% automatically with zero human intervention</b>:
      </p>

      <!-- 5 Visual Pipeline Steps -->
      <div class="pipeline-grid">
        <div class="pipe-step-card" id="pstep-1">
          <div class="step-num">Step 1</div>
          <div class="step-title">Gap Detection</div>
          <div class="step-desc">Identifies user intent & detects missing capability in the body.</div>
        </div>
        <div class="pipe-step-card" id="pstep-2">
          <div class="step-num">Step 2</div>
          <div class="step-title">Web Ingestion</div>
          <div class="step-desc">Searches Wikipedia, Reddit, HN & AI nodes for algorithms & code recipes.</div>
        </div>
        <div class="pipe-step-card" id="pstep-3">
          <div class="step-num">Step 3</div>
          <div class="step-title">Sandbox Testing</div>
          <div class="step-desc">Generates Python code & executes automated unit tests in isolated sandbox.</div>
        </div>
        <div class="pipe-step-card" id="pstep-4">
          <div class="step-num">Step 4</div>
          <div class="step-title">Permanent Learning</div>
          <div class="step-desc">Commits verified capability to memory & telemetry audit logs.</div>
        </div>
        <div class="pipe-step-card" id="pstep-5">
          <div class="step-num">Step 5</div>
          <div class="step-title">Hot-Injection & Run</div>
          <div class="step-desc">Injects handler into the target body and executes the user's task.</div>
        </div>
      </div>

      <!-- Interactive Runner Form -->
      <div style="background: rgba(0, 0, 0, 0.25); border: 1px solid var(--card-border); border-radius: 12px; padding: 18px; margin-top: 14px;">
        <div style="font-size: 14px; font-weight: 700; margin-bottom: 10px;">Test the Autonomous Loop Live:</div>
        
        <div style="margin-bottom: 12px;">
          <span style="font-size: 12px; color: var(--muted); margin-right: 8px;">Try sample tasks:</span>
          <div style="display: inline-block;">
            <span class="task-chip" onclick="quickFillTask('calculate sha256 checksum of this text', 'executor', 'hashtag autonomous intelligence system')">🔐 SHA-256 Checksum</span>
            <span class="task-chip" onclick="quickFillTask('convert this markdown table to json format', 'ocr_formatter', '| Name | Role |\n|---|---|\n| Hashtag Core | Brain |\n| Executor | Physical Body |')">📊 Markdown Table to JSON</span>
            <span class="task-chip" onclick="quickFillTask('extract all emails from this document', 'executor', 'Contact admin@hashtag.ai and support@render.com for details')">📧 Extract Emails</span>
            <span class="task-chip" onclick="quickFillTask('package files into zip archive', 'executor', 'project_backup')">📦 Compress ZIP</span>
          </div>
        </div>

        <div class="grid-2" style="margin-bottom: 12px;">
          <div>
            <label style="font-size: 12px; color: var(--muted); display: block; margin-bottom: 6px;">Target Body:</label>
            <select id="auto-body" class="input-field" style="width: 100%;">
              <option value="executor">Hashtag the Executor (executor)</option>
              <option value="ocr_formatter">OCR Record Formatter (ocr_formatter)</option>
              <option value="console">Hashtag Web Console (console)</option>
            </select>
          </div>
          <div>
            <label style="font-size: 12px; color: var(--muted); display: block; margin-bottom: 6px;">Task Description / Command:</label>
            <input type="text" id="auto-task" class="input-field" style="width: 100%;" placeholder="e.g. calculate sha256 checksum, convert markdown table to json...">
          </div>
        </div>

        <div style="margin-bottom: 14px;">
          <label style="font-size: 12px; color: var(--muted); display: block; margin-bottom: 6px;">Input Payload / Text (Optional):</label>
          <textarea id="auto-input" class="input-field" rows="2" style="width: 100%; resize: vertical;" placeholder="Optional text or data for the task..."></textarea>
        </div>

        <button class="btn btn-accent" style="width: 100%; justify-content: center; font-size: 14px; padding: 12px;" onclick="runAutonomousCycle()">
          🚀 Run Full Autonomous Self-Learning & Hot-Injection Cycle
        </button>

        <div id="auto-status-msg" style="font-size: 13px; margin-top: 10px; font-weight: 600; text-align: center;"></div>
        <div id="auto-console" class="result-console" style="display: none;"></div>
      </div>
    </div>

    <!-- Section: Where Knowledge Comes From (Source Breakdown) -->
    <div class="grid-2">
      <!-- Sources Card -->
      <div class="card">
        <div class="section-title">Where Hashtag Gets Knowledge <span>(Source Reports)</span></div>
        <p style="font-size: 12px; color: var(--muted); margin-bottom: 16px;">Hashtag continuously harvests free public knowledge bases and AI peer nodes across the internet:</p>
        
        <div class="source-row">
          <div class="source-header"><span>🌐 Wikipedia (Articles & Definitions)</span><span id="src-wiki-pct">--%</span></div>
          <div class="source-bar-bg"><div id="bar-wiki" class="source-bar-fill fill-wiki" style="width: 0%;"></div></div>
        </div>
        <div class="source-row">
          <div class="source-header"><span>💬 Reddit Tech (r/programming, r/MachineLearning)</span><span id="src-reddit-pct">--%</span></div>
          <div class="source-bar-bg"><div id="bar-reddit" class="source-bar-fill fill-reddit" style="width: 0%;"></div></div>
        </div>
        <div class="source-row">
          <div class="source-header"><span>📰 HackerNews (Architecture & Best Practices)</span><span id="src-hn-pct">--%</span></div>
          <div class="source-bar-bg"><div id="bar-hn" class="source-bar-fill fill-hn" style="width: 0%;"></div></div>
        </div>
        <div class="source-row">
          <div class="source-header"><span>🤖 AI Federation Mesh (Distilled Model Logic)</span><span id="src-ai-pct">--%</span></div>
          <div class="source-bar-bg"><div id="bar-ai" class="source-bar-fill fill-ai" style="width: 0%;"></div></div>
        </div>

        <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.06);">
          <div style="font-size: 12px; color: var(--muted); margin-bottom: 8px;">Trigger Immediate Knowledge Ingestion:</div>
          <div style="display: flex; gap: 8px;">
            <input type="text" id="custom-topic" class="input-field" placeholder="Topic to learn (e.g. GraphQL, WebSockets, PyTorch)..." style="flex: 1;">
            <button class="btn btn-outline" onclick="triggerHarvest()">Absorb Topic</button>
          </div>
          <div id="harvest-feedback" style="font-size: 12px; margin-top: 6px; color: var(--success);"></div>
        </div>
      </div>

      <!-- Domain Distribution Card -->
      <div class="card">
        <div class="section-title">What Hashtag Learned <span>(Engineering Domains)</span></div>
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
      <div id="modal-summary" style="font-size: 14px; line-height: 1.6; color: #c9d1d9; margin-bottom: 16px; white-space: pre-wrap;"></div>
      <div style="font-size: 12px; color: var(--muted); margin-bottom: 8px;">Tags / Context:</div>
      <div id="modal-tags" style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px;"></div>
      <div id="modal-url"></div>
    </div>
  </div>

  <script>
    var currentData = null;

    function timeAgo(ts) {
      if (!ts) return "recently";
      var s = Math.floor(Date.now() / 1000 - ts);
      if (s < 60) return "just now";
      if (s < 3600) return Math.floor(s / 60) + "m ago";
      if (s < 86400) return Math.floor(s / 3600) + "h ago";
      return Math.floor(s / 86400) + "d ago";
    }

    function loadData() {
      fetch('/v1/knowledge/status')
        .then(function(res) { return res.json(); })
        .then(function(data) {
          currentData = data;
          renderMetrics(data);
          renderSources(data.source_breakdown || {});
          renderDomains(data.domains || {});
          renderStream(data.recent_stream || []);
          renderUsages(data.recent_usages || []);
          doSearch();
        })
        .catch(function(err) {
          console.error("Knowledge fetch error:", err);
        });

      fetch('/v1/body/evolution/status')
        .then(function(res) { return res.json(); })
        .then(function(data) {
          document.getElementById('metric-evolutions').textContent = data.total_evolutions || 0;
          renderBodies(data.bodies || []);
        })
        .catch(function(err) {
          console.error("Evolution fetch error:", err);
        });
    }

    function renderMetrics(data) {
      var count = data.total_concepts || 0;
      var bytes = data.total_bytes || 0;
      var kb = Math.round(bytes / 1024);
      document.getElementById('metric-learned').textContent = count + " (" + kb + " KB)";
      document.getElementById('metric-usages').textContent = data.total_usages || 0;
      document.getElementById('dom-all-cnt').textContent = count;
    }

    function renderSources(sources) {
      var wiki = sources.wikipedia || { count: 0, percentage: 0 };
      var reddit = sources.reddit || { count: 0, percentage: 0 };
      var hn = sources.hackernews || { count: 0, percentage: 0 };
      var ai = sources.ai_federation || { count: 0, percentage: 0 };

      document.getElementById('src-wiki-pct').textContent = wiki.percentage + "% (" + wiki.count + ")";
      document.getElementById('bar-wiki').style.width = wiki.percentage + "%";

      document.getElementById('src-reddit-pct').textContent = reddit.percentage + "% (" + reddit.count + ")";
      document.getElementById('bar-reddit').style.width = reddit.percentage + "%";

      document.getElementById('src-hn-pct').textContent = hn.percentage + "% (" + hn.count + ")";
      document.getElementById('bar-hn').style.width = hn.percentage + "%";

      document.getElementById('src-ai-pct').textContent = ai.percentage + "% (" + ai.count + ")";
      document.getElementById('bar-ai').style.width = ai.percentage + "%";
    }

    function renderDomains(domains) {
      var container = document.getElementById('domain-badges');
      var allCount = currentData ? (currentData.total_concepts || 0) : 0;
      var html = '<div class="domain-badge active" onclick="filterDomain(\\'all\\')">All Domains <span class="domain-count">' + allCount + '</span></div>';
      
      for (var d in domains) {
        if (domains.hasOwnProperty(d)) {
          html += '<div class="domain-badge" onclick="filterDomain(\\'' + d + '\\')">' + d + ' <span class="domain-count">' + domains[d] + '</span></div>';
        }
      }
      container.innerHTML = html;
    }

    function filterDomain(dom) {
      var badges = document.querySelectorAll('.domain-badge');
      badges.forEach(function(b) { b.classList.remove('active'); });
      if (event && event.currentTarget) event.currentTarget.classList.add('active');
      document.getElementById('search-input').value = (dom === 'all' ? '' : dom);
      doSearch();
    }

    function renderStream(stream) {
      var box = document.getElementById('recent-stream-box');
      if (!stream || !stream.length) {
        box.innerHTML = '<div style="color:var(--muted); font-size:12px;">Absorbing knowledge in background...</div>';
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
        urlDiv.innerHTML = '';
      }
      document.getElementById('modal').style.display = 'flex';
    }

    function closeModal(e) {
      document.getElementById('modal').style.display = 'none';
    }

    function triggerHarvest() {
      var input = document.getElementById('custom-topic');
      var val = input.value.trim();
      var fb = document.getElementById('harvest-feedback');
      if (!val) return;
      fb.textContent = "Hashtag is searching & absorbing " + val + "...";
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

    // ------------------------------------------------------------------
    // Autonomous Task Learning & Hot-Injection Runner
    // ------------------------------------------------------------------

    function quickFillTask(task, bodyId, inputPayload) {
      document.getElementById('auto-task').value = task;
      document.getElementById('auto-body').value = bodyId;
      document.getElementById('auto-input').value = inputPayload || "";
    }

    function setStepStatus(stepNum, status) {
      var card = document.getElementById('pstep-' + stepNum);
      if (!card) return;
      card.classList.remove('active', 'completed');
      if (status === 'active') card.classList.add('active');
      if (status === 'completed') card.classList.add('completed');
    }

    function resetPipelineSteps() {
      for (var s = 1; s <= 5; s++) setStepStatus(s, '');
    }

    function runAutonomousCycle() {
      var targetBody = document.getElementById('auto-body').value;
      var task = document.getElementById('auto-task').value.trim();
      var inputText = document.getElementById('auto-input').value;
      var statusMsg = document.getElementById('auto-status-msg');
      var consoleBox = document.getElementById('auto-console');

      if (!task) {
        statusMsg.textContent = "Please enter a task or select a quick task above.";
        statusMsg.style.color = "var(--warning)";
        return;
      }

      resetPipelineSteps();
      setStepStatus(1, 'active');
      statusMsg.textContent = "Hashtag is analyzing request and detecting capability gaps in " + targetBody + "...";
      statusMsg.style.color = "var(--accent)";
      consoleBox.style.display = "block";
      consoleBox.textContent = "[1/5] Analyzing body capabilities... Gap identified!\\n[2/5] Core searching Wikipedia, Reddit, HN & AI Mesh for algorithms...\\n";

      setTimeout(function() {
        setStepStatus(1, 'completed');
        setStepStatus(2, 'active');
        consoleBox.textContent += "[3/5] Generating Python implementation & automated verification test cases...\\n[4/5] Executing sandbox test runner...\\n";
      }, 400);

      fetch('/v1/autonomous/learn-and-execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_body: targetBody,
          request: task,
          inputText: inputText
        })
      })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        for (var s = 1; s <= 5; s++) setStepStatus(s, 'completed');
        
        if (data.ok) {
          statusMsg.textContent = "✓ Task Completed! Learned, sandboxed, injected, and executed successfully.";
          statusMsg.style.color = "var(--success)";
          
          var log = "=== AUTONOMOUS TASK LEARNING & HOT-INJECTION COMPLETE ===\\n";
          log += "Target Body: " + data.target_body + "\\n";
          log += "Capability ID: " + data.capability_id + "\\n\\n";
          log += "--- Execution Steps Completed ---\\n";
          (data.steps_completed || []).forEach(function(st) {
            log += "✓ " + st.name + ": " + st.details + "\\n";
          });
          log += "\\n--- Real Execution Output ---\\n";
          log += JSON.stringify(data.execution_result, null, 2);
          consoleBox.textContent = log;
          
          // Refresh background data to show newly recorded usage and evolution
          setTimeout(loadData, 1000);
        } else {
          statusMsg.textContent = "Pipeline Error: " + (data.error || data.message || "Failed");
          statusMsg.style.color = "red";
          consoleBox.textContent += "\\nERROR: " + (data.error || data.message);
        }
      })
      .catch(function(err) {
        statusMsg.textContent = "Network Error: " + err.message;
        statusMsg.style.color = "red";
        consoleBox.textContent += "\\nNetwork Error: " + err.message;
      });
    }

    // Initialize and start live polling every 10 seconds
    loadData();
    setInterval(loadData, 10000);
  </script>
</body>
</html>
"""
