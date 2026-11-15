# MirrorCV Agent Contracts

This package defines the versioned schemas, TypeScript interfaces, and Pydantic v2 models that form the single source of truth for all data exchanges between the MirrorCV editor, backend, and the three specialized AI agents:

1. **Agent 1 (Template Guardian)**: Produces `TemplateProfile` & `SlotMap` (measuring slot budgets, roles, fonts, and geometry from imported DOCX/PDF or editor layouts).
2. **Agent 2 (Analyst & Tailor)**: Produces `TailoredContent` (optimizing bullets and summary against job descriptions with zero hallucinations and strict inline markup rules).
3. **Agent 3 (Composer)**: Produces `CompositionResult` (synthesizing tailored text into the verified template without visual overflow or font changes).

---

## 1. Embedding Model & Vector Storage (Change #7)

For semantic profile matching, skills gap retrieval, and future Retrieval-Augmented Generation (RAG) over `master_profile_items`:

- **Selected Model**: `text-embedding-3-small` (OpenAI)
- **Vector Dimension**: **`1536`**
- **Distance Metric**: **Cosine Distance** (`<=>` in `pgvector`)
- **Index Type**: `HNSW` (`m = 16`, `ef_construction = 64`)
- **Database Column**: `master_profile_items.embedding vector(1536)`
- **Rationale**:
  - Top-tier price-performance ratio (\$0.02 / 1M tokens) with high multilingual retrieval accuracy on standard MTEB benchmarks.
  - Native standard for Supabase `pgvector` indexing and LangChain/LangGraph embeddings.
  - Dimensionality of 1536 preserves granular semantic clustering for granular resume accomplishments and skills.

---

## 2. Allowed Inline Markup Rules (Change #8)

To maintain absolute template fidelity and prevent broken styling or security exploits, text fields (especially within bullet points and summary paragraphs) permit **only** safe inline markup. Raw HTML, headers, and block-level tags are strictly forbidden.

### Supported Syntax:
1. **Bold**: `**text**` (e.g., `Architected **4.2M daily export jobs**`)
2. **Italic**: `*text*` (e.g., `Published in *ACM Transactions*`)
3. **Link**: `[label](url)` (e.g., `[Project Demo](https://example.com)`)

### Disallowed Syntax:
- **Raw HTML**: `<b>`, `<strong>`, `<i>`, `<span>`, `<div>`, `<script>`, etc.
- **Block Elements**: Headers (`# Header`), horizontal rules (`---`), blockquotes (`> quote`).
- **Code Blocks**: Fenced triple backticks (```).
- **Images**: `![alt](url)` (images must be uploaded through the designated photo/asset pipeline).

### Validation in Agent Contracts:
In `tailored_content.schema.json`, every change is governed by:
- `rules.no_new_facts_allowed`: `true` (enforced by the anti-hallucination verification step).
- `rules.allowed_inline_markup`: `["bold", "italic", "link"]`.
- `tailored_text`: Must validate against safe inline markup expressions and reference an original resume fact (`source_reference.source_item_id`).

---

## 3. Schemas Overview

- `schemas/resume_content.schema.json`: Complete resume content hierarchy with stable UUIDs.
- `schemas/style_tokens.schema.json`: Complete style token tokens with explicit units.
- `schemas/template_profile.schema.json`: Agent 1 output detailing text slots, geometry, and character budgets.
- `schemas/tailored_content.schema.json`: Agent 2 output with tailored text, reasons, and grounded references.
- `schemas/composition_result.schema.json`: Agent 3 output detailing output files, fidelity score, and overflow metrics.
