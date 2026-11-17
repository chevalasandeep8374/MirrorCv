# MirrorCV Visual Redesign: Step 0 Capture & Proposal Report

> **Branch**: `feature/taskflow-visual-redesign`  
> **Status**: **Awaiting User Review & Approval** (No code modified beyond reference capture and mockups)  
> **Reference Template**: [TaskFlow Marketing Template](https://taskflow-marketing-612994.hostingersite.com/)  
> **Strict Guardrails**: Zero reference copy/names ("TaskFlow", "Sophie Mitchell", etc.); zero fake social proof; 100% self-hosted open fonts; zero changes to `<ResumeDocument>` or headless PDF parity baselines.

---

## 1. Visual Parity Side-by-Side Comparisons

Three high-fidelity mockups of MirrorCV screens were crafted directly with the extracted design tokens, typography, radii, and bevel shadows, and composited side-by-side against the live reference captures:

### Screen 1: Landing Hero & Interactive Product Stage
- **Left**: Reference template landing page hero with lavender stage (`#E9E3FA`) and floating app container.
- **Right**: Proposed MirrorCV landing page hero with announcement capsule, deep slate headline, tactile royal blue CTA (`0 3px 0 #1D4FBA`), 3 true micro-claims, and the interactive floating resume workspace.
- **Side-by-side comparison image**: [comparison_1_hero.png](file:///C:/Users/CH%20SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference/comparisons/comparison_1_hero.png)

### Screen 2: Real Product Workspace / Resume Editor
- **Left**: Reference template workspace app with task category tags, avatars, checklist progress, and card layout.
- **Right**: Proposed MirrorCV FlowCV-class editor with dark navigation sidebar, white section cards with category badges and completion fractions, typography/spacing sliders, and live A4 paper preview.
- **Side-by-side comparison image**: [comparison_2_editor.png](file:///C:/Users/CH%20SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference/comparisons/comparison_2_editor.png)

### Screen 3: Pricing Section & Entitlement Cards
- **Left**: Reference template 3-tier pricing layout with pill toggle and highlighted middle card.
- **Right**: Proposed MirrorCV 3-tier pricing grid (**Free Beta**, **Pro Job Hunt Pass**, **Lifetime / Team**) based on real system entitlements, featuring the royal blue 3D bevel CTA and clear guarantee badges.
- **Side-by-side comparison image**: [comparison_3_pricing.png](file:///C:/Users/CH%20SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference/comparisons/comparison_3_pricing.png)

---

## 2. Reference DOM Extraction & Design Token Table

Extracted from DOM inspection of `https://taskflow-marketing-612994.hostingersite.com/` across 1440px, 1024px, 768px, and 390px viewports (source of truth: [reference_styles.json](file:///C:/Users/CH%20SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference/reference_styles.json)):

### 2.1 Color Palette Tokens

| Token Name | Reference Value | CSS Variable (`tokens.css`) | Tailwind Class | Semantic Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Page Background** | `#FFFFFF` | `--bg-page: #FFFFFF;` | `bg-white` | Main body & content surface |
| **Stage Background** | `rgb(233, 227, 250)` (`#E9E3FA`) | `--bg-stage: #E9E3FA;` | `bg-stage` | Signature hero and feature stage band |
| **Stage Border** | `rgb(216, 209, 244)` (`#D8D1F4`) | `--border-stage: #D8D1F4;` | `border-stage` | 1px border framing the stage container |
| **Card Surface** | `#FFFFFF` | `--surface-card: #FFFFFF;` | `bg-card` | Clean white card tiles and editor panes |
| **Subtle Border** | `rgb(227, 230, 237)` (`#E2E8F0`) | `--border-subtle: #E2E8F0;` | `border-subtle` | 1px card boundaries and separators |
| **Heading Ink** | `rgb(30, 41, 59)` (`#1E293B`) | `--text-main: #1E293B;` | `text-slate-900` | H1, H2, H3, prominent card titles |
| **Body Muted** | `rgb(100, 116, 139)` (`#64748B`) | `--text-muted: #64748B;` | `text-slate-500` | Paragraphs, subtitles, form field hints |
| **Dim Text** | `rgb(148, 163, 184)` (`#94A3B8`) | `--text-dim: #94A3B8;` | `text-slate-400` | Footnotes, breadcrumbs, shortcuts |
| **Primary Blue** | `rgb(37, 99, 235)` (`#2563EB`) | `--primary: #2563EB;` | `bg-primary-blue` | Primary action buttons, active tab indicators |
| **Primary Bevel** | `rgb(29, 79, 186)` (`#1D4FBA`) | `--primary-bevel: #1D4FBA;` | `shadow-btn-bevel` | 3px bottom 3D shadow for primary buttons |
| **Primary Hover** | `rgb(29, 78, 216)` (`#1D4ED8`) | `--primary-hover: #1D4ED8;` | `hover:bg-primary-hover` | Button hover background |
| **Lavender Pill BG** | `rgb(238, 234, 255)` (`#EEEAFF`) | `--accent-pill-bg: #EEEAFF;` | `bg-pill-purple` | Announcement badge, category chip background |
| **Lavender Pill Text**| `rgb(119, 91, 204)` (`#775BCC`) | `--accent-pill-text: #775BCC;` | `text-pill-purple` | Announcement badge text, chip label |
| **Success Badge** | `rgb(220, 252, 231)` / `#166534` | `--badge-success-bg: #DCFCE7;` | `bg-emerald-100 text-emerald-800` | "Matched", "ATS Verified", "Complete" badges |
| **Warning Badge** | `rgb(254, 243, 199)` / `#92400E` | `--badge-warning-bg: #FEF3C7;` | `bg-amber-100 text-amber-800` | "Missing Skill", "Review Needed" |
| **Footer Dark** | `rgb(22, 23, 24)` (`#161718`) | `--bg-footer: #161718;` | `bg-dark-footer` | Bottom dark band container |

### 2.2 Typography Specification

- **Headings Font**: `"Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, sans-serif`
  - Self-hosted via Next.js `next/font/google` (`Plus_Jakarta_Sans`).
  - H1 Hero: `font-size: clamp(40px, 5.2vw, 72px);`, `font-weight: 800;`, `line-height: 1.1;`, `letter-spacing: -3.4px;` (desktop) / `-1.8px` (mobile).
  - H2 Section: `font-size: clamp(28px, 3.5vw, 45px);`, `font-weight: 700;`, `line-height: 1.15;`, `letter-spacing: -1.7px;`.
  - H3 Card Title: `font-size: 20px - 24px;`, `font-weight: 700;`, `letter-spacing: -0.8px;`.
  - Eyebrows: `font-size: 12px;`, `font-weight: 700;`, `letter-spacing: 1.2px;`, `text-transform: uppercase;`.
- **Body & UI Font**: `"Manrope", -apple-system, BlinkMacSystemFont, sans-serif`
  - Self-hosted via `next/font/google` (`Manrope`).
  - Body Regular: `font-size: 16px;`, `line-height: 24px;`, `font-weight: 400;`.
  - UI Labels / Controls: `font-size: 13px - 14px;`, `font-weight: 600;`, `letter-spacing: -0.2px;`.
  - Captions / Meta: `font-size: 11px - 12px;`, `font-weight: 500;`.

### 2.3 Radii & Elevation Scale

- **Border Radii**:
  - `radius-sm`: `6px` (tags, small badges, input fields)
  - `radius-btn`: `7px` - `8px` (buttons, segmented controls)
  - `radius-card`: `12px` (content cards, pricing tiles, editor panels)
  - `radius-stage`: `14px` (top hero stage and feature stages)
  - `radius-pill`: `9999px` (announcement capsule, status pills)
- **Shadows**:
  - Primary Button 3D Bevel: `0px 3px 0px 0px #1D4FBA` (active: `0px 1px 0px 0px #1D4FBA; transform: translateY(2px);`)
  - Stage Elevation: `0px 12px 36px rgba(30, 41, 59, 0.08)`
  - Card Elevation: `0px 4px 12px rgba(30, 41, 59, 0.05)`
  - Inset Highlight: `0px -1px 0px 0px rgba(255, 255, 255, 0.8) inset`
  - Floating Resume Preview: `0px 20px 40px -15px rgba(30, 41, 59, 0.15)`

---

## 3. Landing Page Copy Deck & 3 Headline Options

All copy strictly abides by the project guardrails: **no fabricated social proof, no fake user counts, no simulated testimonials, and 100% honest claims** (native PDF and byte-preserved DOCX export, deterministic verification, zero AI hallucinations).

### 3.1 Headline Options for the Hero

| Option | Headline (H1) | Subtitle | Tone & Strategic Rationale |
| :--- | :--- | :--- | :--- |
| **Option A (Recommended)** | **Your resume. Exact template. Tailored in seconds.** | *Keep the typography and layout you spent hours perfecting. Tailor bullet points to any job description with verifiable facts—exported to native PDF and byte-preserved DOCX.* | **Direct, confident, and capability-focused.** Directly attacks the pain point of other builders destroying formatting. |
| **Option B (Editorial / Precision)** | **The resume editor built for precision, not guesswork.** | *Dual-pane control, sub-millimeter print parity, and strict AI tailoring that never invents numbers. Your resume stays yours—every single line.* | **Craft-oriented and trustworthy.** Appeals to senior engineers and professionals who hate generic AI resumes. |
| **Option C (ATS & Match Clarity)** | **Tailor every application without breaking your layout.** | *Match skill requirements from real job postings while preserving your exact DOCX styling. Verifiable bullet improvements with zero hallucinated metrics.* | **Job-hunt pragmatic.** Focuses on the immediate utility of matching job descriptions accurately. |

### 3.2 Full Landing Page Copy Deck

1. **Sticky Header**:
   - Wordmark: **MirrorCV**
   - Navigation:
     - `Product` (Dropdown: *Tailor to a job*, *Keep your template*, *Resume editor*)
     - `Why MirrorCV`
     - `Pricing`
     - `Changelog`
   - Actions: `Log in` (secondary outlined), `Get started free` (primary royal blue 3D bevel).
   - Logged-in state: `My workspace`, `Billing`, `Avatar / Account`.

2. **Announcement Pill**:
   - Tag: `NEW` (white on royal blue)
   - Text: `FlowCV-Class Editor Engine with Sub-Millimeter Parity`
   - Link: `/changelog#flowcv-editor-v2` (links to actual changelog entry)

3. **Hero Section**:
   - Selected H1 Headline (Option A)
   - Primary CTA: `Build your resume free`
   - Secondary CTA: `See it in action` (smooth scroll to editor demo)
   - Micro-Claims Row (3 true claims):
     - `✓ Sub-millimeter PDF & DOCX parity`
     - `✓ Verifier-enforced factual tailoring`
     - `✓ Free export, no watermark`

4. **Floating Product Stage (The Interactive Workspace)**:
   - Eyebrow: `01 / THE WORKSPACE`
   - Realistic editor mockup demonstrating dual-pane synchronization:
     - Left pane: Clean categorized section cards (Personal Details, Experience, Education, Skills) with progress fractions (`4/4`, `3/3`).
     - Right pane: High-fidelity floating A4 resume document rendered with crisp typography and section bars.

5. **Numbered Feature Trio**:
   - **01 Keep Your Template**:
     - Eyebrow: `TEMPLATE FIDELITY`
     - Heading: *Upload your existing DOCX. Keep every millimeter.*
     - Description: *Most tools strip your formatting into generic web templates. MirrorCV parses your exact fonts, margins, tab stops, and bullet indents.*
     - Interactive Illustration: Interactive Before/After slider showing raw Word document vs. parsed editable resume.
   - **02 Tailor to a Job**:
     - Eyebrow: `FACTUAL TAILORING`
     - Heading: *Target key qualifications without inventing experience.*
     - Description: *Our adversarial verifier guarantees that tailored bullets only highlight your genuine history. Hallucinated numbers and unconfirmed skills are automatically rejected.*
     - Interactive Illustration: Split view showing Job Requirements alongside Tailored Bullet with confidence score and diff highlights.
   - **03 ATS Verification**:
     - Eyebrow: `MACHINE READABILITY`
     - Heading: *Standard structure that ATS parsers read cleanly.*
     - Description: *Inspect exact text extraction layers. Avoid invisible tables, corrupt glyphs, or unparseable multi-column layouts that trigger parser drop-offs.*
     - Interactive Illustration: Live ATS parsing preview showing structured section recognition and match checklist.

6. **How It Works (Honest 3-Step Walkthrough)**:
   - Step 1: **Import or Select** — *Upload an existing Word resume or start fresh from proven executive and technical layouts.*
   - Step 2: **Target & Refine** — *Paste any job description to instantly surface keyword gaps and refine bullet impact with guided metrics.*
   - Step 3: **Export with Parity** — *Download in clean native PDF or pixel-preserved DOCX ready for immediate application.*

7. **Pricing Section (True Entitlements Grid)**:
   - **Free Beta** ($0):
     - *Up to 2 active resumes*
     - *Full dual-pane FlowCV-class editor*
     - *Standard PDF & DOCX exports*
     - *No watermark, ever*
   - **Pro Job Hunt Pass** ($14 / month or $29 / 3-month pass) — **Featured with Blue Bevel Button**:
     - *Unlimited active resumes & version histories*
     - *Full job description tailoring & gap analysis*
     - *Adversarial verifier & bullet improver*
     - *Native multi-format export (PDF, DOCX, Plain Text, JSON)*
     - *Priority headless rendering queue*
   - **Lifetime / Team** ($79 one-time):
     - *All Pro features forever*
     - *Master career profile management*
     - *Early access to new layout engines and upcoming features*

8. **FAQ Accordion**:
   - *Will MirrorCV change my Word document layout?* -> No. MirrorCV uses byte-level XML preservation for existing DOCX templates.
   - *Does the AI invent metrics or work experience?* -> Never. Our pipeline enforces strict adversarial verification.
   - *Are my PDFs watermarked?* -> No. Both free and pro exports are 100% clean and unwatermarked.

9. **Bottom Call-to-Action Band**:
   - Dark band (`#161718`)
   - Heading: *Ready for a resume that actually looks like your resume?*
   - Subcopy: *Start building in seconds. No credit card required.*
   - Button: Royal blue 3D bevel `Create your resume now`.

10. **Site Footer**:
    - Clean columns: Product, Capabilities, Resources, Company, Legal.
    - Wordmark and real copyright notice: `© 2026 MirrorCV. Built for career precision.`

---

## 4. Component-by-Component Restyle Plan

| Target Component / Page | Current Implementation | Proposed TaskFlow Restyle | Parity / Functionality Safeguard |
| :--- | :--- | :--- | :--- |
| **Site Header** (`src/app/page.tsx`) | Basic static navbar with generic links | Sticky translucent header (`rgba(255,255,255,0.94)` + `backdrop-blur-md`), 1px bottom border `#E2E8F0`, dropdown menus with rounded items and royal blue hover state. | Zero routing changes. Links to existing routes (`/login`, `/dashboard`, `/pricing`). |
| **Hero Stage** (`src/app/page.tsx`) | Simple 2-column flexbox with text & floating image | Lavender stage wrapper (`#E9E3FA`, border `#D8D1F4`, `rounded-[14px]`) containing the interactive workspace frame with window controls and dual-pane preview. | Pure CSS/HTML container; uses existing resume preview component. |
| **Primary Buttons** (`Button.tsx`) | Flat standard Tailwind colors | Royal blue `#2563EB` with tactile bottom shadow `0 3px 0 #1D4FBA`, active state `translate-y-[2px]` with shadow `0 1px 0 #1D4FBA`. | Preserves all `onClick`, disabled, loading states and props. |
| **Announcement Capsule** | None | Rounded pill `bg-[#EEEAFF] text-[#775BCC]` with nested royal blue badge `NEW`. | Links to `/changelog`. |
| **Workspace / Dashboard** (`src/app/dashboard/page.tsx`) | Gray background with standard cards | Crisp white surface with TaskFlow-styled grid tiles, status tags (`Active`, `Draft`, `Tailored`), category chips, and clean overflow menus. | Keeps exact Supabase queries, actions, duplicate, delete, and download handlers. |
| **Resume Editor Shell** (`src/app/editor/[id]/page.tsx`) | 4-tab bar (Overview, Content, Customize, AI Tools) | Restyled top bar with clean pill tab indicators, dropdown download menu, and 2-pane split view matching the stage styling. | State management, dirty tracking, autosave, and keyboard shortcuts remain 100% untouched. |
| **Customize Controls** (`src/components/editor/customize/*`) | Default HTML range inputs and square swatches | TaskFlow slider tracks with royal blue filled progress, rounded thumb with bevel shadow, segmented pill toggles, and clean color pickers. | Only presentation updated. Debounce timing and undo/redo history remain identical. |
| **Section Cards** (`src/components/editor/content/*`) | Generic accordions | White rounded cards (`rounded-xl border border-slate-200`) with left drag grip, category badge, and fractional counter (`4/4`). | DnD reordering, eye toggles, and item schema remain completely unchanged. |
| **Auth Pages** (`src/app/login/page.tsx`, `signup`) | Basic center form | Clean centered card with rounded corners, subtle border, royal blue primary submit button, and social login buttons with hairline borders. | Auth token handlers, Supabase client calls, and redirect logic remain untouched. |
| **ResumeDocument & PDF** (`src/components/renderer/*`) | Fixed A4 / Letter PDF layout engine | **STRICTLY UNTOUCHED**. Zero changes to canvas, typography ratios, margins, or SVG/canvas rendering. | Existing 28-combination visual regression baseline suite must remain 100% pixel-identical. |

---

## 5. Implementation Roadmap (Post-Approval)

Once approved, the implementation will proceed on branch `feature/taskflow-visual-redesign` in discrete, verified slices:

- **Slice 1: Design Tokens & Base Primitives**
  - Create `src/styles/tokens.css` with the extracted variables.
  - Update `tailwind.config.ts` mapping.
  - Update self-hosted fonts in `src/app/layout.tsx` (`Plus_Jakarta_Sans` and `Manrope`).
  - Restyle core UI primitives (`Button`, `Input`, `Badge`, `Card`, `Slider`, `Dropdown`).
- **Slice 2: Marketing Site Restyle**
  - Implement sticky header with dropdowns and logged-in states.
  - Build the announcement pill, hero section, and lavender stage.
  - Build the numbered feature trio (01, 02, 03) with interactive mini-illustrations.
  - Build How it Works, Pricing grid, FAQ, and dark band footer.
  - Automated check: `git grep` verifying zero reference strings.
- **Slice 3: Workspace & Auth Restyle**
  - Restyle `/login` and `/signup` screens.
  - Restyle `/dashboard` resume grid, filters, and import/create modals.
- **Slice 4: FlowCV-Class Editor Shell & Customize UI Restyle**
  - Restyle Editor Top Bar, tab switchers, and download dropdown.
  - Restyle Content accordion cards, drag handles, and eye toggles.
  - Restyle Customize sliders, color selectors, and font picker.
  - Run full Playwright test suite to verify no regressions in sliders, undo/redo, or Parity exports.
- **Slice 5: Verification & Visual Regression Re-run**
  - Rerun the visual baseline comparison (`py scripts/compare_visual_baselines.py`) to confirm 100% pixel parity of `<ResumeDocument>` and PDF output.
  - Full mobile responsiveness check at 390px, 768px, 1024px, and 1440px.

---

## 6. Approval Checkpoint

Please review the side-by-side mockups, design tokens, copy deck, and headline options:
1. **Side-by-Side Visuals**: [comparison_1_hero.png](file:///C:/Users/CH%20SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference/comparisons/comparison_1_hero.png), [comparison_2_editor.png](file:///C:/Users/CH%20SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference/comparisons/comparison_2_editor.png), [comparison_3_pricing.png](file:///C:/Users/CH%20SANDEEP/.gemini/antigravity/brain/e3539cfe-1379-4d58-868f-a3ad5b4c09bd/redesign_reference/comparisons/comparison_3_pricing.png)
2. **Preferred Headline**: Option A (*"Your resume. Exact template. Tailored in seconds."*), Option B (*"The resume editor built for precision, not guesswork."*), or Option C (*"Tailor every application without breaking your layout."*).
3. **Approval**: Confirm if you approve proceeding with **Slice 1 (Tokens & Primitives)**.
