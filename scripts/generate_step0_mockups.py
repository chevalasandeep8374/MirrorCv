import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
MOCKUP_DIR = ROOT / "redesign_reference" / "mockups"
ARTIFACT_DIR = Path("C:/Users/CH SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference/mockups")

MOCKUP_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Landing Hero Mockup HTML
LANDING_HERO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MirrorCV — Landing Hero Mockup</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap');

    :root {
      --bg-page: #FFFFFF;
      --bg-stage: #E9E3FA;
      --border-stage: #D8D1F4;
      --border-subtle: #E2E8F0;
      --text-main: #1E293B;
      --text-muted: #64748B;
      --text-dim: #94A3B8;
      --primary: #2563EB;
      --primary-bevel: #1D4FBA;
      --accent-purple: #775BCC;
      --accent-purple-light: #EEEAFF;
      --accent-green-badge: #DCFCE7;
      --accent-green-text: #166534;
      --radius-sm: 6px;
      --radius-btn: 7px;
      --radius-card: 12px;
      --radius-stage: 14px;
      --shadow-btn: 0px 3px 0px 0px var(--primary-bevel);
      --shadow-card: 0px 4px 12px rgba(30, 41, 59, 0.05);
      --shadow-inset: 0px -1px 0px 0px rgba(255, 255, 255, 0.8) inset;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-page);
      color: var(--text-main);
      overflow-x: hidden;
      line-height: 1.5;
    }

    /* Site Header */
    header.site-header {
      position: sticky;
      top: 0;
      z-index: 50;
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid #EEF0F6;
      padding: 16px 48px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 3px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-weight: 800;
      font-size: 20px;
      letter-spacing: -0.6px;
      color: var(--text-main);
      text-decoration: none;
    }
    .brand-dot {
      width: 6px;
      height: 6px;
      background: var(--primary);
      border-radius: 50%;
      display: inline-block;
      margin-left: 2px;
    }
    nav.nav-links {
      display: flex;
      align-items: center;
      gap: 28px;
    }
    nav.nav-links a {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-muted);
      text-decoration: none;
      transition: color 0.15s ease;
    }
    nav.nav-links a:hover { color: var(--text-main); }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .btn-login {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      text-decoration: none;
      padding: 8px 14px;
    }
    .btn-primary {
      background: var(--primary);
      color: #FFFFFF;
      font-size: 13px;
      font-weight: 700;
      padding: 10px 18px;
      border-radius: var(--radius-btn);
      border: 1px solid rgba(0,0,0,0.05);
      box-shadow: var(--shadow-btn);
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      transition: transform 0.15s ease, background 0.15s ease;
    }
    .btn-primary:hover {
      background: #1D4ED8;
      transform: translateY(-1px);
    }
    .btn-secondary {
      background: #FFFFFF;
      color: var(--text-main);
      font-size: 13px;
      font-weight: 700;
      padding: 10px 18px;
      border-radius: var(--radius-btn);
      border: 1px solid var(--border-subtle);
      box-shadow: 0 2px 0 #E2E8F0;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }

    /* Hero Section */
    section.hero {
      padding: 56px 24px 0 24px;
      text-align: center;
      max-width: 1240px;
      margin: 0 auto;
    }
    .announcement-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #F1EDFC;
      border: 1px solid #D9CEF7;
      padding: 5px 14px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      color: var(--accent-purple);
      margin-bottom: 24px;
      text-decoration: none;
    }
    .announcement-tag {
      background: var(--accent-purple);
      color: #FFFFFF;
      font-size: 10px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 9999px;
      letter-spacing: 0.5px;
    }
    h1.hero-title {
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-weight: 800;
      font-size: 64px;
      line-height: 1.1;
      letter-spacing: -2.8px;
      color: var(--text-main);
      max-width: 820px;
      margin: 0 auto 20px auto;
    }
    p.hero-subcopy {
      font-size: 17px;
      color: var(--text-muted);
      line-height: 1.6;
      max-width: 600px;
      margin: 0 auto 32px auto;
    }
    .hero-cta-group {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 14px;
      margin-bottom: 32px;
    }
    .micro-claims-row {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 28px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 56px;
    }
    .claim-item {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .claim-dot {
      width: 7px;
      height: 7px;
      background: #10B981;
      border-radius: 50%;
    }

    /* Hero Stage Container */
    .hero-stage {
      background: var(--bg-stage);
      border: 1px solid var(--border-stage);
      border-bottom: none;
      border-radius: var(--radius-stage) var(--radius-stage) 0 0;
      padding: 0 28px 28px 28px;
      max-width: 1120px;
      margin: 0 auto;
      box-shadow: var(--shadow-inset);
      position: relative;
    }
    .stage-caption {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 4px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1px;
      color: #7E7599;
      text-transform: uppercase;
    }
    .stage-inner {
      background: #FFFFFF;
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      box-shadow: 0 12px 36px rgba(30, 41, 59, 0.08);
      display: grid;
      grid-template-columns: 240px 1fr;
      min-height: 520px;
      overflow: hidden;
      text-align: left;
    }

    /* Stage Sidebar */
    .preview-sidebar {
      background: #FAF9FE;
      border-right: 1px solid #EEF0F6;
      padding: 18px 14px;
      display: flex;
      flex-col;
      flex-direction: column;
      justify-content: space-between;
      font-size: 12px;
    }
    .ws-header {
      display: flex;
      align-items: center;
      gap: 10px;
      padding-bottom: 16px;
      border-bottom: 1px solid #EEF0F6;
    }
    .ws-monogram {
      width: 28px;
      height: 28px;
      background: #775BCC;
      color: #FFF;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 13px;
    }
    .ws-title {
      font-weight: 700;
      color: var(--text-main);
      line-height: 1.2;
    }
    .ws-plan {
      font-size: 10px;
      color: #775BCC;
      font-weight: 600;
    }
    .sidebar-nav {
      margin-top: 14px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .side-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 7px 10px;
      border-radius: 6px;
      color: var(--text-muted);
      font-weight: 600;
      cursor: pointer;
    }
    .side-item.active {
      background: #EEEAFF;
      color: #5B3FB8;
    }
    .side-count {
      background: #5B3FB8;
      color: #FFF;
      border-radius: 9999px;
      font-size: 10px;
      padding: 1px 6px;
      font-weight: 700;
    }
    .sidebar-group-title {
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.8px;
      color: #94A3B8;
      text-transform: uppercase;
      margin: 16px 10px 6px 10px;
      display: flex;
      justify-content: space-between;
    }
    .resume-list-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 10px;
      border-radius: 6px;
      font-weight: 600;
      color: var(--text-main);
      font-size: 12px;
    }
    .resume-list-item.active {
      background: #F1F5F9;
    }
    .status-dot-blue { width: 6px; height: 6px; border-radius: 50%; background: #2563EB; }
    .status-dot-purple { width: 6px; height: 6px; border-radius: 50%; background: #775BCC; }

    /* Stage Main Content */
    .preview-main {
      display: flex;
      flex-direction: column;
      background: #FFFFFF;
    }
    .preview-topbar {
      padding: 12px 24px;
      border-bottom: 1px solid #EEF0F6;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      color: var(--text-muted);
    }
    .project-header {
      padding: 18px 24px;
      border-bottom: 1px solid #EEF0F6;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .project-title-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .project-h3 {
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: var(--text-main);
    }
    .chip-badge {
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 9999px;
      background: #DCFCE7;
      color: #166534;
    }
    .preview-tabs {
      padding: 0 24px;
      border-bottom: 1px solid #EEF0F6;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .tab-btn-group {
      display: flex;
      gap: 8px;
    }
    .tab-btn {
      padding: 11px 16px;
      font-size: 12px;
      font-weight: 700;
      color: var(--text-muted);
      border: none;
      background: none;
      border-bottom: 2px solid transparent;
      cursor: pointer;
    }
    .tab-btn.active {
      color: var(--primary);
      border-bottom-color: var(--primary);
    }

    /* Columns Mockup */
    .preview-board {
      padding: 20px 24px;
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 16px;
      background: #F8FAFC;
      flex: 1;
    }
    .col-card {
      background: #F1F5F9;
      border: 1px solid #E2E8F0;
      border-radius: 10px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .col-title {
      font-size: 12px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .task-card {
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 8px;
      padding: 12px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.02);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .task-tag {
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
      padding: 2px 6px;
      border-radius: 4px;
      width: fit-content;
      background: #EEEAFF;
      color: #5B3FB8;
    }
    .task-tag.blue { background: #E0E7FF; color: #3730A3; }
    .task-tag.green { background: #DCFCE7; color: #166534; }
    .task-name {
      font-size: 12px;
      font-weight: 700;
      color: var(--text-main);
    }
    .task-progress {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 10px;
      color: var(--text-muted);
      font-weight: 600;
    }
    .progress-bar-bg {
      flex: 1;
      height: 4px;
      background: #E2E8F0;
      border-radius: 9999px;
      overflow: hidden;
    }
    .progress-bar-fill {
      height: 100%;
      background: #10B981;
      border-radius: 9999px;
    }
  </style>
</head>
<body>

  <!-- Site Header -->
  <header class="site-header">
    <a href="#" class="brand">
      MirrorCV<span class="brand-dot"></span>
    </a>
    <nav class="nav-links">
      <a href="#product">Product</a>
      <a href="#templates">Keep Your Template</a>
      <a href="#why">Why MirrorCV</a>
      <a href="#pricing">Pricing</a>
      <a href="#changelog">Changelog</a>
    </nav>
    <div class="header-actions">
      <a href="#login" class="btn-login">Log in</a>
      <a href="#signup" class="btn-primary">
        <span>Get started free</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
      </a>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="hero">
    <!-- Announcement Pill -->
    <a href="#changelog" class="announcement-pill">
      <span class="announcement-tag">NEW</span>
      <span>v1.2: In-place DOCX tailoring with zero XML drift</span>
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>
    </a>

    <!-- Headline -->
    <h1 class="hero-title">
      Keep your exact template.<br>Tailor every bullet to the job.
    </h1>

    <!-- Subcopy -->
    <p class="hero-subcopy">
      Upload your existing DOCX or build fresh. MirrorCV edits your real document in place—preserving every font, table, margin, and rule without layout drift or hallucinations.
    </p>

    <!-- CTAs -->
    <div class="hero-cta-group">
      <a href="#signup" class="btn-primary" style="font-size: 14px; padding: 13px 26px;">
        <span>Start tailoring free</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
      </a>
      <a href="#demo" class="btn-secondary" style="font-size: 14px; padding: 13px 24px;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
        <span>See it in action</span>
      </a>
    </div>

    <!-- Micro-Claims Row -->
    <div class="micro-claims-row">
      <div class="claim-item">
        <span class="claim-dot"></span>
        <span>1:1 PyMuPDF vector parity (&le; 0.65 pt)</span>
      </div>
      <div class="claim-item">
        <span class="claim-dot"></span>
        <span>Zero hallucinated metrics</span>
      </div>
      <div class="claim-item">
        <span class="claim-dot"></span>
        <span>15 self-hosted open fonts</span>
      </div>
    </div>

    <!-- The Hero Stage Mockup -->
    <div class="hero-stage">
      <div class="stage-caption">
        <span>&bull; LIVE WORKSPACE PREVIEW</span>
        <span>01 / THE RESUME EDITOR &rarr;</span>
      </div>

      <div class="stage-inner">
        <!-- Sidebar -->
        <aside class="preview-sidebar">
          <div>
            <div class="ws-header">
              <div class="ws-monogram">M</div>
              <div>
                <div class="ws-title">Alex's Career</div>
                <div class="ws-plan">Pro Workspace</div>
              </div>
            </div>

            <div class="sidebar-nav">
              <div class="side-item active">
                <span>Overview</span>
              </div>
              <div class="side-item">
                <span>To review</span>
                <span class="side-count">3</span>
              </div>
              <div class="side-item">
                <span>Notifications</span>
              </div>
            </div>

            <div class="sidebar-group-title">
              <span>Resumes</span>
              <span>+</span>
            </div>
            <div class="resume-list-item active">
              <span class="status-dot-blue"></span>
              <span>Principal Engineer (Staff)</span>
            </div>
            <div class="resume-list-item">
              <span class="status-dot-purple"></span>
              <span>Cloud Architect (AWS)</span>
            </div>

            <div class="sidebar-group-title">
              <span>Job Targets</span>
              <span>+</span>
            </div>
            <div class="resume-list-item">
              <span style="font-size: 11px; color: #64748B;">Acme Cloud — Staff Role</span>
            </div>
          </div>

          <div style="padding-top: 14px; border-top: 1px solid #EEF0F6; font-size: 11px; color: #64748B;">
            <div>&bull; All changes saved</div>
          </div>
        </aside>

        <!-- Main Workspace -->
        <main class="preview-main">
          <div class="preview-topbar">
            <span>Resumes / <strong>Principal Engineer (Staff)</strong></span>
            <div style="display: flex; gap: 12px; font-weight: 600;">
              <span>Share</span>
              <span style="color: var(--primary);">Export PDF</span>
            </div>
          </div>

          <div class="project-header">
            <div>
              <div class="project-title-row">
                <h3 class="project-h3">Principal Systems Engineer</h3>
                <span class="chip-badge">Tailored (94% Match)</span>
              </div>
              <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Targeting: Distributed Systems Staff Infrastructure</p>
            </div>
            <div style="display: flex; gap: 8px;">
              <button class="btn-primary" style="padding: 6px 14px; font-size: 11px;">Review Diffs (3)</button>
            </div>
          </div>

          <div class="preview-tabs">
            <div class="tab-btn-group">
              <button class="tab-btn active">Content</button>
              <button class="tab-btn">Customize</button>
              <button class="tab-btn">AI Tools</button>
              <button class="tab-btn">Overview</button>
            </div>
            <div style="font-size: 11px; color: var(--text-muted); font-weight: 600;">
              Undo &bull; Redo &bull; Zoom 100%
            </div>
          </div>

          <!-- Board / Section Cards -->
          <div class="preview-board">
            <div class="col-card">
              <div class="col-title">
                <span>WORK EXPERIENCE</span>
                <span style="font-size: 10px; color: #64748B;">2 Items</span>
              </div>
              <div class="task-card">
                <div class="task-tag">Experience</div>
                <div class="task-name">Apex Cloud Systems</div>
                <div style="font-size: 11px; color: var(--text-muted);">Lead Backend Developer</div>
                <div class="task-progress">
                  <span>Bullets (3/3)</span>
                  <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 100%;"></div></div>
                </div>
              </div>
              <div class="task-card">
                <div class="task-tag">Experience</div>
                <div class="task-name">Nexus Distributed Labs</div>
                <div style="font-size: 11px; color: var(--text-muted);">Senior Systems Engineer</div>
                <div class="task-progress">
                  <span>Bullets (2/3)</span>
                  <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 66%;"></div></div>
                </div>
              </div>
            </div>

            <div class="col-card">
              <div class="col-title">
                <span>SKILLS & EXPERTISE</span>
                <span style="font-size: 10px; color: #64748B;">1 Group</span>
              </div>
              <div class="task-card">
                <div class="task-tag blue">Technical Skills</div>
                <div class="task-name">Languages & Systems</div>
                <div style="font-size: 11px; color: var(--text-muted);">Rust, Go, TypeScript, Raft</div>
                <div class="task-progress">
                  <span>Matched: 4/4</span>
                  <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 100%;"></div></div>
                </div>
              </div>
            </div>

            <div class="col-card">
              <div class="col-title">
                <span>AI TAILORING DIFFS</span>
                <span style="font-size: 10px; color: var(--primary);">3 Pending</span>
              </div>
              <div class="task-card" style="border-left: 3px solid var(--primary);">
                <div class="task-tag green">Verified Diff</div>
                <div class="task-name">Bullet Metric Sharpener</div>
                <div style="font-size: 10px; color: #166534; background: #DCFCE7; padding: 4px; border-radius: 4px;">
                  + "reduced p99 tail latency by 42%"
                </div>
                <div style="display: flex; gap: 6px; margin-top: 4px;">
                  <button style="flex: 1; padding: 3px; font-size: 10px; background: var(--primary); color: #FFF; border: none; border-radius: 4px;">Accept</button>
                  <button style="padding: 3px 8px; font-size: 10px; background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 4px;">Reject</button>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  </section>

</body>
</html>
"""

# 2. Resume Editor Mockup HTML
EDITOR_MOCKUP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MirrorCV — Resume Editor Mockup</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap');

    :root {
      --bg-page: #F8FAFC;
      --border-subtle: #E2E8F0;
      --text-main: #1E293B;
      --text-muted: #64748B;
      --primary: #2563EB;
      --primary-bevel: #1D4FBA;
      --accent-purple: #775BCC;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Manrope', -apple-system, sans-serif;
      background: var(--bg-page);
      color: var(--text-main);
      height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* Top Nav */
    header.editor-navbar {
      height: 56px;
      background: #FFFFFF;
      border-bottom: 1px solid var(--border-subtle);
      padding: 0 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .brand-group {
      display: flex;
      align-items: center;
      gap: 12px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-weight: 800;
      font-size: 18px;
    }
    .breadcrumb {
      font-size: 13px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 500;
    }
    .status-badge {
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 9999px;
      background: #DCFCE7;
      color: #166534;
    }
    .actions-group {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .btn-action {
      font-size: 12px;
      font-weight: 700;
      padding: 7px 14px;
      border-radius: 6px;
      border: 1px solid var(--border-subtle);
      background: #FFF;
      cursor: pointer;
    }
    .btn-primary-action {
      background: var(--primary);
      color: #FFF;
      border: 1px solid var(--primary-bevel);
      box-shadow: 0 2px 0 var(--primary-bevel);
    }

    /* Main Dual Pane View */
    .editor-layout {
      flex: 1;
      display: grid;
      grid-template-columns: 240px 480px 1fr;
      overflow: hidden;
    }

    /* Sidebar */
    aside.app-sidebar {
      background: #FFFFFF;
      border-right: 1px solid var(--border-subtle);
      padding: 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      font-size: 12px;
    }
    .sidebar-section-title {
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.8px;
      color: #94A3B8;
      text-transform: uppercase;
      margin: 16px 0 8px 0;
    }
    .side-tab {
      padding: 8px 10px;
      border-radius: 6px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .side-tab.active {
      background: #EEEAFF;
      color: #5B3FB8;
    }

    /* Middle Pane: Form Controls */
    .controls-pane {
      background: #FAF9FE;
      border-right: 1px solid var(--border-subtle);
      padding: 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .pane-tabs {
      display: flex;
      background: #F1EDFC;
      border-radius: 8px;
      padding: 3px;
      gap: 4px;
    }
    .pane-tab-btn {
      flex: 1;
      padding: 7px;
      text-align: center;
      font-size: 12px;
      font-weight: 700;
      border: none;
      border-radius: 6px;
      background: none;
      color: var(--text-muted);
      cursor: pointer;
    }
    .pane-tab-btn.active {
      background: #FFFFFF;
      color: #1E293B;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .form-card {
      background: #FFFFFF;
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .category-chip {
      font-size: 9px;
      font-weight: 800;
      text-transform: uppercase;
      padding: 2px 7px;
      border-radius: 4px;
      background: #EEEAFF;
      color: #5B3FB8;
    }
    .card-fraction {
      font-size: 11px;
      font-weight: 700;
      color: #10B981;
    }
    .input-label {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-main);
    }
    .text-input {
      width: 100%;
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid var(--border-subtle);
      font-size: 12px;
      background: #F8FAFC;
    }

    /* Right Pane: Live Document Preview */
    .preview-pane {
      background: #E2E8F0;
      padding: 32px;
      overflow-y: auto;
      display: flex;
      justify-content: center;
      align-items: flex-start;
    }
    .paper-sheet {
      width: 520px;
      background: #FFFFFF;
      border-radius: 6px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.12);
      padding: 36px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      font-size: 11px;
    }
    .resume-header-mock {
      border-bottom: 2px solid #1E293B;
      padding-bottom: 12px;
    }
    .resume-name {
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #1E293B;
    }
    .resume-role {
      font-size: 12px;
      font-weight: 600;
      color: var(--primary);
    }
    .section-bar {
      background: #F1F5F9;
      padding: 4px 8px;
      font-weight: 800;
      font-size: 10px;
      letter-spacing: 0.5px;
      color: #1E293B;
      text-transform: uppercase;
      border-left: 3px solid var(--primary);
      margin-bottom: 8px;
    }
  </style>
</head>
<body>
  <!-- Header -->
  <header class="editor-navbar">
    <div class="brand-group">
      <span>MirrorCV</span>
      <div class="breadcrumb">
        <span>/</span>
        <span>Resumes</span>
        <span>/</span>
        <strong style="color: #1E293B;">Staff Infrastructure Architect</strong>
        <span class="status-badge">Tailored (100% Fit)</span>
      </div>
    </div>
    <div class="actions-group">
      <span style="font-size: 11px; color: var(--text-muted); margin-right: 12px;">&bull; All changes saved</span>
      <button class="btn-action">Share Link</button>
      <button class="btn-action btn-primary-action">Download PDF</button>
    </div>
  </header>

  <!-- Editor Layout -->
  <div class="editor-layout">
    <!-- Left Navigation Sidebar -->
    <aside class="app-sidebar">
      <div>
        <div style="font-weight: 800; font-size: 13px; margin-bottom: 12px;">Alex's Workspace</div>
        <div class="side-tab active">Overview</div>
        <div class="side-tab">To Review <span style="background: var(--primary); color:#FFF; border-radius:9999px; font-size:10px; padding:1px 6px; margin-left:auto;">2</span></div>
        <div class="side-tab">Job Targets</div>

        <div class="sidebar-section-title">Resumes</div>
        <div class="side-tab" style="color: #1E293B; font-weight:700;">&bull; Staff Infrastructure</div>
        <div class="side-tab">&bull; Cloud Solutions Lead</div>
      </div>
      <div style="font-size: 11px; color: var(--text-muted);">
        <div>Help & Shortcuts (Ctrl+Z)</div>
      </div>
    </aside>

    <!-- Center Controls Pane -->
    <main class="controls-pane">
      <div class="pane-tabs">
        <button class="pane-tab-btn active">Content</button>
        <button class="pane-tab-btn">Customize</button>
        <button class="pane-tab-btn">AI Tools</button>
        <button class="pane-tab-btn">Overview</button>
      </div>

      <!-- Experience Card Styled like TaskFlow Task Card -->
      <div class="form-card">
        <div class="card-top">
          <span class="category-chip">Work Experience</span>
          <span class="card-fraction">3/3 Bullets</span>
        </div>
        <div class="input-label">Company & Title</div>
        <input type="text" class="text-input" value="Apex Cloud Systems &bull; Staff Infrastructure Architect" />
        <div class="input-label">Date Range & Location</div>
        <input type="text" class="text-input" value="Jan 2022 — Present &bull; Zurich, Switzerland" />
        <div class="input-label">Bullet Points (3)</div>
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 8px; border-radius: 6px; font-size: 11px;">
          &bull; Spearheaded zero-downtime consensus engine migration across 28 global regions.
        </div>
      </div>

      <!-- Skills Card -->
      <div class="form-card">
        <div class="card-top">
          <span class="category-chip" style="background: #E0E7FF; color: #3730A3;">Technical Skills</span>
          <span class="card-fraction">5 Items</span>
        </div>
        <div class="input-label">Languages & Frameworks</div>
        <input type="text" class="text-input" value="Rust, Go, TypeScript, Kubernetes, Raft" />
      </div>
    </main>

    <!-- Right Live Preview Pane -->
    <section class="preview-pane">
      <div class="paper-sheet">
        <div class="resume-header-mock">
          <div class="resume-name">Alex Mercer</div>
          <div class="resume-role">Staff Infrastructure Architect</div>
          <div style="font-size: 10px; color: #64748B; margin-top: 4px;">alex.mercer@systems.io &bull; +41 44 123 4567 &bull; Zurich, CH</div>
        </div>

        <div>
          <div class="section-bar">Executive Summary</div>
          <p style="color: #475569; line-height: 1.5;">
            Infrastructure architect with 12+ years of experience leading distributed consensus, zero-copy serialization, and low-latency storage engines.
          </p>
        </div>

        <div>
          <div class="section-bar">Work Experience</div>
          <div style="font-weight: 700; color: #1E293B;">Apex Cloud Systems &mdash; Staff Infrastructure Architect</div>
          <div style="font-size: 10px; color: #64748B; margin-bottom: 4px;">Jan 2022 &mdash; Present | Zurich</div>
          <ul style="padding-left: 14px; color: #475569; line-height: 1.5;">
            <li>Spearheaded zero-downtime consensus migration across 28 global regions with 99.999% availability.</li>
            <li>Eliminated p99 tail latency spikes by 42% via custom zero-copy memory buffers.</li>
          </ul>
        </div>
      </div>
    </section>
  </div>
</body>
</html>
"""

# 3. Pricing Page Mockup HTML
PRICING_MOCKUP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MirrorCV — Pricing Mockup</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap');

    :root {
      --bg-page: #FFFFFF;
      --border-subtle: #EEF0F6;
      --text-main: #1E293B;
      --text-muted: #64748B;
      --primary: #2563EB;
      --primary-bevel: #1D4FBA;
      --accent-purple: #775BCC;
      --shadow-btn: 0px 3px 0px 0px var(--primary-bevel);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Manrope', -apple-system, sans-serif;
      background: var(--bg-page);
      color: var(--text-main);
      padding-bottom: 80px;
    }

    header.site-header {
      padding: 16px 48px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .brand {
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-weight: 800;
      font-size: 20px;
      color: var(--text-main);
      text-decoration: none;
    }

    .pricing-hero {
      text-align: center;
      padding: 64px 24px 48px 24px;
      max-width: 800px;
      margin: 0 auto;
    }
    .eyebrow {
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 1px;
      color: var(--accent-purple);
      text-transform: uppercase;
      margin-bottom: 12px;
    }
    h1.pricing-h1 {
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 48px;
      font-weight: 800;
      letter-spacing: -2px;
      margin-bottom: 16px;
    }
    p.pricing-subcopy {
      font-size: 16px;
      color: var(--text-muted);
    }

    /* 3 Tiers Grid matching TaskFlow */
    .pricing-grid {
      max-width: 1080px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 24px;
      padding: 0 24px;
    }
    .pricing-card {
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      padding: 32px 28px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 2px 4px rgba(0,0,0,0.02);
      position: relative;
    }
    .pricing-card.featured {
      border: 2px solid var(--primary);
      box-shadow: 0 12px 30px rgba(37, 99, 235, 0.08);
      background: #FAF9FE;
    }
    .featured-tag {
      position: absolute;
      top: -12px;
      left: 50%;
      transform: translateX(-50%);
      background: var(--primary);
      color: #FFF;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      padding: 4px 12px;
      border-radius: 9999px;
      letter-spacing: 0.5px;
    }
    .plan-name {
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 22px;
      font-weight: 800;
      margin-bottom: 6px;
    }
    .plan-pitch {
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 24px;
      min-height: 40px;
    }
    .plan-price-row {
      display: flex;
      align-items: baseline;
      gap: 6px;
      margin-bottom: 24px;
    }
    .plan-price {
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 42px;
      font-weight: 800;
      letter-spacing: -1.5px;
    }
    .plan-cadence {
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 600;
    }
    .feature-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 12px;
      font-size: 13px;
      color: #334155;
      margin-bottom: 32px;
    }
    .feature-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .check-icon {
      color: #10B981;
      font-weight: bold;
    }
    .btn-plan {
      width: 100%;
      padding: 12px;
      font-size: 13px;
      font-weight: 700;
      text-align: center;
      border-radius: 7px;
      border: 1px solid #CBD5E1;
      background: #FFFFFF;
      color: var(--text-main);
      cursor: pointer;
      text-decoration: none;
      display: block;
    }
    .btn-plan.primary {
      background: var(--primary);
      color: #FFFFFF;
      border: 1px solid var(--primary-bevel);
      box-shadow: var(--shadow-btn);
    }
  </style>
</head>
<body>
  <header class="site-header">
    <a href="#" class="brand">MirrorCV<span style="color:var(--primary);">&bull;</span></a>
    <div><a href="#" style="font-size: 13px; font-weight: 600; color: #64748B; text-decoration: none;">Back to Workspace</a></div>
  </header>

  <div class="pricing-hero">
    <div class="eyebrow">SIMPLE PLANS. NO SUBSCRIPTION LOCK-IN.</div>
    <h1 class="pricing-h1">A plan for every stage of your career.</h1>
    <p class="pricing-subcopy">
      Build with total privacy. Free forever with local browser storage. Upgrade only when you need deep automated DOCX XML tailoring.
    </p>
  </div>

  <div class="pricing-grid">
    <!-- Free Tier -->
    <div class="pricing-card">
      <div>
        <div class="plan-name">Free</div>
        <div class="plan-pitch">Complete local resume builder with zero tracking or limits.</div>
        <div class="plan-price-row">
          <span class="plan-price">$0</span>
          <span class="plan-cadence">free forever</span>
        </div>
        <ul class="feature-list">
          <li class="feature-item"><span class="check-icon">&check;</span> Unlimited local resumes</li>
          <li class="feature-item"><span class="check-icon">&check;</span> 15 curated self-hosted fonts</li>
          <li class="feature-item"><span class="check-icon">&check;</span> Live vector PDF export</li>
          <li class="feature-item"><span class="check-icon">&check;</span> Content &amp; style separation</li>
          <li class="feature-item"><span class="check-icon">&check;</span> Zero cloud data sharing</li>
        </ul>
      </div>
      <a href="#" class="btn-plan">Get started free</a>
    </div>

    <!-- Pro Tier (Featured) -->
    <div class="pricing-card featured">
      <div class="featured-tag">Most Popular</div>
      <div>
        <div class="plan-name">Pro</div>
        <div class="plan-pitch">AI-assisted in-place DOCX tailoring and ATS match verification.</div>
        <div class="plan-price-row">
          <span class="plan-price">$12</span>
          <span class="plan-cadence">/ month</span>
        </div>
        <ul class="feature-list">
          <li class="feature-item"><span class="check-icon">&check;</span> Everything in Free</li>
          <li class="feature-item"><span class="check-icon">&check;</span> DOCX in-place XML tailoring</li>
          <li class="feature-item"><span class="check-icon">&check;</span> Adversarial fact verifier</li>
          <li class="feature-item"><span class="check-icon">&check;</span> Keyword &amp; ATS score breakdown</li>
          <li class="feature-item"><span class="check-icon">&check;</span> Cloud sync &amp; share links</li>
        </ul>
      </div>
      <a href="#" class="btn-plan primary">Start 14-day Pro trial</a>
    </div>

    <!-- Team / Lifetime Tier -->
    <div class="pricing-card">
      <div>
        <div class="plan-name">Lifetime Pass</div>
        <div class="plan-pitch">Pay once, own forever. For ambitious professionals and consultants.</div>
        <div class="plan-price-row">
          <span class="plan-price">$79</span>
          <span class="plan-cadence">one-time payment</span>
        </div>
        <ul class="feature-list">
          <li class="feature-item"><span class="check-icon">&check;</span> Everything in Pro</li>
          <li class="feature-item"><span class="check-icon">&check;</span> Lifetime model updates</li>
          <li class="feature-item"><span class="check-icon">&check;</span> Priority rendering queue</li>
          <li class="feature-item"><span class="check-icon">&check;</span> Unlimited custom template locks</li>
          <li class="feature-item"><span class="check-icon">&check;</span> Offline CLI access</li>
        </ul>
      </div>
      <a href="#" class="btn-plan">Get Lifetime Pass</a>
    </div>
  </div>
</body>
</html>
"""

def generate():
    print("Writing HTML mockups...")
    mockup_files = [
        ("mockup_landing_hero.html", LANDING_HERO_HTML),
        ("mockup_resume_editor.html", EDITOR_MOCKUP_HTML),
        ("mockup_pricing.html", PRICING_MOCKUP_HTML),
    ]

    for fname, content in mockup_files:
        (MOCKUP_DIR / fname).write_text(content, encoding="utf-8")
        (ARTIFACT_DIR / fname).write_text(content, encoding="utf-8")
        print(f"Written: {fname}")

    print("Rendering mockup screenshots via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        for fname, _ in mockup_files:
            png_name = fname.replace(".html", ".png")
            page.goto(f"file:///{str(MOCKUP_DIR / fname).replace('\\', '/')}", wait_until="networkidle")
            page.wait_for_timeout(500)
            page.screenshot(path=str(MOCKUP_DIR / png_name), full_page=True)
            page.screenshot(path=str(ARTIFACT_DIR / png_name), full_page=True)
            print(f"Captured screenshot: {png_name}")

        browser.close()

if __name__ == "__main__":
    generate()
