import subprocess

from io import StringIO
try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock

from PIL import Image

from pyocr import cuneiform
from pyocr import builders

from .tests_base import BaseTest


class TestCuneiform(BaseTest):
    """
    These tests make sure the requirements for the tests are met.
    """

    @patch("pyocr.util.is_on_path")
    def test_available(self, is_on_path):
        # XXX is it useful?
        is_on_path.return_value = True
        self.assertTrue(cuneiform.is_available())
        is_on_path.assert_called_once_with("cuneiform")

    @patch("subprocess.Popen")
    def test_version(self, Popen):
        stdout = MagicMock()
        stdout.stdout.read.return_value = (
            "Cuneiform for Linux 1.1.0\n"
            "Usage: cuneiform [-l languagename -f format --dotmatrix --fax"
            " --singlecolumn -o result_file] imagefile"
        ).encode()
        Popen.return_value = stdout
        self.assertSequenceEqual(cuneiform.get_version(), (1, 1, 0))

    @patch("subprocess.Popen")
    def test_version_error(self, Popen):
        stdout = MagicMock()
        stdout.stdout.read.return_value = "\n".encode()
        Popen.return_value = stdout
        self.assertIsNone(cuneiform.get_version())

    @patch("subprocess.Popen")
    def test_langs(self, Popen):
        stdout = MagicMock()
        stdout.stdout.read.return_value = (
            "Cuneiform for Linux 1.1.0\n"
            "Supported languages: eng ger fra rus swe spa ita ruseng ukr srp "
            "hrv pol dan por dut cze rum hun bul slv lav lit est tur."
        ).encode()
        Popen.return_value = stdout
        langs = cuneiform.get_available_languages()
        self.assertIn("eng", langs)
        self.assertIn("fra", langs)
        Popen.assert_called_once_with(
            ["cuneiform", "-l"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

    def test_name(self):
        self.assertEqual(cuneiform.get_name(), "Cuneiform (sh)")

    def test_can_detect_orientation(self):
        self.assertFalse(cuneiform.can_detect_orientation())

    def test_available_builders(self):
        self.assertListEqual(
            cuneiform.get_available_builders(),
            [
                builders.TextBuilder,
                builders.WordBoxBuilder,
                builders.LineBoxBuilder,
            ]
        )


class TestCuneiformTxt(BaseTest):
    """
    These tests make sure the "usual" OCR works fine. (the one generating
    a .txt file)
    """
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.TextBuilder()
        self.image = Image.open(self._get_file_path("text.jpg"))
        self.stdout = MagicMock()
        self.stdout.stdout.read.return_value = (
            "Cuneiform for Linux 1.1.0\n".encode()
        )
        self.stdout.wait.return_value = 0
        self.tmp_filename = "/tmp/cuneiform_n0qfk87otxt"
        self.enter = MagicMock()
        self.enter.__enter__.return_value = MagicMock()
        self.enter.__enter__.return_value.configure_mock(name=self.tmp_filename)

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_image_to_string_defaults_to_text_buidler(self, Popen, copen,
                                                      temp_file, get_version):
        get_version.return_value = (4, 0, 0)
        Popen.return_value = self.stdout
        copen.return_value = StringIO(self._get_file_content("text"))
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(self.image)
        self.assertEqual(output, self._get_file_content("text").strip())
        Popen.assert_called_once_with(
            ["cuneiform", "-f", "text", "-o", self.tmp_filename, "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_lang(self, Popen, copen, temp_file):
        Popen.return_value = self.stdout
        copen.return_value = StringIO(self._get_file_content("text"))
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(self.image, lang="fra",
                                           builder=self.builder)
        self.assertEqual(output, self._get_file_content("text").strip())
        Popen.assert_called_once_with(
            ["cuneiform", "-l", "fra", "-f", "text", "-o", self.tmp_filename,
             "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_text(self, Popen, copen, temp_file):
        Popen.return_value = self.stdout
        copen.return_value = StringIO(self._get_file_content("text"))
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(self.image,
                                           builder=self.builder)
        self.assertEqual(output, self._get_file_content("text").strip())
        Popen.assert_called_once_with(
            ["cuneiform", "-f", "text", "-o", self.tmp_filename, "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    @patch("subprocess.Popen")
    def test_text_error(self, Popen):
        message = ("Cuneiform for Linux 1.1.0\n"
                   "Magick: Improper image header (example.png) reported by "
                   "coders/png.c:2932 (ReadPNGImage)\n")
        self.stdout.stdout.read.return_value = message.encode()
        self.stdout.wait.return_value = 1
        Popen.return_value = self.stdout
        with self.assertRaises(cuneiform.CuneiformError) as ce:
            cuneiform.image_to_string(self.image, builder=self.builder)
        self.assertEqual(ce.exception.status, 1)
        self.assertEqual(ce.exception.message, message)


class TestCuneiformDigits(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.DigitBuilder()

    def test_digits_not_implemented(self):
        image = Image.open(self._get_file_path("digits.png"))
        with self.assertRaises(NotImplementedError):
            cuneiform.image_to_string(image, builder=self.builder)

    def test_digits_box_not_implemented(self):
        image = Image.open(self._get_file_path("digits.png"))
        with self.assertRaises(NotImplementedError):
            cuneiform.image_to_string(image,
                                      builder=self.builder)


class TestCuneiformWordBox(BaseTest):
    """
    These tests make sure that cuneiform box handling works fine.
    """
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.WordBoxBuilder()
        self.image = Image.open(self._get_file_path("paragraph.jpg"))
        self.stdout = MagicMock()
        self.stdout.stdout.read.return_value = (
            "Cuneiform for Linux 1.1.0\n".encode()
        )
        self.stdout.wait.return_value = 0
        self.tmp_filename = "/tmp/cuneiform_n0qfk87otxt"
        self.enter = MagicMock()
        self.enter.__enter__.return_value = MagicMock()
        self.enter.__enter__.return_value.configure_mock(name=self.tmp_filename)

    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_word(self, Popen, copen, temp_file):
        Popen.return_value = self.stdout
        copen.return_value = StringIO(self._get_file_content("cuneiform.words"))
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(self.image,
                                           builder=self.builder)
        Popen.assert_called_once_with(
            ["cuneiform", "-f", "hocr", "-o", self.tmp_filename, "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for box in output:
            self.assertIsInstance(box, builders.Box)

    @patch("subprocess.Popen")
    def test_word_error(self, Popen):
        stdout = MagicMock()
        message = ("Cuneiform for Linux 1.1.0\n"
                   "Magick: Improper image header (example.png) reported by "
                   "coders/png.c:2932 (ReadPNGImage)\n")
        stdout.stdout.read.return_value = message.encode()
        stdout.wait.return_value = 1
        Popen.return_value = stdout
        with self.assertRaises(cuneiform.CuneiformError) as ce:
            cuneiform.image_to_string(self.image,
                                      builder=self.builder)
        self.assertEqual(ce.exception.status, 1)
        self.assertEqual(ce.exception.message, message)


class TestCuneiformLineBox(BaseTest):
    """
    These tests make sure that cuneiform box handling works fine.
    """
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.LineBoxBuilder()
        self.image = Image.open(self._get_file_path("paragraph.jpg"))
        self.stdout = MagicMock()
        self.stdout.stdout.read.return_value = (
            "Cuneiform for Linux 1.1.0\n".encode()
        )
        self.stdout.wait.return_value = 0
        self.tmp_filename = "/tmp/cuneiform_n0qfk87otxt"
        self.enter = MagicMock()
        self.enter.__enter__.return_value = MagicMock()
        self.enter.__enter__.return_value.configure_mock(name=self.tmp_filename)

    @patch("pyocr.cuneiform.temp_file")
    @patch("codecs.open")
    @patch("subprocess.Popen")
    def test_line(self, Popen, copen, temp_file):
        Popen.return_value = self.stdout
        copen.return_value = StringIO(self._get_file_content("cuneiform.lines"))
        temp_file.return_value = self.enter
        output = cuneiform.image_to_string(self.image,
                                           builder=self.builder)
        Popen.assert_called_once_with(
            ["cuneiform", "-f", "hocr", "-o", self.tmp_filename, "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for box in output:
            self.assertIsInstance(box, builders.LineBox)

    @patch("subprocess.Popen")
    def test_line_error(self, Popen):
        message = ("Cuneiform for Linux 1.1.0\n"
                   "Magick: Improper image header (example.png) reported by "
                   "coders/png.c:2932 (ReadPNGImage)\n")
        self.stdout.stdout.read.return_value = message.encode()
        self.stdout.wait.return_value = 1
        Popen.return_value = self.stdout
        with self.assertRaises(cuneiform.CuneiformError) as ce:
            cuneiform.image_to_string(self.image,
                                      builder=self.builder)
        self.assertEqual(ce.exception.status, 1)
        self.assertEqual(ce.exception.message, message)
