"""Evaluate deterministic parsing against metadata-only Phase 1 annotations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.app.rag.normalization import decode_utf8, normalize_document  # noqa: E402
from backend.app.rag.parsing import parse_sections  # noqa: E402


DEFAULT_MANIFEST = (
    REPOSITORY_ROOT / "tests" / "rag" / "fixtures" / "chunking_phase1_manifest.csv"
)


@dataclass(slots=True)
class Counts:
    true_positive: int = 0
    predicted: int = 0
    expected: int = 0
    correct_line_types: int = 0
    lines: int = 0


def _expected_sections(encoded: str) -> list[tuple[str, int, int]]:
    sections: list[tuple[str, int, int]] = []
    for value in encoded.split("|"):
        section_type, line_range = value.split(":", maxsplit=1)
        start, end = line_range.split("-", maxsplit=1)
        sections.append((section_type, int(start), int(end)))
    return sections


def _line_labels(sections: list[tuple[str, int, int]]) -> list[str]:
    labels: list[str] = []
    for section_type, start, end in sections:
        if start != len(labels) + 1:
            raise ValueError("non-contiguous section ranges")
        labels.extend([section_type] * (end - start + 1))
    return labels


def evaluate(
    manifest_path: Path,
    repository_root: Path,
    output_path: Path | None = None,
) -> Counts:
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    counts = Counts()
    output_handle = None
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_handle = output_path.open("w", encoding="utf-8", newline="\n")
    try:
        for row in rows:
            raw_path = repository_root / row["raw_path"]
            payload = raw_path.read_bytes()
            if hashlib.sha256(payload).hexdigest() != row["raw_sha256"]:
                raise ValueError(f"checksum mismatch for {row['raw_document_id']}")
            document = normalize_document(decode_utf8(payload))
            if normalize_document(document.text).text != document.text:
                raise ValueError(f"normalization is not idempotent for {row['raw_document_id']}")
            predicted = parse_sections(document, source_id=row["raw_document_id"])
            if parse_sections(document, source_id=row["raw_document_id"]) != predicted:
                raise ValueError(f"parsing is not deterministic for {row['raw_document_id']}")
            expected = _expected_sections(row["expected_sections"])

            predicted_boundaries = {section.end_line for section in predicted[:-1]}
            expected_boundaries = {end for _, _, end in expected[:-1]}
            counts.true_positive += len(predicted_boundaries & expected_boundaries)
            counts.predicted += len(predicted_boundaries)
            counts.expected += len(expected_boundaries)

            predicted_labels = _line_labels(
                [
                    (section.section_type, section.start_line, section.end_line)
                    for section in predicted
                ]
            )
            expected_labels = _line_labels(expected)
            counts.correct_line_types += sum(
                predicted_label == expected_label
                for predicted_label, expected_label in zip(
                    predicted_labels, expected_labels
                )
            )
            counts.lines += len(expected_labels)

            if output_handle is not None:
                record = {
                    "source_id": row["raw_document_id"],
                    "normalizer_version": document.normalizer_version,
                    "sections": [section.to_dict() for section in predicted],
                }
                output_handle.write(
                    json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
                )
    finally:
        if output_handle is not None:
            output_handle.close()
    return counts


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--minimum-boundary-f1", type=float, default=0.0)
    arguments = parser.parse_args(argv)

    if arguments.output is not None:
        output = arguments.output.resolve()
        artifacts = (arguments.repository_root / "artifacts").resolve()
        if artifacts not in output.parents:
            parser.error("--output must be below the ignored artifacts/ directory")

    try:
        counts = evaluate(
            arguments.manifest.resolve(),
            arguments.repository_root.resolve(),
            arguments.output,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Parser evaluation failed: {error}", file=sys.stderr)
        return 1

    precision = _ratio(counts.true_positive, counts.predicted)
    recall = _ratio(counts.true_positive, counts.expected)
    f1 = _ratio(2 * precision * recall, precision + recall)
    line_accuracy = _ratio(counts.correct_line_types, counts.lines)
    print(
        f"boundary precision={precision:.4f} recall={recall:.4f} f1={f1:.4f}; "
        f"line_type_accuracy={line_accuracy:.4f}; lines={counts.lines}"
    )
    return 0 if f1 >= arguments.minimum_boundary_f1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
