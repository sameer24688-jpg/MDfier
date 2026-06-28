"""Unit tests for converters.py pure logic and PDF text-assembly behavior.

These tests avoid heavy/runtime dependencies (PyQt6, RapidOCR, real PyMuPDF
documents) by exercising pure helper functions and by injecting lightweight fake
`fitz` / `pymupdf4llm` / `ocr` modules for the PDF assembly tests.
"""

import os
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import converters  # noqa: E402


class BoundaryOverlapTests(unittest.TestCase):
    def test_removes_exact_duplicate_across_boundary(self):
        prev = "Some paragraph.\nRunning Header Line"
        nxt = "Running Header Line\nNew body text"
        result = converters._strip_boundary_overlap(prev, nxt)
        self.assertNotIn("Running Header Line\n", result + "\n")
        self.assertIn("New body text", result)

    def test_keeps_short_lines(self):
        # Tail shorter than 8 chars must never be stripped (too risky).
        prev = "intro\nC-C"
        nxt = "C-C\nmore"
        self.assertEqual(converters._strip_boundary_overlap(prev, nxt), nxt)

    def test_keeps_non_matching(self):
        prev = "First page tail line"
        nxt = "Different opening line\nbody"
        self.assertEqual(converters._strip_boundary_overlap(prev, nxt), nxt)

    def test_handles_empty_prev(self):
        self.assertEqual(converters._strip_boundary_overlap("", "anything here"), "anything here")

    def test_only_removes_first_occurrence(self):
        prev = "tail\nRepeated Header Value"
        nxt = "Repeated Header Value\nmid\nRepeated Header Value"
        result = converters._strip_boundary_overlap(prev, nxt)
        self.assertEqual(result.count("Repeated Header Value"), 1)


class BlockquoteTests(unittest.TestCase):
    def test_wraps_lines_and_header(self):
        out = converters._as_blockquote("line one\nline two", "**OCR:**")
        lines = out.splitlines()
        self.assertEqual(lines[0], "> **OCR:**")
        self.assertEqual(lines[1], ">")
        self.assertIn("> line one", lines)
        self.assertIn("> line two", lines)

    def test_blank_lines_become_marker_only(self):
        out = converters._as_blockquote("a\n\nb", "**OCR:**")
        self.assertIn(">\n", out + "\n")
        self.assertTrue(all(ln.startswith(">") for ln in out.splitlines()))


class ExtractTablesTests(unittest.TestCase):
    def test_parses_basic_table(self):
        md = (
            "| Entry | Catalyst | Yield |\n"
            "|---|---|---|\n"
            "| 1 | Pd(OAc)2 | 95 |\n"
            "| 2 | dppb | 88 |\n"
        )
        tables = converters.extract_markdown_tables(md)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0][0], ["Entry", "Catalyst", "Yield"])
        self.assertEqual(tables[0][1], ["1", "Pd(OAc)2", "95"])
        self.assertEqual(tables[0][2], ["2", "dppb", "88"])

    def test_no_table_returns_empty(self):
        self.assertEqual(converters.extract_markdown_tables("# Title\n\nJust prose."), [])

    def test_ragged_rows_are_padded_and_truncated(self):
        md = (
            "| A | B | C |\n"
            "|---|---|---|\n"
            "| 1 | 2 |\n"
            "| x | y | z | extra |\n"
        )
        rows = converters.extract_markdown_tables(md)[0]
        self.assertEqual(rows[1], ["1", "2", ""])
        self.assertEqual(rows[2], ["x", "y", "z"])


class EscapedPipeTests(unittest.TestCase):
    def test_escaped_pipe_in_cell_is_preserved(self):
        md = (
            "| Expr | Note |\n"
            "|---|---|\n"
            "| a \\| b | pipe inside |\n"
        )
        rows = converters.extract_markdown_tables(md)[0]
        self.assertEqual(rows[0], ["Expr", "Note"])
        self.assertEqual(rows[1], ["a | b", "pipe inside"])

    def test_escaped_pipe_does_not_split_cell(self):
        md = "| A | B |\n|---|---|\n| x\\|y | z |\n"
        rows = converters.extract_markdown_tables(md)[0]
        self.assertEqual(len(rows[1]), 2)
        self.assertEqual(rows[1][0], "x|y")


class UniquePathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_free_path_is_returned_unchanged(self):
        target = os.path.join(self.tmp, "fresh.md")
        self.assertEqual(converters._unique_path(target), target)

    def test_existing_file_gets_counter(self):
        target = os.path.join(self.tmp, "doc.md")
        open(target, "w").close()
        result = converters._unique_path(target)
        self.assertEqual(os.path.basename(result), "doc (1).md")

    def test_counter_increments_until_free(self):
        for name in ("doc.md", "doc (1).md", "doc (2).md"):
            open(os.path.join(self.tmp, name), "w").close()
        result = converters._unique_path(os.path.join(self.tmp, "doc.md"))
        self.assertEqual(os.path.basename(result), "doc (3).md")

    def test_directory_without_extension(self):
        target = os.path.join(self.tmp, "doc_images")
        os.makedirs(target)
        result = converters._unique_path(target)
        self.assertEqual(os.path.basename(result), "doc_images (1)")


