import os

from pyocr import builders
from pyocr import tesseract
from . import tests_base as base


class TestContext(object):
    """
    These tests make sure the requirements for the tests are met.
    """
    def setup(self):
        pass

    def test_available(self):
        assert tesseract.is_available()

    def test_version(self):
        assert tesseract.get_version() in (
                (3, 2, 1),
                (3, 2, 2),
                (3, 3, 0),
                (3, 4, 0),
                (3, 4, 1),
                (3, 5, 0),
            )

    def test_langs(self):
        langs = tesseract.get_available_languages()
        assert "eng" in langs
        assert "fra" in langs
        assert "jpn" in langs

    def teardown(self):
        pass


class BaseTesseract(base.BaseTest):
    tool = tesseract

    def _path_to_img(self, image_file):
        return os.path.join(
            "tests", "input", "specific", image_file
        )

    def _path_to_out(self, expected_output_file):
        return os.path.join(
            "tests", "output", "specific", "tesseract", expected_output_file
        )


class TestTxt(base.BaseTestText, BaseTesseract):
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


class TestCharBox(base.BaseTestBox, BaseTesseract):
    """
    These tests make sure that Tesseract box handling works fine.
    """
    def set_builder(self):
        self._builder = tesseract.CharBoxBuilder()

    def _test_equal(self, output, expected_output):
        assert output == expected_output

    def test_basic(self):
        self._test_txt('test.png', 'test.box')

    def test_european(self):
        self._test_txt('test-european.jpg', 'test-european.box')

    def test_french(self):
        self._test_txt('test-french.jpg', 'test-french.box', 'fra')

    def test_japanese(self):
        self._test_txt('test-japanese.jpg', 'test-japanese.box', 'jpn')

    def test_write_read(self, tmpdir):
        image_path = self._path_to_img("test.png")
        original_boxes = self._read_from_img(image_path)
        assert len(original_boxes) > 0

        tmp_path = tmpdir.join('test_write_read.txt')

        with tmp_path.open('w', encoding='utf-8') as fdescriptor:
            self._builder.write_file(fdescriptor, original_boxes)

        with tmp_path.open('r', encoding='utf-8') as fdescriptor:
            new_boxes = self._builder.read_file(fdescriptor)

        assert new_boxes == original_boxes


class TestDigit(base.BaseTestDigit, BaseTesseract):
    """
    These tests make sure that Tesseract digits handling works fine.
    """
    def test_digits(self):
        self._test_txt('test-digits.png', 'test-digits.txt')


class TestWordBox(base.BaseTestWordBox, BaseTesseract):
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

        assert new_boxes == original_boxes


class TestLineBox(base.BaseTestLineBox, BaseTesseract):
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

        assert new_boxes == original_boxes

    def teardown(self):
        pass


class TestDigitLineBox(base.BaseTestDigitLineBox, BaseTesseract):
    def test_digits(self):
        self._test_txt('test-digits.png', 'test-digits.lines')


class TestOrientation(BaseTesseract):
    def set_builder(self):
        self._builder = builders.TextBuilder()

    def test_can_detect_orientation(self):
        assert tesseract.can_detect_orientation()

    def test_orientation_0(self):
        img = base.Image.open(self._path_to_img("test.png"))
        result = tesseract.detect_orientation(img, lang='eng')
        assert result['angle'] == 0

    def test_orientation_90(self):
        img = base.Image.open(self._path_to_img("test-90.png"))
        result = tesseract.detect_orientation(img, lang='eng')
        assert result['angle'] == 90
