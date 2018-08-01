import os

import pytest

import PIL.Image

from pyocr import builders
from pyocr import libtesseract
from pyocr import PyocrException
from . import tests_base as base


class TestContext(object):
    """
    These tests make sure the requirements for the tests are met.
    """
    def setup(self):
        pass

    def test_available(self):
        assert libtesseract.is_available()

    def test_version(self):
        assert libtesseract.get_version() in (
                (3, 2, 1),
                (3, 2, 2),
                (3, 3, 0),
                (3, 4, 0),
                (3, 4, 1),
                (3, 5, 0),
            )

    def test_langs(self):
        langs = libtesseract.get_available_languages()
        assert "eng" in langs
        assert "fra" in langs
        assert "jpn" in langs

    def test_nolangs(self, monkeypatch):
        monkeypatch.setenv('TESSDATA_PREFIX', '/opt/tulipe')
        langs = libtesseract.get_available_languages()
        assert langs == []

    def teardown(self):
        pass


class BaseLibtesseract(base.BaseTest):
    tool = libtesseract

    def _path_to_img(self, image_file):
        return os.path.join(
            "tests", "input", "specific", image_file
        )

    def _path_to_out(self, expected_output_file):
        return os.path.join(
            "tests", "output", "specific", "libtesseract", expected_output_file
        )


class TestTxt(base.BaseTestText, BaseLibtesseract):
    """
    These tests make sure the "usual" OCR works fine. (the one generating
    a .txt file)
    """
    def test_basic(self):
        self._test_txt('test.png', 'test.txt')

    def test_european(self):
        self._test_txt('test-european.jpg', 'test-european.txt')

    def test_french(self):
        self._test_txt('test-french.jpg', 'test-french.txt', 'fra')

    def test_japanese(self):
        self._test_txt('test-japanese.jpg', 'test-japanese.txt', 'jpn')

    def test_multi(self):
        self._test_txt('test-european.jpg', 'test-european.txt', 'eng+fra')

    def test_nolangs(self, monkeypatch):
        """
        Issue #51: Running OCR without any language installed causes a SIGSEGV.
        """
        monkeypatch.setenv('TESSDATA_PREFIX', '/opt/tulipe')
        with pytest.raises(PyocrException):
            self.tool.image_to_string(
                PIL.Image.open(self._path_to_img('test-japanese.jpg')),
                lang='fra'
            )

    def test_nolangs2(self):
        with pytest.raises(PyocrException):
            self.tool.image_to_string(
                PIL.Image.open(self._path_to_img('test-japanese.jpg')),
                lang='doesnotexist'
            )


class TestDigit(base.BaseTestDigit, BaseLibtesseract):
    """
    These tests make sure that Tesseract digits handling works fine.
    """
    def test_digits(self):
        self._test_txt('test-digits.png', 'test-digits.txt')


class TestWordBox(base.BaseTestWordBox, BaseLibtesseract):
    """
    These tests make sure that Tesseract box handling works fine.
    """
    def test_basic(self):
        self._test_txt('test.png', 'test.words')

    def test_european(self):
        self._test_txt('test-european.jpg', 'test-european.words')

    def test_french(self):
        self._test_txt('test-french.jpg', 'test-french.words', 'fra')

    def test_japanese(self):
        self._test_txt('test-japanese.jpg', 'test-japanese.words', 'jpn')

    def test_write_read(self, tmpdir):
        image_path = self._path_to_img("test.png")
        original_boxes = self._read_from_img(image_path)
        assert len(original_boxes) > 0

        tmp_path = tmpdir.join('test_write_read.txt')

        with tmp_path.open('w', encoding='utf-8') as fdescriptor:
            self._builder.write_file(fdescriptor, original_boxes)

        with tmp_path.open('r', encoding='utf-8') as fdescriptor:
            new_boxes = self._builder.read_file(fdescriptor)

        assert len(new_boxes) == len(original_boxes)
        for i in range(0, len(original_boxes)):
            assert new_boxes[i] == original_boxes[i]


class TestLineBox(base.BaseTestLineBox, BaseLibtesseract):
    """
    These tests make sure that Tesseract box handling works fine.
    """
    def test_basic(self):
        self._test_txt('test.png', 'test.lines')

    def test_european(self):
        self._test_txt('test-european.jpg', 'test-european.lines')

    def test_french(self):
        self._test_txt('test-french.jpg', 'test-french.lines', 'fra')

    def test_japanese(self):
        self._test_txt('test-japanese.jpg', 'test-japanese.lines', 'jpn')

    def test_write_read(self, tmpdir):
        image_path = self._path_to_img("test.png")
        original_boxes = self._read_from_img(image_path)
        assert len(original_boxes) > 0

        tmp_path = tmpdir.join('test_write_read.txt')

        with tmp_path.open('w', encoding='utf-8') as fdescriptor:
            self._builder.write_file(fdescriptor, original_boxes)

        with tmp_path.open('r', encoding='utf-8') as fdescriptor:
            new_boxes = self._builder.read_file(fdescriptor)

        assert len(new_boxes) == len(original_boxes)
        for i in range(0, len(original_boxes)):
            assert new_boxes[i] == original_boxes[i]


class TestDigitLineBox(base.BaseTestDigitLineBox, BaseLibtesseract):
    def test_digits(self):
        self._test_txt('test-digits.png', 'test-digits.lines')


class TestOrientation(BaseLibtesseract):
    def set_builder(self):
        self._builder = builders.TextBuilder()

    def test_can_detect_orientation(self):
        assert libtesseract.can_detect_orientation()

    def test_orientation_0(self):
        img = base.Image.open(self._path_to_img("test.png"))
        result = libtesseract.detect_orientation(img, lang='eng')
        assert result['angle'] == 0

    def test_orientation_90(self):
        img = base.Image.open(self._path_to_img("test-90.png"))
        result = libtesseract.detect_orientation(img, lang='eng')
        assert result['angle'] == 90


class TestBasicDoc(base.BaseTestLineBox):
    """
    These tests make sure that Tesseract box handling works fine.
    """
    tool = libtesseract

    def _path_to_img(self, image_file):
        return os.path.join(
            "tests", "input", "real", image_file
        )

    def _path_to_out(self, expected_output_file):
        return os.path.join(
            "tests", "output", "real", "libtesseract", expected_output_file
        )

    def test_basic(self):
        self._test_txt('basic_doc.jpg', 'basic_doc.lines')


class TestPdf(base.BaseTestPdf):
    tool = libtesseract

    def _path_to_img(self, image_file):
        return os.path.join(
            "tests", "input", "real", image_file
        )

    def _path_to_out(self, output_file):
        return os.path.join(
            "tests", "output", "real", "libtesseract", output_file
        )

    def test_basic(self):
        self._test_pdf('basic_doc.jpg')
