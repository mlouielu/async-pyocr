import os

import pytest

from pyocr import cuneiform
from . import tests_base as base


class TestContext(object):
    """
    These tests make sure the requirements for the tests are met.
    """
    def setup(self):
        pass

    def test_available(self):
        assert cuneiform.is_available()

    def test_version(self):
        assert cuneiform.get_version() == (1, 1, 0)

    def test_langs(self):
        langs = cuneiform.get_available_languages()
        assert "eng" in langs
        assert "fra" in langs

    def teardown(self):
        pass


class BaseCuneiform(base.BaseTest):
    def _path_to_img(self, image_file):
        return os.path.join(
            "tests", "input", "specific", image_file
        )

    def _path_to_out(self, expected_output_file):
        return os.path.join(
            "tests", "output", "specific", "cuneiform", expected_output_file
        )


class TestTxt(base.BaseTestText, BaseCuneiform):
    """
    These tests make sure the "usual" OCR works fine. (the one generating
    a .txt file)
    """
    def setup(self):
        super(TestTxt, self).setup()
        self.tool = cuneiform
        self.set_builder()

    def test_basic(self):
        self._test_txt('test.png', 'test.txt')

    def test_european(self):
        self._test_txt('test-european.jpg', 'test-european.txt')

    def test_french(self):
        self._test_txt('test-french.jpg', 'test-french.txt', 'fra')

    def teardown(self):
        pass


class TestDigit(base.BaseTestDigit, BaseCuneiform):
    def setup(self):
        super(TestDigit, self).setup()
        self.tool = cuneiform
        self.set_builder()

    def test_digits_not_implemented(self):
        image_path = self._path_to_img("test-digits.png")
        with pytest.raises(NotImplementedError):
            self._read_from_img(image_path)


class TestWordBox(base.BaseTestWordBox, BaseCuneiform):
    """
    These tests make sure that cuneiform box handling works fine.
    """
    def setup(self):
        super(TestWordBox, self).setup()
        self.tool = cuneiform
        self.set_builder()

    def test_basic(self):
        self._test_txt('test.png', 'test.words')

    def test_european(self):
        self._test_txt('test-european.jpg', 'test-european.words')

    def test_french(self):
        self._test_txt('test-french.jpg', 'test-french.words', 'fra')

    def test_write_read(self, tmpdir):
        original_boxes = self._read_from_img(
            os.path.join("tests", "input", "specific", "test.png")
        )
        assert len(original_boxes) > 0

        tmp_path = tmpdir.join('test_write_read.txt')

        with tmp_path.open('w', encoding='utf-8') as file_desc:
            self._builder.write_file(file_desc, original_boxes)

        with tmp_path.open('r', encoding='utf-8') as file_desc:
            new_boxes = self._builder.read_file(file_desc)

        assert new_boxes == original_boxes


class TestOrientation(object):
    def test_can_detect_orientation(self):
        assert not cuneiform.can_detect_orientation()