class StripInlineTests(unittest.TestCase):
    def test_strips_markup(self):
        self.assertEqual(converters._strip_inline("**bold**"), "bold")
        self.assertEqual(converters._strip_inline("*it*"), "it")
        self.assertEqual(converters._strip_inline("`code`"), "code")
        self.assertEqual(converters._strip_inline("[text](http://x)"), "text")
        self.assertEqual(converters._strip_inline("![alt](img.png)"), "alt")


class ReverseConversionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def _write_md(self, text):
        path = os.path.join(self.tmp, "doc.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def test_csv_single_table(self):
        path = self._write_md("| A | B |\n|---|---|\n| 1 | 2 |\n")
        outputs = converters.markdown_to_csv(path)
        self.assertEqual(len(outputs), 1)
        with open(outputs[0], encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("A,B", content)
        self.assertIn("1,2", content)

    def test_csv_fallback_line_per_row(self):
        path = self._write_md("first line\nsecond line\n")
        outputs = converters.markdown_to_csv(path)
        with open(outputs[0], encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("first line", content)
        self.assertIn("second line", content)

    def test_txt_strips_markdown(self):
        path = self._write_md("# Heading\n\n**bold** and *italic* text\n")
        outputs = converters.markdown_to_txt(path)
        with open(outputs[0], encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("Heading", content)
        self.assertIn("bold", content)
        self.assertNotIn("**", content)


class InputLimitationTests(unittest.TestCase):
    def test_excel_csv_excluded_from_inputs(self):
        for ext in (".xlsx", ".xls", ".csv"):
            self.assertNotIn(ext, converters.TO_MARKDOWN_EXTS)
            self.assertIn(ext, converters.EXCLUDED_INPUT_EXTS)

    def test_to_markdown_rejects_spreadsheets(self):
        for name in ("data.xlsx", "data.xls", "data.csv"):
            with self.assertRaises(ValueError):
                converters.to_markdown(name)


def _fake_page(text):
    page = types.SimpleNamespace()
    page.get_text = lambda _kind="text": text
    return page


class _FakeDoc:
    def __init__(self, pages):
        self.pages = pages
        self.page_count = len(pages)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __iter__(self):
        return iter(self.pages)

    def __getitem__(self, index):
        return self.pages[index]


class PdfAssemblyTests(unittest.TestCase):
    """Verify the root-cause fix (use_ocr=False) and scanned-page blockquoting."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.pdf_path = os.path.join(self.tmp, "sample.pdf")
        open(self.pdf_path, "wb").close()

    def _run_with_fakes(self, pages, to_markdown_impl, ocr_module=None):
        fake_fitz = types.ModuleType("fitz")
        fake_fitz.open = lambda _path: _FakeDoc(pages)

        fake_p4 = types.ModuleType("pymupdf4llm")
        fake_p4.to_markdown = to_markdown_impl

        modules = {"fitz": fake_fitz, "pymupdf4llm": fake_p4}
        if ocr_module is not None:
            modules["ocr"] = ocr_module

        with mock.patch.dict(sys.modules, modules):
            return converters.pdf_to_markdown(self.pdf_path)

    def test_digital_page_disables_internal_ocr(self):
        captured = {}

        def fake_to_markdown(_path, **kwargs):
            captured.update(kwargs)
            return [{"metadata": {"page_number": 1}, "text": "## Hello\n\nWorld"}]

        outputs = self._run_with_fakes([_fake_page("x" * 50)], fake_to_markdown)

        self.assertFalse(captured.get("use_ocr"), "use_ocr must be False to avoid double-read")
        self.assertTrue(captured.get("force_text"), "force_text should keep the real text layer")
        with open(outputs[0], encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("Hello", content)

    def test_scanned_page_is_blockquoted(self):
        fake_ocr = types.ModuleType("ocr")
        fake_ocr.render_pdf_page = lambda _page: types.SimpleNamespace(close=lambda: None)
        fake_ocr.ocr_pil_image = lambda _img, _lang: "Scanned Heading 2026"

        def fake_to_markdown(_path, **_kwargs):  # not used for a fully scanned doc
            return []

        outputs = self._run_with_fakes(
            [_fake_page("")], fake_to_markdown, ocr_module=fake_ocr
        )
        with open(outputs[0], encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("> **OCR text (scanned page 1):**", content)
        self.assertIn("> Scanned Heading 2026", content)


if __name__ == "__main__":
    unittest.main()
