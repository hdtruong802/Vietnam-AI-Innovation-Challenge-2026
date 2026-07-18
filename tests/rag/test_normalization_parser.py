"""Tests for deterministic Phase 2 normalization and section parsing."""

from __future__ import annotations

import unittest

from backend.app.rag.normalization import normalize_document
from backend.app.rag.parsing import parse_sections


class NormalizationTests(unittest.TestCase):
    def test_normalization_is_idempotent_and_preserves_line_count(self) -> None:
        source = "\ufeffTha\u0300nh pha\u0302\u0300n\t ho\u0302\u0300 so\u031b\r\n\r\n Ba\u0309n sao  "
        first = normalize_document(source)
        second = normalize_document(first.text)

        self.assertEqual(first.text, second.text)
        self.assertEqual(3, len(first.lines))
        self.assertEqual("Thành phần hồ sơ", first.lines[0])
        self.assertIn("byte_order_mark_removed", first.warnings)
        self.assertEqual((0, len(first.lines[0])), first.line_span(1, 1))

    def test_invalid_line_span_is_rejected(self) -> None:
        document = normalize_document("one\ntwo")
        with self.assertRaises(ValueError):
            document.line_span(0, 1)


class ParserTests(unittest.TestCase):
    def test_parser_covers_document_with_stable_sections(self) -> None:
        document = normalize_document(
            "Đăng ký khai sinh\n"
            "Thông tin thủ tục\n"
            "Thành phần hồ sơ\n"
            "Bản chính giấy chứng sinh\n"
            "Thời hạn giải quyết: 03 ngày làm việc\n"
            "Lệ phí: không"
        )
        first = parse_sections(document, "fixture-1")
        second = parse_sections(document, "fixture-1")

        self.assertEqual(first, second)
        self.assertEqual(1, first[0].start_line)
        self.assertEqual(len(document.lines), first[-1].end_line)
        self.assertEqual(
            ["overview", "documents", "processing_time", "fees"],
            [section.section_type for section in first],
        )
        self.assertTrue(all(section.section_id for section in first))

    def test_parser_rejects_empty_source_id(self) -> None:
        with self.assertRaises(ValueError):
            parse_sections(normalize_document("Nội dung"), "")

    def test_distinct_fields_remain_distinct_when_types_match(self) -> None:
        sections = parse_sections(
            normalize_document(
                "Cơ quan thực hiện: Ủy ban nhân dân\n"
                "Cơ quan có thẩm quyền: Ủy ban nhân dân"
            ),
            "fixture-2",
        )
        self.assertEqual(["authority", "authority"], [s.section_type for s in sections])
        self.assertEqual([(1, 1), (2, 2)], [(s.start_line, s.end_line) for s in sections])


if __name__ == "__main__":
    unittest.main()
