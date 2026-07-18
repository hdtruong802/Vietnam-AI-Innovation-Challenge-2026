# Phase 1 chunking fixtures

This directory contains metadata-only fixture annotations for the three MVP procedures. Raw TXT content remains in the ignored local `dataset_raw/` directory and is never copied into Git.

## Selection

- 1,500 documents were selected at even positions across the 5,652-file corpus.
- Keyword scoring produced candidate pools without sending raw data to a model/provider.
- Ten candidates per procedure were chosen with a mix of standard, short, long, long-line, navigation-noise and encoding-review cases.
- Procedure labels and section boundaries are machine-seeded and remain `needs_review` until K1 review.

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

The keyword retrieval baseline filters to `approved` chunks only. Current Phase 1
fixtures remain `needs_review`, so the smoke command should fail closed with
`official_review_required` instead of returning evidence:

```powershell
python scripts/data/evaluate_keyword_retrieval.py
```
