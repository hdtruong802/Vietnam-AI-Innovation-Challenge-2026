# Phase 1 chunking fixtures

This directory contains metadata-only fixture annotations for the three MVP procedures. Raw TXT content remains in the ignored local `dataset_raw/` directory and is never copied into Git.

## Selection

- 1,500 documents were selected at even positions across the 5,652-file corpus.
- Keyword scoring produced candidate pools without sending raw data to a model/provider.
- Ten candidates per procedure were chosen with a mix of standard, short, long, long-line, navigation-noise and encoding-review cases.
- Procedure labels and section boundaries are machine-seeded at first and can move through the review lifecycle after K1 review.

`expected_sections` uses `section_type:start_line-end_line` spans separated by `|`. Spans are one-based, contiguous and cover the complete decoded document including blank lines. The CSV stores only IDs, hashes, metrics, tags and offsets.

## Validation

Manifest-only validation works without the ignored corpus and is suitable for CI:

```powershell
python scripts/data/validate_chunking_fixtures.py
```

Local strict validation also checks raw-file presence, UTF-8 decoding, SHA-256 and structural metrics:

```powershell
python scripts/data/validate_chunking_fixtures.py --verify-raw
```

Strict validation does not print raw text. A passing validator does not mean that legal/procedure labels are approved; K1 review is still mandatory.

## Phase 2 parser evaluation

The deterministic normalizer/parser can be evaluated locally without committing raw
content or generated sections:

```powershell
python scripts/data/evaluate_chunking_parser.py
```

Use `--output artifacts/chunking/phase2-sections.jsonl` only when a local parsed
artifact is needed. The CLI rejects output paths outside the ignored `artifacts/`
directory. Phase 1 annotations remain `needs_review`, so the reported boundary F1
is diagnostic until K1 confirms the labels.

## Phase 3 diagnostic chunk build

The deterministic chunk builder consumes Phase 2 parser output and keeps fixture
chunks in `needs_review` status. It enforces the 450-token hard maximum with the
standard-library heuristic tokenizer and does not create an embedding or index:

```powershell
python scripts/data/build_chunking_fixtures.py
```

Use `--output artifacts/chunking/phase3-chunks.jsonl --report-output artifacts/chunking/phase3-report.json`
only for ignored local artifacts. The CLI rejects output paths outside
`artifacts/`.

## Phase 4 keyword retrieval smoke

The keyword retrieval baseline filters to `approved` chunks only. If Phase 1
fixtures remain `needs_review`, the smoke command should fail closed with
`official_review_required` instead of returning evidence:

```powershell
python scripts/data/evaluate_keyword_retrieval.py
```

## Phase 5/6 source gate and Recall@K

`SourceDocument` validation blocks unreviewed, stale, future-effective or
incomplete provenance from producing `approved` chunk metadata. Recall@K
evaluation is available for approved chunk JSONL artifacts, with a synthetic
smoke path that does not use raw corpus data:

```powershell
python scripts/data/evaluate_retrieval_golden.py --sample
```

For real K1-approved chunks, pass `--chunks artifacts/...jsonl`; the CLI rejects
tracked output paths so approved/rebuilt artifacts stay local unless a separate
publication task allows them.

## Phase 7 approved pack build

Create a local candidate manifest from parser-boundary rows marked `approved`:

```powershell
python scripts/data/prepare_approved_source_manifest.py --output artifacts/chunking/approved-sources-template.csv
```

That annotation only approves chunk boundaries; it is not K1 content/legal
approval. A reviewer must fill provenance, permission/effective/verification
dates, `reviewed_by`, `reviewed_at`, and explicitly change `review_status` from
`needs_review` to `approved`. Then build approved chunks:

```powershell
python scripts/data/build_approved_rag_pack.py --approved-manifest artifacts/chunking/approved-sources-template.csv --output artifacts/chunking/approved-chunks.jsonl --report-output artifacts/chunking/approved-report.json
```

The chatbot clean-pack wrapper also requires that explicitly reviewed manifest;
it no longer invents local K1 provenance:

```powershell
python scripts/data/build_demo_clean_rag_pack.py --approved-manifest artifacts/chunking/approved-sources-reviewed.csv
```

This writes `artifacts/chatbot/clean-rag-chunks.jsonl` only after the manifest
passes the approved-source gate. Candidate or incomplete manifests fail closed.
