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
