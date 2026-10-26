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
    /* === STUDIO DUAL-MODE VIEWPORT SLIDER (GitHub Cloud Studio <-> PC Cloud Studio) === */
    html, body {
      margin: 0;
      padding: 0;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      background: #070b14;
    }
    .studio-viewport-stage {
      position: relative;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }
    .studio-slider {
      display: flex;
      flex-direction: row;
      flex-wrap: nowrap;
      width: 200vw;
      height: 100vh;
      transform: translate3d(0, 0, 0);
      transition: transform 0.48s cubic-bezier(0.16, 1, 0.3, 1);
      will-change: transform;
    }
    body.mode-pc .studio-slider {
      transform: translate3d(-100vw, 0, 0);
    }
    .studio-page {
      width: 100vw;
      height: 100vh;
      flex-shrink: 0;
      overflow: hidden;
      position: relative;
    }
    /* Mode switcher buttons */
    .btn-switch-mode {
      border-color: rgba(56, 189, 248, 0.5) !important;
      color: #38bdf8 !important;
      background: rgba(56, 189, 248, 0.08) !important;
      font-size: 11px !important;
      font-weight: 700 !important;
      display: inline-flex !important;
      align-items: center !important;
      gap: 6px !important;
      padding: 3px 10px !important;
      border-radius: 6px !important;
      cursor: pointer !important;
      transition: all 0.2s ease !important;
      user-select: none !important;
    }
    .btn-switch-mode:hover {
      background: rgba(56, 189, 248, 0.2) !important;
      color: #fff !important;
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.4) !important;
      transform: translateY(-1px);
    }
    .btn-switch-mode.gh-mode-btn {
      border-color: rgba(168, 85, 247, 0.5) !important;
      color: #c084fc !important;
      background: rgba(168, 85, 247, 0.08) !important;
    }
    .btn-switch-mode.gh-mode-btn:hover {
      background: rgba(168, 85, 247, 0.2) !important;
      color: #fff !important;
      box-shadow: 0 0 12px rgba(168, 85, 247, 0.4) !important;
    }
    /* Dock buttons for PC / GH mode switching */
    .aux-dock-btn.dock-pc {
      border-color: rgba(56, 189, 248, 0.6);
      color: #38bdf8;
      background: linear-gradient(135deg, rgba(13, 20, 36, 0.95), rgba(15, 23, 42, 0.98));
    }
    .aux-dock-btn.dock-pc:hover {
      border-color: #7dd3fc;
      color: #fff;
      box-shadow: 0 6px 22px rgba(56, 189, 248, 0.5), 0 0 16px rgba(56, 189, 248, 0.6);
      transform: scale(1.12);
    }
    .aux-dock-btn.dock-gh {
      border-color: rgba(168, 85, 247, 0.6);
      color: #c084fc;
      background: linear-gradient(135deg, rgba(20, 13, 36, 0.95), rgba(15, 23, 42, 0.98));
    }
    .aux-dock-btn.dock-gh:hover {
      border-color: #d8b4fe;
      color: #fff;
      box-shadow: 0 6px 22px rgba(168, 85, 247, 0.5), 0 0 16px rgba(168, 85, 247, 0.6);
      transform: scale(1.12);
    }
    /* PC Theme accents */
    .pc-badge {
      background: linear-gradient(135deg, rgba(56,189,248,0.25), rgba(168,85,247,0.25)) !important;
      border: 1px solid rgba(56,189,248,0.5) !important;
      color: #7dd3fc !important;
    }
    .pc-save-btn {
      background: linear-gradient(135deg, #0284c7, #2563eb) !important;
      border-color: #38bdf8 !important;
      color: #fff !important;
    }
    .pc-save-btn:hover {
      box-shadow: 0 0 14px rgba(56,189,248,0.5) !important;
    }

    /* PC Breadcrumbs */
    .pc-breadcrumbs-bar {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 12px;
      background: rgba(255, 255, 255, 0.02);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 11px;
      overflow-x: auto;
      white-space: nowrap;
      scrollbar-width: none;
    }
    .pc-breadcrumbs-bar::-webkit-scrollbar { display: none; }
    .pc-crumb-item {
      color: #94a3b8;
      cursor: pointer;
      padding: 2px 4px;
      border-radius: 4px;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 3px;
    }
    .pc-crumb-item:hover {
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.12);
    }
    .pc-crumb-sep {
      color: #475569;
      font-size: 10px;
    }

    /* Context Menu */
    .studio-context-menu {
      position: fixed;
      background: rgba(13, 20, 36, 0.98);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 8px;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.8), 0 0 20px rgba(56, 189, 248, 0.25);
      padding: 5px 0;
      min-width: 230px;
      z-index: 99999999;
      user-select: none;
      font-size: 12px;
      animation: ctxFadeIn 0.12s ease-out;
    }
    @keyframes ctxFadeIn {
      from { opacity: 0; transform: scale(0.96); }
      to { opacity: 1; transform: scale(1); }
    }
    .ctx-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 14px;
      color: #edf4ff;
      cursor: pointer;
      transition: background 0.12s, color 0.12s;
    }
    .ctx-item:hover {
      background: rgba(56, 189, 248, 0.18);
      color: #38bdf8;
    }
    .ctx-item.transfer-action {
      font-weight: 700;
      color: #7dd3fc;
      background: rgba(56, 189, 248, 0.08);
    }
    .ctx-item.transfer-action:hover {
      background: rgba(56, 189, 248, 0.25);
      color: #fff;
    }
    .ctx-divider {
      height: 1px;
      background: rgba(255, 255, 255, 0.08);
      margin: 4px 0;
    }

    /* Native Elements & Select Theme Perfection (Image 4 Dark Mode) */
    html, body {
      color-scheme: dark !important;
    }
    select, option, optgroup {
      color-scheme: dark !important;
      background-color: #0b1120 !important;
      color: #e2e8f0 !important;
    }
    .repo-select-wrap select {
      color-scheme: dark !important;
      background: transparent;
      border: none;
      color: var(--text);
      font-size: 12px;
      font-weight: 600;
      outline: none;
      cursor: pointer;
      padding: 4px 6px;
      max-width: 220px;
    }
    .repo-select-wrap select option {
      background-color: #090e1a !important;
      color: #e2e8f0 !important;
      padding: 8px 10px;
    }

        /* User Auth & Plan Badges */
    .plan-badge {
      font-size: 10px !important;
      font-weight: 800 !important;
      padding: 2px 7px !important;
      border-radius: 999px !important;
      text-transform: uppercase !important;
      letter-spacing: 0.04em !important;
      line-height: 1 !important;
    }
    .plan-badge.free {
      background: rgba(148, 163, 184, 0.15) !important;
      color: #94a3b8 !important;
      border: 1px solid rgba(148, 163, 184, 0.3) !important;
    }
    .plan-badge.pro {
      background: rgba(56, 189, 248, 0.15) !important;
      color: #38bdf8 !important;
      border: 1px solid rgba(56, 189, 248, 0.4) !important;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.25) !important;
    }
    .plan-badge.lifetime {
      background: linear-gradient(135deg, #f59e0b, #eab308) !important;
      color: #000 !important;
      font-weight: 900 !important;
      box-shadow: 0 0 12px rgba(245, 158, 11, 0.4) !important;
    }
    .btn-upgrade-pill {
      background: linear-gradient(135deg, #f59e0b, #d97706) !important;
      color: #000 !important;
      font-weight: 800 !important;
      border: none !important;
      padding: 3px 10px !important;
      border-radius: 999px !important;
      box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3) !important;
      cursor: pointer !important;
      font-size: 11px !important;
      display: inline-flex !important;
      align-items: center !important;
      gap: 4px !important;
    }
    .btn-upgrade-pill:hover {
      filter: brightness(1.1) !important;
      transform: translateY(-1px) !important;
    }

    /* Navbar Active File Title Scrollable (Image 1: Prevent Displacing Buttons) */
    .nav-center {
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 10px !important;
      flex: 0 1 auto !important;
      max-width: 380px !important;
      min-width: 0 !important;
      overflow: hidden !important;
    }
    #active-file-title,
    #pc-active-file-title {
      font-size: 12px !important;
      font-weight: 700 !important;
      color: var(--text) !important;
      display: flex !important;
      align-items: center !important;
      gap: 6px !important;
      max-width: 360px !important;
      min-width: 0 !important;
      overflow-x: auto !important;
      overflow-y: hidden !important;
      white-space: nowrap !important;
      flex-shrink: 1 !important;
      scrollbar-width: thin !important;
      scrollbar-color: rgba(56, 189, 248, 0.4) transparent !important;
      padding-bottom: 2px !important;
    }
    #active-file-title span,
    #pc-active-file-title span {
      white-space: nowrap !important;
      flex-shrink: 0 !important;
    }
    #active-file-title::-webkit-scrollbar,
    #pc-active-file-title::-webkit-scrollbar {
      height: 3px !important;
    }
    #active-file-title::-webkit-scrollbar-track,
    #pc-active-file-title::-webkit-scrollbar-track {
      background: transparent !important;
    }
    #active-file-title::-webkit-scrollbar-thumb,
    #pc-active-file-title::-webkit-scrollbar-thumb {
      background: rgba(56, 189, 248, 0.4) !important;
      border-radius: 3px !important;
    }

    /* True Fullscreen Overlay (Image 2: Hide Entire Workspace & Surrounding Controls) */
    body.has-preview-fullscreen .studio-statusbar,
    body.has-preview-fullscreen .studio-header,
    body.has-preview-fullscreen .studio-dock,
    body.has-preview-fullscreen .studio-sidebar,
    body.has-preview-fullscreen .studio-workspace,
    body.has-preview-fullscreen .editor-panel,
    body.has-preview-fullscreen .sidebar-panel,
    body.has-preview-fullscreen .code-editor-main {
      display: none !important;
    }

    .preview-container.is-fullscreen {
      position: fixed !important;
      inset: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      z-index: 99999999 !important;
      background: #070b14 !important;
      box-sizing: border-box !important;
      display: flex !important;
      flex-direction: column !important;
      overflow: hidden !important;
    }
    .preview-container.is-fullscreen .preview-toolbar {
      position: fixed !important;
      top: 14px !important;
      left: 50% !important;
      transform: translateX(-50%) !important;
      z-index: 100000000 !important;
      background: rgba(13, 20, 36, 0.95) !important;
      backdrop-filter: blur(12px) !important;
      border: 1px solid rgba(56, 189, 248, 0.35) !important;
      border-radius: 9999px !important;
      padding: 6px 16px !important;
      box-shadow: 0 12px 36px rgba(0,0,0,0.8) !important;
      width: auto !important;
      gap: 12px !important;
    }
    .preview-container.is-fullscreen .preview-viewport-wrap {
      flex: 1 1 0% !important;
      width: 100vw !important;
      height: 100vh !important;
      max-height: 100vh !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      background: #070b14 !important;
      padding: 68px 16px 24px 16px !important;
      box-sizing: border-box !important;
      overflow: auto !important;
    }

    /* Fluid Responsive Device Frames (Image 2: Device height constrained to viewport - no bottom cutoff) */
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
      height: min(1024px, calc(100vh - 110px)) !important;
      max-height: calc(100% - 10px) !important;
      aspect-ratio: 768 / 1024 !important;
      width: auto !important;
      max-width: min(768px, calc(100% - 24px)) !important;
      border-radius: 20px !important;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7), 0 0 0 10px #1e293b, 0 0 0 11px rgba(255,255,255,0.15) !important;
      overflow: hidden !important;
      margin: auto !important;
      box-sizing: border-box !important;
    }
    .preview-frame-holder.landscape.device-tablet {
      height: min(768px, calc(100vh - 110px)) !important;
      max-height: calc(100% - 10px) !important;
      aspect-ratio: 1024 / 768 !important;
      width: auto !important;
      max-width: min(1024px, calc(100% - 24px)) !important;
    }
    .preview-frame-holder.device-mobile {
      height: min(812px, calc(100vh - 110px)) !important;
      max-height: calc(100% - 10px) !important;
      aspect-ratio: 375 / 812 !important;
      width: auto !important;
      max-width: min(375px, calc(100% - 24px)) !important;
      border-radius: 28px !important;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7), 0 0 0 10px #1e293b, 0 0 0 11px rgba(255,255,255,0.15) !important;
      overflow: hidden !important;
      margin: auto !important;
      box-sizing: border-box !important;
    }
    .preview-frame-holder.landscape.device-mobile {
      height: min(375px, calc(100vh - 110px)) !important;
      max-height: calc(100% - 10px) !important;
      aspect-ratio: 812 / 375 !important;
      width: auto !important;
      max-width: min(812px, calc(100% - 24px)) !important;
    }
    .preview-container.is-fullscreen .preview-frame-holder:not(.device-tablet):not(.device-mobile) {
      width: 100% !important;
      height: 100% !important;
      max-width: 100% !important;
      max-height: 100% !important;
      border-radius: 0 !important;
      box-shadow: none !important;
      border: none !important;
    }

    /* Aux Panel & Visible Divider Collapse Button (Images 1 & 3) */
    .aux-panel {
      background: var(--panel);
      border-left: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      height: 100% !important;
      max-height: 100% !important;
      min-height: 0 !important;
      min-width: 0;
      overflow: visible !important;
      position: relative !important;
      box-sizing: border-box;
    }
    .aux-collapse-btn {
      position: absolute !important;
      left: -18px !important;
      top: 50% !important;
      transform: translateY(-50%) !important;
      width: 18px !important;
      height: 64px !important;
      background: #111827 !important;
      border: 1.5px solid #38bdf8 !important;
      border-right: none !important;
      border-radius: 10px 0 0 10px !important;
      color: #38bdf8 !important;
      cursor: pointer !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      z-index: 9999 !important;
      padding: 0 !important;
      box-shadow: -4px 0 16px rgba(56, 189, 248, 0.45) !important;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
      font-size: 17px !important;
      font-weight: 800 !important;
      line-height: 1 !important;
      user-select: none !important;
    }
    .aux-collapse-btn:hover {
      background: #1f293d !important;
      color: #7dd3fc !important;
      border-color: #7dd3fc !important;
      width: 22px !important;
      left: -22px !important;
      box-shadow: -6px 0 20px rgba(56, 189, 248, 0.7) !important;
    }
    /* Hide redundant header buttons as divider button handles collapse */
    #btn-close-aux-header, #pc-btn-close-aux-header {
      display: none !important;
    }
    .ai-assistant-container {
      flex: 1 1 0%;
      display: flex;
      flex-direction: column;
      height: calc(100% - 38px);
      max-height: calc(100% - 38px);
      min-height: 0;
      padding: 10px 12px 10px 12px;
      box-sizing: border-box;
      overflow: hidden;
      width: 100%;
      max-width: 100%;
      min-width: 0;
      position: relative;
    }
    .preview-container {
      flex: 1 1 0%;
      display: flex;
      flex-direction: column;
      height: calc(100% - 38px);
      max-height: calc(100% - 38px);
      min-height: 0;
      box-sizing: border-box;
      overflow: hidden;
      width: 100%;
      position: relative;
    }
    .ai-assistant-container[style*="display:none"],
    .ai-assistant-container[style*="display: none"] {
      display: none !important;
    }
    .preview-container[style*="display:none"],
    .preview-container[style*="display: none"] {
      display: none !important;
    }
    .ai-chat-messages {
      flex: 1 1 0% !important;
      min-height: 0 !important;
      height: 0 !important;
      max-height: 100% !important;
      overflow-y: scroll !important;
      overflow-x: hidden !important;
      padding: 4px 6px 16px 6px !important;
      display: flex !important;
      flex-direction: column !important;
      gap: 12px !important;
      font-size: 12.5px !important;
      box-sizing: border-box !important;
      width: 100% !important;
      min-width: 0 !important;
      max-width: 100% !important;
      overscroll-behavior-y: contain;
      scroll-behavior: smooth;
      scrollbar-width: thin;
      scrollbar-color: #38bdf8 rgba(15, 23, 42, 0.85);
      touch-action: pan-y;
    }
    .ai-chat-messages::-webkit-scrollbar {
      width: 8px !important;
    }
    .ai-chat-messages::-webkit-scrollbar-track {
      background: rgba(15, 23, 42, 0.85) !important;
      border-radius: 8px;
    }
    .ai-chat-messages::-webkit-scrollbar-thumb {
      background: #38bdf8 !important;
      border-radius: 8px;
      border: 2px solid #0f172a;
    }
    .ai-chat-messages::-webkit-scrollbar-thumb:hover {
      background: #7dd3fc !important;
    }
    .ai-composer {
      flex-shrink: 0 !important;
      display: flex !important;
      flex-direction: column !important;
      gap: 8px !important;
      padding: 10px !important;
      background: rgba(13, 20, 36, 0.95) !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
      border-radius: 8px !important;
      margin-top: auto !important;
      box-sizing: border-box !important;
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
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
      padding: 14px 16px 16px 16px;
      box-sizing: border-box !important;
      overflow: hidden;
      width: 100%;
    }
    .ai-chat-messages {
      flex: 1 1 0%;
      min-height: 0 !important;
      overflow-y: auto !important;
      overflow-x: hidden !important;
      padding: 4px 6px 28px 6px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      font-size: 12.5px;
      box-sizing: border-box;
      width: 100%;
    }
    .ai-chat-messages::-webkit-scrollbar {
      width: 6px;
    }
    .ai-chat-messages::-webkit-scrollbar-thumb {
      background: rgba(120, 169, 255, 0.25);
      border-radius: 4px;
    }
    .ai-chat-messages::-webkit-scrollbar-thumb:hover {
      background: rgba(120, 169, 255, 0.5);
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
      gap: 8px;
      margin-top: 10px;
      flex-shrink: 0;
      box-sizing: border-box;
      width: 100%;
    }
    .ai-composer textarea {
      width: 100%;
      height: 68px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text);
      padding: 10px 12px;
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
<div class="studio-viewport-stage">
  <div class="studio-slider">
    <!-- SLIDE 1: GITHUB CLOUD STUDIO -->
    <div id="page-github-studio" class="studio-page">
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
      <button id="btn-switch-to-pc-nav" class="btn btn-switch-mode pc-mode-btn" title="Switch to PC Cloud Studio" onclick="switchToPcStudio()">
        <span>💻 PC Studio ➡</span>
      </button>
    </div>

    <div class="nav-center">
      <div id="active-file-title" style="font-size:12px;font-weight:700;color:var(--text);display:flex;align-items:center;gap:6px">
        <span>📄 Select a file from the explorer</span>
      </div>
    </div>

    <div class="nav-right">
      <!-- User Account & Subscription Badge -->
      <div id="gh-auth-nav-slot" style="display:inline-flex;align-items:center;gap:6px">
        <button type="button" id="btn-auth-user" class="btn" style="padding:3px 10px;font-size:11px;font-weight:700;display:inline-flex;align-items:center;gap:6px" onclick="openAuthModal()">
          <span id="auth-nav-icon">👤</span>
          <span id="auth-nav-label">Sign In</span>
          <span id="auth-nav-badge" class="plan-badge free" style="display:none">FREE</span>
        </button>
        <button type="button" id="btn-nav-upgrade" class="btn-upgrade-pill" onclick="openPricingModal()">
          <span>⚡</span> <span>Upgrade</span>
        </button>
      </div>
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
        <input type="text" id="file-search" placeholder="Search files in repository..." autocomplete="off" spellcheck="false" style="padding-right:24px">
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
      <button id="dock-btn-to-pc" class="aux-dock-btn dock-pc" title="Switch to PC Cloud Studio (Direct Machine Workspace)" onclick="switchToPcStudio()">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
          <line x1="8" y1="21" x2="16" y2="21"/>
          <line x1="12" y1="17" x2="12" y2="21"/>
        </svg>
      </button>
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
    </div><!-- end page-github-studio -->

    <!-- ======================================================== -->
    <!-- SLIDE 2: PC CLOUD STUDIO (Direct Local Machine Workspace) -->
    <!-- ======================================================== -->
    <div id="page-pc-studio" class="studio-page">
      <div class="studio-app pc-theme">
        <!-- TOP BAR (PC) - Clean navbar without redundant PC button -->
        <header class="studio-nav pc-nav">
          <div class="nav-left">
            <div class="brand-title">
              <img src="/assets/hashtag_logo.jpg" alt="Logo" style="width:24px;height:24px;border-radius:6px;object-fit:cover;box-shadow:0 0 10px rgba(56,189,248,0.4);">
              <span>Hashtag</span>
              <span class="badge pc-badge">PC Cloud Studio</span>
            </div>
            <div class="repo-select-wrap">
              <span style="font-size:12px">💻</span>
              <select id="pc-root-select" title="Target PC Workspace / Drive / Directory">
                <option value=".">Local PC Workspace (Connect PC)</option>
              </select>
              <button id="pc-back-btn" class="btn" style="padding:2px 6px;font-size:11px" title="Go back to parent directory (⬆)">⬆</button>
              <button id="pc-refresh-btn" class="btn" style="padding:2px 6px;font-size:11px" title="Refresh local PC files">↻</button>
            </div>
            <button id="btn-switch-to-gh-nav" class="btn btn-switch-mode gh-mode-btn" title="Switch back to GitHub Cloud Studio" onclick="switchToGitHubStudio()">
              <span>⬅ 🐙 GitHub Studio</span>
            </button>
          </div>

          <div class="nav-center">
            <div id="pc-active-file-title" style="font-size:12px;font-weight:700;color:var(--text);display:flex;align-items:center;gap:6px">
              <span>📄 Connect your PC or select a file</span>
            </div>
          </div>

          <div class="nav-right">
            <!-- User Account & Subscription Badge -->
            <div id="pc-auth-nav-slot" style="display:inline-flex;align-items:center;gap:6px">
              <button type="button" id="pc-btn-auth-user" class="btn" style="padding:3px 10px;font-size:11px;font-weight:700;display:inline-flex;align-items:center;gap:6px" onclick="openAuthModal()">
                <span id="pc-auth-nav-icon">👤</span>
                <span id="pc-auth-nav-label">Sign In</span>
                <span id="pc-auth-nav-badge" class="plan-badge free" style="display:none">FREE</span>
              </button>
              <button type="button" id="pc-btn-nav-upgrade" class="btn-upgrade-pill" onclick="openPricingModal()">
                <span>⚡</span> <span>Upgrade</span>
              </button>
            </div>
            <button id="pc-top-new-file-btn" class="btn" style="display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600" title="Create New File on PC (Ctrl+N)" onclick="openPcNewFileModal()">
              <span>➕ New File</span>
            </button>
            <button id="pc-commit-btn" class="btn btn-commit pc-save-btn" title="Save changes directly to PC disk (Ctrl+S)">
              <span>💾 Save to PC</span>
            </button>
            <a href="/ai" class="btn" target="_blank" style="border-color:rgba(56,189,248,0.4);color:#38bdf8;" title="Open Hashtag AI Chat">💬 Chat ↗</a>
            <a href="/console" class="btn" target="_blank" title="Open Hashtag Console">💬 Console ↗</a>
          </div>
        </header>

        <!-- WORKSPACE (PC) - IDENTICAL GRID TO GITHUB STUDIO -->
        <main id="pc-workspace" class="studio-workspace">
          <!-- LEFT: PC EXPLORER -->
          <aside class="sidebar-panel">
            <div class="sidebar-head">
              <div style="display:flex;align-items:center;gap:6px">
                <span>PC Explorer</span>
                <span id="pc-file-count" style="font-weight:600;color:var(--accent)">0 files</span>
              </div>
              <div style="display:flex;align-items:center;gap:6px">
                <button id="sidebar-pc-btn" class="btn btn-primary" style="padding:3px 10px;font-size:11px;display:inline-flex;align-items:center;gap:5px;border-color:rgba(56,189,248,0.4)" title="PC Machine Status" onclick="openPcAuthModal()">
                  <span id="sidebar-pc-label">💻 Connect PC</span>
                </button>
              </div>
            </div>
            
            <!-- Breadcrumbs path navigation -->
            <div id="pc-breadcrumbs" class="pc-breadcrumbs-bar">
              <span class="pc-crumb-item" data-crumb-path=".">💻 Local PC</span>
            </div>

            <div class="search-filter" style="position:relative">
              <input type="text" id="pc-file-search" placeholder="Search local PC files..." autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" name="pc_search_file_unique" style="padding-right:24px">
              <button id="pc-clear-search-btn" type="button" style="display:none;position:absolute;right:14px;top:50%;transform:translateY(-50%);background:transparent;border:none;color:var(--muted);cursor:pointer;font-size:12px">✕</button>
            </div>
            <div id="pc-file-tree" class="file-tree">
              <!-- Initial Connection Card -->
              <div id="pc-disconnected-state" style="padding:22px 14px;text-align:center;color:var(--muted);font-size:12px">
                <div style="font-size:34px;margin-bottom:10px">📂</div>
                <div style="font-weight:700;color:var(--text);font-size:13px;margin-bottom:6px">Connect Your Local PC Folder</div>
                <div style="margin-bottom:14px;line-height:1.5;color:#94a3b8;font-size:11px">Select a local project folder directly from your browser with zero terminal commands, zero installation, and complete sandbox security.</div>
                <button type="button" class="btn btn-primary" style="padding:7px 18px;font-size:12px;font-weight:700;background:linear-gradient(135deg, #0284c7, #38bdf8);border:none;box-shadow:0 2px 10px rgba(56,189,248,0.4)" onclick="connectNativePcFolder()"><span>📂 Open Local Folder</span></button>
                <div style="margin-top:12px">
                  <a href="javascript:void(0)" onclick="openPcTerminalBridgeModal()" style="color:#7dd3fc;font-size:10px;text-decoration:none;border-bottom:1px dashed #7dd3fc">Or use Advanced Terminal Command ↗</a>
                </div>
              </div>
            </div>
          </aside>

          <!-- CENTER: CODE EDITOR -->
          <section class="editor-panel">
            <div id="pc-editor-tabs" class="editor-tabs" style="display:flex;justify-content:space-between;align-items:center">
              <div style="display:flex;align-items:center">
                <div class="editor-tab active" id="pc-tab-primary">
                  <span id="pc-tab-name">untitled</span>
                  <span id="pc-tab-dirty" style="display:none;color:var(--warning)">●</span>
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:6px;padding-right:10px">
                <button id="pc-btn-toggle-wrap" class="btn" title="Toggle Word Wrap" style="padding:2px 8px;font-size:11px">Wrap: OFF</button>
              </div>
            </div>
            <div class="editor-body-wrap">
              <div id="pc-line-numbers" class="line-numbers">1</div>
              <textarea id="pc-code-editor" class="code-textarea" wrap="off" spellcheck="false" placeholder="// Connect your PC or open any file to edit directly on local disk..."></textarea>
            </div>
          </section>

          <!-- RIGHT: PC LIVE PREVIEW & AI ASSISTANT -->
          <aside id="pc-aux-panel" class="aux-panel">
            <button id="pc-btn-collapse-aux" class="aux-collapse-btn" title="Collapse Side Panel (Hide Preview & AI)">
              <span>›</span>
            </button>

            <div class="aux-tabs">
              <div id="pc-tab-btn-preview" class="aux-tab active" style="display:flex;align-items:center;justify-content:center;gap:7px">
                <div class="cyber-eye" id="pc-eye-tab">
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
              <div id="pc-tab-btn-ai" class="aux-tab">🤖 Hashtag AI Co-Pilot</div>
              <button id="pc-btn-expand-aux" class="btn" style="padding:2px 8px;margin-right:8px;font-size:11px;border-color:rgba(56,189,248,0.4);color:#38bdf8;display:flex;align-items:center;gap:4px" title="Toggle Wide Panel">
                <span id="pc-expand-aux-icon">⛶</span>
                <span id="pc-expand-aux-label">Widen</span>
              </button>
            </div>

            <!-- PREVIEW TAB -->
            <div id="pc-view-preview" class="preview-container">
              <div class="preview-toolbar">
                <div class="dev-group">
                  <button id="pc-dev-desktop" class="dev-btn active" title="Desktop Screen (100% Fluid)">🖥️ <span class="dev-btn-label">Desktop</span></button>
                  <button id="pc-dev-tablet" class="dev-btn" title="Tablet Screen (768x1024)">📟 <span class="dev-btn-label">Tablet</span></button>
                  <button id="pc-dev-mobile" class="dev-btn" title="Mobile Screen (375x812)">📱 <span class="dev-btn-label">Mobile</span></button>
                  <button id="pc-dev-rotate" class="dev-btn" title="Rotate Screen Orientation">🔄 <span class="dev-btn-label">Rotate</span></button>
                </div>
                <div class="preview-toolbar-actions">
                  <span id="pc-preview-dim-badge" style="font-size:10px;color:var(--muted);font-variant-numeric:tabular-nums;text-align:right">100% Fluid</span>
                  <button id="pc-preview-fullscreen-btn" class="btn btn-primary" title="Full Screen Preview (F)" style="padding:2px 8px;font-size:11px;font-weight:600">⛶ Fullscreen</button>
                  <button id="pc-preview-popout-btn" class="btn" title="Open in New Real Browser Tab" style="padding:2px 8px;font-size:11px">↗ Pop Out</button>
                  <button id="pc-refresh-preview-btn" class="btn" style="padding:2px 8px;font-size:10px" title="Re-render">↻</button>
                </div>
              </div>
              <div class="preview-viewport-wrap">
                <div id="pc-preview-frame-holder" class="preview-frame-holder">
                  <iframe id="pc-preview-frame" class="preview-frame"
                    sandbox="allow-scripts allow-modals allow-same-origin allow-forms allow-popups allow-pointer-lock allow-downloads allow-top-navigation-by-user-activation"
                    referrerpolicy="no-referrer-when-downgrade"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"></iframe>
                </div>
              </div>
            </div>

            <!-- AI ASSISTANT TAB -->
            <div id="pc-view-ai" class="ai-assistant-container" style="display:none">
              <div id="pc-ai-chat" class="ai-chat-messages">
                <div class="ai-msg assistant">
                  👋 <b>Hashtag PC Cloud Co-Pilot</b> ready! Connected to your local machine. I can inspect files, write code, run terminal diagnostics, and refactor directly on your computer.
                </div>
              </div>
              <div class="ai-composer">
                <textarea id="pc-ai-prompt" placeholder="Ask Hashtag PC Co-Pilot to edit local files, refactor, or build... (Enter to send)"></textarea>
                <button id="pc-ai-send-btn" class="btn btn-primary" style="align-self:flex-end">
                  <span>Ask Hashtag</span> <span>➜</span>
                </button>
              </div>
            </div>
          </aside>

          <!-- DOCKED BUTTONS IN PC STUDIO -->
          <div id="pc-aux-dock-buttons" class="aux-dock-buttons">
            <button id="pc-dock-btn-ai" class="aux-dock-btn dock-ai" title="Open Hashtag PC AI Co-Pilot">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="10" rx="3"/>
                <circle cx="12" cy="5" r="2"/>
                <path d="M12 7v4"/>
                <line x1="8" y1="16" x2="8.01" y2="16" stroke-width="3"/>
                <line x1="16" y1="16" x2="16.01" y2="16" stroke-width="3"/>
                <path d="M9 19h6"/>
              </svg>
            </button>
            <button id="pc-dock-btn-preview" class="aux-dock-btn dock-preview" title="Open Live Web Preview">
              <div class="cyber-eye dock-size" id="pc-eye-dock">
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
            <button id="dock-btn-to-gh" class="aux-dock-btn dock-gh" title="Switch back to GitHub Cloud Studio" onclick="switchToGitHubStudio()">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
            </button>
          </div>
        </main>

        <!-- STATUSBAR (PC) -->
        <footer class="studio-statusbar pc-statusbar">
          <div class="status-item">
            <span id="pc-sync-dot" class="status-indicator"></span>
            <span id="pc-sync-status">Ready</span>
          </div>
          <div class="status-item">
            <span id="pc-editor-meta">Lines: 1 · Chars: 0</span>
            <span>|</span>
            <span id="pc-active-root">Target: Local PC</span>
            <span>|</span>
            <span style="color:#38bdf8">Hashtag PC Local Bridge</span>
          </div>
        </footer>
      </div>
    </div>

  </div><!-- end studio-slider -->
