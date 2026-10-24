"""Hashtag GitHub Direct Cloud Web IDE & Development Studio.

Allows developers to build, edit, preview, and commit projects directly to GitHub
without ever needing local PC setup, git installations, or cloning.
"""

STUDIO_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Hashtag GitHub Cloud Studio</title>
  <link rel="icon" type="image/jpeg" href="/favicon.ico">
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
    /* === 100% RELIABLE ROCK-SOLID FULLSCREEN === */
    body.has-preview-fullscreen {
      overflow: hidden !important;
    }
    body.has-preview-fullscreen .preview-container {
      position: fixed !important;
      inset: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      z-index: 999999 !important;
      background: #070b14 !important;
      display: flex !important;
      flex-direction: column !important;
      overflow: hidden !important;
    }
    body.has-preview-fullscreen .preview-toolbar {
      position: fixed !important;
      top: 14px !important;
      left: 50% !important;
      transform: translateX(-50%) !important;
      z-index: 1000000 !important;
      background: rgba(15, 23, 42, 0.94) !important;
      backdrop-filter: blur(16px) !important;
      -webkit-backdrop-filter: blur(16px) !important;
      border: 1px solid rgba(120, 169, 255, 0.35) !important;
      border-radius: 9999px !important;
      padding: 6px 16px !important;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8), 0 0 20px rgba(56, 189, 248, 0.3) !important;
      display: flex !important;
      align-items: center !important;
    }
    body.has-preview-fullscreen .preview-viewport-wrap {
      position: absolute !important;
      inset: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      padding: 56px 0 0 0 !important;
      box-sizing: border-box !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      overflow: hidden !important;
    }
    body.has-preview-fullscreen .preview-frame-holder:not(.device-tablet):not(.device-mobile) {
      width: 100% !important;
      height: 100% !important;
      border-radius: 0 !important;
      border: none !important;
    }

    /* MAIN WORKSPACE */
    .studio-workspace {
      display: grid;
      grid-template-columns: 260px 1fr 420px;
      height: 100%;
      min-height: 0;
      overflow: hidden;
      transition: grid-template-columns 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
    }
    .studio-workspace.preview-closed,
    .studio-workspace.preview-closed.aux-expanded,
    .studio-workspace.preview-closed.aux-maximized {
      grid-template-columns: 260px 1fr 0px !important;
    }
    .studio-workspace.preview-closed .aux-panel {
      border-left: none !important;
      display: none !important;
    }
    .studio-workspace.aux-expanded {
      grid-template-columns: 260px 1fr 650px;
    }
    .studio-workspace.aux-maximized {
      grid-template-columns: 0px 0px 1fr;
    }
    /* LEFT PANEL: FILE EXPLORER */
    .sidebar-panel {
      background: var(--panel);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
      overflow: hidden;
      box-sizing: border-box;
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
      flex-shrink: 0;
    }
    .search-filter {
      padding: 8px 10px;
      border-bottom: 1px solid var(--border);
      flex-shrink: 0;
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
      flex: 1 1 0%;
      min-height: 0 !important;
      overflow-y: auto !important;
      overflow-x: hidden;
      padding: 6px 4px;
      box-sizing: border-box;
    }
    .file-tree::-webkit-scrollbar {
      width: 6px;
    }
    .file-tree::-webkit-scrollbar-thumb {
      background: rgba(120, 169, 255, 0.25);
      border-radius: 4px;
    }
    .file-tree::-webkit-scrollbar-thumb:hover {
      background: rgba(120, 169, 255, 0.5);
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
      min-width: 0;
      overflow: hidden;
      position: relative;
      box-sizing: border-box;
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
      flex-shrink: 0;
      overflow: hidden;
    }
    .code-textarea {
      flex: 1 1 0%;
      min-width: 0 !important;
      width: 100%;
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
      word-break: normal;
      overflow-wrap: normal;
      tab-size: 2;
      overflow: auto !important;
      overflow-x: auto !important;
      overflow-y: auto !important;
      box-sizing: border-box;
    }
    .code-textarea::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
    .code-textarea::-webkit-scrollbar-thumb {
      background: rgba(120, 169, 255, 0.25);
      border-radius: 4px;
    }
    .code-textarea::-webkit-scrollbar-thumb:hover {
      background: rgba(120, 169, 255, 0.5);
    }
    /* RIGHT PANEL: LIVE PREVIEW & AI ASSISTANT */
    .studio-workspace.preview-closed .aux-panel {
      border-left: none !important;
      display: none !important;
    }
    .aux-panel {
      background: var(--panel);
      border-left: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      height: 100%;
      min-width: 0;
      overflow: visible;
      position: relative;
    }
    .aux-collapse-btn {
      position: absolute;
      left: -18px;
      top: 50%;
      transform: translateY(-50%);
      width: 18px;
      height: 64px;
      background: #161b22;
      border: 1.5px solid #38bdf8;
      border-right: none;
      border-radius: 9px 0 0 9px;
      color: #38bdf8;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 100;
      padding: 0;
      transition: all 0.2s ease;
      font-size: 17px;
      font-weight: 800;
      line-height: 1;
      user-select: none;
      box-shadow: -3px 0 14px rgba(56, 189, 248, 0.4);
    }
    .aux-collapse-btn:hover {
      background: #1e293b;
      color: #fff;
      border-color: #7dd3fc;
      box-shadow: -4px 0 20px rgba(56, 189, 248, 0.65);
      width: 22px;
      left: -22px;
    }
    .aux-dock-buttons {
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      display: none;
      flex-direction: column;
      gap: 12px;
      z-index: 40;
    }
    .studio-workspace.preview-closed .aux-dock-buttons {
      display: flex;
    }
    .aux-dock-btn {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: rgba(13, 17, 23, 0.92);
      backdrop-filter: blur(8px);
      border: 1.5px solid rgba(88, 166, 255, 0.4);
      color: #58a6ff;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45), 0 0 12px rgba(88, 166, 255, 0.15);
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .aux-dock-btn:hover {
      transform: scale(1.1);
      border-color: #38bdf8;
      color: #38bdf8;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5), 0 0 16px rgba(56, 189, 248, 0.45);
    }
    .aux-dock-btn.dock-ai {
      border-color: rgba(167, 139, 250, 0.5);
      color: #c084fc;
    }
    .aux-dock-btn.dock-ai:hover {
      border-color: #c084fc;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5), 0 0 16px rgba(192, 132, 252, 0.45);
    }
    .aux-dock-btn.dock-preview {
      border-color: rgba(56, 189, 248, 0.5);
      color: #38bdf8;
    }
    .aux-dock-btn.dock-preview:hover {
      border-color: #38bdf8;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5), 0 0 16px rgba(56, 189, 248, 0.45);
    }

    /* === INTERACTIVE CYBER EYE COMPONENT === */
    .cyber-eye {
      position: relative;
      width: 22px;
      height: 14px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      user-select: none;
      flex-shrink: 0;
    }
    .cyber-eye.dock-size {
      width: 28px;
      height: 18px;
    }
    
    .eye-socket {
      position: relative;
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: radial-gradient(circle at center, #0f172a 20%, #020617 100%);
      border: 1.5px solid #38bdf8;
      overflow: hidden;
      box-shadow: 0 0 8px rgba(56, 189, 248, 0.5), inset 0 0 4px rgba(56, 189, 248, 0.35);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    
    .eye-ball {
      position: absolute;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .eye-iris {
      position: absolute;
      width: 9.5px;
      height: 9.5px;
      border-radius: 50%;
      background: radial-gradient(circle at 35% 35%, #7dd3fc 0%, #0284c7 60%, #0369a1 100%);
      box-shadow: 0 0 6px rgba(56, 189, 248, 0.9);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.08s ease-out;
      will-change: transform;
    }
    .cyber-eye.dock-size .eye-iris {
      width: 12px;
      height: 12px;
    }
    
    .eye-pupil {
      width: 4.5px;
      height: 4.5px;
      border-radius: 50%;
      background: #000814;
      position: relative;
    }
    .cyber-eye.dock-size .eye-pupil {
      width: 5.5px;
      height: 5.5px;
    }
    
    .eye-glint {
      position: absolute;
      width: 2px;
      height: 2px;
      border-radius: 50%;
      background: #ffffff;
      top: 0.5px;
      left: 0.5px;
      box-shadow: 0 0 2px #fff;
    }
    /* Eyelids for blinking */
    .eye-lid {
      position: absolute;
      left: 0;
      width: 100%;
      height: 50%;
      background: #0b1120;
      z-index: 5;
      transition: transform 0.08s cubic-bezier(0.4, 0, 0.2, 1);
      pointer-events: none;
    }
    .top-lid {
      top: 0;
      transform: translateY(-100%);
      border-bottom: 0.5px solid rgba(56, 189, 248, 0.4);
    }
    .bottom-lid {
      bottom: 0;
      transform: translateY(100%);
      border-top: 0.5px solid rgba(56, 189, 248, 0.4);
    }
    .cyber-eye.blinking .top-lid {
      transform: translateY(0%);
    }
    .cyber-eye.blinking .bottom-lid {
      transform: translateY(0%);
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
      background: #090d16;
      overflow: hidden;
      box-sizing: border-box;
    }
    .preview-container.is-fullscreen {
      position: fixed !important;
      inset: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      z-index: 99999 !important;
      background: #070b14 !important;
      display: flex !important;
      flex-direction: column !important;
      overflow: hidden !important;
      box-sizing: border-box !important;
    }
    .preview-container.is-fullscreen .preview-toolbar {
      position: fixed !important;
      top: 14px !important;
      left: 50% !important;
      transform: translateX(-50%) !important;
      z-index: 100000 !important;
      background: rgba(15, 23, 42, 0.94) !important;
      backdrop-filter: blur(16px) !important;
      -webkit-backdrop-filter: blur(16px) !important;
      border: 1px solid rgba(120, 169, 255, 0.28) !important;
      border-radius: 9999px !important;
      padding: 5px 14px !important;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8), 0 0 20px rgba(56, 189, 248, 0.2) !important;
      display: flex !important;
      align-items: center !important;
      gap: 10px !important;
      width: auto !important;
      max-width: 95vw !important;
      opacity: 1 !important;
    }
    .preview-container.is-fullscreen .dev-group {
      display: inline-flex !important;
      align-items: center !important;
      gap: 3px !important;
      background: rgba(255, 255, 255, 0.08) !important;
      padding: 2px 4px !important;
      border-radius: 9999px !important;
    }
    .preview-container.is-fullscreen .preview-viewport-wrap {
      flex: 1;
      width: 100vw;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #070b14;
      overflow: hidden;
      padding: 62px 0 0 0 !important;
      box-sizing: border-box !important;
    }
    .preview-container.is-fullscreen .preview-frame-holder {
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      box-sizing: border-box;
    }
    .preview-container.is-fullscreen .preview-frame-holder:not(.device-tablet):not(.device-mobile) {
      width: 100% !important;
      height: 100% !important;
      max-width: 100% !important;
      max-height: 100% !important;
      border-radius: 0 !important;
      box-shadow: none !important;
      border: none !important;
      box-sizing: border-box !important;
    }
    .preview-container.is-fullscreen .preview-frame-holder.device-tablet {
      width: 768px !important;
      height: 1024px !important;
      max-width: 96vw !important;
      max-height: calc(100vh - 84px) !important;
      border-radius: 28px !important;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9), 0 0 0 12px #1e293b, 0 0 0 13px rgba(255,255,255,0.15) !important;
      border: 1px solid rgba(255, 255, 255, 0.12) !important;
      overflow: hidden !important;
      flex-shrink: 0;
      margin: auto;
      box-sizing: border-box;
    }
    .preview-container.is-fullscreen .preview-frame-holder.landscape.device-tablet {
      width: 1024px !important;
      height: 768px !important;
      max-width: 96vw !important;
      max-height: calc(100vh - 84px) !important;
    }
    .preview-container.is-fullscreen .preview-frame-holder.device-mobile {
      width: 375px !important;
      height: 812px !important;
      max-width: 92vw !important;
      max-height: calc(100vh - 84px) !important;
      border-radius: 38px !important;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9), 0 0 0 12px #1e293b, 0 0 0 13px rgba(255,255,255,0.15) !important;
      border: 1px solid rgba(255, 255, 255, 0.12) !important;
      overflow: hidden !important;
      flex-shrink: 0;
      margin: auto;
      box-sizing: border-box;
    }
    .preview-container.is-fullscreen .preview-frame-holder.landscape.device-mobile {
      width: 812px !important;
      height: 375px !important;
      max-width: 96vw !important;
      max-height: calc(100vh - 84px) !important;
    }
    .preview-toolbar {
      background: var(--panel2);
      padding: 6px 8px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
      min-height: 38px;
      flex-shrink: 0;
      box-sizing: border-box;
    }
    .preview-toolbar-actions {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      flex-shrink: 0;
      margin-left: auto;
    }
    .dev-group {
      display: inline-flex;
      align-items: center;
      gap: 2px;
      background: rgba(255, 255, 255, 0.05);
      padding: 2px;
      border-radius: 6px;
      flex-shrink: 0;
    }
    .dev-btn {
      background: transparent;
      border: none;
      color: var(--muted);
      font-size: 11px;
      padding: 3px 6px;
      border-radius: 4px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 3px;
      white-space: nowrap;
      transition: all 0.15s ease;
    }
    .dev-btn:hover { color: #fff; background: rgba(255, 255, 255, 0.08); }
    .dev-btn.active { color: #fff; background: var(--accent); font-weight: 600; }
    
    .preview-container:not(.is-fullscreen) .dev-btn-label {
      display: none;
    }
    .preview-container.is-fullscreen .dev-btn-label {
      display: inline !important;
    }
    
    .preview-viewport-wrap {
      flex: 1 1 0%;
      min-height: 0 !important;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #0b0f19;
      overflow: hidden;
      padding: 0 !important;
      box-sizing: border-box !important;
      position: relative;
      width: 100%;
      height: 100%;
    }
    .preview-frame-holder {
      width: 100%;
      height: 100%;
      background: #fff;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      display: flex;
      position: relative;
      box-sizing: border-box;
    }
    .preview-frame-holder.device-tablet {
      width: 768px;
      height: 1024px;
      max-width: 100%;
      max-height: 88vh;
      border-radius: 20px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), 0 0 0 10px #1e293b;
      overflow: hidden;
      margin: auto;
      box-sizing: border-box;
    }
    .preview-frame-holder.device-mobile {
      width: 375px;
      height: 812px;
      max-width: 100%;
      max-height: 85vh;
      border-radius: 28px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), 0 0 0 10px #1e293b;
      overflow: hidden;
      margin: auto;
      box-sizing: border-box;
    }
    .preview-frame-holder.landscape.device-tablet {
      width: 1024px;
      height: 768px;
      max-width: 100%;
      max-height: 88vh;
    }
    .preview-frame-holder.landscape.device-mobile {
      width: 812px;
      height: 375px;
      max-width: 100%;
      max-height: 85vh;
    }
    .preview-frame {
      width: 100%;
      height: 100%;
      border: none;
      background: #fff;
      display: block;
      box-sizing: border-box;
    }
    .ai-assistant-container {
      flex: 1 1 0%;
      display: flex;
      flex-direction: column;
      height: calc(100% - 38px);
      max-height: calc(100% - 38px);
      min-height: 0 !important;
      padding: 12px 14px 12px 14px;
      box-sizing: border-box !important;
      overflow: hidden;
      width: 100%;
      position: relative;
    }
    .ai-chat-messages {
      flex: 1 1 0%;
      min-height: 0 !important;
      overflow-y: scroll !important; /* Always enable vertical scrolling */
      overflow-x: hidden !important;
      padding: 4px 6px 20px 6px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      font-size: 12.5px;
      box-sizing: border-box;
      width: 100%;
      overscroll-behavior-y: contain;
      scroll-behavior: smooth;
      scrollbar-width: thin;
      scrollbar-color: rgba(56, 189, 248, 0.5) rgba(15, 23, 42, 0.6);
      touch-action: pan-y;
    }
    .ai-chat-messages::-webkit-scrollbar {
      width: 8px !important;
    }
    .ai-chat-messages::-webkit-scrollbar-track {
      background: rgba(15, 23, 42, 0.6);
      border-radius: 6px;
    }
    .ai-chat-messages::-webkit-scrollbar-thumb {
      background: rgba(56, 189, 248, 0.45);
      border-radius: 6px;
      border: 1px solid rgba(56, 189, 248, 0.2);
    }
    .ai-chat-messages::-webkit-scrollbar-thumb:hover {
      background: rgba(56, 189, 248, 0.85);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.6);
    }
    .ai-msg {
      padding: 12px 14px;
      border-radius: 10px;
      line-height: 1.55;
      box-sizing: border-box;
      width: 100%;
      max-width: 100%;
      word-break: break-word;
      overflow-wrap: break-word;
    }
    .ai-msg.user {
      background: rgba(120, 169, 255, 0.15);
      border: 1px solid rgba(120, 169, 255, 0.25);
      align-self: flex-end;
      color: #fff;
      max-width: 90%;
    }
    .ai-msg.assistant {
      background: var(--panel2);
      border: 1px solid var(--border);
      align-self: stretch;
      color: var(--text);
      margin-left: 0;
      margin-right: 0;
    }
    .ai-msg pre {
      max-width: 100%;
      overflow-x: auto !important;
      white-space: pre !important;
      word-break: normal !important;
      box-sizing: border-box;
    }
    .ai-composer {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-top: 8px;
      flex-shrink: 0;
      box-sizing: border-box;
      width: 100%;
    }
    .ai-composer textarea {
      width: 100%;
      height: 54px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text);
      padding: 8px 10px;
      font-size: 12px;
      outline: none;
      resize: none;
      box-sizing: border-box;
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
        <img src="/assets/hashtag_logo.jpg" alt="Logo" style="width:24px;height:24px;border-radius:6px;object-fit:cover;box-shadow:0 0 10px rgba(120,169,255,0.4);">
        <span>Hashtag</span>
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
      <a href="/ai" class="btn" target="_blank" style="border-color:rgba(88,166,255,0.4);color:#58a6ff;" title="Open Hashtag AI Chat">💬 Chat ↗</a>
      <a href="/console" class="btn" target="_blank" title="Open Hashtag Console">💬 Console ↗</a>
    </div>
  </header>

  <!-- WORKSPACE -->
  <main id="workspace" class="studio-workspace">
    <!-- SIDEBAR: FILES -->
    <aside class="sidebar-panel">
      <div class="sidebar-head">
        <div style="display:flex;align-items:center;gap:6px">
          <span>Project Explorer</span>
          <span id="file-count" style="font-weight:600;color:var(--accent)">0 files</span>
        </div>
        <button id="sidebar-gh-btn" class="btn" style="padding:2px 8px;font-size:11px;display:inline-flex;align-items:center;gap:5px;border-color:rgba(120,169,255,0.3)" title="GitHub Account on this Device">
          <span id="sidebar-gh-label">🐙 GitHub</span>
        </button>
      </div>
      <div class="search-filter" style="position:relative">
        <input type="text" id="file-search" placeholder="Search files in repository..." style="padding-right:24px">
        <button id="clear-search-btn" type="button" style="display:none;position:absolute;right:14px;top:50%;transform:translateY(-50%);background:transparent;border:none;color:var(--muted);cursor:pointer;font-size:12px;padding:2px 4px" title="Clear Search">✕</button>
      </div>
      <div id="file-tree" class="file-tree">
        <div style="padding:20px;text-align:center;color:var(--muted);font-size:12px">
          Connecting to GitHub repository...
        </div>
      </div>
    </aside>

    <!-- CENTER: CODE EDITOR -->
    <section class="editor-panel">
      <div id="editor-tabs" class="editor-tabs" style="display:flex;justify-content:space-between;align-items:center">
        <div style="display:flex;align-items:center">
          <div class="editor-tab active" id="tab-primary">
            <span id="tab-name">untitled</span>
            <span id="tab-dirty" style="display:none;color:var(--warning)">●</span>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:6px;padding-right:10px">
          <button id="btn-format-code" class="btn" title="Beautify / Format HTML, CSS, JS code" style="padding:2px 8px;font-size:11px">✨ Format</button>
          <button id="btn-toggle-wrap" class="btn" title="Toggle Word Wrap" style="padding:2px 8px;font-size:11px">Wrap: OFF</button>
        </div>
      </div>
      <div class="editor-body-wrap">
        <div id="line-numbers" class="line-numbers">1</div>
        <textarea id="code-editor" class="code-textarea" wrap="off" spellcheck="false" placeholder="// Click any file from the explorer to open and edit directly on GitHub..."></textarea>
      </div>
    </section>

    <!-- RIGHT: LIVE PREVIEW & AI ASSISTANT -->
    <aside id="aux-panel" class="aux-panel">
      <!-- COLLAPSE HANDLE BUTTON (Collapses side panel) -->
      <button id="btn-collapse-aux" class="aux-collapse-btn" title="Collapse Side Panel (Hide Preview & AI)">
        <span>›</span>
      </button>

      <div class="aux-tabs">
        <div id="tab-btn-preview" class="aux-tab active" style="display:flex;align-items:center;justify-content:center;gap:7px">
          <div class="cyber-eye" id="eye-tab">
            <div class="eye-socket">
              <div class="eye-lid top-lid"></div>
              <div class="eye-ball">
                <div class="eye-iris">
                  <div class="eye-pupil">
                    <div class="eye-glint"></div>
                  </div>
                </div>
              </div>
              <div class="eye-lid bottom-lid"></div>
            </div>
          </div>
          <span>Live Web Preview</span>
        </div>
        <div id="tab-btn-ai" class="aux-tab">🤖 Hashtag AI Co-Pilot</div>
        <button id="btn-expand-aux" class="btn" style="padding:2px 8px;font-size:11px;border-color:rgba(120,169,255,0.35);display:flex;align-items:center;gap:4px" title="Toggle Wide Panel (Read AI response clearly)">
          <span id="expand-aux-icon">⛶</span>
          <span id="expand-aux-label">Widen</span>
        </button>
        <button id="btn-close-aux-header" class="btn" style="padding:2px 8px;margin-right:8px;font-size:11px;border-color:rgba(56,189,248,0.4);color:#38bdf8;display:flex;align-items:center;gap:4px" title="Minimize / Hide Side Panel">
          <span>›</span>
          <span>Close</span>
        </button>
      </div>

      <!-- PREVIEW TAB -->
      <div id="view-preview" class="preview-container">
        <div class="preview-toolbar">
          <div class="dev-group">
            <button id="dev-desktop" class="dev-btn active" title="Desktop Screen (100% Fluid)">🖥️ <span class="dev-btn-label">Desktop</span></button>
            <button id="dev-tablet" class="dev-btn" title="Tablet Screen (768x1024)">📟 <span class="dev-btn-label">Tablet</span></button>
            <button id="dev-mobile" class="dev-btn" title="Mobile Screen (375x812)">📱 <span class="dev-btn-label">Mobile</span></button>
            <button id="dev-rotate" class="dev-btn" title="Rotate Screen Orientation">🔄 <span class="dev-btn-label">Rotate</span></button>
          </div>
          <div class="preview-toolbar-actions">

            <span id="preview-dim-badge" style="font-size:10px;color:var(--muted);font-variant-numeric:tabular-nums;text-align:right">100% Fluid</span>
            <button id="preview-fullscreen-btn" class="btn btn-primary" title="Full Screen Preview (F)" style="padding:2px 8px;font-size:11px;font-weight:600">⛶ Fullscreen</button>
            <button id="preview-popout-btn" class="btn" title="Open in New Real Browser Tab" style="padding:2px 8px;font-size:11px">↗ Pop Out</button>
            <button id="refresh-preview-btn" class="btn" style="padding:2px 8px;font-size:10px" title="Re-render">↻</button>
          </div>
        </div>
        <div class="preview-viewport-wrap">
          
          <div id="preview-frame-holder" class="preview-frame-holder">
            <iframe id="preview-frame" class="preview-frame" 
              sandbox="allow-scripts allow-modals allow-same-origin allow-forms allow-popups allow-pointer-lock allow-downloads allow-top-navigation-by-user-activation"
              referrerpolicy="no-referrer-when-downgrade"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"></iframe>
          </div>
        </div>
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

    <!-- DOCKED QUICK-ACCESS BUTTONS (Visible when aux-panel is collapsed) -->
    <div id="aux-dock-buttons" class="aux-dock-buttons">
      <button id="dock-btn-ai" class="aux-dock-btn dock-ai" title="Open Hashtag AI Co-Pilot">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="11" width="18" height="10" rx="3"/>
          <circle cx="12" cy="5" r="2"/>
          <path d="M12 7v4"/>
          <line x1="8" y1="16" x2="8.01" y2="16" stroke-width="3"/>
          <line x1="16" y1="16" x2="16.01" y2="16" stroke-width="3"/>
          <path d="M9 19h6"/>
        </svg>
      </button>
      <button id="dock-btn-preview" class="aux-dock-btn dock-preview" title="Open Live Web Preview">
        <div class="cyber-eye dock-size" id="eye-dock">
          <div class="eye-socket">
            <div class="eye-lid top-lid"></div>
            <div class="eye-ball">
              <div class="eye-iris">
                <div class="eye-pupil">
                  <div class="eye-glint"></div>
                </div>
              </div>
            </div>
            <div class="eye-lid bottom-lid"></div>
          </div>
        </div>
      </button>
    </div>
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


<!-- GITHUB AUTH MODAL -->
<div id="github-auth-modal" class="modal-backdrop">
  <div class="modal" style="max-width:500px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3 style="margin:0;display:flex;align-items:center;gap:8px"><span>🐙</span> <span>Connect GitHub Account</span></h3>
      <span id="gh-auth-status-pill" class="badge" style="background:rgba(255,255,255,0.08);color:var(--muted)">Not Connected</span>
    </div>

    <!-- Active Connected Profile Card -->
    <div id="gh-profile-card" style="display:none;background:rgba(255,255,255,0.03);border:1px solid rgba(63,185,80,0.3);border-radius:8px;padding:12px;margin-bottom:14px;align-items:center;gap:12px">
      <img id="gh-avatar-img" src="" alt="Avatar" style="width:38px;height:38px;border-radius:50%;border:1px solid var(--border)">
      <div style="flex:1">
        <div id="gh-user-name" style="font-size:13px;font-weight:700;color:#fff"></div>
        <div id="gh-user-login" style="font-size:11px;color:var(--muted)"></div>
      </div>
      <span class="badge" style="background:rgba(63,185,80,0.2);color:#3fb950;border:1px solid rgba(63,185,80,0.4)">Active</span>
    </div>

    <!-- Browser Session Notice -->
    <div style="background:rgba(88,166,255,0.08);border:1px solid rgba(88,166,255,0.25);border-radius:8px;padding:12px;margin-bottom:14px;font-size:12px;line-height:1.5">
      <div style="font-weight:600;color:#58a6ff;margin-bottom:4px">🌐 Browser Login vs Same-Origin Isolation</div>
      <div style="color:var(--muted)">
        If you are already logged into GitHub in this browser, <b>"1-Click Browser Authorize"</b> loads the pre-configured authorization immediately. If not logged in, GitHub will prompt for your username/password.
      </div>
    </div>

    <!-- 1-Click Browser Connect Button -->
    <div style="margin-bottom:14px">
      <button id="gh-browser-auth-btn" type="button" class="btn btn-primary" style="width:100%;padding:10px;font-size:12px;font-weight:600;display:flex;align-items:center;justify-content:center;gap:8px">
        <span>⚡ 1-Click Browser Authorize</span>
      </button>
    </div>

    <div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <label style="font-size:11px;color:var(--muted)">
          GitHub Personal Access Token:
        </label>
        <button id="gh-paste-token-btn" type="button" class="btn" style="padding:1px 8px;font-size:10px" title="Paste from clipboard and connect">📋 Paste & Connect</button>
      </div>
      <div style="position:relative">
        <input type="password" id="gh-token-input" placeholder="ghp_xxxxxxxxxxxxxxxxxxxx or github_pat_..." style="padding-right:70px">
        <button id="gh-toggle-token-btn" type="button" class="btn" style="position:absolute;right:4px;top:4px;bottom:4px;padding:0 8px;font-size:11px">Show</button>
      </div>
      <div id="gh-auth-error" style="color:var(--danger);font-size:11px;margin-top:6px;display:none"></div>
      <p style="font-size:11px;color:var(--muted);margin:6px 0 0 0">
        Requires <code style="color:#58a6ff">repo</code> scope for private repositories & direct commits. Stored only in this device's browser.
      </p>
    </div>

    <div class="modal-actions" style="margin-top:18px;display:flex;justify-content:space-between;align-items:center">
      <button id="disconnect-gh-btn" class="btn btn-danger" style="display:none">Disconnect / Log Out</button>
      <div style="display:flex;gap:8px;margin-left:auto">
        <button id="cancel-gh-auth-btn" class="btn">Cancel</button>
        <button id="save-gh-token-btn" class="btn btn-primary">
          <span>Connect Token</span>
        </button>
      </div>
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
    var userToken = localStorage.getItem("hashtag_studio_gh_token");
    if (userToken && userToken.trim()) {
      headers["X-GitHub-Token"] = userToken.trim();
    }
    var controller = new AbortController();
    var timeoutId = setTimeout(function() { controller.abort(); }, 15000);
    return fetch(url, {
      method: options.method || "GET",
      headers: headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal: controller.signal
    }).then(function(r) {
      clearTimeout(timeoutId);
      return r.json().then(function(d) {
        if (!r.ok) throw new Error(d.detail || d.error || ("HTTP " + r.status));
        return d;
      });
    }).catch(function(err) {
      clearTimeout(timeoutId);
      throw err;
    });
  }

  function renderRepoList(repos, current) {
    var select = $("repo-select");
    if (!select || !repos || !repos.length) return;
    var html = "";
    current = current || state.repo || repos[0].full_name;
    repos.forEach(function(r) {
      var sel = (r.full_name === current) ? "selected" : "";
      html += '<option value="' + esc(r.full_name) + '" ' + sel + '>' + esc(r.full_name) + (r.private ? " 🔒" : "") + '</option>';
    });
    select.innerHTML = html;
    state.repo = select.value;
  }

  function updateGitHubNavBadge(user) {
    var sBtn = $("sidebar-gh-btn");
    var sLabel = $("sidebar-gh-label");
    if (sLabel) {
      if (user && (user.login || user.username)) {
        var uname = user.login || user.username;
        sLabel.innerHTML = '🐙 <b>@' + esc(uname) + '</b>';
        if (sBtn) {
          sBtn.style.borderColor = "rgba(63,185,80,0.5)";
          sBtn.title = "Connected as @" + uname + " (Click to manage)";
        }
      } else {
        sLabel.textContent = "🐙 Connect";
        if (sBtn) {
          sBtn.style.borderColor = "rgba(120,169,255,0.35)";
          sBtn.title = "Connect your GitHub account";
        }
      }
    }
    var btn = $("btn-gh-account");
    var label = $("gh-nav-label");
    if (btn && label) {
      if (user && (user.login || user.username)) {
        var uname = user.login || user.username;
        label.innerHTML = '🐙 <b>@' + esc(uname) + '</b>';
        btn.style.borderColor = "rgba(63,185,80,0.5)";
        btn.title = "Connected as @" + uname + " on this computer (Click to manage)";
      } else {
        label.textContent = "🐙 Connect GitHub";
        btn.style.borderColor = "rgba(120,169,255,0.35)";
        btn.title = "Connect your GitHub account on this computer";
      }
    }
  }

  // 1. Load User's GitHub Repositories (Auto-connect to server token or localStorage token)
  function loadRepositories(retryCount) {
    retryCount = retryCount || 0;
    var select = $("repo-select");

    $("sync-status").textContent = "Fetching repositories...";
    api("/v1/github/project/repos").then(function(res) {
      var repos = res && (res.repositories || res.repos || (Array.isArray(res) ? res : []));
      var isConnected = res && (res.connected || (repos && repos.length > 0) || (res.user && (res.user.login || res.user.username)));

      if (res && res.user && (res.user.login || res.user.username)) {
        updateGitHubNavBadge(res.user);
      }

      if (isConnected && repos && repos.length) {
        renderRepoList(repos, res.current);
        loadProjectTree();
        $("sync-status").textContent = "Ready (" + repos.length + " repos)";
      } else {
        if (select) select.innerHTML = '<option value="">🐙 Connect GitHub Account...</option>';
        state.repo = "";
        state.tree = [];
        updateGitHubNavBadge(null);
        renderFileTree([]);
        $("sync-status").textContent = "No GitHub Connected";
      }
    }).catch(function(err) {
      console.warn("loadRepositories error:", err);
      if (select) select.innerHTML = '<option value="">🐙 Connect GitHub Account...</option>';
      state.repo = "";
      state.tree = [];
      updateGitHubNavBadge(null);
      renderFileTree([]);
      $("sync-status").textContent = "Connect GitHub";
    });
  }

  // 2. Load Recursive Project Tree
  function loadProjectTree() {
    var treeEl = $("file-tree");
    if (!state.repo) {
      renderFileTree([]);
      return;
    }
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
    items = items || state.tree || [];
    var treeEl = $("file-tree");
    var searchEl = $("file-search");
    var filter = (searchEl && searchEl.value || "").toLowerCase().trim();
    var clearBtn = $("clear-search-btn");
    if (clearBtn) {
      clearBtn.style.display = filter ? "block" : "none";
    }

    if (!items || !items.length) {
      var userToken = localStorage.getItem("hashtag_studio_gh_token");
      if (!userToken || !userToken.trim()) {
        treeEl.innerHTML = '<div style="padding:32px 16px;text-align:center;color:var(--muted);font-size:12px;line-height:1.6">'
          + '<div style="font-size:28px;margin-bottom:10px">🐙</div>'
          + '<div style="font-size:13px;font-weight:600;color:#fff;margin-bottom:6px">No GitHub Account Connected</div>'
          + '<div style="margin-bottom:14px">Connect your GitHub Personal Access Token to browse and edit repositories on this computer.</div>'
          + '<button id="empty-connect-gh-btn" class="btn btn-primary" style="font-size:11px">Connect GitHub</button>'
          + '</div>';
        var b = $("empty-connect-gh-btn");
        if (b) b.onclick = openGitHubAuthModal;
      } else {
        treeEl.innerHTML = '<div style="padding:20px;text-align:center;color:var(--muted);font-size:12px">Repository is empty. Click "+ New File" to start!</div>';
      }
      return;
    }

    var matching = 0;
    var totalBlobs = 0;
    var html = "";
    items.forEach(function(item) {
      if (item.type === "tree") return; // Flat list of file paths works reliably for all depths
      totalBlobs++;
      if (filter && !item.path.toLowerCase().includes(filter)) return;
      matching++;

      var isAct = (item.path === state.activePath) ? "active" : "";
      var icon = getFileIcon(item.path);
      html += '<div class="tree-item ' + isAct + '" data-path="' + esc(item.path) + '">'
            + '<span class="icon">' + icon + '</span>'
            + '<span style="flex:1;overflow:hidden;text-overflow:ellipsis">' + esc(item.path) + '</span>'
            + '</div>';
    });

    var countEl = $("file-count");
    if (countEl) {
      if (filter) {
        countEl.textContent = matching + " / " + totalBlobs;
      } else {
        countEl.textContent = totalBlobs + " files";
      }
    }

    if (!html && filter) {
      treeEl.innerHTML = '<div style="padding:28px 16px;text-align:center;color:var(--muted);font-size:12px">'
        + '<div style="font-size:20px;margin-bottom:8px">🔍</div>'
        + 'No files matching "<b style="color:var(--text)">' + esc(filter) + '</b>"'
        + '<div style="margin-top:10px"><button id="btn-tree-clear-search" class="btn" style="padding:2px 8px;font-size:11px">Clear Search</button></div>'
        + '</div>';
      var tClear = $("btn-tree-clear-search");
      if (tClear) {
        tClear.onclick = function() {
          if (searchEl) searchEl.value = "";
          renderFileTree(state.tree);
          if (searchEl) searchEl.focus();
        };
      }
      return;
    }

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
    var lines = val.split(String.fromCharCode(10)).length;
    var numHtml = "";
    for (var i = 1; i <= lines; i++) {
      numHtml += i + "<br>";
    }
    $("line-numbers").innerHTML = numHtml;
    $("editor-meta").textContent = "Lines: " + lines + " | Chars: " + val.length;
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
    updatePreviewDebounced();
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

  // 6. Live Web Preview - High-Speed Direct DOM & Resource Resolution Engine
  var previewTimer = null;
  var previewBlobUrl = null;

  function updatePreviewDebounced() {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(updatePreview, 250);
  }

  function updatePreview() {
    var frame = $("preview-frame");
    if (!frame) return;

    var content = $("code-editor").value || "";
    var path = (state.activePath || "index.html").toLowerCase();

    // Check if Markdown file
    if (path.endsWith(".md") || path.endsWith(".markdown")) {
      frame.removeAttribute("src");
      frame.srcdoc = '<!doctype html><html><head><meta charset="utf-8">'
                   + '<style>body{font-family:system-ui,-apple-system,sans-serif;background:#0d1424;color:#edf4ff;padding:28px 36px;line-height:1.6;max-width:860px;margin:0 auto}pre{background:#070b14;padding:14px;border-radius:8px;overflow:auto;color:#78a9ff;border:1px solid rgba(255,255,255,0.08)}h1,h2,h3{color:#fff;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:6px}code{background:rgba(255,255,255,0.08);padding:2px 6px;border-radius:4px;color:#38bdf8}table{border-collapse:collapse;width:100%}th,td{border:1px solid rgba(255,255,255,0.15);padding:8px 12px;text-align:left}</style>'
                   + '</head><body>' + (typeof renderStudioMarkdown === "function" ? renderStudioMarkdown(content) : ('<pre>' + esc(content) + '</pre>')) + '</body></html>';
      return;
    }

    // Check if CSS file
    if (path.endsWith(".css")) {
      frame.removeAttribute("src");
      frame.srcdoc = '<!doctype html><html><head><meta charset="utf-8"><style>' + content + '</style>'
                   + '<style>body{font-family:system-ui,sans-serif;padding:30px;background:#0f172a;color:#f8fafc;display:flex;flex-direction:column;gap:16px;align-items:center}.demo-box{padding:24px;border-radius:12px;background:#1e293b;border:1px solid rgba(255,255,255,0.1);max-width:500px;text-align:center}button{padding:8px 16px;border-radius:8px;cursor:pointer}</style>'
                   + '</head><body><div class="demo-box"><h2>🎨 CSS Live Testbed</h2><p>Previewing <code>' + esc(state.activePath || "styles.css") + '</code> styles live.</p><button>Sample Button</button></div></body></html>';
      return;
    }

    // Check if standalone JavaScript file
    if (path.endsWith(".js") || path.endsWith(".ts")) {
      frame.removeAttribute("src");
      frame.srcdoc = '<!doctype html><html><head><meta charset="utf-8">'
                   + '<style>body{font-family:monospace;background:#0d1424;color:#78a9ff;padding:20px;margin:0}#console-log{background:#070b14;padding:16px;border-radius:8px;border:1px solid rgba(120,169,255,0.2);min-height:220px;white-space:pre-wrap}.log-line{padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.05)}.log-err{color:#f87171}</style>'
                   + '</head><body><h3 style="color:#fff;margin-top:0">⚡ Live JavaScript Console (' + esc(state.activePath || "script.js") + ')</h3><div id="console-log"></div>'
                   + '<script>'
                   + 'var logEl = document.getElementById("console-log");'
                   + 'function log(msg, isErr) { var d = document.createElement("div"); d.className = "log-line" + (isErr ? " log-err" : ""); d.textContent = (isErr ? "❌ " : "▶ ") + msg; logEl.appendChild(d); }'
                   + 'console.log = function() { var args = Array.prototype.slice.call(arguments); log(args.map(function(a){ return typeof a === "object" ? JSON.stringify(a) : a; }).join(" ")); };'
                   + 'console.error = function() { var args = Array.prototype.slice.call(arguments); log(args.map(function(a){ return typeof a === "object" ? JSON.stringify(a) : a; }).join(" "), true); };'
                   + 'window.onerror = function(m, u, l) { log(m + " (line " + l + ")", true); };'
                   + 'try { ' + content + ' } catch(e) { log(e.stack || e.message, true); }'
                   + '<\/script></body></html>';
      return;
    }

    // Default: Full HTML Live Document Rendering
    var processedContent = processHtmlForPreview(content, state.activePath, state.repo, state.branch);
    
    // Direct synchronous srcdoc assignment - works in all modern browsers with zero blob leaks
    frame.removeAttribute("src");
    frame.srcdoc = processedContent;
    frame.style.opacity = "1";
  }

  function processHtmlForPreview(html, activePath, repo, branch) {
    if (!html || !html.trim()) {
      return "<!doctype html><html><body style='background:#0f172a;color:#94a3b8;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0'><div style='text-align:center'><h3>👁️ Live Web Preview</h3><p>Enter HTML code in the editor or select a file to preview.</p></div></body></html>";
    }

    var processed = html;
    var dirPath = "";
    if (activePath && activePath.includes("/")) {
      dirPath = activePath.substring(0, activePath.lastIndexOf("/") + 1);
    }

    // Resolve relative assets using jsDelivr CDN (proper MIME types for CSS/images)
    if (repo && branch) {
      var cdnBase = "https://cdn.jsdelivr.net/gh/" + repo + "@" + branch + "/" + dirPath;

      // 1. Resolve relative CSS stylesheets
      processed = processed.replace(/<link([^>]+)href\s*=\s*["']([^"']+)["']([^>]*)>/gi, function(match, before, href, after) {
        if (href.startsWith("http://") || href.startsWith("https://") || href.startsWith("//") || href.startsWith("data:") || href.startsWith("#")) {
          return match;
        }
        var cleanHref = href.replace(/^\.\//, "");
        return '<link' + before + 'href="' + cdnBase + cleanHref + '"' + after + '>';
      });

      // 2. Resolve relative image sources
      processed = processed.replace(/<img([^>]+)src\s*=\s*["']([^"']+)["']([^>]*)>/gi, function(match, before, src, after) {
        if (src.startsWith("http://") || src.startsWith("https://") || src.startsWith("//") || src.startsWith("data:") || src.startsWith("#")) {
          return match;
        }
        var cleanSrc = src.replace(/^\.\//, "");
        return '<img' + before + 'src="' + cdnBase + cleanSrc + '"' + after + '>';
      });

      // 3. Resolve relative CSS background url(...)
      processed = processed.replace(/url\(["']?([^"')]+)["']?\)/gi, function(match, url) {
        if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("//") || url.startsWith("data:") || url.startsWith("#")) {
          return match;
        }
        var cleanUrl = url.replace(/^\.\//, "");
        return 'url("' + cdnBase + cleanUrl + '")';
      });
    }

    // Inject non-intrusive runtime error HUD inside preview iframe
    var errHudScript = '<script>'
      + 'window.addEventListener("error", function(e) {'
      + '  var b = document.getElementById("__studio_err_banner__");'
      + '  if (!b) {'
      + '    b = document.createElement("div");'
      + '    b.id = "__studio_err_banner__";'
      + '    b.style.cssText = "position:fixed;bottom:10px;left:10px;right:10px;background:rgba(239,68,68,0.92);color:#fff;padding:8px 14px;border-radius:8px;font-family:system-ui,monospace;font-size:12px;z-index:999999;box-shadow:0 4px 14px rgba(0,0,0,0.5);display:flex;justify-content:space-between;align-items:center;";'
      + '    (document.body || document.documentElement).appendChild(b);'
      + '  }'
      + '  b.innerHTML = "<span>⚠️ <b>Runtime Error:</b> " + (e.message || "Script execution error") + " (line " + (e.lineno || "?") + ")</span><button onclick=\'this.parentElement.remove()\' style=\'background:none;border:none;color:#fff;font-weight:bold;cursor:pointer;font-size:15px;padding:0 4px\'>✕</button>";'
      + '});'
      + '<\/script>';

    if (processed.includes("</body>")) {
      processed = processed.replace("</body>", errHudScript + "</body>");
    } else {
      processed += errHudScript;
    }

    return processed;
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
      alert("Successfully committed to GitHub! Commit SHA: " + (res.commit ? res.commit.sha.substring(0, 8) : "ok"));
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
    if (!this.value) {
      openGitHubAuthModal();
      return;
    }
    state.repo = this.value;
    state.activePath = "";
    $("delete-btn").style.display = "none";
    $("code-editor").value = "";
    markClean();
    api("/v1/github/target_repo", { method: "POST", body: { target_repo: state.repo } }).catch(function(){});
    loadProjectTree();
  };
  $("refresh-repo-btn").onclick = function() { loadRepositories(0); };

  // 12. Aux Tabs: Preview vs AI Assistant
  $("tab-btn-preview").onclick = function() {
    $("tab-btn-preview").classList.add("active");
    $("tab-btn-ai").classList.remove("active");
    $("view-preview").style.display = "flex";
    $("view-ai").style.display = "none";
    updatePreview();
  };
  $("tab-btn-ai").onclick = function() {
    $("tab-btn-ai").classList.add("active");
    $("tab-btn-preview").classList.remove("active");
    $("view-preview").style.display = "none";
    $("view-ai").style.display = "flex";
  };

  // Aux panel collapse & dock triggers (Fixed: cleanly clear wide/maximized classes upon minimize)
  function collapseAuxPanel() {
    var ws = $("workspace");
    if (!ws) return;
    ws.classList.add("preview-closed");
    ws.classList.remove("aux-expanded", "aux-maximized");
    var expLabel = $("expand-aux-label");
    if (expLabel) expLabel.textContent = "Widen";
  }

  var bCollapse = $("btn-collapse-aux");
  if (bCollapse) bCollapse.onclick = collapseAuxPanel;

  var bCloseHdr = $("btn-close-aux-header");
  if (bCloseHdr) bCloseHdr.onclick = collapseAuxPanel;

  var dockAi = $("dock-btn-ai");
  if (dockAi) {
    dockAi.onclick = function() {
      var ws = $("workspace");
      if (ws) ws.classList.remove("preview-closed");
      $("tab-btn-ai").click();
      var aiInput = $("ai-prompt");
      if (aiInput) setTimeout(function() { aiInput.focus(); }, 150);
    };
  }

  var dockPrev = $("dock-btn-preview");
  if (dockPrev) {
    dockPrev.onclick = function() {
      var ws = $("workspace");
      if (ws) ws.classList.remove("preview-closed");
      $("tab-btn-preview").click();
    };
  }

  var tPrev = $("toggle-preview-btn"); if (tPrev) tPrev.onclick = function() {
    var ws = $("workspace");
    if (ws.classList.contains("preview-closed")) {
      ws.classList.remove("preview-closed");
      $("tab-btn-preview").click();
    } else {
      ws.classList.add("preview-closed");
    }
  };
  $("refresh-preview-btn").onclick = updatePreview;

  // 13. Hashtag AI Co-Pilot integration
  $("ai-send-btn").onclick = sendAiPrompt;

  // Forward mouse wheel scrolling anywhere in the AI panel directly to the messages container
  var auxAiPanel = $("view-ai");
  var auxAiChat = $("ai-chat");
  if (auxAiPanel && auxAiChat) {
    auxAiPanel.addEventListener("wheel", function(e) {
      if (e.target && e.target.id === "ai-prompt") return;
      if (e.target && e.target.closest && e.target.closest("pre")) {
        var preEl = e.target.closest("pre");
        if (preEl.scrollHeight > preEl.clientHeight && Math.abs(e.deltaY) > 0) return;
      }
      auxAiChat.scrollTop += e.deltaY;
    }, { passive: true });
  }
  $("ai-prompt").onkeydown = function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendAiPrompt();
    }
  };

  // --- CODE BEAUTIFIER / FORMATTER ---
  function formatCurrentCode() {
    var editor = $("code-editor");
    var code = editor.value;
    if (!code.trim()) return;

    var ext = (state.activePath || "").split(".").pop().toLowerCase();
    var formatted = code;

    if (ext === "html" || ext === "htm" || (!ext && code.includes("<html"))) {
      formatted = formatHtml(code);
    } else if (ext === "json") {
      try { formatted = JSON.stringify(JSON.parse(code), null, 2); } catch(e) {}
    } else {
      formatted = formatHtml(code);
    }

    if (formatted !== code) {
      editor.value = formatted;
      markDirty();
      updateLineNumbers();
      updatePreview();
    }
  }

  function formatHtml(html) {
    var tab = "  ";
    var result = "";
    var indent = 0;
    var clean = html.replace(/>\\s*</g, ">\n<").trim();
    var lines = clean.split("\n");

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();
      if (!line) continue;

      if (line.match(/^<\/[^>]+>/)) {
        indent = Math.max(0, indent - 1);
      }

      var pad = "";
      for (var s = 0; s < indent; s++) pad += tab;
      result += pad + line + "\n";

      if (line.match(/^<[^\/!][^>]*[^\/]>/) && 
          !line.match(/<(area|base|br|col|embed|hr|img|input|link|meta|param|source|track|wbr)/i) &&
          !line.match(/^<([^>]+)>.*<\/\1>$/)) {
        indent++;
      }
    }
    return result.trim();
  }

  $("btn-format-code").onclick = formatCurrentCode;

  // --- WORD WRAP TOGGLE (With guaranteed horizontal scroll when OFF) ---
  var isWrapped = false;
  $("btn-toggle-wrap").onclick = function() {
    isWrapped = !isWrapped;
    var editor = $("code-editor");
    if (isWrapped) {
      editor.setAttribute("wrap", "soft");
      editor.style.whiteSpace = "pre-wrap";
      editor.style.wordBreak = "break-word";
      editor.style.overflowWrap = "break-word";
      editor.style.overflowX = "hidden";
      this.textContent = "Wrap: ON";
      this.style.color = "var(--accent)";
    } else {
      editor.setAttribute("wrap", "off");
      editor.style.whiteSpace = "pre";
      editor.style.wordBreak = "normal";
      editor.style.overflowWrap = "normal";
      editor.style.overflowX = "auto";
      this.textContent = "Wrap: OFF";
      this.style.color = "";
    }
  };

  // --- RESPONSIVE DEVICE PREVIEW CONTROLS ---
  var currentDevice = "desktop";
  var isLandscape = false;

  function setPreviewDevice(device) {
    currentDevice = device;
    var holder = $("preview-frame-holder");
    holder.className = "preview-frame-holder";

    $("dev-desktop").classList.remove("active");
    $("dev-tablet").classList.remove("active");
    $("dev-mobile").classList.remove("active");

    if (device === "desktop") {
      $("dev-desktop").classList.add("active");
      $("preview-dim-badge").textContent = "100% Fluid";
      // Reset landscape for desktop
      isLandscape = false;
      $("dev-rotate").classList.remove("active");
      $("dev-rotate").style.color = "";
    } else if (device === "tablet") {
      $("dev-tablet").classList.add("active");
      holder.classList.add("device-tablet");
      if (isLandscape) holder.classList.add("landscape");
      $("preview-dim-badge").textContent = isLandscape ? "1024 × 768 · Tablet" : "768 × 1024 · Tablet";
      $("dev-rotate").classList.toggle("active", isLandscape);
      $("dev-rotate").style.color = isLandscape ? "var(--accent)" : "";
    } else if (device === "mobile") {
      $("dev-mobile").classList.add("active");
      holder.classList.add("device-mobile");
      if (isLandscape) holder.classList.add("landscape");
      $("preview-dim-badge").textContent = isLandscape ? "812 × 375 · Mobile" : "375 × 812 · Mobile";
      $("dev-rotate").classList.toggle("active", isLandscape);
      $("dev-rotate").style.color = isLandscape ? "var(--accent)" : "";
    }
  }

  $("dev-desktop").onclick = function() { setPreviewDevice("desktop"); };
  $("dev-tablet").onclick = function() { setPreviewDevice("tablet"); };
  $("dev-mobile").onclick = function() { setPreviewDevice("mobile"); };
  $("dev-rotate").onclick = function() {
    if (currentDevice === "desktop") return;
    isLandscape = !isLandscape;
    setPreviewDevice(currentDevice);
    // Update rotate button visual state
    if (isLandscape) {
      $("dev-rotate").classList.add("active");
      $("dev-rotate").style.color = "var(--accent)";
    } else {
      $("dev-rotate").classList.remove("active");
      $("dev-rotate").style.color = "";
    }
  };

  // --- STUDIO CO-PILOT CHAT & MARKDOWN ---
  function renderStudioMarkdown(md) {
    if (!md) return "";
    var html = esc(md);
    var codeBlockIdx = 0;
    html = html.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, function(m, lang, code) {
      var id = "copilot_code_" + (++codeBlockIdx);
      var rawCode = code.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
      window["_codeBlock_" + id] = rawCode;
      return '<div style="background:rgba(0,0,0,0.45);border:1px solid var(--border);border-radius:8px;margin:8px 0;overflow:hidden">' +
             '<div style="background:rgba(255,255,255,0.06);padding:4px 10px;display:flex;justify-content:space-between;align-items:center">' +
             '<span style="font-size:10px;color:var(--muted);text-transform:uppercase;font-weight:600">' + (lang || 'code') + '</span>' +
             '<div style="display:flex;gap:6px">' +
             '<button class="btn" style="padding:2px 8px;font-size:10.5px" onclick="copyStudioSnippet(\'' + id + '\', this)">Copy</button>' +
             '<button class="btn btn-primary" style="padding:2px 8px;font-size:10.5px" onclick="applySnippetToEditor(\'' + id + '\')">⚡ Apply to Editor</button>' +
             '</div></div>' +
             '<pre style="padding:10px 12px;margin:0;overflow-x:auto;font-family:monospace;font-size:11.5px"><code id="' + id + '">' + code + '</code></pre></div>';
    });
    html = html.replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.08);padding:1px 5px;border-radius:4px;font-family:monospace">$1</code>');
    html = html.replace(/\*\*([^\*]+)\*\*/g, '<b>$1</b>');
    html = html.replace(/\n/g, '<br>');
    return html;
  }

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
    botBubble.innerHTML = '<span class="spinner"></span> Hashtag AI is analyzing & generating...';
    chat.appendChild(botBubble);
    chat.scrollTop = chat.scrollHeight;

    var activeCode = $("code-editor").value;
    api("/v1/console/request", {
      method: "POST",
      body: {
        request: txt,
        message: txt,
        body_id: "cloud-studio",
        context: {
          target_repo: state.repo,
          repository: state.repo,
          active_path: state.activePath,
          active_file: state.activePath,
          file_content: activeCode
        }
      }
    }).then(function(res) {
      var summary = "✓ Done! Hashtag processed the request.";
      if (res.response) summary = res.response;
      else if (res.plan && res.plan.message) summary = res.plan.message;
      else if (res.execution && res.execution.result) {
        var r = res.execution.result;
        if (typeof r.text === "string") summary = r.text;
        else if (r.message) summary = r.message;
      }
      botBubble.innerHTML = '<b>Hashtag AI Co-Pilot:</b><br><br>' + renderStudioMarkdown(summary);
      chat.scrollTop = chat.scrollHeight;
      loadProjectTree();
    }).catch(function(err) {
      botBubble.innerHTML = '<span style="color:var(--danger)">Error: ' + esc(err.message) + '</span>';
      chat.scrollTop = chat.scrollHeight;
    });
  }


  // Fullscreen Preview Handlers
  var fullscreenState = {
    isFullscreen: false,
    toolbarHideTimer: null
  };

  function updateFullscreenButtons(isFullscreen) {
    var fBtn = $("preview-fullscreen-btn");
    var nBtn = $("nav-fullscreen-btn");
    if (fBtn) {
      fBtn.textContent = isFullscreen ? "✕ Exit" : "⛶ Fullscreen";
      fBtn.style.color = isFullscreen ? "var(--danger)" : "";
    }
    if (nBtn) {
      nBtn.textContent = isFullscreen ? "✕ Exit Fullscreen" : "⛶ Fullscreen";
      nBtn.style.color = isFullscreen ? "var(--danger)" : "#38bdf8";
    }
  }

  function enterFullscreen() {
    var prev = $("view-preview");
    if (!prev) return;
    
    // Ensure preview pane is open and active
    var ws = $("workspace");
    if (ws) ws.classList.remove("preview-closed");
    $("tab-btn-preview").classList.add("active");
    $("tab-btn-ai").classList.remove("active");
    $("view-preview").style.display = "flex";
    $("view-ai").style.display = "none";
    updatePreview();
    

    var req = prev.requestFullscreen || prev.webkitRequestFullscreen || prev.mozRequestFullScreen || prev.msRequestFullscreen;
    if (req) {
      req.call(prev).then(function() {
        fullscreenState.isFullscreen = true;
        prev.classList.add("is-fullscreen");
        updateFullscreenButtons(true);
      }).catch(function(err) {
        console.warn("Native fullscreen failed, fallback to CSS fullscreen:", err);
        fallbackFullscreen();
      });
    } else {
      fallbackFullscreen();
    }
  }

  function fallbackFullscreen() {
    var prev = $("view-preview");
    fullscreenState.isFullscreen = true;
    if (prev) prev.classList.add("is-fullscreen");
    updateFullscreenButtons(true);
  }

  function exitFullscreen() {
    var prev = $("view-preview");
    var exit = document.exitFullscreen || document.webkitExitFullscreen || document.mozCancelFullScreen || document.msExitFullscreen;
    if (document.fullscreenElement && exit) {
      exit.call(document).then(function() {
        cleanupFullscreen();
      
      }).catch(function() {
        cleanupFullscreen();
      
      });
    } else {
      cleanupFullscreen();
      
    }
  }

  function cleanupFullscreen() {
    var prev = $("view-preview");
    fullscreenState.isFullscreen = false;
    if (prev) {
      prev.classList.remove("is-fullscreen");
    }
    updateFullscreenButtons(false);
  }

  function toggleFullscreen() {
    var prev = $("view-preview");
    var body = document.body;
    var isFs = body.classList.contains("has-preview-fullscreen");

    if (isFs) {
      body.classList.remove("has-preview-fullscreen");
      if (prev) prev.classList.remove("is-fullscreen");
      fullscreenState.isFullscreen = false;
      updateFullscreenButtons(false);
      try {
        if (document.fullscreenElement) {
          (document.exitFullscreen || document.webkitExitFullscreen).call(document);
        }
      } catch(e) {}
    } else {
      var ws = $("workspace");
      if (ws) ws.classList.remove("preview-closed");
      $("tab-btn-preview").click();

      body.classList.add("has-preview-fullscreen");
      if (prev) prev.classList.add("is-fullscreen");
      fullscreenState.isFullscreen = true;
      updateFullscreenButtons(true);
      try {
        if (prev && prev.requestFullscreen) {
          prev.requestFullscreen().catch(function(){});
        }
      } catch(e) {}
    }
    
  }

  function enterFullscreen() {
    if (!fullscreenState.isFullscreen) toggleFullscreen();
  }

  function exitFullscreen() {
    if (fullscreenState.isFullscreen) toggleFullscreen();
  }

  document.addEventListener("fullscreenchange", function() {
    if (!document.fullscreenElement && fullscreenState.isFullscreen) {
      cleanupFullscreen();
      
    }
  });

  document.addEventListener("keydown", function(e) {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT") return;
    if (e.key === "f" || e.key === "F") {
      e.preventDefault();
      toggleFullscreen();
    } else if (e.key === "Escape" && fullscreenState.isFullscreen) {
      exitFullscreen();
    }
  });

  $("preview-fullscreen-btn").onclick = toggleFullscreen;
  var navFs = $("nav-fullscreen-btn");
  if (navFs) navFs.onclick = toggleFullscreen;

  // Pop-out preview - clean new tab launch
  $("preview-popout-btn").onclick = function() {
    var content = $("code-editor").value || "<!DOCTYPE html><html><body><h1>No preview content</h1></body></html>";
    var processed = processHtmlForPreview(content, state.activePath, state.repo, state.branch);
    var blob = new Blob([processed], { type: "text/html; charset=utf-8" });
    var url = URL.createObjectURL(blob);
    window.open(url, "_blank");
  };

  window.copyStudioSnippet = function(id, btn) {
    var code = window["_codeBlock_" + id];
    if (!code) {
      var el = $(id);
      code = el ? (el.innerText || el.textContent) : "";
    }
    navigator.clipboard.writeText(code).then(function() {
      var orig = btn.textContent;
      btn.textContent = "Copied!";
      btn.style.color = "#3fb950";
      setTimeout(function() { btn.textContent = orig; btn.style.color = ""; }, 2000);
    });
  };

  window.applySnippetToEditor = function(id) {
    var code = window["_codeBlock_" + id];
    if (!code) {
      var el = $(id);
      code = el ? (el.innerText || el.textContent) : "";
    }
    if (code) {
      $("code-editor").value = code;
      markDirty();
      updateLineNumbers();
      updatePreview();
      alert("✓ Applied code directly into the editor!");
    }
  };

  // Expose processHtmlForPreview globally for popout button
  window.processHtmlForPreview = processHtmlForPreview;

  // Cleanup blob URLs on page unload
  window.addEventListener("beforeunload", function() {
    if (previewBlobUrl) {
      URL.revokeObjectURL(previewBlobUrl);
    }
  });


  // --- GITHUB AUTH MODAL LOGIC ---
  function openGitHubAuthModal() {
    var modal = $("github-auth-modal");
    if (!modal) return;
    var currentToken = localStorage.getItem("hashtag_studio_gh_token") || "";
    var tokenInput = $("gh-token-input");
    if (tokenInput) tokenInput.value = currentToken;
    $("gh-auth-error").style.display = "none";
    
    if (currentToken) {
      $("gh-auth-status-pill").textContent = "Validating...";
      $("disconnect-gh-btn").style.display = "inline-flex";
      api("/v1/github/status").then(function(d) {
        if (d && d.connected) {
          $("gh-auth-status-pill").textContent = "Connected";
          $("gh-auth-status-pill").style.color = "#3fb950";
          $("gh-profile-card").style.display = "flex";
          $("gh-avatar-img").src = d.avatar_url || "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png";
          $("gh-user-name").textContent = d.name || d.username;
          $("gh-user-login").textContent = "@" + d.username;
        } else {
          $("gh-auth-status-pill").textContent = "Invalid Token";
          $("gh-auth-status-pill").style.color = "var(--danger)";
          $("gh-profile-card").style.display = "none";
        }
      }).catch(function() {
        $("gh-auth-status-pill").textContent = "Saved";
        $("gh-profile-card").style.display = "none";
      });
    } else {
      $("gh-auth-status-pill").textContent = "Not Connected";
      $("gh-auth-status-pill").style.color = "var(--muted)";
      $("gh-profile-card").style.display = "none";
      $("disconnect-gh-btn").style.display = "none";
    }
    modal.classList.add("open");
  }

  function closeGitHubAuthModal() {
    var modal = $("github-auth-modal");
    if (modal) modal.classList.remove("open");
  }

  function saveGitHubToken() {
    var val = ($("gh-token-input").value || "").trim();
    if (!val) {
      var err = $("gh-auth-error");
      err.textContent = "Please enter your GitHub Personal Access Token.";
      err.style.display = "block";
      return;
    }
    localStorage.setItem("hashtag_studio_gh_token", val);
    $("gh-auth-error").style.display = "none";
    $("save-gh-token-btn").textContent = "Connecting...";
    
    api("/v1/github/status").then(function(d) {
      $("save-gh-token-btn").textContent = "Connect Token";
      if (d && d.connected) {
        updateGitHubNavBadge(d);
        closeGitHubAuthModal();
        loadRepositories(0);
      } else {
        var err = $("gh-auth-error");
        err.textContent = "GitHub rejected this token. Check token scope & validity.";
        err.style.display = "block";
      }
    }).catch(function(e) {
      $("save-gh-token-btn").textContent = "Connect Token";
      var err = $("gh-auth-error");
      err.textContent = "Error: " + (e.message || "Failed validating token");
      err.style.display = "block";
    });
  }

  function disconnectGitHub() {
    localStorage.removeItem("hashtag_studio_gh_token");
    localStorage.removeItem("hashtag_cached_repos");
    $("gh-token-input").value = "";
    closeGitHubAuthModal();
    loadRepositories(0);
  }

  var bGh = $("btn-gh-account");
  if (bGh) bGh.onclick = openGitHubAuthModal;
  var sGh = $("sidebar-gh-btn");
  if (sGh) sGh.onclick = openGitHubAuthModal;
  $("cancel-gh-auth-btn").onclick = closeGitHubAuthModal;
  $("save-gh-token-btn").onclick = saveGitHubToken;
  $("disconnect-gh-btn").onclick = disconnectGitHub;
  var bBrowser = $("gh-browser-auth-btn");
  if (bBrowser) {
    bBrowser.onclick = function() {
      var url = "https://github.com/settings/tokens/new?scopes=repo,read:user&description=Hashtag+Studio+Token";
      window.open(url, "_blank");
    };
  }
  var bPaste = $("gh-paste-token-btn");
  if (bPaste) {
    bPaste.onclick = function() {
      if (navigator.clipboard && navigator.clipboard.readText) {
        navigator.clipboard.readText().then(function(text) {
          text = (text || "").trim();
          if (text) {
            $("gh-token-input").value = text;
            saveGitHubToken();
          }
        }).catch(function() {
          $("gh-token-input").focus();
        });
      } else {
        $("gh-token-input").focus();
      }
    };
  }
  $("gh-toggle-token-btn").onclick = function() {
    var input = $("gh-token-input");
    if (input.type === "password") {
      input.type = "text";
      this.textContent = "Hide";
    } else {
      input.type = "password";
      this.textContent = "Show";
    }
  };

  // File search live filtering
  var searchInput = $("file-search");
  if (searchInput) {
    searchInput.addEventListener("input", function() {
      renderFileTree(state.tree);
    });
    searchInput.addEventListener("keydown", function(e) {
      if (e.key === "Escape") {
        this.value = "";
        renderFileTree(state.tree);
      }
    });
  }
  var clearSearchBtn = $("clear-search-btn");
  if (clearSearchBtn) {
    clearSearchBtn.onclick = function() {
      if (searchInput) {
        searchInput.value = "";
        searchInput.focus();
      }
      renderFileTree(state.tree);
    };
  }

  // Aux panel expand / widen handler (allows comfortable reading of AI outputs)
  var auxExpandState = 0;
  var expandBtn = $("btn-expand-aux");
  if (expandBtn) {
    expandBtn.onclick = function() {
      var ws = $("workspace");
      if (!ws) return;
      auxExpandState = (auxExpandState + 1) % 3;
      ws.classList.remove("aux-expanded", "aux-maximized", "preview-closed");
      var label = $("expand-aux-label");
      var icon = $("expand-aux-icon");
      if (auxExpandState === 1) {
        ws.classList.add("aux-expanded");
        if (label) label.textContent = "Maximize";
        if (icon) icon.textContent = "⛶";
        expandBtn.title = "Maximize panel across screen";
      } else if (auxExpandState === 2) {
        ws.classList.add("aux-maximized");
        if (label) label.textContent = "Restore";
        if (icon) icon.textContent = "✕";
        expandBtn.title = "Restore normal panel size";
      } else {
        if (label) label.textContent = "Widen";
        if (icon) icon.textContent = "⛶";
        expandBtn.title = "Widen panel to 650px";
      }
      
    };
  }

  // Init
  loadRepositories();
  updatePreview();

  // ========================================================
  // --- CYBER EYE ENGINE (EXACTLY 2 EYES: PREVIEW TAB EYE & DOCK BUTTON EYE) ---
  (function initCyberEyeEngine() {
    var eyes = [
      { id: "eye-tab", el: $("eye-tab"), iris: null },
      { id: "eye-dock", el: $("eye-dock"), iris: null }
    ];

    eyes.forEach(function(e) {
      if (e.el) {
        e.iris = e.el.querySelector(".eye-iris");
      }
    });

    var isTyping = false;
    var typingTimer = null;
    var lastMouseX = window.innerWidth / 2;
    var lastMouseY = window.innerHeight / 2;

    // 1. Natural Blinking Loop
    function scheduleBlink() {
      var nextBlink = 2200 + Math.random() * 3800;
      setTimeout(function() {
        triggerBlink();
        scheduleBlink();
      }, nextBlink);
    }

    function triggerBlink(doubleBlink) {
      eyes.forEach(function(e) { if (e.el) e.el.classList.add("blinking"); });
      setTimeout(function() {
        eyes.forEach(function(e) { if (e.el) e.el.classList.remove("blinking"); });
        if (doubleBlink || Math.random() < 0.2) {
          setTimeout(function() {
            eyes.forEach(function(e) { if (e.el) e.el.classList.add("blinking"); });
            setTimeout(function() {
              eyes.forEach(function(e) { if (e.el) e.el.classList.remove("blinking"); });
            }, 80);
          }, 110);
        }
      }, 90);
    }

    scheduleBlink();

    // 2. Coordinate Tracker: looks towards (targetX, targetY)
    function lookAt(targetX, targetY) {
      eyes.forEach(function(e) {
        if (!e.iris || !e.el) return;

        var rect = e.el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) return;

        var eyeX = rect.left + rect.width / 2;
        var eyeY = rect.top + rect.height / 2;

        var dx = targetX - eyeX;
        var dy = targetY - eyeY;
        var dist = Math.hypot(dx, dy);
        var angle = Math.atan2(dy, dx);

        var isDock = (e.id === "eye-dock");
        var maxTravelX = isDock ? 5.5 : 4.0;
        var maxTravelY = isDock ? 3.5 : 2.5;
        var scale = Math.min(dist / 50, 1);

        var moveX = Math.cos(angle) * maxTravelX * scale;
        var moveY = Math.sin(angle) * maxTravelY * scale;

        e.iris.style.transform = "translate(" + moveX.toFixed(2) + "px, " + moveY.toFixed(2) + "px)";
      });
    }

    // 3. Mouse Move Tracking (Anywhere on Page)
    document.addEventListener("mousemove", function(e) {
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
      if (!isTyping) {
        lookAt(e.clientX, e.clientY);
      }
    }, { passive: true });

    // 4. Code Editor Typing Tracker (Locks gaze directly on editor)
    var editor = $("code-editor");
    if (editor) {
      function onEditorActivity() {
        isTyping = true;
        clearTimeout(typingTimer);

        var edRect = editor.getBoundingClientRect();
        var targetX = edRect.left + Math.min(edRect.width * 0.35, 300);
        var targetY = edRect.top + Math.min(edRect.height * 0.4, 250);

        lookAt(targetX, targetY);

        typingTimer = setTimeout(function() {
          isTyping = false;
          lookAt(lastMouseX, lastMouseY);
        }, 1200);
      }

      editor.addEventListener("input", onEditorActivity, { passive: true });
      editor.addEventListener("keydown", function(e) {
        if (e.key && (e.key.length === 1 || e.key === "Backspace" || e.key === "Enter")) {
          onEditorActivity();
        }
      }, { passive: true });
    }

    // 5. Idle Autonomous Wander
    setInterval(function() {
      if (isTyping) return;
      if (Math.random() < 0.28) {
        var wanderX = lastMouseX + (Math.random() - 0.5) * 220;
        var wanderY = lastMouseY + (Math.random() - 0.5) * 160;
        lookAt(wanderX, wanderY);
        setTimeout(function() {
          if (!isTyping) lookAt(lastMouseX, lastMouseY);
        }, 900);
      }
    }, 3000);
  })();

})();
</script>
</body>
</html>
"""
