"""Unit tests for ocr.py language/model registry and availability filtering.

These avoid loading RapidOCR itself - only the pure registry logic and the
on-disk model-availability filter are exercised.
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ocr  # noqa: E402


class ModelMapConsistencyTests(unittest.TestCase):
    def test_every_script_model_has_a_file(self):
        for lang, model in ocr.LANG_TO_MODEL.items():
            if model is not None:
                self.assertIn(
                    model, ocr.MODEL_FILES,
                    f"{lang}: model key '{model}' missing from MODEL_FILES",
                )

    def test_builtin_languages_present(self):
        builtins = [l for l, m in ocr.LANG_TO_MODEL.items() if m is None]
        self.assertIn("English", builtins)
        self.assertIn("Chinese (Mandarin)", builtins)

    def test_model_files_are_onnx(self):
        for name in ocr.MODEL_FILES.values():
            self.assertTrue(name.endswith(".onnx"))


class AvailableLanguagesTests(unittest.TestCase):
    def test_only_builtins_when_no_models_on_disk(self):
        with mock.patch.object(ocr.os.path, "exists", return_value=False):
            langs = ocr.available_languages()
        expected = [l for l, m in ocr.LANG_TO_MODEL.items() if m is None]
        self.assertEqual(langs, expected)
        self.assertIn("English", langs)

    def test_all_languages_when_models_present(self):
        with mock.patch.object(ocr.os.path, "exists", return_value=True):
            langs = ocr.available_languages()
        self.assertEqual(set(langs), set(ocr.LANG_TO_MODEL.keys()))

    def test_english_always_available(self):
        self.assertIn("English", ocr.available_languages())


if __name__ == "__main__":
    unittest.main()