</div><!-- end studio-viewport-stage -->

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



<!-- ======================================================== -->
<!-- GLOBAL RIGHT-CLICK CONTEXT MENU -->
<!-- ======================================================== -->
<div id="studio-context-menu" class="studio-context-menu" style="display:none">
  <div class="ctx-item transfer-action" id="ctx-transfer-btn">
    <span id="ctx-transfer-icon">🐙</span>
    <span id="ctx-transfer-label">Transfer File...</span>
  </div>
  <div class="ctx-divider"></div>
  <div class="ctx-item" id="ctx-open-btn">
    <span>📄</span>
    <span>Open in Editor</span>
  </div>
  <div class="ctx-item" id="ctx-preview-btn">
    <span>👁️</span>
    <span>Render Preview</span>
  </div>
  <div class="ctx-item" id="ctx-copy-btn">
    <span>📋</span>
    <span>Copy File Path</span>
  </div>
</div>

<!-- ======================================================== -->
<!-- MODAL: CREATE NEW FILE ON PC -->
<!-- ======================================================== -->
<div id="pc-new-file-modal" class="modal-backdrop">
  <div class="modal" style="max-width:440px">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:8px">
        <span style="font-size:20px">📄</span>
        <h3 style="margin:0;font-size:16px;font-weight:700">Create New File on PC</h3>
      </div>
      <button type="button" class="btn" style="padding:2px 8px;font-size:12px" onclick="closePcNewFileModal()">✕</button>
    </div>
    <div style="font-size:12px;color:var(--muted);margin-bottom:12px">
      <span>Location: </span><code id="pc-new-file-dir" style="color:#7dd3fc">...</code>
    </div>
    <div style="margin-bottom:16px">
      <label style="display:block;font-size:11px;font-weight:600;color:var(--muted);margin-bottom:6px">New File Name:</label>
      <input type="text" id="pc-new-file-name-input" placeholder="e.g. app.js, index.html, notes.md" autocomplete="off" spellcheck="false" style="width:100%;background:#030712;border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:8px 12px;color:#fff;font-size:12px">
    </div>
    <div id="pc-new-file-status" style="font-size:11px;color:#94a3b8;margin-bottom:14px;min-height:16px"></div>
    <div style="display:flex;justify-content:flex-end;gap:8px">
      <button type="button" class="btn" onclick="closePcNewFileModal()">Cancel</button>
      <button type="button" id="pc-new-file-confirm-btn" class="btn btn-primary" onclick="confirmPcCreateFile()">
        <span>Create File</span>
      </button>
    </div>
  </div>
</div>

<!-- ======================================================== -->
<!-- MODAL: TRANSFER PC FILE -> GITHUB REPOSITORY -->
<!-- ======================================================== -->
<div id="modal-transfer-to-gh" class="modal-backdrop">
  <div class="modal" style="max-width:520px">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:8px">
        <span style="font-size:22px">🐙</span>
        <h3 style="margin:0;font-size:16px;font-weight:700">Transfer File to GitHub Repository</h3>
      </div>
      <button type="button" class="btn" style="padding:2px 8px;font-size:12px" onclick="closeGhTransferModal()">✕</button>
    </div>

    <div style="background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.3);border-radius:8px;padding:12px;margin-bottom:14px;font-size:12px">
      <div style="font-weight:700;color:#c084fc;margin-bottom:4px">Source File on PC:</div>
      <div id="trans-gh-source-path" style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#fff;word-break:break-all">C:\path\file.js</div>
    </div>

    <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:16px">
      <div>
        <label style="display:block;font-size:11px;font-weight:600;color:var(--muted);margin-bottom:4px">Target GitHub Repository:</label>
        <select id="trans-gh-target-repo" class="btn" style="width:100%;text-align:left;background:#0d1424;border:1px solid rgba(255,255,255,0.15);padding:6px 10px;font-size:12px;color:#fff">
          <option value="">Loading repositories...</option>
        </select>
      </div>

      <div style="display:grid;grid-template-columns:1fr 2fr;gap:10px">
        <div>
          <label style="display:block;font-size:11px;font-weight:600;color:var(--muted);margin-bottom:4px">Target Branch:</label>
          <input type="text" id="trans-gh-branch" value="main" style="width:100%;background:#030712;border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:6px 10px;color:#fff;font-size:12px">
        </div>
        <div>
          <label style="display:block;font-size:11px;font-weight:600;color:var(--muted);margin-bottom:4px">Target Path in Repo:</label>
          <input type="text" id="trans-gh-repo-path" value="" placeholder="e.g. src/index.js" style="width:100%;background:#030712;border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:6px 10px;color:#fff;font-size:12px">
        </div>
      </div>

      <div>
        <label style="display:block;font-size:11px;font-weight:600;color:var(--muted);margin-bottom:4px">Commit Message:</label>
        <input type="text" id="trans-gh-commit-msg" value="" style="width:100%;background:#030712;border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:6px 10px;color:#fff;font-size:12px">
      </div>
    </div>

    <div id="trans-gh-status-line" style="font-size:11px;color:#94a3b8;margin-bottom:14px;min-height:16px"></div>

    <div style="display:flex;justify-content:flex-end;gap:8px">
      <button type="button" class="btn" onclick="closeGhTransferModal()">Cancel</button>
      <button type="button" id="trans-gh-submit-btn" class="btn btn-primary" onclick="executeTransferToGitHub()">
        <span>🚀 Commit & Transfer to GitHub</span>
      </button>
    </div>
  </div>
