import unittest
import sys

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pyocr

from pyocr.util import (
    digits_only,
    is_on_path,
    to_unicode,
)


class TestPyOCR(unittest.TestCase):

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    @patch("pyocr.libtesseract.tesseract_raw.is_available")
    @patch("pyocr.util.is_on_path")
    def test_available_tools_tesseract4(self, is_on_path,
                                        is_available, libtess):
        is_on_path.return_value = True
        is_available.return_value = True
        libtess.TessVersion.return_value = b"4.0.0"
        self.assertListEqual(
            pyocr.get_available_tools(),
            [
                pyocr.tesseract,
                pyocr.libtesseract,
                pyocr.cuneiform,
            ]
        )

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    @patch("pyocr.libtesseract.tesseract_raw.is_available")
    @patch("pyocr.util.is_on_path")
    def test_available_tools_tesseract3(self, is_on_path,
                                        is_available, libtess):
        is_on_path.return_value = True
        is_available.return_value = True
        libtess.TessVersion.return_value = b"3.5.0"
        self.assertListEqual(
            pyocr.get_available_tools(),
            [
                pyocr.tesseract,
                pyocr.libtesseract,
                pyocr.cuneiform,
            ]
        )

    @patch("pyocr.libtesseract.tesseract_raw.g_libtesseract")
    @patch("pyocr.libtesseract.tesseract_raw.is_available")
    @patch("pyocr.util.is_on_path")
    def test_available_tools_tesseract3_0(self, is_on_path,
                                          is_available, libtess):
        is_on_path.return_value = True
        is_available.return_value = True
        libtess.TessVersion.return_value = b"3.0.0"
        self.assertListEqual(
            pyocr.get_available_tools(),
            [
                pyocr.tesseract,
                pyocr.cuneiform,
            ]
        )

    def test_digits_only(self):
        self.assertEqual(digits_only("azer"), 0)
        self.assertEqual(digits_only("10.0.1"), 10)
        self.assertEqual(digits_only("42azer"), 42)
        self.assertEqual(digits_only("qsdf42azer"), 0)

    def test_is_on_path(self):
        self.assertTrue(any((is_on_path("python"), is_on_path("python2"),
                            is_on_path("python3"))))
        # let's hope nobody is crazy enough to name an executable like this
        self.assertFalse(is_on_path("windows95"))

    def test_to_unicode(self):
        self.assertEqual(to_unicode("salut, \u00e7a va ?"),
                         u"salut, \u00e7a va ?")

    @unittest.skipUnless(sys.version_info >= (3, 0),
                         "Test for python3 to_unicode")
    def test_to_unicode_python3(self):
        self.assertEqual(to_unicode("salut, \u00e7a va ?".encode("utf-8")),
                         u"salut, \u00e7a va ?".encode("utf-8"))

    @unittest.skipIf(sys.version_info >= (3, 0),
                     "Test for python2 unicode support")
    def test_to_unicode_python2(self):
        self.assertEqual(to_unicode("salut, \u00e7a va ?".encode("utf-8")),
                         u"salut, \u00e7a va ?")
