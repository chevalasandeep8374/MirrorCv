import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
MOCKUP_DIR = ROOT / "redesign_reference" / "mockups"
COMP_DIR = ROOT / "redesign_reference" / "comparisons"
MATRIX_DIR = ROOT / "redesign_reference" / "glass_matrix"
ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference")
ARTIFACT_MATRIX = ARTIFACT_DIR / "glass_matrix"
ARTIFACT_COMP = ARTIFACT_DIR / "comparisons"

MOCKUP_DIR.mkdir(parents=True, exist_ok=True)
COMP_DIR.mkdir(parents=True, exist_ok=True)
MATRIX_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_MATRIX.mkdir(parents=True, exist_ok=True)
ARTIFACT_COMP.mkdir(parents=True, exist_ok=True)

# 1. Read existing HTML definitions or define them cleanly without external fonts
LANDING_HERO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MirrorCV — Landing Hero (Dual-Pane Editor Structure & Glass System)</title>
  <style>
    :root {
      --bg-page: #FFFFFF;
      --bg-stage: #E9E3FA;
      --border-stage: #D8D1F4;
      --border-subtle: #E2E8F0;
      --text-main: #0F172A;
      --text-muted: #475569;
      --text-dim: #94A3B8;
      --primary: #2563EB;
      --primary-bevel: #1D4FBA;
      --primary-hover: #1D4ED8;
      --accent-purple: #775BCC;
      --accent-purple-light: #EEEAFF;
      --badge-success-bg: #DCFCE7;
      --badge-success-text: #166534;
      --radius-sm: 6px;
      --radius-btn: 8px;
      --radius-card: 12px;
      --radius-stage: 14px;
      --shadow-btn: 0px 3px 0px 0px var(--primary-bevel);
      --shadow-card: 0px 4px 12px rgba(15, 23, 42, 0.05);

      /* Glass System Variables */
      --glass-1-bg: rgba(255, 255, 255, 0.70);
      --glass-1-blur: 16px;
      --glass-1-border: rgba(255, 255, 255, 0.65);
      --glass-1-edge: rgba(15, 23, 42, 0.06);
      --glass-1-highlight: inset 0 1px 0 0 rgba(255, 255, 255, 0.90);
      --glass-1-shadow: 0 4px 16px 0 rgba(15, 23, 42, 0.05);

      --glass-2-bg: rgba(255, 255, 255, 0.82);
      --glass-2-blur: 20px;
      --glass-2-border: rgba(255, 255, 255, 0.80);
      --glass-2-edge: rgba(15, 23, 42, 0.08);
      --glass-2-shadow: 0 10px 25px -3px rgba(15, 23, 42, 0.08);

      --frosted-card-bg: rgba(255, 255, 255, 0.92);
      --frosted-card-border: #E2E8F0;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
      background: var(--bg-page);
      color: var(--text-main);
      overflow-x: hidden;
      line-height: 1.5;
    }

    /* Ambient Hero Radial Gradient */
    .hero-wrapper {
      background: radial-gradient(75% 65% at 50% 0%, #E9E3FA 0%, #DBEAFE 35%, #FDF8F3 70%, #FFFFFF 100%);
      padding-bottom: 80px;
    }

    /* Glass-1 Sticky Header */
    header.site-header {
      position: sticky;
      top: 0;
      z-index: 50;
      background: var(--glass-1-bg);
      -webkit-backdrop-filter: blur(var(--glass-1-blur)) saturate(160%);
      backdrop-filter: blur(var(--glass-1-blur)) saturate(160%);
      border-bottom: 1px solid var(--border-subtle);
      height: 64px;
      display: flex;
      align-items: center;
      padding: 0 40px;
    }
    .header-inner {
      width: 100%;
      max-width: 1240px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .brand-logo {
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.8px;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 6px;
      text-decoration: none;
    }
    .brand-logo .dot {
      width: 8px;
      height: 8px;
      background: var(--primary);
      border-radius: 50%;
    }
    nav.nav-links {
      display: flex;
      align-items: center;
      gap: 28px;
    }
    nav.nav-links a {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 14px;
      font-weight: 600;
      transition: color 0.15s ease;
    }
    nav.nav-links a:hover {
      color: var(--text-main);
    }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .btn-login {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-main);
      text-decoration: none;
      padding: 7px 16px;
      border-radius: var(--radius-btn);
      border: 1px solid var(--border-subtle);
      background: #FFFFFF;
      transition: all 0.15s;
    }
    .btn-login:hover {
      background: #F8FAFC;
    }
    .btn-cta {
      font-size: 14px;
      font-weight: 600;
      color: #FFFFFF;
      text-decoration: none;
      padding: 8px 18px;
      border-radius: var(--radius-btn);
      background: var(--primary);
      box-shadow: var(--shadow-btn);
      transition: all 0.15s ease;
    }
    .btn-cta:hover {
      background: var(--primary-hover);
    }

    /* Hero Center Section */
    .hero-container {
      max-width: 1240px;
      margin: 0 auto;
      padding: 56px 24px 32px;
      text-align: center;
    }
    .announcement-pill {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: rgba(255, 255, 255, 0.75);
      -webkit-backdrop-filter: blur(12px);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.8);
      outline: 1px solid rgba(119, 91, 204, 0.15);
      padding: 4px 14px 4px 6px;
      border-radius: 9999px;
      margin-bottom: 24px;
      box-shadow: 0 2px 8px rgba(119, 91, 204, 0.08);
      font-size: 13px;
      color: var(--accent-purple);
      font-weight: 600;
      text-decoration: none;
    }
    .announcement-badge {
      background: var(--primary);
      color: #FFFFFF;
      font-size: 11px;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 9999px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    h1.hero-title {
      font-size: clamp(40px, 5.2vw, 68px);
      font-weight: 800;
      line-height: 1.1;
      letter-spacing: -2.8px;
      color: var(--text-main);
      max-width: 980px;
      margin: 0 auto 18px;
    }
    p.hero-sub {
      font-size: 18px;
      color: var(--text-muted);
      max-width: 680px;
      margin: 0 auto 32px;
      line-height: 1.6;
    }
    .hero-buttons {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 14px;
      margin-bottom: 24px;
    }
    .btn-hero-primary {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 700;
      color: #FFFFFF;
      background: var(--primary);
      padding: 13px 28px;
      border-radius: var(--radius-btn);
      text-decoration: none;
      box-shadow: 0px 3px 0px 0px var(--primary-bevel);
      transition: all 0.15s ease;
    }
    .btn-hero-primary:hover {
      background: var(--primary-hover);
    }
    .btn-hero-secondary {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.85);
      -webkit-backdrop-filter: blur(12px);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-subtle);
      padding: 13px 24px;
      border-radius: var(--radius-btn);
      text-decoration: none;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
      transition: all 0.15s ease;
    }
    .btn-hero-secondary:hover {
      background: #FFFFFF;
    }
    .micro-claims {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 28px;
      font-size: 13px;
      color: var(--text-muted);
      font-weight: 500;
      margin-bottom: 40px;
    }
    .micro-claim-item {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .micro-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #10B981;
    }

    /* STAGE WRAPPER */
    .stage-wrapper {
      max-width: 1240px;
      margin: 0 auto;
      padding: 0 16px;
    }
    .stage-container {
      background: var(--bg-stage);
      background-image: radial-gradient(110% 90% at 50% 10%, #E9E3FA 0%, #EEEAFF 55%, #F4F1FD 100%);
      border: 1px solid var(--border-stage);
      border-radius: var(--radius-stage);
      padding: 24px;
      box-shadow: 0px 12px 36px rgba(15, 23, 42, 0.08);
    }
    .stage-header-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      padding: 0 4px;
    }
    .stage-label-live {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: #5B3FB8;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      background: #10B981;
      border-radius: 50%;
      box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }
    .stage-caption {
      font-size: 12px;
      font-weight: 700;
      color: #6D54B5;
      text-decoration: none;
    }

    /* App Window */
    .app-window {
      background: #FFFFFF;
      border-radius: 12px;
      border: 1px solid rgba(216, 209, 244, 0.8);
      box-shadow: 0 16px 40px -10px rgba(45, 30, 90, 0.12);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    /* Window Top Bar (Glass-1) */
    .app-topbar {
      background: var(--glass-1-bg);
      -webkit-backdrop-filter: blur(16px) saturate(160%);
      backdrop-filter: blur(16px) saturate(160%);
      border-bottom: 1px solid var(--border-subtle);
      height: 52px;
      padding: 0 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .window-controls {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-right: 16px;
    }
    .window-dot {
      width: 11px;
      height: 11px;
      border-radius: 50%;
    }
    .dot-close { background: #FF5F56; }
    .dot-min { background: #FFBD2E; }
    .dot-max { background: #27C93F; }

    .app-topbar-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .resume-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
    }
    .resume-name {
      font-weight: 700;
      color: var(--text-main);
    }
    .save-pill {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      background: rgba(255, 255, 255, 0.8);
      border: 1px solid var(--border-subtle);
      border-radius: 9999px;
      padding: 2px 10px;
      font-size: 11px;
      font-weight: 600;
      color: #166534;
    }
    .save-dot {
      width: 6px;
      height: 6px;
      background: #166534;
      border-radius: 50%;
    }

    /* Tab Strip */
    .app-tabs {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .app-tab {
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
    }
    .app-tab.active {
      color: var(--primary);
      background: rgba(37, 99, 235, 0.08);
    }

    .app-topbar-right {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .btn-action-sm {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      background: #FFFFFF;
      border: 1px solid var(--border-subtle);
      padding: 5px 12px;
      border-radius: 6px;
    }
    .btn-export-primary {
      font-size: 12px;
      font-weight: 700;
      color: #FFFFFF;
      background: var(--primary);
      padding: 6px 14px;
      border-radius: 6px;
      box-shadow: 0px 2px 0px 0px var(--primary-bevel);
    }

    /* DUAL-PANE BODY */
    .app-body {
      display: grid;
      grid-template-columns: 46% 54%;
      height: 580px;
      background: #FAFAFC;
    }

    /* LEFT PANE: FORM CARDS & AI VERIFIER */
    .editor-pane {
      border-right: 1px solid var(--border-subtle);
      padding: 20px;
      overflow-y: hidden;
      display: flex;
      flex-direction: column;
      gap: 16px;
      background: #F8FAFC;
    }

    /* Section Card */
    .section-card {
      background: var(--frosted-card-bg);
      border: 1px solid var(--frosted-card-border);
      border-radius: 10px;
      padding: 16px;
      box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
    }
    .section-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .section-card-title {
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .section-tag {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      padding: 2px 8px;
      border-radius: 4px;
      background: #EEEAFF;
      color: #775BCC;
    }
    .entry-badge {
      font-size: 11px;
      color: var(--text-dim);
      font-weight: 600;
    }

    /* Experience Item in Editor */
    .form-item {
      margin-bottom: 12px;
    }
    .item-role-line {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 4px;
    }
    .item-role {
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
    }
    .item-company {
      font-size: 12px;
      color: var(--primary);
      font-weight: 600;
    }
    .item-dates {
      font-size: 11px;
      color: var(--text-dim);
    }

    /* Bullet Point with Verifier Diff */
    .bullet-box {
      background: #FFFFFF;
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 12px;
      line-height: 1.5;
      color: var(--text-main);
    }
    .verifier-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--badge-success-bg);
      color: var(--badge-success-text);
      font-size: 10px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      margin-bottom: 6px;
    }
    .diff-highlight {
      background: rgba(34, 197, 94, 0.12);
      color: #15803D;
      font-weight: 600;
      padding: 0 4px;
      border-radius: 2px;
    }

    /* Skills Card */
    .skills-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }
    .skill-chip {
      font-size: 11px;
      font-weight: 600;
      background: #FFFFFF;
      border: 1px solid var(--border-subtle);
      padding: 3px 8px;
      border-radius: 4px;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .skill-level-dot {
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: var(--primary);
    }

    /* RIGHT PANE: LIVE FLOATING A4 RESUME PREVIEW */
    .preview-pane {
      background: #EEF2F6;
      padding: 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      position: relative;
      overflow: hidden;
    }

    /* Floating A4 Paper Sheet */
    .resume-paper {
      width: 100%;
      max-width: 480px;
      background: #FFFFFF;
      border-radius: 4px;
      border: 1px solid #CBD5E1;
      box-shadow: 0 16px 36px -8px rgba(15, 23, 42, 0.16), 0 4px 12px -2px rgba(15, 23, 42, 0.08);
      padding: 28px 24px;
      transform: scale(0.98);
      transform-origin: top center;
    }
    .paper-header {
      border-bottom: 2px solid #1E293B;
      padding-bottom: 12px;
      margin-bottom: 14px;
    }
    .paper-name {
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #0F172A;
      margin-bottom: 2px;
    }
    .paper-title {
      font-size: 11px;
      font-weight: 700;
      color: #2563EB;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }
    .paper-contact {
      font-size: 9.5px;
      color: #64748B;
      display: flex;
      gap: 8px;
    }
    .paper-section-title {
      font-size: 10.5px;
      font-weight: 800;
      letter-spacing: 0.8px;
      text-transform: uppercase;
      color: #0F172A;
      border-bottom: 1px solid #E2E8F0;
      padding-bottom: 3px;
      margin: 12px 0 8px;
    }
    .paper-exp-header {
      display: flex;
      justify-content: space-between;
      font-size: 10.5px;
      margin-bottom: 2px;
    }
    .paper-exp-role {
      font-weight: 700;
      color: #0F172A;
    }
    .paper-exp-company {
      color: #475569;
    }
    .paper-exp-date {
      font-size: 9.5px;
      color: #64748B;
    }
    .paper-bullet {
      font-size: 9.5px;
      color: #334155;
      line-height: 1.45;
      margin-left: 12px;
      list-style-type: disc;
      margin-top: 4px;
    }

    /* Floating Glass-1 Preview Toolbar */
    .floating-toolbar {
      position: absolute;
      bottom: 20px;
      background: var(--glass-1-bg);
      -webkit-backdrop-filter: blur(16px) saturate(160%);
      backdrop-filter: blur(16px) saturate(160%);
      border: 1px solid var(--glass-1-border);
      outline: 1px solid var(--glass-1-edge);
      outline-offset: -1px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
      border-radius: 9999px;
      padding: 6px 14px;
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-main);
    }
    .toolbar-btn {
      cursor: pointer;
      color: var(--text-muted);
    }
    .toolbar-sep {
      width: 1px;
      height: 14px;
      background: var(--border-subtle);
    }
  </style>
</head>
<body>
  <div class="hero-wrapper">
    <!-- Sticky Glass-1 Header -->
    <header class="site-header">
      <div class="header-inner">
        <a href="/" class="brand-logo">
          MirrorCV
          <div class="dot"></div>
        </a>
        <nav class="nav-links">
          <a href="#product">Product</a>
          <a href="#how-it-works">Why MirrorCV</a>
          <a href="#pricing">Pricing</a>
          <a href="/changelog">Changelog</a>
        </nav>
        <div class="header-actions">
          <a href="/login" class="btn-login">Log in</a>
          <a href="/signup" class="btn-cta">Get started free</a>
        </div>
      </div>
    </header>

    <!-- Hero Content -->
    <div class="hero-container">
      <a href="/changelog" class="announcement-pill">
        <span class="announcement-badge">NEW</span>
        FlowCV-Class Editor Engine with Sub-Millimeter Parity →
      </a>

      <h1 class="hero-title">Your resume. Exact template. Tailored in seconds.</h1>
      <p class="hero-sub">
        Keep the typography and layout you spent hours perfecting. Tailor bullet points to any job description with verifiable facts—exported to native PDF and byte-preserved DOCX.
      </p>

      <div class="hero-buttons">
        <a href="/signup" class="btn-hero-primary">Start tailoring free →</a>
        <a href="#demo" class="btn-hero-secondary">See it in action</a>
      </div>

      <div class="micro-claims">
        <div class="micro-claim-item">
          <span class="micro-dot"></span>
          Sub-millimeter PDF parity (&le; 0.65 pt)
        </div>
        <div class="micro-claim-item">
          <span class="micro-dot"></span>
          Zero hallucinated metrics
        </div>
        <div class="micro-claim-item">
          <span class="micro-dot"></span>
          15 self-hosted open fonts
        </div>
      </div>
    </div>

    <!-- HERO STAGE (DUAL-PANE FLOWCV-CLASS RESUME EDITOR) -->
    <div class="stage-wrapper">
      <div class="stage-container">
        <div class="stage-header-bar">
          <div class="stage-label-live">
            <span class="pulse-dot"></span>
            Live Workspace Preview
          </div>
          <div class="stage-caption">01 / DUAL-PANE FLOWCV-CLASS EDITOR →</div>
        </div>

        <!-- The App Window -->
        <div class="app-window">
          <!-- Window Top Bar (Glass-1 Chrome) -->
          <div class="app-topbar">
            <div class="app-topbar-left">
              <div class="window-controls">
                <span class="window-dot dot-close"></span>
                <span class="window-dot dot-min"></span>
                <span class="window-dot dot-max"></span>
              </div>
              <div class="resume-meta">
                <span class="resume-name">Principal Systems Engineer</span>
                <div class="save-pill">
                  <span class="save-dot"></span>
                  All changes saved
                </div>
              </div>
            </div>

            <!-- Tab Strip -->
            <div class="app-tabs">
              <div class="app-tab active">Content</div>
              <div class="app-tab">Customize</div>
              <div class="app-tab">AI Tools</div>
              <div class="app-tab">Overview</div>
            </div>

            <!-- Right Controls -->
            <div class="app-topbar-right">
              <span class="btn-action-sm">Undo</span>
              <span class="btn-action-sm">Redo</span>
              <span class="btn-export-primary">Export PDF ▾</span>
            </div>
          </div>

          <!-- Dual-Pane Body -->
          <div class="app-body">
            <!-- Left Pane: Editor Cards -->
            <div class="editor-pane">
              <!-- Work Experience Section Card -->
              <div class="section-card">
                <div class="section-card-header">
                  <div class="section-card-title">
                    <span>💼 Work Experience</span>
                    <span class="section-tag">Targeted</span>
                  </div>
                  <span class="entry-badge">2 entries</span>
                </div>

                <div class="form-item">
                  <div class="item-role-line">
                    <span class="item-role">Lead Systems Engineer</span>
                    <span class="item-dates">2021 – Present</span>
                  </div>
                  <div class="item-company">Apex Cloud Systems · Full-time</div>
                </div>

                <!-- Verified Bullet Point Diff -->
                <div class="bullet-box">
                  <div class="verifier-pill">
                    ✓ 94% Job Match · Verifier Approved
                  </div>
                  <div>
                    Engineered multi-region Raft consensus replication engine <span class="diff-highlight">reducing p99 tail latency by 42%</span> across 12 distributed clusters.
                  </div>
                </div>
              </div>

              <!-- Skills & Expertise Card -->
              <div class="section-card">
                <div class="section-card-header">
                  <div class="section-card-title">
                    <span>⚡ Core Technical Skills</span>
                  </div>
                  <span class="entry-badge">5 matched</span>
                </div>
                <div class="skills-row">
                  <div class="skill-chip"><span class="skill-level-dot"></span>Rust</div>
                  <div class="skill-chip"><span class="skill-level-dot"></span>Go</div>
                  <div class="skill-chip"><span class="skill-level-dot"></span>Raft Protocol</div>
                  <div class="skill-chip"><span class="skill-level-dot"></span>Distributed Consensus</div>
                  <div class="skill-chip"><span class="skill-level-dot"></span>Kubernetes</div>
                </div>
              </div>
            </div>

            <!-- Right Pane: Real Floating A4 Resume Sheet -->
            <div class="preview-pane">
              <div class="resume-paper">
                <div class="paper-header">
                  <div class="paper-name">ALEX RIVERA</div>
                  <div class="paper-title">Principal Systems Engineer</div>
                  <div class="paper-contact">
                    <span>alex.rivera@example.com</span> ·
                    <span>(555) 234-5678</span> ·
                    <span>Seattle, WA</span> ·
                    <span>linkedin.com/in/alexrivera</span>
                  </div>
                </div>

                <div class="paper-section-title">Professional Experience</div>
                <div class="paper-exp-header">
                  <span class="paper-exp-role">Lead Systems Engineer — Apex Cloud Systems</span>
                  <span class="paper-exp-date">2021 – Present</span>
                </div>
                <div class="paper-bullet">
                  Engineered multi-region Raft consensus replication engine reducing p99 tail latency by 42% across 12 distributed clusters.
                </div>
                <div class="paper-bullet">
                  Architected asynchronous message serialization pipeline processing 3.4M writes/sec with strict zero-data-loss guarantees.
                </div>

                <div class="paper-section-title">Core Competencies</div>
                <div style="font-size: 9.5px; color: #334155; line-height: 1.5;">
                  <strong>Systems & Infrastructure:</strong> Rust, Go, Raft Protocol, Distributed Consensus, Kubernetes, Linux eBPF, CockroachDB.
                </div>
              </div>

              <!-- Floating Glass-1 Preview Toolbar -->
              <div class="floating-toolbar">
                <span class="toolbar-btn">−</span>
                <span>100%</span>
                <span class="toolbar-btn">+</span>
                <div class="toolbar-sep"></div>
                <span class="toolbar-btn">Fit Width</span>
                <div class="toolbar-sep"></div>
                <span>Page 1 / 1</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

GLASS_MATRIX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MirrorCV Glass System Matrix</title>
  <style>
    :root {
      --primary: #2563EB;
      --primary-bevel: #1D4FBA;
      --text-main: #0F172A;
      --text-muted: #475569;

      /* Glass Tiers */
      --glass-1-bg: rgba(255, 255, 255, 0.70);
      --glass-1-blur: 16px;
      --glass-1-border: rgba(255, 255, 255, 0.65);
      --glass-1-edge: rgba(15, 23, 42, 0.06);

      --glass-2-bg: rgba(255, 255, 255, 0.82);
      --glass-2-blur: 20px;
      --glass-2-border: rgba(255, 255, 255, 0.80);
      --glass-2-edge: rgba(15, 23, 42, 0.08);

      --glass-3-bg: rgba(255, 255, 255, 0.88);
      --glass-3-blur: 24px;
      --glass-3-border: rgba(255, 255, 255, 0.85);
      --glass-3-edge: rgba(15, 23, 42, 0.10);

      --glass-card-bg: rgba(255, 255, 255, 0.75);
      --glass-card-blur: 16px;
      --glass-card-border: rgba(255, 255, 255, 0.70);

      --glass-dark-bg: rgba(255, 255, 255, 0.08);
      --glass-dark-blur: 16px;
      --glass-dark-border: rgba(255, 255, 255, 0.14);
      --glass-dark-edge: rgba(0, 0, 0, 0.30);

      --frosted-solid-bg: rgba(255, 255, 255, 0.92);
      --frosted-solid-border: #E2E8F0;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
      background: #F1F5F9;
      padding: 30px 20px;
      color: var(--text-main);
    }
    h1 {
      font-size: 28px;
      font-weight: 800;
      margin-bottom: 6px;
    }
    p.sub {
      color: var(--text-muted);
      margin-bottom: 24px;
      font-size: 14px;
    }

    .matrix-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }

    .backdrop-column {
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .col-title {
      font-size: 14px;
      font-weight: 700;
      padding-bottom: 10px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      margin-bottom: 2px;
    }

    /* 4 Distinct Backdrops */
    .bg-light {
      background: radial-gradient(circle at 50% 0%, #FFFFFF 0%, #F1F5F9 100%);
      border: 1px solid #E2E8F0;
    }
    .bg-lavender {
      background: radial-gradient(circle at 50% 0%, #E9E3FA 0%, #D8D1F4 100%);
      border: 1px solid #D8D1F4;
    }
    .bg-dark {
      background: #161718;
      border: 1px solid #2A2C30;
      color: #F8FAFC;
    }
    .bg-dark .col-title {
      border-bottom-color: rgba(255, 255, 255, 0.15);
      color: #F8FAFC;
    }
    .bg-image {
      background: linear-gradient(135deg, #1E293B 0%, #3B82F6 50%, #EC4899 100%);
      border: 1px solid #CBD5E1;
      color: #FFFFFF;
    }
    .bg-image .col-title {
      border-bottom-color: rgba(255, 255, 255, 0.2);
      color: #FFFFFF;
    }

    /* Glass Elements */
    .glass-box {
      border-radius: 8px;
      padding: 12px;
      position: relative;
    }
    .tier-badge {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      margin-bottom: 4px;
      display: inline-block;
    }
    .glass-title {
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 2px;
    }
    .glass-desc {
      font-size: 11px;
      line-height: 1.4;
    }

    /* Glass-1 */
    .box-glass-1 {
      background: var(--glass-1-bg);
      -webkit-backdrop-filter: blur(var(--glass-1-blur)) saturate(160%);
      backdrop-filter: blur(var(--glass-1-blur)) saturate(160%);
      border: 1px solid var(--glass-1-border);
      outline: 1px solid var(--glass-1-edge);
      outline-offset: -1px;
      color: var(--text-main);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9), 0 4px 12px rgba(15, 23, 42, 0.05);
    }
    .box-glass-1 .glass-desc { color: var(--text-muted); }

    /* Glass-2 */
    .box-glass-2 {
      background: var(--glass-2-bg);
      -webkit-backdrop-filter: blur(var(--glass-2-blur)) saturate(160%);
      backdrop-filter: blur(var(--glass-2-blur)) saturate(160%);
      border: 1px solid var(--glass-2-border);
      outline: 1px solid var(--glass-2-edge);
      outline-offset: -1px;
      color: var(--text-main);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.95), 0 8px 20px rgba(15, 23, 42, 0.08);
    }
    .box-glass-2 .glass-desc { color: var(--text-muted); }

    /* Glass-3 */
    .box-glass-3 {
      background: var(--glass-3-bg);
      -webkit-backdrop-filter: blur(var(--glass-3-blur)) saturate(160%);
      backdrop-filter: blur(var(--glass-3-blur)) saturate(160%);
      border: 1px solid var(--glass-3-border);
      outline: 1px solid var(--glass-3-edge);
      outline-offset: -1px;
      color: var(--text-main);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.98), 0 12px 28px rgba(15, 23, 42, 0.12);
    }
    .box-glass-3 .glass-desc { color: var(--text-muted); }

    /* Glass-Dark */
    .box-glass-dark {
      background: var(--glass-dark-bg);
      -webkit-backdrop-filter: blur(var(--glass-dark-blur)) saturate(150%);
      backdrop-filter: blur(var(--glass-dark-blur)) saturate(150%);
      border: 1px solid var(--glass-dark-border);
      outline: 1px solid var(--glass-dark-edge);
      outline-offset: -1px;
      color: #F8FAFC;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }
    .box-glass-dark .glass-desc { color: #CBD5E1; }

    /* Frosted Solid */
    .box-frosted {
      background: var(--frosted-solid-bg);
      -webkit-backdrop-filter: blur(8px);
      backdrop-filter: blur(8px);
      border: 1px solid var(--frosted-solid-border);
      color: var(--text-main);
      box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
    }
    .box-frosted .glass-desc { color: var(--text-muted); }
  </style>
</head>
<body>
  <h1>MirrorCV Glass System Matrix</h1>
  <p class="sub">Visual matrix rendering all 5 glass levels across 4 real backdrops: Light Ambient, Lavender Stage, Dark Band, and Image Backdrop.</p>

  <div class="matrix-grid">
    <!-- 1. LIGHT AMBIENT BACKDROP -->
    <div class="backdrop-column bg-light">
      <div class="col-title">1. Light Ambient</div>
      <div class="glass-box box-glass-1">
        <span class="tier-badge" style="color: #2563EB;">Glass-1 Chrome</span>
        <div class="glass-title">App Topbar & Header</div>
        <div class="glass-desc">70% white, 16px blur. Contrast: 17.85:1 AAA.</div>
      </div>
      <div class="glass-box box-glass-2">
        <span class="tier-badge" style="color: #775BCC;">Glass-2 Floating</span>
        <div class="glass-title">Dropdowns & Popovers</div>
        <div class="glass-desc">82% white, 20px blur. Contrast: 17.85:1 AAA.</div>
      </div>
      <div class="glass-box box-glass-3">
        <span class="tier-badge" style="color: #0F172A;">Glass-3 Overlay</span>
        <div class="glass-title">Modal Container</div>
        <div class="glass-desc">88% white, 24px blur. Contrast: 17.85:1 AAA.</div>
      </div>
      <div class="glass-box box-frosted">
        <span class="tier-badge" style="color: #166534;">Frosted-Solid</span>
        <div class="glass-title">Editor Section Card</div>
        <div class="glass-desc">92% solid surface for typing. Contrast: 17.85:1 AAA.</div>
      </div>
    </div>

    <!-- 2. LAVENDER STAGE BACKDROP -->
    <div class="backdrop-column bg-lavender">
      <div class="col-title" style="color: #1E293B;">2. Lavender Stage</div>
      <div class="glass-box box-glass-1">
        <span class="tier-badge" style="color: #2563EB;">Glass-1 Chrome</span>
        <div class="glass-title">Stage Window Header</div>
        <div class="glass-desc">70% white, 16px blur. Contrast: 16.77:1 AAA.</div>
      </div>
      <div class="glass-box box-glass-2">
        <span class="tier-badge" style="color: #775BCC;">Glass-2 Floating</span>
        <div class="glass-title">Filter / Template Menu</div>
        <div class="glass-desc">82% white, 20px blur. Contrast: 17.18:1 AAA.</div>
      </div>
      <div class="glass-box box-glass-3">
        <span class="tier-badge" style="color: #0F172A;">Glass-3 Overlay</span>
        <div class="glass-title">Template Gallery Sheet</div>
        <div class="glass-desc">88% white, 24px blur. Contrast: 17.42:1 AAA.</div>
      </div>
      <div class="glass-box box-frosted">
        <span class="tier-badge" style="color: #166534;">Frosted-Solid</span>
        <div class="glass-title">Tailoring Diff Box</div>
        <div class="glass-desc">92% solid surface on stage. Contrast: 17.57:1 AAA.</div>
      </div>
    </div>

    <!-- 3. DARK BAND BACKDROP -->
    <div class="backdrop-column bg-dark">
      <div class="col-title">3. Dark Band</div>
      <div class="glass-box box-glass-dark">
        <span class="tier-badge" style="color: #60A5FA;">Glass-Dark Chip</span>
        <div class="glass-title">ATS Readability Pill</div>
        <div class="glass-desc">8% white on dark. Text #F8FAFC. Contrast: 13.76:1 AAA.</div>
      </div>
      <div class="glass-box box-glass-2">
        <span class="tier-badge" style="color: #775BCC;">Glass-2 Floating</span>
        <div class="glass-title">Dark Band Context Menu</div>
        <div class="glass-desc">82% white over dark. Contrast: 12.16:1 AAA.</div>
      </div>
      <div class="glass-box box-glass-3">
        <span class="tier-badge" style="color: #0F172A;">Glass-3 Overlay</span>
        <div class="glass-title">Dark Scrim Modal</div>
        <div class="glass-desc">88% white over dark. Contrast: 13.91:1 AAA.</div>
      </div>
      <div class="glass-box box-glass-dark">
        <span class="tier-badge" style="color: #34D399;">Glass-Dark Tag</span>
        <div class="glass-title">Export Parity Badge</div>
        <div class="glass-desc">Muted #CBD5E1. Contrast: 9.70:1 AAA.</div>
      </div>
    </div>

    <!-- 4. IMAGE / TEXTURED BACKDROP -->
    <div class="backdrop-column bg-image">
      <div class="col-title">4. Vibrant Image</div>
      <div class="glass-box box-glass-1">
        <span class="tier-badge" style="color: #2563EB;">Glass-1 Chrome</span>
        <div class="glass-title">Floating Navigation Bar</div>
        <div class="glass-desc">Smooth 16px diffusion over vivid tones.</div>
      </div>
      <div class="glass-box box-glass-2">
        <span class="tier-badge" style="color: #775BCC;">Glass-2 Floating</span>
        <div class="glass-title">Quick Action Palette</div>
        <div class="glass-desc">20px optical dispersion, legible text.</div>
      </div>
      <div class="glass-box box-glass-3">
        <span class="tier-badge" style="color: #0F172A;">Glass-3 Overlay</span>
        <div class="glass-title">Focus Dialog Surface</div>
        <div class="glass-desc">24px deep blur, 88% white isolation.</div>
      </div>
      <div class="glass-box box-frosted">
        <span class="tier-badge" style="color: #166534;">Frosted-Solid</span>
        <div class="glass-title">Readable Content Sheet</div>
        <div class="glass-desc">92% solid ensures zero color vibration.</div>
      </div>
    </div>
  </div>
</body>
</html>
"""

print("Writing HTML files...")
with open(MOCKUP_DIR / "mockup_landing_hero.html", "w", encoding="utf-8") as f:
    f.write(LANDING_HERO_HTML)

with open(MATRIX_DIR / "glass_matrix.html", "w", encoding="utf-8") as f:
    f.write(GLASS_MATRIX_HTML)

with open(ARTIFACT_DIR / "mockups" / "mockup_landing_hero.html", "w", encoding="utf-8") as f:
    f.write(LANDING_HERO_HTML)

with open(ARTIFACT_MATRIX / "glass_matrix.html", "w", encoding="utf-8") as f:
    f.write(GLASS_MATRIX_HTML)

print("Capturing screenshots via Playwright...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # 1. Capture updated hero mockup
    page = browser.new_page(viewport={"width": 1440, "height": 1250})
    page.goto(f"file:///{str(MOCKUP_DIR / 'mockup_landing_hero.html').replace(os.sep, '/')}", wait_until="load")
    page.screenshot(path=str(MOCKUP_DIR / "mockup_landing_hero.png"))
    page.screenshot(path=str(ARTIFACT_DIR / "mockups" / "mockup_landing_hero.png"))
    print("Captured: mockup_landing_hero.png")
    page.close()

    # 2. Capture Glass Matrix at 1440, 1024, 390
    viewports = [
        ("desktop_1440", {"width": 1440, "height": 780}),
        ("tablet_1024", {"width": 1024, "height": 800}),
        ("mobile_390", {"width": 390, "height": 1100})
    ]

    for label, vp in viewports:
        page_vp = browser.new_page(viewport=vp)
        page_vp.goto(f"file:///{str(MATRIX_DIR / 'glass_matrix.html').replace(os.sep, '/')}", wait_until="load")
        out_name = f"glass_matrix_{label}.png"
        page_vp.screenshot(path=str(MATRIX_DIR / out_name))
        page_vp.screenshot(path=str(ARTIFACT_MATRIX / out_name))
        print(f"Captured: {out_name}")
        page_vp.close()

    # 3. Capture with prefers-reduced-transparency: reduce simulation
    page_reduced = browser.new_page(viewport={"width": 1440, "height": 780})
    page_reduced.goto(f"file:///{str(MATRIX_DIR / 'glass_matrix.html').replace(os.sep, '/')}", wait_until="load")
    page_reduced.add_style_tag(content="""
      .box-glass-1, .box-glass-2, .box-glass-3, .box-frosted {
        background: #FFFFFF !important;
        -webkit-backdrop-filter: none !important;
        backdrop-filter: none !important;
        box-shadow: 0 2px 8px rgba(15,23,42,0.08) !important;
      }
      .box-glass-dark {
        background: #1E293B !important;
        -webkit-backdrop-filter: none !important;
        backdrop-filter: none !important;
      }
    """)
    page_reduced.screenshot(path=str(MATRIX_DIR / "glass_matrix_reduced_transparency.png"))
    page_reduced.screenshot(path=str(ARTIFACT_MATRIX / "glass_matrix_reduced_transparency.png"))
    print("Captured: glass_matrix_reduced_transparency.png")
    page_reduced.close()

    # 4. Capture no-backdrop-filter fallback simulation
    page_fallback = browser.new_page(viewport={"width": 1440, "height": 780})
    page_fallback.goto(f"file:///{str(MATRIX_DIR / 'glass_matrix.html').replace(os.sep, '/')}", wait_until="load")
    page_fallback.add_style_tag(content="""
      * { -webkit-backdrop-filter: none !important; backdrop-filter: none !important; }
      .box-glass-1, .box-glass-2, .box-glass-3, .box-frosted {
        background: rgba(255, 255, 255, 0.98) !important;
        border: 1px solid #CBD5E1 !important;
      }
      .box-glass-dark {
        background: #1E293B !important;
        border: 1px solid #475569 !important;
      }
    """)
    page_fallback.screenshot(path=str(MATRIX_DIR / "glass_matrix_no_backdrop_fallback.png"))
    page_fallback.screenshot(path=str(ARTIFACT_MATRIX / "glass_matrix_no_backdrop_fallback.png"))
    print("Captured: glass_matrix_no_backdrop_fallback.png")
    page_fallback.close()

    browser.close()

print("All glass matrix captures complete successfully!")