</div>

<!-- ======================================================== -->
<!-- MODAL: TRANSFER GITHUB FILE -> LOCAL PC -->
<!-- ======================================================== -->
<div id="modal-transfer-to-pc" class="modal-backdrop">
  <div class="modal" style="max-width:520px">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:8px">
        <span style="font-size:22px">💻</span>
        <h3 style="margin:0;font-size:16px;font-weight:700">Transfer File to Local PC Disk</h3>
      </div>
      <button type="button" class="btn" style="padding:2px 8px;font-size:12px" onclick="closePcTransferModal()">✕</button>
    </div>

    <div style="background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.3);border-radius:8px;padding:12px;margin-bottom:14px;font-size:12px">
      <div style="font-weight:700;color:#38bdf8;margin-bottom:4px">Source File on GitHub:</div>
      <div id="trans-pc-source-path" style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#fff;word-break:break-all">repo/path/to/file.js</div>
    </div>

    <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:16px">
      <div>
        <label style="display:block;font-size:11px;font-weight:600;color:var(--muted);margin-bottom:6px">Quick Destination Folder on PC:</label>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
          <button type="button" class="btn" style="padding:3px 8px;font-size:11px" onclick="setPcTargetFolder('current')">📍 Current Folder</button>
          <button type="button" class="btn" style="padding:3px 8px;font-size:11px" onclick="setPcTargetFolder('desktop')">🖥️ Desktop</button>
          <button type="button" class="btn" style="padding:3px 8px;font-size:11px" onclick="setPcTargetFolder('documents')">📁 Documents</button>
          <button type="button" class="btn" style="padding:3px 8px;font-size:11px" onclick="setPcTargetFolder('downloads')">📥 Downloads</button>
        </div>
      </div>

      <div>
        <label style="display:block;font-size:11px;font-weight:600;color:var(--muted);margin-bottom:4px">Destination Directory on PC:</label>
        <input type="text" id="trans-pc-target-dir" value="" placeholder="e.g. C:\Users\user\Desktop" style="width:100%;background:#030712;border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:6px 10px;color:#fff;font-size:12px" oninput="updatePcTargetFullPathPreview()">
      </div>

      <div>
        <label style="display:block;font-size:11px;font-weight:600;color:var(--muted);margin-bottom:4px">Target File Name:</label>
        <input type="text" id="trans-pc-target-filename" value="" placeholder="filename.ext" style="width:100%;background:#030712;border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:6px 10px;color:#fff;font-size:12px" oninput="updatePcTargetFullPathPreview()">
      </div>

      <div style="font-size:11px;color:var(--muted)">
        <span>Will save to: </span>
        <code id="trans-pc-target-full-path" style="color:#7dd3fc;word-break:break-all">...</code>
      </div>
    </div>

    <div id="trans-pc-status-line" style="font-size:11px;color:#94a3b8;margin-bottom:14px;min-height:16px"></div>

    <div style="display:flex;justify-content:flex-end;gap:8px">
      <button type="button" class="btn" onclick="closePcTransferModal()">Cancel</button>
      <button type="button" id="trans-pc-submit-btn" class="btn btn-primary" onclick="executeTransferToPc()">
        <span>💾 Save to Local PC</span>
      </button>
    </div>
  </div>
</div>

<!-- ======================================================== -->
<!-- PC CONNECT MODAL (NATIVE BROWSER FS & TERMINAL BRIDGE) -->
<!-- ======================================================== -->
<div id="pc-connect-modal" class="modal-backdrop">
  <div class="modal" style="max-width:580px;width:94%">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div style="display:flex;align-items:center;gap:8px">
        <span style="font-size:22px">💻</span>
        <h3 style="margin:0;font-size:16px;font-weight:700">Connect Local PC</h3>
      </div>
      <div style="display:flex;align-items:center;gap:8px">
        <span id="pc-modal-status-badge" class="badge" style="background:rgba(248,113,113,0.15);color:#f87171;border:1px solid rgba(248,113,113,0.3)">Disconnected</span>
        <button type="button" class="btn" style="padding:2px 8px;font-size:12px" onclick="closePcAuthModal()">✕</button>
      </div>
    </div>

    <!-- Active Connected PC Profile Card -->
    <div id="pc-profile-card" style="display:none;background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.3);border-radius:8px;padding:12px 14px;margin-bottom:14px;align-items:center;gap:12px">
      <div style="font-size:26px" id="pc-profile-icon">📂</div>
      <div style="flex:1">
        <div id="pc-modal-machine-name" style="font-size:13px;font-weight:700;color:#fff">Local Project Folder</div>
        <div id="pc-modal-os-name" style="font-size:11px;color:#7dd3fc">Native Browser File System Access · Zero Setup</div>
      </div>
      <button type="button" id="modal-pc-disconnect-btn" class="btn" style="border-color:#f87171;color:#f87171;padding:4px 10px;font-size:11px" onclick="disconnectPc()">Disconnect</button>
    </div>

    <!-- Connection Mode Selector Tabs (Responsive Flex-Wrap prevents overflow) -->
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:10px">
      <button type="button" id="tab-btn-mode-native" class="btn" style="flex:1 1 220px;padding:7px 12px;font-size:12px;font-weight:700;border-color:#38bdf8;color:#38bdf8;background:rgba(56,189,248,0.15);display:flex;align-items:center;justify-content:center;gap:6px" onclick="switchPcConnectMode('native')">
        <span>📁</span> <span>Instant Folder Access (Recommended)</span>
      </button>
      <button type="button" id="tab-btn-mode-terminal" class="btn" style="flex:1 1 200px;padding:7px 12px;font-size:12px;color:var(--muted);display:flex;align-items:center;justify-content:center;gap:6px" onclick="switchPcConnectMode('terminal')">
        <span>⚡</span> <span>Advanced Terminal Bridge</span>
      </button>
    </div>

    <!-- SECTION 1: NATIVE BROWSER FILE SYSTEM ACCESS (Zero Terminal) -->
    <div id="pc-mode-native-section">
      <div style="background:linear-gradient(135deg, rgba(56,189,248,0.08), rgba(2,132,199,0.04));border:1px solid rgba(56,189,248,0.5);border-radius:10px;padding:14px 16px;margin-bottom:12px">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <span style="font-size:20px">✨</span>
          <div style="font-weight:700;color:#fff;font-size:13px">1-Click Native Project Connection</div>
        </div>
        <p style="font-size:11px;color:#94a3b8;line-height:1.5;margin:0 0 12px 0">
          No terminal commands, no PowerShell execution policy errors, and no installation. Select your local project folder to immediately read, edit, save to disk, and transfer files between PC and GitHub.
        </p>
        <button type="button" id="btn-native-pick-folder" class="btn" onclick="connectNativePcFolder()" style="width:100%;padding:12px 16px;font-size:13px;font-weight:700;background:linear-gradient(135deg, #0284c7, #38bdf8);color:#fff;border:none;border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;box-shadow:0 3px 12px rgba(56,189,248,0.3)">
          <span style="font-size:16px">📂</span>
          <span>Select Project Folder on Your PC</span>
        </button>
      </div>

      <div style="display:flex;flex-direction:column;gap:6px;font-size:11px;color:#64748b;padding:0 4px">
        <div style="display:flex;align-items:center;gap:6px">
          <span style="color:#10b981">✓</span> <span>100% Secure & Sandboxed: Only accesses the specific project folder you select</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px">
          <span style="color:#10b981">✓</span> <span>Works natively in Chrome, Edge, Brave, Opera & Chromium browsers</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px">
          <span style="color:#10b981">✓</span> <span>Real-time local file saves, new file creation, and live web preview</span>
        </div>
      </div>
    </div>

    <!-- SECTION 2: ADVANCED TERMINAL BRIDGE (PowerShell / CMD) -->
    <div id="pc-mode-terminal-section" style="display:none">
      <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:12px;margin-bottom:12px;font-size:11px;color:#94a3b8;line-height:1.5">
        <div style="font-weight:700;color:#38bdf8;margin-bottom:4px;display:flex;align-items:center;gap:6px">
          <span>⚡</span> Full Machine Terminal Access
        </div>
        <div>For running build commands (`npm install`, `python`, etc.) or accessing entire drive letters. Runs a lightweight local bridge script connected only to your browser session.</div>
      </div>

      <div style="display:flex;gap:6px;margin-bottom:8px">
        <button type="button" id="modal-tab-ps" class="btn" style="padding:3px 10px;font-size:11px;font-weight:700;border-color:#38bdf8;color:#38bdf8;background:rgba(56,189,248,0.15)" onclick="switchPcModalTab('ps')">PowerShell (Windows)</button>
        <button type="button" id="modal-tab-cmd" class="btn" style="padding:3px 10px;font-size:11px;color:var(--muted)" onclick="switchPcModalTab('cmd')">CMD (Command Prompt)</button>
      </div>

      <div style="background:#030712;border:1px solid rgba(56,189,248,0.3);border-radius:6px;padding:8px 12px;display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px">
        <code id="modal-pc-cmd" style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#7dd3fc;word-break:break-all">irm https://executor.hashtagai.online/connect.ps1 | iex</code>
        <button type="button" id="modal-pc-copy-btn" class="btn btn-primary" style="padding:3px 10px;font-size:11px;white-space:nowrap" onclick="copyPcModalCmd()">
          <span id="modal-pc-copy-text">Copy</span>
        </button>
      </div>

      <div id="modal-pc-status-line" style="font-size:11px;color:#facc15;display:flex;align-items:center;gap:6px;margin-bottom:10px">
        <span class="spinner" style="width:12px;height:12px"></span>
        <span id="modal-pc-status-msg">Waiting for terminal bridge connection...</span>
      </div>
    </div>

    <!-- Modal Footer -->
    <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:14px;border-top:1px solid rgba(255,255,255,0.08);padding-top:10px">
      <button type="button" class="btn" style="padding:4px 14px;font-size:11px" onclick="closePcAuthModal()">Close</button>
    </div>
  </div>
</div>

<!-- ======================================================== -->
<!-- MODAL: HYBRID AUTHENTICATION (GITHUB + GOOGLE + EMAIL) -->
<!-- ======================================================== -->
<div id="modal-auth" class="modal-backdrop">
  <div class="modal" style="max-width:440px;background:#0d1527;border:1px solid rgba(56,189,248,0.4);box-shadow:0 25px 60px rgba(0,0,0,0.85);padding:24px">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
      <div style="display:flex;align-items:center;gap:10px">
        <span style="font-size:24px">⚡</span>
        <div>
          <h3 style="margin:0;font-size:16px;font-weight:800;color:#fff" id="auth-modal-title">Sign In to Hashtag Studio</h3>
          <div style="font-size:11px;color:rgba(255,255,255,0.6)">Access cloud repos, PC bridge, and AI Co-Pilot</div>
        </div>
      </div>
      <button type="button" class="btn" style="padding:2px 8px;font-size:12px" onclick="closeAuthModal()">✕</button>
    </div>

    <!-- Logged In Profile View (If already authenticated) -->
    <div id="auth-logged-in-view" style="display:none;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:16px;margin-bottom:16px">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
        <img id="auth-profile-avatar" src="" style="width:42px;height:42px;border-radius:50%;border:2px solid #38bdf8;background:#070b14">
        <div style="flex:1">
          <div style="display:flex;align-items:center;gap:8px">
            <span id="auth-profile-name" style="font-size:14px;font-weight:800;color:#fff">Developer</span>
            <span id="auth-profile-badge" class="plan-badge free">FREE</span>
          </div>
          <div id="auth-profile-email" style="font-size:11.5px;color:rgba(255,255,255,0.6)">alex@example.com</div>
        </div>
      </div>

      <div style="display:flex;gap:8px">
        <button type="button" class="btn btn-primary" style="flex:1;padding:7px;font-size:11.5px;justify-content:center" onclick="closeAuthModal();openPricingModal()">
          <span>👑 View Upgrade Plans</span>
        </button>
        <button type="button" class="btn" style="padding:7px 12px;font-size:11.5px;border-color:#f87171;color:#f87171" onclick="signOutUser()">
          <span>Sign Out</span>
        </button>
      </div>
    </div>

    <!-- Anonymous / Log In View -->
    <div id="auth-logged-out-view">
      <!-- 1-Click Social / OAuth Providers -->
      <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:18px">
        <button type="button" class="btn" style="width:100%;padding:10px 14px;font-size:12.5px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:10px;background:#24292e;color:#fff;border:1px solid rgba(255,255,255,0.2)" onclick="signInWithProvider('github')">
          <span style="font-size:16px">🐙</span>
          <span>Continue with GitHub</span>
        </button>

        <button type="button" class="btn" style="width:100%;padding:10px 14px;font-size:12.5px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:10px;background:#ffffff;color:#1f2937;border:1px solid #e5e7eb" onclick="signInWithProvider('google')">
          <span style="font-size:16px">🌐</span>
          <span>Continue with Google</span>
        </button>
      </div>

      <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
        <div style="flex:1;height:1px;background:rgba(255,255,255,0.12)"></div>
        <span style="font-size:10px;font-weight:700;letter-spacing:0.06em;color:rgba(255,255,255,0.4)">OR USE EMAIL</span>
        <div style="flex:1;height:1px;background:rgba(255,255,255,0.12)"></div>
      </div>

      <!-- Email Sign In / Sign Up Tabs -->
      <div style="display:flex;gap:6px;background:rgba(0,0,0,0.3);padding:3px;border-radius:6px;margin-bottom:14px">
        <button type="button" id="tab-auth-login" class="btn active" style="flex:1;font-size:11px;padding:5px;justify-content:center" onclick="switchAuthTab('login')">Sign In</button>
        <button type="button" id="tab-auth-register" class="btn" style="flex:1;font-size:11px;padding:5px;justify-content:center" onclick="switchAuthTab('register')">Create Account</button>
      </div>

      <!-- Email Form -->
      <form id="auth-email-form" onsubmit="handleEmailAuthSubmit(event)">
        <div id="auth-name-field" style="display:none;margin-bottom:12px">
          <label style="display:block;font-size:11px;font-weight:600;margin-bottom:4px;color:rgba(255,255,255,0.8)">Your Name</label>
          <input type="text" id="auth-input-name" placeholder="Alex Dev" style="width:100%;box-sizing:border-box">
        </div>

        <div style="margin-bottom:12px">
          <label style="display:block;font-size:11px;font-weight:600;margin-bottom:4px;color:rgba(255,255,255,0.8)">Email Address</label>
          <input type="email" id="auth-input-email" required placeholder="alex@example.com" style="width:100%;box-sizing:border-box">
        </div>

        <div style="margin-bottom:14px">
          <label style="display:block;font-size:11px;font-weight:600;margin-bottom:4px;color:rgba(255,255,255,0.8)">Password</label>
          <input type="password" id="auth-input-password" required placeholder="••••••••" style="width:100%;box-sizing:border-box">
        </div>

        <div id="auth-form-error" style="display:none;color:#f87171;font-size:11.5px;margin-bottom:12px;padding:6px 10px;background:rgba(248,113,113,0.1);border-radius:4px;border:1px solid rgba(248,113,113,0.25)"></div>

        <button type="submit" id="auth-submit-btn" class="btn btn-primary" style="width:100%;padding:10px;font-size:12.5px;font-weight:700;justify-content:center">
          <span>Sign In</span>
        </button>
      </form>

      <!-- Instant Test Sandbox Bar -->
      <div style="margin-top:16px;padding-top:12px;border-top:1px dashed rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:space-between">
        <span style="font-size:10px;color:rgba(255,255,255,0.4)">⚡ Quick Sandbox:</span>
        <div style="display:flex;gap:6px">
          <button type="button" class="btn" style="padding:2px 6px;font-size:10px" onclick="quickTestSignIn('free')">Test Free</button>
          <button type="button" class="btn" style="padding:2px 6px;font-size:10px;border-color:#10b981;color:#10b981" onclick="quickTestSignIn('pro_monthly')">Test Pro</button>
          <button type="button" class="btn" style="padding:2px 6px;font-size:10px;border-color:#f59e0b;color:#f59e0b" onclick="quickTestSignIn('pro_lifetime')">Test Lifetime</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ======================================================== -->
<!-- MODAL: PRICING & SUBSCRIPTION PLANS (LEMONSQUEEZY) -->
<!-- ======================================================== -->
<div id="modal-pricing" class="modal-backdrop">
  <div class="modal" style="max-width:860px;width:95%;background:#090e1a;border:1px solid rgba(56,189,248,0.4);box-shadow:0 30px 80px rgba(0,0,0,0.9);padding:26px">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px">
      <div>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-size:24px">👑</span>
          <h2 style="margin:0;font-size:18px;font-weight:800;color:#fff">Hashtag Cloud Studio Plans</h2>
          <span class="badge" style="background:rgba(56,189,248,0.15);color:#38bdf8;font-size:11px">Simple & Transparent</span>
        </div>
        <div style="font-size:12px;color:rgba(255,255,255,0.6);margin-top:4px">Pick the plan that accelerates your development workflow. Cancel anytime.</div>
      </div>
      <button type="button" class="btn" style="padding:3px 10px;font-size:13px" onclick="closePricingModal()">✕</button>
    </div>

    <!-- 3 Plan Grid -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(240px, 1fr));gap:16px;margin-bottom:16px">
      <!-- 1. Free Starter -->
      <div style="background:#0d1527;border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:20px;display:flex;flex-direction:column;position:relative">
        <div style="font-size:13px;font-weight:700;color:rgba(255,255,255,0.7);text-transform:uppercase;letter-spacing:0.05em">Starter</div>
        <div style="font-size:28px;font-weight:850;color:#fff;margin:10px 0 4px 0">$0 <span style="font-size:12px;font-weight:500;color:rgba(255,255,255,0.5)">/ forever</span></div>
        <div style="font-size:11px;color:rgba(255,255,255,0.5);margin-bottom:16px">Essential cloud IDE for beginner coders and students.</div>
        
        <button type="button" id="btn-plan-card-free" class="btn" style="width:100%;padding:9px;font-size:12px;font-weight:700;justify-content:center;margin-bottom:16px" disabled>
          Current Plan
        </button>

        <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px;font-size:11.5px;color:rgba(255,255,255,0.8)">
          <li>✅ GitHub Cloud Studio & PC Studio</li>
          <li>✅ Connect 1 Local PC Project Folder</li>
          <li>✅ Desktop Live Responsive View</li>
          <li>✅ 5 Cross-Bridge File Moves / Day</li>
          <li>✅ 10 AI Co-Pilot Prompts / Day</li>
          <li style="color:rgba(255,255,255,0.4)">❌ Tablet & Mobile Device Frames</li>
          <li style="color:rgba(255,255,255,0.4)">❌ Unlimited File Moves & AI</li>
        </ul>
      </div>

      <!-- 2. Pro Monthly ($5) -->
      <div style="background:linear-gradient(180deg, rgba(56,189,248,0.12), rgba(13,21,39,0.95));border:1.5px solid #38bdf8;border-radius:12px;padding:20px;display:flex;flex-direction:column;position:relative;box-shadow:0 10px 30px rgba(56,189,248,0.2)">
        <div style="position:absolute;top:-10px;right:16px;background:#38bdf8;color:#000;font-size:10px;font-weight:800;padding:2px 8px;border-radius:999px;text-transform:uppercase">Popular</div>
        <div style="font-size:13px;font-weight:700;color:#38bdf8;text-transform:uppercase;letter-spacing:0.05em">Pro Monthly</div>
        <div style="font-size:28px;font-weight:850;color:#fff;margin:10px 0 4px 0">$5 <span style="font-size:12px;font-weight:500;color:rgba(255,255,255,0.5)">/ month</span></div>
        <div style="font-size:11px;color:rgba(255,255,255,0.5);margin-bottom:16px">Full power for active developers and engineers.</div>
        
        <button type="button" id="btn-plan-card-monthly" class="btn btn-primary" style="width:100%;padding:9px;font-size:12px;font-weight:700;justify-content:center;margin-bottom:16px;background:#38bdf8;color:#000" onclick="triggerLemonCheckout('pro_monthly')">
          Subscribe Monthly ($5/mo)
        </button>

        <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px;font-size:11.5px;color:rgba(255,255,255,0.85)">
          <li>✅ <b>Everything in Free Starter</b></li>
          <li>✅ <b>Tablet & Mobile Device Simulators</b></li>
          <li>✅ <b>Landscape & Portrait Orientation</b></li>
          <li>✅ <b>True Native Fullscreen Mode</b></li>
          <li>✅ <b>Unlimited 1-Click File Transfers</b></li>
          <li>✅ <b>Unlimited AI Co-Pilot Assistance</b></li>
          <li>✅ <b>Unlimited GitHub Repositories</b></li>
        </ul>
      </div>

      <!-- 3. Lifetime VIP ($27) -->
      <div style="background:linear-gradient(180deg, rgba(245,158,11,0.14), rgba(13,21,39,0.95));border:1.5px solid #f59e0b;border-radius:12px;padding:20px;display:flex;flex-direction:column;position:relative;box-shadow:0 10px 30px rgba(245,158,11,0.2)">
        <div style="position:absolute;top:-10px;right:16px;background:linear-gradient(135deg, #f59e0b, #eab308);color:#000;font-size:10px;font-weight:850;padding:2px 8px;border-radius:999px;text-transform:uppercase">Best Value · 90% Off</div>
        <div style="font-size:13px;font-weight:700;color:#f59e0b;text-transform:uppercase;letter-spacing:0.05em">Lifetime VIP</div>
        <div style="font-size:28px;font-weight:850;color:#fff;margin:10px 0 4px 0">$27 <span style="font-size:12px;font-weight:500;color:rgba(255,255,255,0.5)">one-time</span></div>
        <div style="font-size:11px;color:rgba(255,255,255,0.5);margin-bottom:16px">Pay once. Keep Pro features forever. Zero subscriptions.</div>
        
        <button type="button" id="btn-plan-card-lifetime" class="btn" style="width:100%;padding:9px;font-size:12px;font-weight:800;justify-content:center;margin-bottom:16px;background:linear-gradient(135deg, #f59e0b, #d97706);color:#000;border:none" onclick="triggerLemonCheckout('pro_lifetime')">
          ⚡ Get Lifetime Access ($27)
        </button>

        <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px;font-size:11.5px;color:rgba(255,255,255,0.9)">
          <li>⚡ <b>All Pro Monthly Features FOREVER</b></li>
          <li>⚡ <b>Zero Recurring Monthly Fees</b></li>
          <li>⚡ <b>Unlimited Device Mockups & Rotate</b></li>
          <li>⚡ <b>Unlimited Cross-Bridge File Moves</b></li>
          <li>⚡ <b>Unlimited AI Co-Pilot + BYOK Key</b></li>
          <li>⚡ <b>Early Access to All Future Studio Features</b></li>
          <li>⚡ <b>Early Supporter VIP Gold Badge</b></li>
        </ul>
      </div>
    </div>

    <!-- Security & Guarantee Badge -->
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px 14px;display:flex;align-items:center;justify-content:space-between;font-size:11px;color:rgba(255,255,255,0.6)">
      <div style="display:flex;align-items:center;gap:6px">
        <span>🔒</span>
        <span>Secure LemonSqueezy Checkout · 256-bit SSL · Instant Tier Activation</span>
      </div>
      <div>Questions? Reach us at founder@hashtagai.online</div>
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
    var bodyData = undefined;
    if (options.body !== undefined && options.body !== null) {
      bodyData = (typeof options.body === "string") ? options.body : JSON.stringify(options.body);
    }
    return fetch(url, {
      method: options.method || "GET",
      headers: headers,
      body: bodyData,
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
    if (device === "tablet" || device === "mobile") {
      if (typeof requireProFeature === "function" && !requireProFeature("device_simulator", "Tablet and Mobile live testing is a Pro feature! Upgrade for just $5/mo or $27 lifetime to simulate all screens.")) {
        if ($("dev-desktop")) $("dev-desktop").classList.add("active");
        return;
      }
    }
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
    if (typeof canSendAiPrompt === "function" && !canSendAiPrompt()) return;
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
    

    enterFullscreen();
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

  var ghPreviewPlaceholder = null;

  function toggleFullscreen() {
    if (fullscreenState.isFullscreen) {
      exitFullscreen();
    } else {
      enterFullscreen();
    }
  }

  function enterFullscreen() {
    var prev = $("view-preview");
    if (!prev || fullscreenState.isFullscreen) return;
    var ws = $("workspace");
    if (ws) ws.classList.remove("preview-closed");
    var tabBtn = $("tab-btn-preview");
    if (tabBtn) tabBtn.click();

    ghPreviewPlaceholder = document.createElement("div");
    ghPreviewPlaceholder.id = "gh-prev-placeholder";
    prev.parentNode.insertBefore(ghPreviewPlaceholder, prev);
    document.body.appendChild(prev);

    document.body.classList.add("has-preview-fullscreen");
    prev.classList.add("is-fullscreen");
    fullscreenState.isFullscreen = true;
    updateFullscreenButtons(true);

    try {
      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(function(){});
      } else if (document.documentElement.webkitRequestFullscreen) {
        document.documentElement.webkitRequestFullscreen();
      }
    } catch(e) {}
  }

  function exitFullscreen() {
    var prev = $("view-preview");
    if (!prev || !fullscreenState.isFullscreen) return;
    document.body.classList.remove("has-preview-fullscreen");
    prev.classList.remove("is-fullscreen");
    fullscreenState.isFullscreen = false;
    updateFullscreenButtons(false);

    try {
      if (document.fullscreenElement) {
        (document.exitFullscreen || document.webkitExitFullscreen).call(document);
      }
    } catch(e) {}

    if (ghPreviewPlaceholder && ghPreviewPlaceholder.parentNode) {
      ghPreviewPlaceholder.parentNode.insertBefore(prev, ghPreviewPlaceholder);
      ghPreviewPlaceholder.parentNode.removeChild(ghPreviewPlaceholder);
      ghPreviewPlaceholder = null;
    }
  }

  document.addEventListener("fullscreenchange", function() {
    if (!document.fullscreenElement) {
      if (typeof fullscreenState !== "undefined" && fullscreenState.isFullscreen) exitFullscreen();
      if (typeof pcFullscreenState !== "undefined" && pcFullscreenState.isFullscreen) exitPcFullscreen();
    }
  });
  document.addEventListener("webkitfullscreenchange", function() {
    if (!document.webkitFullscreenElement) {
      if (typeof fullscreenState !== "undefined" && fullscreenState.isFullscreen) exitFullscreen();
      if (typeof pcFullscreenState !== "undefined" && pcFullscreenState.isFullscreen) exitPcFullscreen();
    }
  });

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
      if (document.body.classList.contains("mode-pc")) {
        var pcEd = $("pc-code-editor");
        if (pcEd) pcEd.value = code;
        var dirty = $("pc-tab-dirty");
        if (dirty) dirty.style.display = "inline";
        updatePcLineNumbers();
        updatePcPreview();
      } else {
        $("code-editor").value = code;
        markDirty();
        updateLineNumbers();
        updatePreview();
      }
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
  // --- PC STUDIO STATE & SYSTEM INFO ---
  // ========================================================
  var pcState = {
    activePath: "index.html",
    isDirty: false
  };
  var currentPcModalCmd = "irm https://executor.hashtagai.online/connect.ps1 | iex";
  var isPcConnected = false;
  var pcConnectionMode = "disconnected"; // "native_fs" or "bridge"
  var activePcDirHandle = null;
  var pcHandleMap = {}; // relative_path -> FileSystemHandle
  var pcParentMap = {}; // relative_path -> parent FileSystemDirectoryHandle
  var pcCurrentPath = ".";
  var pcPreviewTimer = null;
  var pcInfo = {};
  var pcDrivesList = [];
  window.pcFilesLoaded = false;

  // Context menu target tracking
  var currentContextTarget = {
    source: null, // "gh" or "pc"
    path: null,
    isDir: false,
    name: null
  };

  // ========================================================
  // --- STUDIO SLIDER & DUAL-MODE VIEWPORT CONTROLLER ---
  // ========================================================
  
  // ========================================================
  // --- AUTHENTICATION & SUBSCRIPTION CONTROLLER ---
  // ========================================================
  window.currentUser = null;
  window.currentAuthTab = "login";

  window.checkUserAuth = function() {
    var token = localStorage.getItem("hashtag_auth_token");
    var headers = token ? { "Authorization": "Bearer " + token } : {};

    fetch("/v1/auth/me", { headers: headers }).then(function(r) {
      return r.json();
    }).then(function(res) {
      if (res.ok && res.authenticated && res.user) {
        window.currentUser = res.user;
      } else {
        window.currentUser = null;
      }
      updateAuthUI();
    }).catch(function() {
      window.currentUser = null;
      updateAuthUI();
    });
  };

  function updateAuthUI() {
    var u = window.currentUser;
    var ghBtn = $("btn-auth-user");
    var pcBtn = $("pc-btn-auth-user");
    var ghUp = $("btn-nav-upgrade");
    var pcUp = $("pc-btn-nav-upgrade");

    var isPro = u && (u.is_pro || u.tier === "pro_monthly" || u.tier === "pro_lifetime");
    var isLifetime = u && (u.is_lifetime || u.tier === "pro_lifetime");

    if (u) {
      var badgeText = isLifetime ? "LIFETIME" : (isPro ? "PRO" : "FREE");
      var badgeClass = isLifetime ? "plan-badge lifetime" : (isPro ? "plan-badge pro" : "plan-badge free");

      [ghBtn, pcBtn].forEach(function(btn) {
        if (!btn) return;
        btn.innerHTML = '<img src="' + esc(u.avatar_url || '') + '" style="width:16px;height:16px;border-radius:50%;object-fit:cover">'
          + '<span>' + esc(u.name.split(' ')[0]) + '</span>'
          + '<span class="' + badgeClass + '">' + badgeText + '</span>';
      });

      if (ghUp) ghUp.style.display = isPro ? "none" : "inline-flex";
      if (pcUp) pcUp.style.display = isPro ? "none" : "inline-flex";

      // Update Modal Profile View
      var loggedInView = $("auth-logged-in-view");
      var loggedOutView = $("auth-logged-out-view");
      if (loggedInView) loggedInView.style.display = "block";
      if (loggedOutView) loggedOutView.style.display = "none";

      if ($("auth-profile-name")) $("auth-profile-name").textContent = u.name;
      if ($("auth-profile-email")) $("auth-profile-email").textContent = u.email;
      if ($("auth-profile-avatar")) $("auth-profile-avatar").src = u.avatar_url;
      if ($("auth-profile-badge")) {
        $("auth-profile-badge").className = badgeClass;
        $("auth-profile-badge").textContent = badgeText;
      }
    } else {
      [ghBtn, pcBtn].forEach(function(btn) {
        if (!btn) return;
        btn.innerHTML = '<span>👤</span> <span>Sign In</span>';
      });
      if (ghUp) ghUp.style.display = "inline-flex";
      if (pcUp) pcUp.style.display = "inline-flex";

      var loggedInView = $("auth-logged-in-view");
      var loggedOutView = $("auth-logged-out-view");
      if (loggedInView) loggedInView.style.display = "none";
      if (loggedOutView) loggedOutView.style.display = "block";
    }

    // Update Pricing Modal Cards
    var cardFreeBtn = $("btn-plan-card-free");
    var cardMonthBtn = $("btn-plan-card-monthly");
    var cardLifeBtn = $("btn-plan-card-lifetime");

    if (cardFreeBtn) {
      cardFreeBtn.textContent = (!u || !isPro) ? "Current Plan" : "Downgrade";
      cardFreeBtn.disabled = (!u || !isPro);
    }
    if (cardMonthBtn) {
      cardMonthBtn.textContent = (u && u.tier === "pro_monthly") ? "Active Monthly Subscription" : "Subscribe Monthly ($5/mo)";
      cardMonthBtn.disabled = (u && u.tier === "pro_monthly");
    }
    if (cardLifeBtn) {
      cardLifeBtn.textContent = isLifetime ? "Active Lifetime VIP" : "⚡ Get Lifetime Access ($27)";
      cardLifeBtn.disabled = isLifetime;
    }
  }

  window.openAuthModal = function() {
    var m = $("modal-auth");
    if (m) m.classList.add("open");
  };

  window.closeAuthModal = function() {
    var m = $("modal-auth");
    if (m) m.classList.remove("open");
  };

  window.openPricingModal = function() {
    var m = $("modal-pricing");
    if (m) m.classList.add("open");
  };

  window.closePricingModal = function() {
    var m = $("modal-pricing");
    if (m) m.classList.remove("open");
  };

  window.switchAuthTab = function(tab) {
    window.currentAuthTab = tab;
    var tLog = $("tab-auth-login");
    var tReg = $("tab-auth-register");
    var nameField = $("auth-name-field");
    var submitBtn = $("auth-submit-btn");

    if (tab === "register") {
      if (tLog) tLog.classList.remove("active");
      if (tReg) tReg.classList.add("active");
      if (nameField) nameField.style.display = "block";
      if (submitBtn) submitBtn.innerHTML = "<span>Create Account</span>";
    } else {
      if (tLog) tLog.classList.add("active");
      if (tReg) tReg.classList.remove("active");
      if (nameField) nameField.style.display = "none";
      if (submitBtn) submitBtn.innerHTML = "<span>Sign In</span>";
    }
    var err = $("auth-form-error");
    if (err) err.style.display = "none";
  };

  window.signInWithProvider = function(provider) {
    if (provider === "github") {
      window.location.href = "/v1/auth/github";
    } else if (provider === "google") {
      window.location.href = "/v1/auth/google";
    }
  };

  window.handleEmailAuthSubmit = function(e) {
    if (e && e.preventDefault) e.preventDefault();
    var email = ($("auth-input-email") ? $("auth-input-email").value : "").trim();
    var password = ($("auth-input-password") ? $("auth-input-password").value : "").trim();
    var name = ($("auth-input-name") ? $("auth-input-name").value : "").trim();
    var errEl = $("auth-form-error");

    if (!email || !password) {
      if (errEl) { errEl.textContent = "Please fill in all fields."; errEl.style.display = "block"; }
      return;
    }

    var endpoint = (window.currentAuthTab === "register") ? "/v1/auth/email/register" : "/v1/auth/email/login";
    var payload = { email: email, password: password, name: name };

    fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }).then(function(r) { return r.json(); }).then(function(res) {
      if (!res.ok) {
        if (errEl) { errEl.textContent = res.error || "Authentication failed."; errEl.style.display = "block"; }
        return;
      }
      localStorage.setItem("hashtag_auth_token", res.token);
      window.currentUser = res.user;
      closeAuthModal();
      updateAuthUI();
      alert("✓ Welcome back, " + res.user.name + "!");
    }).catch(function(err) {
      if (errEl) { errEl.textContent = "Network error: " + err.message; errEl.style.display = "block"; }
    });
  };

  window.quickTestSignIn = function(tier) {
    fetch("/v1/auth/test-activate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tier: tier })
    }).then(function(r) { return r.json(); }).then(function(res) {
      if (res.ok) {
        localStorage.setItem("hashtag_auth_token", res.token);
        window.currentUser = res.user;
        closeAuthModal();
        closePricingModal();
        updateAuthUI();
        alert("✓ Activated test session as " + tier.toUpperCase() + "!");
      }
    });
  };

  window.signOutUser = function() {
    localStorage.removeItem("hashtag_auth_token");
    window.currentUser = null;
    updateAuthUI();
    closeAuthModal();
    alert("Signed out successfully.");
  };

  window.triggerLemonCheckout = function(tier) {
    if (!window.currentUser) {
      closePricingModal();
      openAuthModal();
      alert("Please sign in or create an account first before subscribing.");
      return;
    }

    var token = localStorage.getItem("hashtag_auth_token");
    fetch("/v1/billing/checkout", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({ tier: tier })
    }).then(function(r) { return r.json(); }).then(function(res) {
      if (res.ok && res.url) {
        if (res.is_test_mode) {
          quickTestSignIn(tier);
        } else {
          window.location.href = res.url;
        }
      } else {
        alert("Checkout error: " + (res.error || "Could not generate checkout session"));
      }
    }).catch(function(err) {
      alert("Checkout connection error: " + err.message);
    });
  };

  // --- FEATURE GATEKEEPERS ---
  window.requireProFeature = function(featureName, message) {
    var u = window.currentUser;
    var isPro = u && (u.is_pro || u.tier === "pro_monthly" || u.tier === "pro_lifetime");
    if (!isPro) {
      openPricingModal();
      alert("👑 Pro Feature: " + message);
      return false;
    }
    return true;
  };

  window.canPerformTransfer = function() {
    var u = window.currentUser;
    var isPro = u && (u.is_pro || u.tier === "pro_monthly" || u.tier === "pro_lifetime");
    if (isPro) return true;
    var todayKey = "hashtag_transfers_" + new Date().toISOString().slice(0, 10);
    var count = parseInt(localStorage.getItem(todayKey) || "0", 10);
    if (count >= 5) {
      openPricingModal();
      alert("⚡ Free Daily Limit Reached: You have used your 5 free cross-bridge file transfers today. Upgrade to Pro ($5/mo) or Lifetime ($27) for unlimited transfers!");
      return false;
    }
    localStorage.setItem(todayKey, (count + 1).toString());
    return true;
  };

  window.canSendAiPrompt = function() {
    var u = window.currentUser;
    var isPro = u && (u.is_pro || u.tier === "pro_monthly" || u.tier === "pro_lifetime");
    if (isPro) return true;
    var todayKey = "hashtag_ai_prompts_" + new Date().toISOString().slice(0, 10);
    var count = parseInt(localStorage.getItem(todayKey) || "0", 10);
    if (count >= 10) {
      openPricingModal();
      alert("⚡ Free Daily Limit Reached: You have reached your 10 free AI Co-Pilot requests for today. Upgrade to Pro ($5/mo) or Lifetime ($27) for unlimited AI assistance!");
      return false;
    }
    localStorage.setItem(todayKey, (count + 1).toString());
    return true;
  };

  // Check URL params for auth callbacks or success
  (function() {
    var urlParams = new URLSearchParams(window.location.search);
    var authToken = urlParams.get("auth_token");
    if (authToken) {
      localStorage.setItem("hashtag_auth_token", authToken);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    var activateTier = urlParams.get("activate_test_tier");
    if (activateTier) {
      window.quickTestSignIn(activateTier);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    checkUserAuth();
  })();

  window.switchToPcStudio = function(e) {
    if (e && e.preventDefault) e.preventDefault();
    document.body.classList.add("mode-pc");
    localStorage.setItem("hashtag_studio_mode", "pc");
    var slider = document.querySelector(".studio-slider");
    if (slider) {
      slider.style.transform = "translate3d(-100vw, 0, 0)";
    }
    if (typeof updatePcPreview === "function") updatePcPreview();
    if (typeof checkPcConnectorStatus === "function") checkPcConnectorStatus();
  };

  window.switchToGitHubStudio = function(e) {
    if (e && e.preventDefault) e.preventDefault();
    document.body.classList.remove("mode-pc");
    localStorage.setItem("hashtag_studio_mode", "github");
    var slider = document.querySelector(".studio-slider");
    if (slider) {
      slider.style.transform = "translate3d(0, 0, 0)";
    }
    if (typeof updatePreview === "function") updatePreview();
  };

  // Slide trigger buttons (GitHub -> PC)
  var btnToPcDock = $("dock-btn-to-pc");
  if (btnToPcDock) btnToPcDock.onclick = window.switchToPcStudio;

  var btnToPcNav = $("btn-switch-to-pc-nav");
  if (btnToPcNav) btnToPcNav.onclick = window.switchToPcStudio;

  // Slide trigger buttons (PC -> GitHub)
  var btnToGhDock = $("dock-btn-to-gh");
  if (btnToGhDock) btnToGhDock.onclick = window.switchToGitHubStudio;

  var btnToGhNav = $("btn-switch-to-gh-nav");
  if (btnToGhNav) btnToGhNav.onclick = window.switchToGitHubStudio;

  // Restore last mode on page load
  if (localStorage.getItem("hashtag_studio_mode") === "pc") {
    document.body.classList.add("mode-pc");
    var initSlider = document.querySelector(".studio-slider");
    if (initSlider) {
      initSlider.style.transform = "translate3d(-100vw, 0, 0)";
    }
  }

  // ========================================================
  // --- PC CONNECT MODAL & HEARTBEAT CONTROLLER ---
  // ========================================================
  // Native Browser File System Access API
  window.connectNativePcFolder = async function() {
    if (!window.showDirectoryPicker) {
      alert("Your current browser does not support the File System Access API. Please use Google Chrome, Microsoft Edge, Brave, or Opera, or use the Advanced Terminal Command.");
      switchPcConnectMode("terminal");
      return;
    }
    try {
      var dirHandle = await window.showDirectoryPicker({
        mode: "readwrite"
      });
      if (!dirHandle) return;

      activePcDirHandle = dirHandle;
      pcConnectionMode = "native_fs";
      isPcConnected = true;
      window.pcFilesLoaded = true;

      closePcAuthModal();
      await loadNativePcFolder(dirHandle);

      var status = $("pc-sync-status");
      if (status) status.textContent = "Local folder: " + dirHandle.name;
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error("Native FS connect error:", err);
        alert("Could not open folder: " + err.message);
      }
    }
  };

  async function loadNativePcFolder(dirHandle) {
    activePcDirHandle = dirHandle;
    pcConnectionMode = "native_fs";
    isPcConnected = true;
    pcHandleMap = {};
    pcParentMap = {};

    var statusDot = $("pc-status-dot");
    if (statusDot) {
      statusDot.className = "status-dot connected";
      statusDot.title = "Connected to local folder: " + dirHandle.name;
    }
    var sideLabel = $("sidebar-pc-label");
    if (sideLabel) {
      sideLabel.innerHTML = '🟢 ' + esc(dirHandle.name);
    }
    var modalBadge = $("pc-modal-status-badge");
    if (modalBadge) {
      modalBadge.textContent = "Connected";
      modalBadge.style.background = "rgba(16,185,129,0.15)";
      modalBadge.style.color = "#10b981";
      modalBadge.style.borderColor = "rgba(16,185,129,0.3)";
    }
    var profileCard = $("pc-profile-card");
    if (profileCard) {
      profileCard.style.display = "flex";
      $("pc-modal-machine-name").textContent = dirHandle.name;
      $("pc-modal-os-name").textContent = "Native Browser Project · " + location.hostname;
    }

    var sel = $("pc-root-select");
    if (sel) {
      sel.innerHTML = '<option value="native_root" selected>📁 ' + esc(dirHandle.name) + ' (Local Project)</option>';
    }

    // Build recursive items
    var entries = [];
    async function scan(handle, currentPath) {
      for await (const [name, entry] of handle.entries()) {
        if (name.startsWith(".") || name === "node_modules" || name === "__pycache__" || name === ".venv") continue;
        var relPath = currentPath ? (currentPath + "/" + name) : name;
        pcHandleMap[relPath] = entry;
        pcParentMap[relPath] = handle;
        if (entry.kind === "directory") {
          await scan(entry, relPath);
          entries.push({
            name: name,
            path: relPath,
            is_dir: true,
            handle: entry
          });
        } else {
          var fObj = await entry.getFile();
          entries.push({
            name: name,
            path: relPath,
            is_dir: false,
            size: fObj.size,
            handle: entry
          });
        }
      }
    }

    await scan(dirHandle, "");
    entries.sort(function(a, b) {
      if (a.is_dir !== b.is_dir) return b.is_dir ? 1 : -1;
      return a.name.localeCompare(b.name);
    });

    pcState.files = entries;
    pcCurrentPath = ".";
    
    // Hide disconnected state card immediately
    var disc = $("pc-disconnected-state");
    if (disc) disc.style.display = "none";

    renderPcFileTree(entries);
    var searchEl = $("pc-file-search");
    if (searchEl) searchEl.value = "";

    var countEl = $("pc-file-count");
    if (countEl) countEl.textContent = entries.filter(function(e) { return !e.is_dir; }).length + " files";

    var bc = $("pc-breadcrumbs");
    if (bc) {
      bc.innerHTML = '<span class="pc-crumb-item" data-crumb-path=".">📁 ' + esc(dirHandle.name) + '</span>';
    }

    var defaultFile = entries.find(function(e) {
      return !e.is_dir && (e.name.toLowerCase() === "index.html" || e.name.toLowerCase() === "readme.md");
    }) || entries.find(function(e) { return !e.is_dir; });

    if (defaultFile) {
      openPcFile(defaultFile.path);
    }
  }

  // --- RENDER PC FILE TREE (Native & General Tree Renderer) ---
  window.renderPcFileTree = function(entries) {
    entries = entries || pcState.files || [];
    var treeEl = $("pc-file-tree");
    if (!treeEl) return;

    var searchEl = $("pc-file-search");
    var filter = (searchEl && searchEl.value || "").toLowerCase().trim();
    var clearBtn = $("pc-clear-search-btn");
    if (clearBtn) clearBtn.style.display = filter ? "block" : "none";

    if (!entries || !entries.length) {
      treeEl.innerHTML = '<div style="padding:28px 14px;text-align:center;color:var(--muted);font-size:12px">'
        + '<div style="font-size:28px;margin-bottom:8px">📂</div>'
        + '<div style="color:var(--text);font-weight:600;margin-bottom:4px">No files found in this folder</div>'
        + '<div style="font-size:11px;color:rgba(255,255,255,0.4)">Click "+ New File" in the top bar to create a file.</div>'
        + '</div>';
      var countEl = $("pc-file-count");
      if (countEl) countEl.textContent = "0 files";
      return;
    }

    var disc = $("pc-disconnected-state");
    if (disc) disc.style.display = "none";

    var matching = 0;
    var totalFiles = 0;
    var html = '<div class="file-list-items" style="padding:4px 0">';

    entries.forEach(function(item) {
      if (item.is_dir) return; // Flat list of file paths (e.g. index.html, src/main.js)
      totalFiles++;
      var p = item.path || item.name || "";
      if (filter && !p.toLowerCase().includes(filter)) return;
      matching++;

      var isAct = (p === pcState.activePath) ? "active" : "";
      var icon = typeof getFileIcon === "function" ? getFileIcon(p) : "📄";
      var sizeText = "";
      if (item.size != null && !isNaN(item.size)) {
        if (item.size < 1024) sizeText = item.size + " B";
        else if (item.size < 1024 * 1024) sizeText = (item.size / 1024).toFixed(1) + " KB";
        else sizeText = (item.size / (1024 * 1024)).toFixed(1) + " MB";
      }

      html += '<div class="file-item file-leaf ' + isAct + '" data-path="' + esc(p) + '" data-is-dir="false" data-name="' + esc(item.name || p.split("/").pop()) + '" style="display:flex;align-items:center;gap:6px;padding:6px 10px;cursor:pointer;border-radius:4px;font-size:12px;user-select:none">'
            + '<span class="icon" style="font-size:13px">' + icon + '</span>'
            + '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="' + esc(p) + '">' + esc(p) + '</span>'
            + (sizeText ? ('<span class="file-size" style="font-size:10px;color:rgba(255,255,255,0.35);margin-left:auto">' + sizeText + '</span>') : '')
            + '</div>';
    });

    html += '</div>';

    var countEl = $("pc-file-count");
    if (countEl) {
      countEl.textContent = filter ? (matching + " / " + totalFiles) : (totalFiles + " files");
    }

    if (totalFiles > 0 && matching === 0 && filter) {
      treeEl.innerHTML = '<div style="padding:28px 16px;text-align:center;color:var(--muted);font-size:12px">'
        + '<div style="font-size:20px;margin-bottom:8px">🔍</div>'
        + 'No files matching "<b style="color:var(--text)">' + esc(filter) + '</b>"'
        + '<div style="margin-top:10px"><button id="btn-pc-tree-clear-search" class="btn" style="padding:2px 8px;font-size:11px">Clear Search</button></div>'
        + '</div>';
      var tClear = $("btn-pc-tree-clear-search");
      if (tClear) {
        tClear.onclick = function() {
          if (searchEl) searchEl.value = "";
          renderPcFileTree(pcState.files);
          if (searchEl) searchEl.focus();
        };
      }
      return;
    }

    treeEl.innerHTML = html;

    // Attach click events
    treeEl.querySelectorAll(".file-item.file-leaf").forEach(function(el) {
      el.onclick = function() {
        var p = el.getAttribute("data-path");
        if (p) openPcFile(p);
      };
    });
  };

  // Switching Connect PC Modal Tabs (Native vs Terminal)
  window.switchPcConnectMode = function(mode) {
    var nativeTab = $("tab-btn-mode-native");
    var termTab = $("tab-btn-mode-terminal");
    var nativeSec = $("pc-mode-native-section");
    var termSec = $("pc-mode-terminal-section");

    if (mode === "terminal") {
      if (nativeTab) {
        nativeTab.style.borderColor = "var(--border)";
        nativeTab.style.color = "var(--muted)";
        nativeTab.style.background = "transparent";
      }
      if (termTab) {
        termTab.style.borderColor = "#38bdf8";
        termTab.style.color = "#38bdf8";
        termTab.style.background = "rgba(56,189,248,0.15)";
      }
      if (nativeSec) nativeSec.style.display = "none";
      if (termSec) termSec.style.display = "block";
    } else {
      if (nativeTab) {
        nativeTab.style.borderColor = "#38bdf8";
        nativeTab.style.color = "#38bdf8";
        nativeTab.style.background = "rgba(56,189,248,0.15)";
      }
      if (termTab) {
        termTab.style.borderColor = "var(--border)";
        termTab.style.color = "var(--muted)";
        termTab.style.background = "transparent";
      }
      if (nativeSec) nativeSec.style.display = "block";
      if (termSec) termSec.style.display = "none";
    }
  };

  window.openPcTerminalBridgeModal = function() {
    openPcAuthModal("terminal");
  };

  window.openPcAuthModal = function(initialTab) {
    var modal = $("pc-connect-modal");
    if (modal) modal.classList.add("open");
    if (initialTab === "terminal") {
      switchPcConnectMode("terminal");
    } else {
      switchPcConnectMode("native");
    }
    if (typeof checkPcConnectorStatus === "function") checkPcConnectorStatus();
  };

  window.closePcAuthModal = function() {
    var m = $("pc-connect-modal");
    if (m) m.classList.remove("open");
  };

  var pcModalEl = $("pc-connect-modal");
  if (pcModalEl) {
    pcModalEl.addEventListener("click", function(e) {
      if (e.target === pcModalEl) closePcAuthModal();
    });
  }

  window.switchPcModalTab = function(tab) {
    var btnPs = $("modal-tab-ps");
    var btnCmd = $("modal-tab-cmd");
    var snippet = $("modal-pc-cmd");
    if (tab === "ps") {
      if (btnPs) {
        btnPs.style.background = "rgba(56,189,248,0.15)";
        btnPs.style.borderColor = "#38bdf8";
        btnPs.style.color = "#38bdf8";
        btnPs.style.fontWeight = "700";
      }
      if (btnCmd) {
        btnCmd.style.background = "";
        btnCmd.style.borderColor = "";
        btnCmd.style.color = "var(--muted)";
        btnCmd.style.fontWeight = "normal";
      }
      currentPcModalCmd = "irm https://executor.hashtagai.online/connect.ps1 | iex";
    } else {
      if (btnCmd) {
        btnCmd.style.background = "rgba(56,189,248,0.15)";
        btnCmd.style.borderColor = "#38bdf8";
        btnCmd.style.color = "#38bdf8";
        btnCmd.style.fontWeight = "700";
      }
      if (btnPs) {
        btnPs.style.background = "";
        btnPs.style.borderColor = "";
        btnPs.style.color = "var(--muted)";
        btnPs.style.fontWeight = "normal";
      }
      currentPcModalCmd = "curl -sSf https://executor.hashtagai.online/connect.cmd | cmd";
    }
    if (snippet) snippet.textContent = currentPcModalCmd;
  };

  window.copyPcModalCmd = function() {
    var snippet = $("modal-pc-cmd");
    var copyText = $("modal-pc-copy-text");
    var textToCopy = snippet ? (snippet.innerText || snippet.textContent) : currentPcModalCmd;

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(textToCopy).then(function() {
        if (copyText) copyText.textContent = "✓ Copied!";
        setTimeout(function() { if (copyText) copyText.textContent = "Copy"; }, 2000);
      });
    } else {
      var ta = document.createElement("textarea");
      ta.value = textToCopy;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      if (copyText) copyText.textContent = "✓ Copied!";
      setTimeout(function() { if (copyText) copyText.textContent = "Copy"; }, 2000);
    }
  };

  // Immediate disconnect handler
  window.disconnectPc = function() {
    isPcConnected = false;
    pcConnectionMode = "disconnected";
    activePcDirHandle = null;
    pcHandleMap = {};
    pcParentMap = {};
    pcInfo = {};
    pcState.files = [];

    var dot = $("pc-status-dot");
    if (dot) {
      dot.className = "status-dot";
      dot.title = "Local PC Disconnected";
    }
    var sideLabel = $("sidebar-pc-label");
    if (sideLabel) sideLabel.textContent = "💻 Connect PC";
    var tree = $("pc-file-tree");
    if (tree) {
      tree.innerHTML = '<div id="pc-disconnected-state" style="padding:22px 14px;text-align:center;color:var(--muted);font-size:12px">'
        + '<div style="font-size:34px;margin-bottom:10px">📂</div>'
        + '<div style="font-weight:700;color:var(--text);font-size:13px;margin-bottom:6px">Connect Your Local PC Folder</div>'
        + '<div style="margin-bottom:14px;line-height:1.5;color:#94a3b8;font-size:11px">Select a local project folder directly from your browser with zero terminal commands, zero installation, and complete sandbox security.</div>'
        + '<button type="button" class="btn btn-primary" style="padding:7px 18px;font-size:12px;font-weight:700;background:linear-gradient(135deg, #0284c7, #38bdf8);border:none;box-shadow:0 2px 10px rgba(56,189,248,0.4)" onclick="connectNativePcFolder()"><span>📂 Open Local Folder</span></button>'
        + '<div style="margin-top:12px"><a href="javascript:void(0)" onclick="openPcTerminalBridgeModal()" style="color:#7dd3fc;font-size:10px;text-decoration:none;border-bottom:1px dashed #7dd3fc">Or use Advanced Terminal Command ↗</a></div>'
        + '</div>';
    }
    var modalBadge = $("pc-modal-status-badge");
    if (modalBadge) {
      modalBadge.textContent = "Disconnected";
      modalBadge.style.background = "rgba(248,113,113,0.15)";
      modalBadge.style.color = "#f87171";
      modalBadge.style.borderColor = "rgba(248,113,113,0.3)";
    }
    var pCard = $("pc-profile-card");
    if (profileCard) profileCard.style.display = "none";
    var mBtn = $("modal-pc-disconnect-btn");
    if (mBtn) mBtn.style.display = "none";
    var statusLine = $("modal-pc-status-line");
    if (statusLine) statusLine.style.display = "flex";

    // Attempt backend disconnect if bridge was used
    api("/v1/connector/disconnect", { method: "POST" }).catch(function(){});
  };

  // Heartbeat Poller for PC Status
  function checkPcConnectorStatus() {
    api("/v1/connector/status", { method: "GET" }).then(function(res) {
      var connected = !!(res && res.connected);
      isPcConnected = connected;

      var sideLabel = $("sidebar-pc-label");
      var modalBadge = $("pc-modal-status-badge");
      var modalMsg = $("modal-pc-status-msg");
      var profileCard = $("pc-profile-card");
      var disconnectBtn = $("modal-pc-disconnect-btn");

      if (connected) {
        var machine = res.hostname || (res.info && res.info.hostname) || "PC";
        pcInfo = res.info || {};
        pcInfo.hostname = machine;
        pcDrivesList = res.drives || pcInfo.drives || [];

        if (sideLabel) sideLabel.textContent = "💻 " + machine;
        var sideBtn = $("sidebar-pc-btn");
        if (sideBtn) sideBtn.title = "Connected to " + machine + " - Click to manage";

        if (modalBadge) {
          modalBadge.textContent = "Connected";
          modalBadge.style.background = "rgba(82,227,150,0.15)";
          modalBadge.style.color = "#52e396";
          modalBadge.style.borderColor = "rgba(82,227,150,0.4)";
        }
        if (modalMsg) modalMsg.innerHTML = '<span style="color:#52e396">✓ Live bridge connected to ' + esc(machine) + ' (' + esc(pcInfo.system || "Windows") + ')</span>';
        if (profileCard) {
          profileCard.style.display = "flex";
          var mName = $("pc-modal-machine-name");
          var oName = $("pc-modal-os-name");
          if (mName) mName.textContent = machine;
          if (oName) oName.textContent = (pcInfo.system || "Windows") + " · Active root: " + (pcCurrentPath || ".");
        }
        if (disconnectBtn) disconnectBtn.style.display = "inline-block";

        updatePcRoots(pcInfo, pcDrivesList);

        if (!window.pcFilesLoaded) {
          loadPcFiles(pcCurrentPath);
        }
      } else {
        if (sideLabel) sideLabel.textContent = "💻 Connect PC";
        if (modalBadge) {
          modalBadge.textContent = "Disconnected";
          modalBadge.style.background = "rgba(248,113,113,0.15)";
          modalBadge.style.color = "#f87171";
          modalBadge.style.borderColor = "rgba(248,113,113,0.3)";
        }
        if (modalMsg) modalMsg.textContent = "Waiting for terminal command execution on your PC...";
        if (profileCard) profileCard.style.display = "none";
        if (disconnectBtn) disconnectBtn.style.display = "none";

        var treeEl = $("pc-file-tree");
        if (treeEl && !treeEl.querySelector(".file-list-items")) {
          treeEl.innerHTML = '<div style="padding:18px 14px;text-align:center;color:var(--muted);font-size:12px">' +
            '<div style="font-size:28px;margin-bottom:8px">💻</div>' +
            '<div style="font-weight:700;color:var(--text);margin-bottom:6px">PC Disconnected</div>' +
            '<div style="margin-bottom:12px;line-height:1.4">Connect your PC using the 1-click terminal command to explore & edit files directly on your machine.</div>' +
            '<button type="button" class="btn btn-primary" style="padding:4px 14px;font-size:11px" onclick="openPcAuthModal()">' +
            '<span>⚡ Connect Local PC</span>' +
            '</button>' +
            '</div>';
        }
      }
    }).catch(function() {});
  }

  // Populate Drive & Folder Dropdown in PC Studio Navbar
  function updatePcRoots(info, drives) {
    var sel = $("pc-root-select");
    if (!sel) return;
    info = info || {};
    drives = drives || info.drives || [];

    var currentVal = sel.value;
    var html = "";

    if (drives && drives.length) {
      html += '<optgroup label="PC Drives">';
      drives.forEach(function(d) {
        html += '<option value="' + esc(d) + '">Drive ' + esc(d) + '</option>';
      });
      html += '</optgroup>';
    }

    var folders = [];
    if (info.desktop) folders.push({ label: "🖥️ Desktop", path: info.desktop });
    if (info.documents) folders.push({ label: "📁 Documents", path: info.documents });
    if (info.downloads) folders.push({ label: "📥 Downloads", path: info.downloads });
    if (info.user_home) folders.push({ label: "🏠 User Home", path: info.user_home });
    if (info.cwd) folders.push({ label: "📍 Workdir", path: info.cwd });

    if (folders.length) {
      html += '<optgroup label="Common Folders">';
      folders.forEach(function(f) {
        html += '<option value="' + esc(f.path) + '">' + esc(f.label) + ' (' + esc(f.path) + ')</option>';
      });
      html += '</optgroup>';
    }

    if (!html) {
      html = '<option value=".">Local PC Workspace</option>';
    }

    sel.innerHTML = html;
    if (currentVal && Array.from(sel.options).some(function(o){ return o.value === currentVal; })) {
      sel.value = currentVal;
    } else if (drives && drives.length && (!pcCurrentPath || pcCurrentPath === ".")) {
      sel.value = drives[0];
      pcCurrentPath = drives[0];
    }
  }

  // Root selector change
  var pcRootSelectEl = $("pc-root-select");
  if (pcRootSelectEl) {
    pcRootSelectEl.onchange = function() {
      var p = this.value;
      if (p) {
        pcCurrentPath = p;
        loadPcFiles(p);
      }
    };
  }

  // Helper: Get Parent Directory
  function getParentDirectory(p) {
    if (!p || p === "." || p === "/" || /^[A-Za-z]:[\\/]?$/.test(p)) return null;
    var norm = p.replace(/[\\/]+$/, "");
    var lastSlash = Math.max(norm.lastIndexOf("/"), norm.lastIndexOf("\\"));
    if (lastSlash === -1) return null;
    var parent = norm.substring(0, lastSlash);
    if (/^[A-Za-z]:$/.test(parent)) parent += "\\";
    if (!parent) parent = "/";
    return parent;
  }

  // Update Breadcrumbs Navigation Bar
  function updatePcBreadcrumbs(dirPath) {
    var bc = $("pc-breadcrumbs");
    if (!bc) return;
    if (!dirPath || dirPath === ".") {
      bc.innerHTML = '<span class="pc-crumb-item" data-crumb-path=".">💻 ' + esc(pcInfo.hostname || "PC") + '</span>';
      return;
    }
    var sep = dirPath.includes("\\") ? "\\" : "/";
    var clean = dirPath.replace(/[\\/]+$/, "");
    var accum = "";
    var html = '<span class="pc-crumb-item" data-crumb-path=".">💻 ' + esc(pcInfo.hostname || "PC") + '</span>';

    var driveMatch = clean.match(/^([A-Za-z]:)(.*)$/);
    if (driveMatch) {
      var driveRoot = driveMatch[1] + "\\";
      accum = driveRoot;
      html += '<span class="pc-crumb-sep">&gt;</span><span class="pc-crumb-item" data-crumb-path="' + esc(driveRoot) + '">' + esc(driveMatch[1]) + '</span>';
      var rem = driveMatch[2].replace(/^[\\/]+/, "");
      if (rem) {
        var segments = rem.split(/[\\/]/).filter(Boolean);
        segments.forEach(function(seg) {
          if (!accum.endsWith("\\") && !accum.endsWith("/")) accum += "\\";
          accum += seg;
          html += '<span class="pc-crumb-sep">&gt;</span><span class="pc-crumb-item" data-crumb-path="' + esc(accum) + '">' + esc(seg) + '</span>';
        });
      }
    } else {
      var parts = clean.split(/[\\/]/).filter(Boolean);
      parts.forEach(function(part) {
        accum += (accum ? "/" : "") + part;
        html += '<span class="pc-crumb-sep">&gt;</span><span class="pc-crumb-item" data-crumb-path="' + esc(accum) + '">' + esc(part) + '</span>';
      });
    }
    bc.innerHTML = html;
  }

  // Breadcrumbs click delegation
  var bcEl = $("pc-breadcrumbs");
  if (bcEl) {
    bcEl.onclick = function(e) {
      var item = e.target.closest(".pc-crumb-item");
      if (item) {
        var p = item.getAttribute("data-crumb-path");
        if (p) loadPcFiles(p);
      }
    };
  }

  // Load PC Files via REST
  function loadPcFiles(dirPath) {
    if (!isPcConnected) return;
    window.pcFilesLoaded = true;
    pcCurrentPath = dirPath;

    // Reset search input value when switching folders so files are never accidentally hidden
    var pcSearchInput = $("pc-file-search");
    if (pcSearchInput && !window._isPcSearching) {
      pcSearchInput.value = "";
      var cBtn = $("pc-clear-search-btn");
      if (cBtn) cBtn.style.display = "none";
    }

    var treeEl = $("pc-file-tree");
    if (!treeEl) return;
    treeEl.innerHTML = '<div style="padding:15px;color:var(--muted);font-size:11px"><span class="spinner"></span> Loading local files from PC...</div>';

    updatePcBreadcrumbs(dirPath);

    var activeRoot = $("pc-active-root");
    if (activeRoot) activeRoot.textContent = "Target: " + (pcInfo.hostname || "PC") + " (" + dirPath + ")";

    api("/v1/connector/files?path=" + encodeURIComponent(dirPath), { method: "GET" }).then(function(res) {
      if (!res.ok) {
        treeEl.innerHTML = '<div style="padding:15px;color:var(--danger);font-size:11px">Failed loading files: ' + esc(res.error || "") + '</div>';
        return;
      }
      var entries = res.entries || [];
      var countEl = $("pc-file-count");
      if (countEl) countEl.textContent = entries.length + " items";

      entries.sort(function(a, b) {
        if (a.is_dir && !b.is_dir) return -1;
        if (!a.is_dir && b.is_dir) return 1;
        return a.name.localeCompare(b.name);
      });

      var parentDir = getParentDirectory(dirPath);
      var html = '<div class="file-list-items" style="padding:4px 0">';

      // "Go Back to Parent Folder" item if not root
      if (parentDir) {
        html += '<div class="file-item dir-item dir-parent-item" data-path="' + esc(parentDir) + '" data-is-dir="true" style="padding:5px 10px;cursor:pointer;display:flex;align-items:center;gap:6px;font-size:12px;color:#38bdf8;background:rgba(56,189,248,0.06);border-radius:4px;margin-bottom:4px;border:1px solid rgba(56,189,248,0.15)">'
              + '<span>⬆</span>'
              + '<span style="font-weight:600;flex:1">.. (Back to Parent Folder)</span>'
              + '<span style="font-size:10px;color:var(--muted)">' + esc(parentDir) + '</span>'
              + '</div>';
      }

      if (entries.length === 0 && !parentDir) {
        treeEl.innerHTML = '<div style="padding:15px;color:var(--muted);font-size:11px">Directory is empty. Click "➕ New File" to create one.</div>';
        return;
      }

      entries.forEach(function(item) {
        var icon = item.is_dir ? "📁" : "📄";
        var isDir = item.is_dir ? "true" : "false";
        var sep = (dirPath.endsWith("/") || dirPath.endsWith("\\")) ? "" : "/";
        var fullPath = dirPath + sep + item.name;
        html += '<div class="file-item ' + (item.is_dir ? 'dir-item' : '') + '" data-path="' + esc(fullPath) + '" data-is-dir="' + isDir + '" data-name="' + esc(item.name) + '" style="padding:4px 10px;cursor:pointer;display:flex;align-items:center;gap:6px;font-size:12px;border-radius:4px">';
        html += '<span>' + icon + '</span>';
        html += '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + esc(item.name) + '</span>';
        html += '</div>';
      });
      html += '</div>';
      treeEl.innerHTML = html;

      // Attach left-click handlers
      treeEl.querySelectorAll(".file-item").forEach(function(el) {
        el.onclick = function() {
          var p = this.getAttribute("data-path");
          var isD = this.getAttribute("data-is-dir") === "true";
          if (isD) {
            pcCurrentPath = p;
            loadPcFiles(p);
          } else {
            openPcFile(p);
          }
        };
      });
    }).catch(function(err) {
      treeEl.innerHTML = '<div style="padding:15px;color:var(--danger);font-size:11px">Error: ' + esc(err.message) + '</div>';
    });
  }

  // Refresh & Back navigation buttons
  var pcBackBtn = $("pc-back-btn");
  if (pcBackBtn) {
    pcBackBtn.onclick = function() {
      var p = getParentDirectory(pcCurrentPath);
      if (p) {
        pcCurrentPath = p;
        loadPcFiles(p);
      }
    };
  }

  var pcRefreshBtn = $("pc-refresh-btn");
  if (pcRefreshBtn) {
    pcRefreshBtn.onclick = function() {
      loadPcFiles(pcCurrentPath || ".");
    };
  }

  // --- PC NEW FILE CREATION MODAL LOGIC ---
  window.openPcNewFileModal = function() {
    if (!isPcConnected) {
      alert("Please connect your PC first before creating files.");
      return;
    }
    var m = $("pc-new-file-modal");
    if (!m) return;
    $("pc-new-file-dir").textContent = pcCurrentPath || ".";
    var inp = $("pc-new-file-name-input");
    if (inp) {
      inp.value = "";
      setTimeout(function() { inp.focus(); }, 100);
    }
    $("pc-new-file-status").textContent = "";
    m.classList.add("open");
  };

  window.closePcNewFileModal = function() {
    var m = $("pc-new-file-modal");
    if (m) m.classList.remove("open");
  };

  window.confirmPcCreateFile = async function() {
    var inp = $("pc-new-file-name-input");
    var name = inp ? inp.value.trim() : "";
    if (!name) {
      alert("Please enter a file name.");
      return;
    }
    var statusEl = $("pc-new-file-status");
    var btn = $("pc-new-file-confirm-btn");

    if (pcConnectionMode === "native_fs" && activePcDirHandle) {
      if (btn) btn.disabled = true;
      if (statusEl) statusEl.innerHTML = '<span class="spinner" style="width:12px;height:12px"></span> Creating file...';
      try {
        var fileHandle = await activePcDirHandle.getFileHandle(name, { create: true });
        if (btn) btn.disabled = false;
        closePcNewFileModal();
        await loadNativePcFolder(activePcDirHandle);
        openPcFile(name);
      } catch (err) {
        if (btn) btn.disabled = false;
        if (statusEl) statusEl.innerHTML = '<span style="color:var(--danger)">Error: ' + esc(err.message) + '</span>';
      }
      return;
    }

    
    var inp = $("pc-new-file-name-input");
    var name = inp ? inp.value.trim() : "";
    if (!name) {
      alert("Please enter a file name.");
      return;
    }
    var sep = pcCurrentPath.includes("/") ? "/" : "\\";
    var fullPath = pcCurrentPath + ((pcCurrentPath.endsWith("/") || pcCurrentPath.endsWith("\\")) ? "" : sep) + name;
    var statusEl = $("pc-new-file-status");
    var btn = $("pc-new-file-confirm-btn");
    if (statusEl) statusEl.innerHTML = '<span class="spinner" style="width:12px;height:12px"></span> Creating file on PC...';
    if (btn) btn.disabled = true;

    api("/v1/connector/file", {
      method: "POST",
      body: { path: fullPath, content: "" }
    }).then(function(res) {
      if (btn) btn.disabled = false;
      if (!res.ok) throw new Error(res.error || "Failed to create file");
      closePcNewFileModal();
      loadPcFiles(pcCurrentPath);
      openPcFile(fullPath);
    }).catch(function(err) {
      if (btn) btn.disabled = false;
      if (statusEl) statusEl.innerHTML = '<span style="color:var(--danger)">Error: ' + esc(err.message) + '</span>';
    });
  };

  function openPcFile(filePath) {
    pcState.activePath = filePath;
    var fileName = filePath.split(/[\/]/).pop();
    var titleEl = $("pc-active-file-title");
    if (titleEl) titleEl.innerHTML = '<span>📄 ' + esc(filePath) + '</span>';
    var tabName = $("pc-tab-name");
    if (tabName) tabName.textContent = fileName;

    // Highlight active in tree
    document.querySelectorAll("#pc-file-tree .file-item").forEach(function(el) {
      if (el.getAttribute("data-path") === filePath) el.classList.add("active");
      else el.classList.remove("active");
    });

    if (pcConnectionMode === "native_fs") {
      var handle = pcHandleMap[filePath];
      if (!handle) {
        console.warn("Handle not found for:", filePath);
        return;
      }
      handle.getFile().then(function(file) {
        return file.text();
      }).then(function(text) {
        var ed = $("pc-code-editor");
        if (ed) {
          ed.value = text;
          updatePcLineNumbers();
          updatePcPreview();
        }
        var status = $("pc-sync-status");
        if (status) status.textContent = "Opened " + fileName;
        var dirty = $("pc-tab-dirty");
        if (dirty) dirty.style.display = "none";
      }).catch(function(err) {
        alert("Could not read local file: " + err.message);
      });
      return;
    }

    api("/v1/connector/file?path=" + encodeURIComponent(filePath), { method: "GET" }).then(function(res) {
      if (!res.ok) {
        alert("Failed reading file: " + (res.error || ""));
        return;
      }
      var ed = $("pc-code-editor");
      if (ed) {
        ed.value = res.content || "";
        updatePcLineNumbers();
        updatePcPreview();
      }
      var status = $("pc-sync-status");
      if (status) status.textContent = "Opened " + fileName;
      var dirty = $("pc-tab-dirty");
      if (dirty) dirty.style.display = "none";
    }).catch(function(err) {
      alert("Error opening file: " + err.message);
    });
  }

  function updatePcLineNumbers() {
    var editor = $("pc-code-editor");
    var lineBox = $("pc-line-numbers");
    if (!editor || !lineBox) return;
    var count = (editor.value.match(/\n/g) || []).length + 1;
    var html = "";
    for (var i = 1; i <= count; i++) {
      html += "<div>" + i + "</div>";
    }
    lineBox.innerHTML = html;
    var meta = $("pc-editor-meta");
    if (meta) meta.textContent = "Lines: " + count + " · Chars: " + editor.value.length;
  }

  function updatePcPreview() {
    var frame = $("pc-preview-frame");
    if (!frame) return;

    var content = $("pc-code-editor") ? $("pc-code-editor").value : "";
    var path = (pcState.activePath || "index.html").toLowerCase();

    if (path.endsWith(".md") || path.endsWith(".markdown")) {
      frame.removeAttribute("src");
      frame.srcdoc = '<!doctype html><html><head><meta charset="utf-8">'
                   + '<style>body{font-family:system-ui,-apple-system,sans-serif;background:#0d1424;color:#edf4ff;padding:28px 36px;line-height:1.6;max-width:860px;margin:0 auto}pre{background:#070b14;padding:14px;border-radius:8px;overflow:auto;color:#78a9ff;border:1px solid rgba(255,255,255,0.08)}h1,h2,h3{color:#fff;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:6px}code{background:rgba(255,255,255,0.08);padding:2px 6px;border-radius:4px;color:#38bdf8}table{border-collapse:collapse;width:100%}th,td{border:1px solid rgba(255,255,255,0.15);padding:8px 12px;text-align:left}</style>'
                   + '</head><body>' + (typeof renderStudioMarkdown === "function" ? renderStudioMarkdown(content) : ('<pre>' + esc(content) + '</pre>')) + '</body></html>';
      return;
    }

    if (path.endsWith(".css")) {
      frame.removeAttribute("src");
      frame.srcdoc = '<!doctype html><html><head><meta charset="utf-8"><style>' + content + '</style>'
                   + '<style>body{font-family:system-ui,sans-serif;padding:30px;background:#0f172a;color:#f8fafc;display:flex;flex-direction:column;gap:16px;align-items:center}.demo-box{padding:24px;border-radius:12px;background:#1e293b;border:1px solid rgba(255,255,255,0.1);max-width:500px;text-align:center}button{padding:8px 16px;border-radius:8px;cursor:pointer}</style>'
                   + '</head><body><div class="demo-box"><h2>🎨 CSS Live Testbed</h2><p>Previewing <code>' + esc(pcState.activePath || "styles.css") + '</code> styles live on PC.</p><button>Sample Button</button></div></body></html>';
      return;
    }

    if (path.endsWith(".js") || path.endsWith(".ts")) {
      frame.removeAttribute("src");
      frame.srcdoc = '<!doctype html><html><head><meta charset="utf-8">'
                   + '<style>body{font-family:monospace;background:#0d1424;color:#78a9ff;padding:20px;margin:0}#console-log{background:#070b14;padding:16px;border-radius:8px;border:1px solid rgba(120,169,255,0.2);min-height:220px;white-space:pre-wrap}.log-line{padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.05)}.log-err{color:#f87171}</style>'
                   + '</head><body><h3 style="color:#fff;margin-top:0">⚡ Live JavaScript Console (' + esc(pcState.activePath || "script.js") + ')</h3><div id="console-log"></div>'
                   + '<script>'
                   + 'var logEl = document.getElementById("console-log");'
                   + 'function log(msg, isErr) { var d = document.createElement("div"); d.className = "log-line" + (isErr ? " log-err" : ""); d.textContent = (isErr ? "❌ " : "▶ ") + msg; logEl.appendChild(d); }'
                   + 'console.log = function() { var args = Array.prototype.slice.call(arguments); log(args.map(function(a){ return typeof a === "object" ? JSON.stringify(a) : a; }).join(" ")); };'
                   + 'console.error = function() { var args = Array.prototype.slice.call(arguments); log(args.map(function(a){ return typeof a === "object" ? JSON.stringify(a) : a; }).join(" "), true); };'
                   + 'window.onerror = function(m, u, l) { log(m + " (line " + l + ")", true); };'
                   + 'try { ' + content + ' } catch(e) { log(e.stack || e.message, true); }'
                   + '</' + 'script></body></html>';
      return;
    }

    if (!content || !content.trim()) {
      frame.removeAttribute("src");
      frame.srcdoc = "<!doctype html><html><body style='background:#0f172a;color:#94a3b8;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0'><div style='text-align:center'><h3>👁️ PC Live Web Preview</h3><p>Enter HTML code in the editor or select a local file to render live from your PC.</p></div></body></html>";
      return;
    }

    frame.removeAttribute("src");
    frame.srcdoc = content;
    frame.style.opacity = "1";
  }

  // Device switcher for PC Preview
  var pcCurrentDevice = "desktop";
  var pcIsLandscape = false;

  function setPcPreviewDevice(device) {
    if (device === "tablet" || device === "mobile") {
      if (typeof requireProFeature === "function" && !requireProFeature("device_simulator", "Tablet and Mobile live testing is a Pro feature! Upgrade for just $5/mo or $27 lifetime to simulate all screens.")) {
        if ($("pc-dev-desktop")) $("pc-dev-desktop").classList.add("active");
        return;
      }
    }
    pcCurrentDevice = device;
    var holder = $("pc-preview-frame-holder");
    if (!holder) return;
    holder.className = "preview-frame-holder";

    if ($("pc-dev-desktop")) $("pc-dev-desktop").classList.remove("active");
    if ($("pc-dev-tablet")) $("pc-dev-tablet").classList.remove("active");
    if ($("pc-dev-mobile")) $("pc-dev-mobile").classList.remove("active");

    if (device === "desktop") {
      if ($("pc-dev-desktop")) $("pc-dev-desktop").classList.add("active");
      if ($("pc-preview-dim-badge")) $("pc-preview-dim-badge").textContent = "100% Fluid";
      pcIsLandscape = false;
      if ($("pc-dev-rotate")) {
        $("pc-dev-rotate").classList.remove("active");
        $("pc-dev-rotate").style.color = "";
      }
    } else if (device === "tablet") {
      if ($("pc-dev-tablet")) $("pc-dev-tablet").classList.add("active");
      holder.classList.add("device-tablet");
      if (pcIsLandscape) holder.classList.add("landscape");
      if ($("pc-preview-dim-badge")) $("pc-preview-dim-badge").textContent = pcIsLandscape ? "1024 × 768 · Tablet" : "768 × 1024 · Tablet";
      if ($("pc-dev-rotate")) {
        $("pc-dev-rotate").classList.toggle("active", pcIsLandscape);
        $("pc-dev-rotate").style.color = pcIsLandscape ? "var(--accent)" : "";
      }
    } else if (device === "mobile") {
      if ($("pc-dev-mobile")) $("pc-dev-mobile").classList.add("active");
      holder.classList.add("device-mobile");
      if (pcIsLandscape) holder.classList.add("landscape");
      if ($("pc-preview-dim-badge")) $("pc-preview-dim-badge").textContent = pcIsLandscape ? "812 × 375 · Mobile" : "375 × 812 · Mobile";
      if ($("pc-dev-rotate")) {
        $("pc-dev-rotate").classList.toggle("active", pcIsLandscape);
        $("pc-dev-rotate").style.color = pcIsLandscape ? "var(--accent)" : "";
      }
    }
  }

  if ($("pc-dev-desktop")) $("pc-dev-desktop").onclick = function() { setPcPreviewDevice("desktop"); };
  if ($("pc-dev-tablet")) $("pc-dev-tablet").onclick = function() { setPcPreviewDevice("tablet"); };
  if ($("pc-dev-mobile")) $("pc-dev-mobile").onclick = function() { setPcPreviewDevice("mobile"); };
  if ($("pc-dev-rotate")) {
    $("pc-dev-rotate").onclick = function() {
      if (pcCurrentDevice === "desktop") return;
      pcIsLandscape = !pcIsLandscape;
      setPcPreviewDevice(pcCurrentDevice);
    };
  }

  // ========================================================
  // --- CSS-ONLY PREVIEW FULLSCREEN (NO BROWSER FULLSCREEN) ---
  // ========================================================
  var pcFullscreenState = { isFullscreen: false };
  var pcPreviewPlaceholder = null;

  function togglePcFullscreen() {
    var prev = $("pc-view-preview");
    if (!prev) return;
    if (pcFullscreenState.isFullscreen) {
      exitPcFullscreen();
    } else {
      enterPcFullscreen();
    }
  }

  function enterPcFullscreen() {
    var prev = $("pc-view-preview");
    if (!prev || pcFullscreenState.isFullscreen) return;
    var ws = $("pc-workspace");
    if (ws) ws.classList.remove("preview-closed");
    var tabBtn = $("pc-tab-btn-preview");
    if (tabBtn) tabBtn.click();

    pcPreviewPlaceholder = document.createElement("div");
    pcPreviewPlaceholder.id = "pc-prev-placeholder";
    prev.parentNode.insertBefore(pcPreviewPlaceholder, prev);
    document.body.appendChild(prev);

    document.body.classList.add("has-preview-fullscreen");
    prev.classList.add("is-fullscreen");
    pcFullscreenState.isFullscreen = true;

    var fBtn = $("pc-preview-fullscreen-btn");
    if (fBtn) {
      fBtn.textContent = "✕ Exit Fullscreen";
      fBtn.style.color = "var(--danger)";
    }

    try {
      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(function(){});
      } else if (document.documentElement.webkitRequestFullscreen) {
        document.documentElement.webkitRequestFullscreen();
      }
    } catch(e) {}
  }

  function exitPcFullscreen() {
    var prev = $("pc-view-preview");
    if (!prev || !pcFullscreenState.isFullscreen) return;
    document.body.classList.remove("has-preview-fullscreen");
    prev.classList.remove("is-fullscreen");
    pcFullscreenState.isFullscreen = false;

    var fBtn = $("pc-preview-fullscreen-btn");
    if (fBtn) {
      fBtn.textContent = "⛶ Fullscreen";
      fBtn.style.color = "";
    }

    try {
      if (document.fullscreenElement) {
        (document.exitFullscreen || document.webkitExitFullscreen).call(document);
      }
    } catch(e) {}

    if (pcPreviewPlaceholder && pcPreviewPlaceholder.parentNode) {
      pcPreviewPlaceholder.parentNode.insertBefore(prev, pcPreviewPlaceholder);
      pcPreviewPlaceholder.parentNode.removeChild(pcPreviewPlaceholder);
      pcPreviewPlaceholder = null;
    }
  }

  if ($("pc-preview-fullscreen-btn")) $("pc-preview-fullscreen-btn").onclick = togglePcFullscreen;

  if ($("pc-preview-popout-btn")) {
    $("pc-preview-popout-btn").onclick = function() {
      var content = $("pc-code-editor") ? $("pc-code-editor").value : "";
      var blob = new Blob([content], { type: "text/html" });
      var url = URL.createObjectURL(blob);
      window.open(url, "_blank");
    };
  }

  if ($("pc-refresh-preview-btn")) {
    $("pc-refresh-preview-btn").onclick = updatePcPreview;
  }

  // PC editor input syncing
  var pcEditor = $("pc-code-editor");
  if (pcEditor) {
    pcEditor.addEventListener("input", function() {
      updatePcLineNumbers();
      clearTimeout(pcPreviewTimer);
      pcPreviewTimer = setTimeout(updatePcPreview, 250);
      var dirty = $("pc-tab-dirty");
      if (dirty) dirty.style.display = "inline";
    });
    pcEditor.addEventListener("scroll", function() {
      var lines = $("pc-line-numbers");
      if (lines) lines.scrollTop = this.scrollTop;
    });
    pcEditor.addEventListener("keydown", function(e) {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        var saveBtn = $("pc-commit-btn");
        if (saveBtn) saveBtn.click();
      }
    });
  }

  // Save to PC Disk Button (passes clean object, no double stringify)
  var pcSaveBtn = $("pc-commit-btn");
  if (pcSaveBtn) {
    pcSaveBtn.onclick = async function() {
      if (!isPcConnected) {
        alert("Cannot save: No local PC or project folder connected.");
        return;
      }
      var path = pcState.activePath;
      if (!path) {
        alert("No active file to save.");
        return;
      }
      var content = $("pc-code-editor") ? $("pc-code-editor").value : "";

      if (pcConnectionMode === "native_fs") {
        try {
          var handle = pcHandleMap[path];
          if (!handle) throw new Error("File handle not found in folder map");
          var writable = await handle.createWritable();
          await writable.write(content);
          await writable.close();

          var dirty = $("pc-tab-dirty");
          if (dirty) dirty.style.display = "none";
          var status = $("pc-sync-status");
          if (status) status.textContent = "Saved to PC (" + new Date().toLocaleTimeString() + ")";

          var btn = $("pc-commit-btn");
          if (btn) {
            var orig = btn.innerHTML;
            btn.innerHTML = '<span>✅ Saved to PC!</span>';
            setTimeout(function() { btn.innerHTML = orig; }, 1400);
          }
          updatePcPreview();
        } catch (err) {
          alert("Error saving file: " + err.message);
        }
        return;
      }

      var status = $("pc-sync-status");
      if (status) status.textContent = "Saving to PC disk...";

      api("/v1/connector/file", {
        method: "POST",
        body: { path: path, content: content }
      }).then(function(res) {
        if (!res.ok) {
          alert("Failed saving file: " + (res.error || ""));
          return;
        }
        var dirty = $("pc-tab-dirty");
        if (dirty) dirty.style.display = "none";
        if (status) status.textContent = "Saved to PC at " + new Date().toLocaleTimeString();
      }).catch(function(err) {
        alert("Error saving: " + err.message);
      });
    };
  }

  // PC Aux Panel Tab Switching
  if ($("pc-tab-btn-preview")) {
    $("pc-tab-btn-preview").onclick = function() {
      $("pc-tab-btn-preview").classList.add("active");
      if ($("pc-tab-btn-ai")) $("pc-tab-btn-ai").classList.remove("active");
      if ($("pc-view-preview")) $("pc-view-preview").style.display = "flex";
      if ($("pc-view-ai")) $("pc-view-ai").style.display = "none";
    };
  }
  if ($("pc-tab-btn-ai")) {
    $("pc-tab-btn-ai").onclick = function() {
      $("pc-tab-btn-ai").classList.add("active");
      if ($("pc-tab-btn-preview")) $("pc-tab-btn-preview").classList.remove("active");
      if ($("pc-view-preview")) $("pc-view-preview").style.display = "none";
      if ($("pc-view-ai")) $("pc-view-ai").style.display = "flex";
    };
  }

  // PC Aux Collapse Button
  var pcBtnCollapseAux = $("pc-btn-collapse-aux");
  if (pcBtnCollapseAux) {
    pcBtnCollapseAux.onclick = function() {
      var ws = $("pc-workspace");
      if (ws) ws.classList.toggle("preview-closed");
    };
  }
  var pcBtnCloseAux = $("pc-btn-close-aux-header");
  if (pcBtnCloseAux) {
    pcBtnCloseAux.onclick = function() {
      var ws = $("pc-workspace");
      if (ws) ws.classList.add("preview-closed");
    };
  }

  // PC Dock Buttons
  var pcDockPreview = $("pc-dock-btn-preview");
  if (pcDockPreview) {
    pcDockPreview.onclick = function() {
      var ws = $("pc-workspace");
      if (ws) ws.classList.remove("preview-closed");
      if ($("pc-tab-btn-preview")) $("pc-tab-btn-preview").click();
    };
  }
  var pcDockAi = $("pc-dock-btn-ai");
  if (pcDockAi) {
    pcDockAi.onclick = function() {
      var ws = $("pc-workspace");
      if (ws) ws.classList.remove("preview-closed");
      if ($("pc-tab-btn-ai")) $("pc-tab-btn-ai").click();
    };
  }

  // PC Widen / Maximize Aux Button
  var pcExpandAux = $("pc-btn-expand-aux");
  if (pcExpandAux) {
    pcExpandAux.onclick = function() {
      var p = $("pc-aux-panel");
      var ws = $("pc-workspace");
      if (!p) return;
      if (ws) ws.classList.remove("preview-closed");
      p.classList.toggle("aux-wide");
      var isW = p.classList.contains("aux-wide");
      var lbl = $("pc-expand-aux-label");
      if (lbl) lbl.textContent = isW ? "Standard" : "Widen";
    };
  }

  // Wrap toggle
  var pcWrapBtn = $("pc-btn-toggle-wrap");
  if (pcWrapBtn) {
    pcWrapBtn.onclick = function() {
      var ed = $("pc-code-editor");
      if (!ed) return;
      var cur = ed.getAttribute("wrap") === "on";
      ed.setAttribute("wrap", cur ? "off" : "on");
      this.textContent = cur ? "Wrap: OFF" : "Wrap: ON";
    };
  }

  // PC Search filter with tracking flag
  var pcSearch = $("pc-file-search");
  if (pcSearch) {
    pcSearch.addEventListener("input", function() {
      window._isPcSearching = true;
      var val = this.value.toLowerCase().trim();
      var clearBtn = $("pc-clear-search-btn");
      if (clearBtn) clearBtn.style.display = val ? "block" : "none";
      var items = document.querySelectorAll("#pc-file-tree .file-item:not(.dir-parent-item)");
      var visible = 0;
      items.forEach(function(item) {
        var p = (item.getAttribute("data-path") || "").toLowerCase();
        var match = !val || p.includes(val);
        item.style.display = match ? "flex" : "none";
        if (match) visible++;
      });
      var countEl = $("pc-file-count");
      if (countEl) countEl.textContent = val ? (visible + " / " + items.length) : (items.length + " items");
    });
  }
  var pcClearSearch = $("pc-clear-search-btn");
  if (pcClearSearch) {
    pcClearSearch.onclick = function() {
      window._isPcSearching = false;
      if (pcSearch) {
        pcSearch.value = "";
        pcSearch.dispatchEvent(new Event("input"));
      }
    };
  }

  // PC AI Co-Pilot chat send - routes to console/request with full active context
  function sendPcAiPrompt() {
    if (typeof canSendAiPrompt === "function" && !canSendAiPrompt()) return;
    var promptEl = $("pc-ai-prompt");
    var chat = $("pc-ai-chat");
    if (!promptEl || !chat) return;
    var q = promptEl.value.trim();
    if (!q) return;

    var uMsg = document.createElement("div");
    uMsg.className = "ai-msg user";
    uMsg.textContent = q;
    chat.appendChild(uMsg);
    promptEl.value = "";

    var sMsg = document.createElement("div");
    sMsg.className = "ai-msg assistant";
    sMsg.innerHTML = '<span class="spinner" style="width:12px;height:12px"></span> Analyzing with Hashtag PC Co-Pilot...';
    chat.appendChild(sMsg);
    chat.scrollTop = chat.scrollHeight;

    var edContent = $("pc-code-editor") ? $("pc-code-editor").value : "";
    var currentFile = pcState.activePath || "untitled";

    api("/v1/console/request", {
      method: "POST",
      body: {
        request: q,
        message: q,
        body_id: "pc-cloud-studio",
        context: {
          target_pc: pcInfo.hostname || "PC",
          active_path: currentFile,
          active_file: currentFile,
          file_content: edContent
        }
      }
    }).then(function(res) {
      var ans = res.response || res.result || res.answer || res.reply || res.text || "Done.";
      if (typeof ans === "object") {
        ans = ans.response || ans.message || JSON.stringify(ans, null, 2);
      }
      sMsg.innerHTML = typeof renderStudioMarkdown === "function" ? renderStudioMarkdown(ans) : ('<pre style="white-space:pre-wrap">' + esc(ans) + '</pre>');
      chat.scrollTop = chat.scrollHeight;
    }).catch(function(err) {
      sMsg.innerHTML = '<span style="color:var(--danger)">Error: ' + esc(err.message) + '</span>';
    });
  }

  var pcAiSendBtn = $("pc-ai-send-btn");
  if (pcAiSendBtn) pcAiSendBtn.onclick = sendPcAiPrompt;

  var pcAiPrompt = $("pc-ai-prompt");
  if (pcAiPrompt) {
    pcAiPrompt.onkeydown = function(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendPcAiPrompt();
      }
    };
  }

  // ========================================================
  // --- CONTEXT MENU & CROSS-BRIDGE FILE TRANSFER ---
  // ========================================================
  var ctxMenu = $("studio-context-menu");

  function showContextMenu(x, y, source, path, isDir, name) {
    if (!ctxMenu) return;
    currentContextTarget = { source: source, path: path, isDir: isDir, name: name };

    var transIcon = $("ctx-transfer-icon");
    var transLabel = $("ctx-transfer-label");

    if (source === "pc") {
      if (transIcon) transIcon.textContent = "🐙";
      if (transLabel) transLabel.textContent = "Transfer to GitHub Repository...";
    } else {
      if (transIcon) transIcon.textContent = "💻";
      if (transLabel) transLabel.textContent = "Transfer to Local PC...";
    }

    ctxMenu.style.display = "block";
    var mw = ctxMenu.offsetWidth || 230;
    var mh = ctxMenu.offsetHeight || 150;
    var posX = (x + mw > window.innerWidth) ? (window.innerWidth - mw - 10) : x;
    var posY = (y + mh > window.innerHeight) ? (window.innerHeight - mh - 10) : y;
    ctxMenu.style.left = posX + "px";
    ctxMenu.style.top = posY + "px";
  }

  function closeContextMenu() {
    if (ctxMenu) ctxMenu.style.display = "none";
  }

  document.addEventListener("click", function(e) {
    if (ctxMenu && !ctxMenu.contains(e.target)) {
      closeContextMenu();
    }
  });

  // Attach event delegation for Right-Click Context Menu on BOTH GitHub and PC trees
  var ghFileTree = $("file-tree");
  if (ghFileTree) {
    ghFileTree.addEventListener("contextmenu", function(e) {
      var item = e.target.closest(".tree-item");
      if (item) {
        e.preventDefault();
        e.stopPropagation();
        var p = item.getAttribute("data-path");
        if (p) {
          var nm = p.split("/").pop();
          showContextMenu(e.clientX, e.clientY, "gh", p, false, nm);
        }
      }
    });
  }

  var pcFileTree = $("pc-file-tree");
  if (pcFileTree) {
    pcFileTree.addEventListener("contextmenu", function(e) {
      var item = e.target.closest(".file-item:not(.dir-parent-item)");
      if (item) {
        e.preventDefault();
        e.stopPropagation();
        var p = item.getAttribute("data-path");
        var isD = item.getAttribute("data-is-dir") === "true";
        var nm = item.getAttribute("data-name") || p.split(/[\\/]/).pop();
        showContextMenu(e.clientX, e.clientY, "pc", p, isD, nm);
      }
    });
  }

  // Context Menu Actions
  var ctxTransferBtn = $("ctx-transfer-btn");
  if (ctxTransferBtn) {
    ctxTransferBtn.onclick = function() {
      closeContextMenu();
      if (currentContextTarget.source === "pc") {
        openGhTransferModal(currentContextTarget.path, currentContextTarget.name);
      } else {
        openPcTransferModal(currentContextTarget.path, currentContextTarget.name);
      }
    };
  }

  var ctxOpenBtn = $("ctx-open-btn");
  if (ctxOpenBtn) {
    ctxOpenBtn.onclick = function() {
      closeContextMenu();
      if (currentContextTarget.source === "pc") {
        openPcFile(currentContextTarget.path);
      } else {
        if (typeof openFile === "function") openFile(currentContextTarget.path);
      }
    };
  }

  var ctxPreviewBtn = $("ctx-preview-btn");
  if (ctxPreviewBtn) {
    ctxPreviewBtn.onclick = function() {
      closeContextMenu();
      if (currentContextTarget.source === "pc") {
        openPcFile(currentContextTarget.path);
        if ($("pc-tab-btn-preview")) $("pc-tab-btn-preview").click();
      } else {
        if (typeof openFile === "function") openFile(currentContextTarget.path);
        if ($("tab-btn-preview")) $("tab-btn-preview").click();
      }
    };
  }

  var ctxCopyBtn = $("ctx-copy-btn");
  if (ctxCopyBtn) {
    ctxCopyBtn.onclick = function() {
      closeContextMenu();
      var p = currentContextTarget.path || "";
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(p);
      }
      alert("Copied to clipboard: " + p);
    };
  }

  // --- PC -> GitHub Transfer Modal Logic ---
  window.openGhTransferModal = function(pcFilePath, fileName) {
    var modal = $("modal-transfer-to-gh");
    if (!modal) return;
    $("trans-gh-source-path").textContent = pcFilePath;
    var baseName = fileName || pcFilePath.split(/[\\/]/).pop();
    $("trans-gh-repo-path").value = baseName;
    $("trans-gh-commit-msg").value = "feat: transfer " + baseName + " from local PC";
    $("trans-gh-status-line").textContent = "";

    var repoSel = $("trans-gh-target-repo");
    if (repoSel) {
      // Fast pre-population from current session options or state.repos
      var reposList = [];
      var ghSelect = $("repo-select");
      if (ghSelect && ghSelect.options && ghSelect.options.length) {
        Array.from(ghSelect.options).forEach(function(opt) {
          if (opt.value && !opt.value.startsWith("(")) {
            reposList.push(opt.value);
          }
        });
      }
      if (typeof state !== "undefined" && state.repos && state.repos.length) {
        state.repos.forEach(function(r) {
          var name = r.full_name || r.name;
          if (name && !reposList.includes(name)) reposList.push(name);
        });
      }

      function populateRepos(list) {
        if (!list || !list.length) {
          repoSel.innerHTML = '<option value="">No repositories found (Connect GitHub)</option>';
          return;
        }
        var h = "";
        list.forEach(function(r) {
          var val = typeof r === "string" ? r : (r.full_name || r.name);
          var curRepo = (typeof state !== "undefined" && state.repo) ? state.repo : "";
          var sel = (val === curRepo) ? "selected" : "";
          h += '<option value="' + esc(val) + '" ' + sel + '>' + esc(val) + '</option>';
        });
        repoSel.innerHTML = h;
      }

      if (reposList.length) {
        populateRepos(reposList);
      } else {
        repoSel.innerHTML = '<option value="">Loading repositories...</option>';
      }

      // Always fetch latest from server too
      api("/v1/github/project/repos").then(function(res) {
        var fetched = res && (res.repositories || res.repos || (Array.isArray(res) ? res : []));
        if (fetched && fetched.length) {
          populateRepos(fetched);
        } else if (!reposList.length) {
          repoSel.innerHTML = '<option value="">No repositories found (Connect GitHub)</option>';
        }
      }).catch(function(err) {
        if (!reposList.length) {
          repoSel.innerHTML = '<option value="">Failed loading repositories: ' + esc(err.message) + '</option>';
        }
      });
    }

    modal.classList.add("open");
  };

  window.closeGhTransferModal = function() {
    var modal = $("modal-transfer-to-gh");
    if (modal) modal.classList.remove("open");
  };

  window.executeTransferToGitHub = function() {
    if (typeof canPerformTransfer === "function" && !canPerformTransfer()) return;
    var pcFilePath = $("trans-gh-source-path").textContent;
    var repo = $("trans-gh-target-repo").value;
    var branch = $("trans-gh-branch").value.trim() || "main";
    var repoPath = $("trans-gh-repo-path").value.trim();
    var commitMsg = $("trans-gh-commit-msg").value.trim();
    var statusLine = $("trans-gh-status-line");
    var submitBtn = $("trans-gh-submit-btn");

    if (!repo) {
      alert("Please select a target GitHub repository.");
      return;
    }
    if (!repoPath) {
      alert("Please specify the target file path in the repository.");
      return;
    }

    if (submitBtn) submitBtn.disabled = true;
    if (statusLine) statusLine.innerHTML = '<span class="spinner" style="width:12px;height:12px"></span> Reading file from PC...';

    var readPromise;
    if (pcConnectionMode === "native_fs") {
      var handle = pcHandleMap[pcFilePath];
      readPromise = handle ? handle.getFile().then(function(f){ return f.text(); }) : Promise.reject(new Error("File not found in local folder"));
    } else {
      readPromise = api("/v1/connector/file?path=" + encodeURIComponent(pcFilePath), { method: "GET" }).then(function(fileRes) {
        if (!fileRes.ok) throw new Error("Failed to read file from PC: " + (fileRes.error || ""));
        return fileRes.content || "";
      });
    }

    readPromise.then(function(content) {
      if (statusLine) statusLine.innerHTML = '<span class="spinner" style="width:12px;height:12px"></span> Committing to ' + esc(repo) + ' (' + esc(branch) + ')...';

      return api("/v1/github/project/file", {
        method: "POST",
        body: {
          repo: repo,
          branch: branch,
          path: repoPath,
          content: content,
          message: commitMsg || ("feat: transfer " + repoPath + " from local PC")
        }
      });
    }).then(function(ghRes) {
      if (submitBtn) submitBtn.disabled = false;
      if (!ghRes.ok) {
        throw new Error(ghRes.error || "GitHub commit failed");
      }
      if (statusLine) statusLine.innerHTML = '<span style="color:#52e396;font-weight:700">✓ Successfully committed to ' + esc(repo) + '/' + esc(repoPath) + '!</span>';
      setTimeout(function() {
        closeGhTransferModal();
        alert("✓ File successfully transferred to GitHub repository " + repo + " (" + branch + ")!");
        if (typeof state !== "undefined" && state.repo === repo && typeof loadProjectTree === "function") {
          loadProjectTree();
        }
      }, 900);
    }).catch(function(err) {
      if (submitBtn) submitBtn.disabled = false;
      if (statusLine) statusLine.innerHTML = '<span style="color:var(--danger)">Error: ' + esc(err.message) + '</span>';
    });
  };

  // --- GitHub -> PC Transfer Modal Logic ---
  window.openPcTransferModal = function(ghFilePath, fileName) {
    var modal = $("modal-transfer-to-pc");
    if (!modal) return;
    var fullSrc = (typeof state !== "undefined" && state.repo ? state.repo + "/" : "") + ghFilePath;
    $("trans-pc-source-path").textContent = fullSrc;
    $("trans-pc-source-path").setAttribute("data-gh-path", ghFilePath);

    var fName = fileName || ghFilePath.split(/[\\/]/).pop();
    $("trans-pc-target-filename").value = fName;

    // Set default target directory
    var defDir = (pcCurrentPath && pcCurrentPath !== ".") ? pcCurrentPath : (pcInfo.desktop || (pcDrivesList && pcDrivesList[0]) || "C:\\");
    $("trans-pc-target-dir").value = defDir;

    updatePcTargetFullPathPreview();
    $("trans-pc-status-line").textContent = "";
    modal.classList.add("open");
  };

  window.closePcTransferModal = function() {
    var modal = $("modal-transfer-to-pc");
    if (modal) modal.classList.remove("open");
  };

  window.setPcTargetFolder = function(type) {
    var dirInput = $("trans-pc-target-dir");
    if (!dirInput) return;
    if (type === "current") {
      dirInput.value = pcCurrentPath || ".";
    } else if (type === "desktop") {
      dirInput.value = pcInfo.desktop || "C:\\Users\\" + (pcInfo.username || "user") + "\\Desktop";
    } else if (type === "documents") {
      dirInput.value = pcInfo.documents || "C:\\Users\\" + (pcInfo.username || "user") + "\\Documents";
    } else if (type === "downloads") {
      dirInput.value = pcInfo.downloads || "C:\\Users\\" + (pcInfo.username || "user") + "\\Downloads";
    }
    updatePcTargetFullPathPreview();
  };

  window.updatePcTargetFullPathPreview = function() {
    var dir = ($("trans-pc-target-dir") ? $("trans-pc-target-dir").value.trim() : "");
    var fn = ($("trans-pc-target-filename") ? $("trans-pc-target-filename").value.trim() : "file.txt");
    var previewEl = $("trans-pc-target-full-path");
    var sep = dir.includes("/") ? "/" : "\\";
    var full = dir + ((dir.endsWith("/") || dir.endsWith("\\")) ? "" : sep) + fn;
    if (previewEl) previewEl.textContent = full;
  };

  window.executeTransferToPc = function() {
    if (typeof canPerformTransfer === "function" && !canPerformTransfer()) return;
    if (!isPcConnected) {
      alert("No local PC connected. Please connect your PC first.");
      return;
    }
    var ghPath = $("trans-pc-source-path").getAttribute("data-gh-path");
    var repo = (typeof state !== "undefined" && state.repo) ? state.repo : "";
    var targetFull = $("trans-pc-target-full-path").textContent.trim();
    var statusLine = $("trans-pc-status-line");
    var submitBtn = $("trans-pc-submit-btn");

    if (!targetFull || targetFull === "...") {
      alert("Please provide a valid target file path on PC.");
      return;
    }

    if (submitBtn) submitBtn.disabled = true;
    if (statusLine) statusLine.innerHTML = '<span class="spinner" style="width:12px;height:12px"></span> Reading file from GitHub...';

    api("/v1/github/project/file?repo=" + encodeURIComponent(repo) + "&path=" + encodeURIComponent(ghPath)).then(async function(ghRes) {
      if (!ghRes.ok) {
        throw new Error("Failed to read file from GitHub: " + (ghRes.error || ""));
      }
      var content = ghRes.content || "";

      if (pcConnectionMode === "native_fs" && activePcDirHandle) {
        if (statusLine) statusLine.innerHTML = '<span class="spinner" style="width:12px;height:12px"></span> Writing file to local project folder...';
        var fileName = ghPath.split(/[\/]/).pop();
        var handle = await activePcDirHandle.getFileHandle(fileName, { create: true });
        var writable = await handle.createWritable();
        await writable.write(content);
        await writable.close();

        if (statusLine) statusLine.innerHTML = '<span style="color:#10b981;font-weight:700">✅ File transferred to PC folder successfully!</span>';
        if (submitBtn) submitBtn.disabled = false;
        setTimeout(function() {
          closePcTransferModal();
          loadNativePcFolder(activePcDirHandle);
          openPcFile(fileName);
        }, 1200);
        return;
      }

      if (statusLine) statusLine.innerHTML = '<span class="spinner" style="width:12px;height:12px"></span> Writing file to PC disk...';

      return api("/v1/connector/file", {
        method: "POST",
        body: {
          path: targetFull,
          content: content
        }
      });
    }).then(function(pcRes) {
      if (submitBtn) submitBtn.disabled = false;
      if (!pcRes.ok) {
        throw new Error(pcRes.error || "Failed to write file on PC");
      }
      if (statusLine) statusLine.innerHTML = '<span style="color:#52e396;font-weight:700">✓ Successfully saved file to PC disk!</span>';
      setTimeout(function() {
        closePcTransferModal();
        alert("✓ File successfully transferred and saved to PC at:\n" + targetFull);
        var dirOfFile = getParentDirectory(targetFull);
        if (dirOfFile && dirOfFile === pcCurrentPath) {
          loadPcFiles(pcCurrentPath);
        }
      }, 900);
    }).catch(function(err) {
      if (submitBtn) submitBtn.disabled = false;
      if (statusLine) statusLine.innerHTML = '<span style="color:var(--danger)">Error: ' + esc(err.message) + '</span>';
    });
  };

  // Keyboard shortcut: Escape exits preview fullscreen and context menu
  document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
      if (typeof exitFullscreen === "function" && fullscreenState.isFullscreen) exitFullscreen();
      if (pcFullscreenState.isFullscreen) exitPcFullscreen();
      closeContextMenu();
    }
  });

  // Heartbeat initialization
  checkPcConnectorStatus();
  setInterval(checkPcConnectorStatus, 2500);


  // ========================================================
  // --- CYBER EYE ENGINE (EXACTLY 2 EYES: PREVIEW TAB EYE & DOCK BUTTON EYE) ---
  (function initCyberEyeEngine() {
    var eyes = [
      { id: "eye-tab", el: $("eye-tab"), iris: null },
      { id: "eye-dock", el: $("eye-dock"), iris: null },
      { id: "pc-eye-tab", el: $("pc-eye-tab"), iris: null },
      { id: "pc-eye-dock", el: $("pc-eye-dock"), iris: null }
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

    // 4. Code Editor Typing Tracker (Locks gaze directly on active editor)
    var ghEditor = $("code-editor");
    var localPcEditor = $("pc-code-editor");

    function onEditorActivity(activeEditorEl) {
      if (!activeEditorEl) return;
      isTyping = true;
      clearTimeout(typingTimer);

      var edRect = activeEditorEl.getBoundingClientRect();
      var targetX = edRect.left + Math.min(edRect.width * 0.35, 300);
      var targetY = edRect.top + Math.min(edRect.height * 0.4, 250);

      lookAt(targetX, targetY);

      typingTimer = setTimeout(function() {
        isTyping = false;
        lookAt(lastMouseX, lastMouseY);
      }, 1200);
    }

    if (ghEditor) {
      ghEditor.addEventListener("input", function() { onEditorActivity(ghEditor); }, { passive: true });
      ghEditor.addEventListener("keydown", function(e) {
        if (e.key && (e.key.length === 1 || e.key === "Backspace" || e.key === "Enter")) {
          onEditorActivity(ghEditor);
        }
      }, { passive: true });
    }

    if (localPcEditor) {
      localPcEditor.addEventListener("input", function() { onEditorActivity(localPcEditor); }, { passive: true });
      localPcEditor.addEventListener("keydown", function(e) {
        if (e.key && (e.key.length === 1 || e.key === "Backspace" || e.key === "Enter")) {
          onEditorActivity(localPcEditor);
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
