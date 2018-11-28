import os
import subprocess

from io import StringIO
try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

from PIL import Image

from pyocr import builders
from pyocr import tesseract

from .tests_base import BaseTest


class TestTesseract(BaseTest):
    """
    These tests make sure the requirements for the tests are met.
    """
    def setUp(self):
        self.stdout = MagicMock()
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.message = (
            "tesseract 4.0.0\n leptonica-1.76.0\n"
            "  libgif 5.1.4 : libjpeg 6b (libjpeg-turbo 1.5.2) : libpng 1.6.34 "
            ": libtiff 4.0.9 : zlib 1.2.11 : libwebp 0.6.1 : libopenjp2 2.3.0\n"
            " Found AVX2\n Found AVX\n Found SSE\n"
        )
        self.stdout.stdout.read.return_value = self.message.encode()
        self.stdout.wait.return_value = 0

    @patch("pyocr.util.is_on_path")
    def test_available(self, is_on_path):
        is_on_path.return_value = True
        self.assertTrue(tesseract.is_available())
        is_on_path.assert_called_once_with("tesseract")

    @patch("subprocess.Popen")
    def test_version_error(self, Popen):
        self.stdout.wait.return_value = 2
        Popen.return_value = self.stdout
        with self.assertRaises(tesseract.TesseractError) as te:
            tesseract.get_version()
        self.assertEqual(te.exception.status, 2)
        self.assertEqual(te.exception.message, self.message)

    @patch("subprocess.Popen")
    def test_version_tesseract4(self, Popen):
        Popen.return_value = self.stdout
        self.assertSequenceEqual(tesseract.get_version(), (4, 0, 0))

    @patch("subprocess.Popen")
    def test_version_tesseract4dev(self, Popen):
        message = (
            "tesseract 4.00.00dev2\n leptonica-1.74.4\n"
            "  libgif 5.1.4 : libjpeg 6b (libjpeg-turbo 1.5.1) : libpng 1.6.34 "
            ": libtiff 4.0.9 : zlib 1.2.8 : libwebp 0.6.0 : libopenjp2 2.3.0\n"
            "\n Found AVX\n Found SSE\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        self.assertSequenceEqual(tesseract.get_version(), (4, 0, 0))

    @patch("subprocess.Popen")
    def test_version_tesseract4alpha(self, Popen):
        message = (
            "tesseract 4.00.00alpha\n leptonica-1.74.4\n"
            "  libgif 5.1.4 : libjpeg 6b (libjpeg-turbo 1.5.1) : libpng 1.6.34 "
            ": libtiff 4.0.9 : zlib 1.2.8 : libwebp 0.6.0 : libopenjp2 2.3.0\n"
            "\n Found AVX\n Found SSE\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        self.assertSequenceEqual(tesseract.get_version(), (4, 0, 0))

    @patch("subprocess.Popen")
    def test_version_tesseract3(self, Popen):
        message = (
            "tesseract 3.05\n leptonica-1.76.0\n"
            "  libgif 5.1.4 : libjpeg 6b (libjpeg-turbo 1.5.2) : libpng 1.6.34 "
            ": libtiff 4.0.9 : zlib 1.2.11 : libwebp 0.6.1 : libopenjp2 2.3.0\n"
            " Found AVX2\n Found AVX\n Found SSE\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        self.assertSequenceEqual(tesseract.get_version(), (3, 5, 0))

    @patch("subprocess.Popen")
    def test_version_tesseract3_no_minor(self, Popen):
        message = (
            "tesseract 3.0\n leptonica-1.76.0\n"
            "  libgif 5.1.4 : libjpeg 6b (libjpeg-turbo 1.5.2) : libpng 1.6.34 "
            ": libtiff 4.0.9 : zlib 1.2.11 : libwebp 0.6.1 : libopenjp2 2.3.0\n"
            " Found AVX2\n Found AVX\n Found SSE\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        self.assertSequenceEqual(tesseract.get_version(), (3, 0, 0))

    @patch("subprocess.Popen")
    def test_version_error_splitting(self, Popen):
        message = (
            "tesseract 3\n leptonica-1.76.0\n"
            "  libgif 5.1.4 : libjpeg 6b (libjpeg-turbo 1.5.2) : libpng 1.6.34 "
            ": libtiff 4.0.9 : zlib 1.2.11 : libwebp 0.6.1 : libopenjp2 2.3.0\n"
            " Found AVX2\n Found AVX\n Found SSE\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with self.assertRaises(tesseract.TesseractError) as te:
            tesseract.get_version()
        self.assertEqual(te.exception.status, 0)
        self.assertIn("Unable to parse Tesseract version (spliting failed): ",
                      te.exception.message)

    @patch("subprocess.Popen")
    def test_version_error_nan(self, Popen):
        message = (
            "tesseract A.B.C\n leptonica-1.76.0\n"
            "  libgif 5.1.4 : libjpeg 6b (libjpeg-turbo 1.5.2) : libpng 1.6.34 "
            ": libtiff 4.0.9 : zlib 1.2.11 : libwebp 0.6.1 : libopenjp2 2.3.0\n"
            " Found AVX2\n Found AVX\n Found SSE\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with self.assertRaises(tesseract.TesseractError) as te:
            tesseract.get_version()
        self.assertEqual(te.exception.status, 0)
        self.assertIn("Unable to parse Tesseract version (not a number): ",
                      te.exception.message)

    @patch("subprocess.Popen")
    def test_langs(self, Popen):
        message = (
            "List of available languages (4):\n"
            "eng\n"
            "fra\n"
            "jpn\n"
            "osd\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        langs = tesseract.get_available_languages()
        for lang in ("eng", "fra", "jpn", "osd"):
            self.assertIn(lang, langs)
        Popen.assert_called_once_with(
            ["tesseract", "--list-langs"],
            startupinfo=None, creationflags=0,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

    @patch("subprocess.Popen")
    def test_langs_error(self, Popen):
        message = (
            "No languages\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        self.stdout.wait.return_value = 1
        Popen.return_value = self.stdout
        with self.assertRaises(tesseract.TesseractError) as te:
            tesseract.get_available_languages()
        self.assertEqual(te.exception.status, 1)
        self.assertEqual("unable to get languages", te.exception.message)
        Popen.assert_called_once_with(
            ["tesseract", "--list-langs"],
            startupinfo=None, creationflags=0,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

    @patch("pyocr.tesseract.get_version")
    def test_can_detect_orientation_tesseract4(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.assertTrue(tesseract.can_detect_orientation())

    @patch("pyocr.tesseract.get_version")
    def test_can_detect_orientation_tesseract3(self, get_version):
        get_version.return_value = (3, 3, 0)
        self.assertTrue(tesseract.can_detect_orientation())

    @patch("pyocr.tesseract.get_version")
    def test_cannot_detect_orientation_tesseract3(self, get_version):
        get_version.return_value = (3, 2, 1)
        self.assertFalse(tesseract.can_detect_orientation())

    def test_name(self):
        self.assertEqual(tesseract.get_name(), "Tesseract (sh)")

    @patch("pyocr.tesseract.get_version")
    def test_psm_parameter(self, get_version):
        get_version.return_value = (3, 5, 0)
        self.assertEqual(tesseract.psm_parameter(), "-psm")
        get_version.return_value = (4, 0, 0)
        self.assertEqual(tesseract.psm_parameter(), "--psm")


    def test_available_builders(self):
        self.assertListEqual(
            tesseract.get_available_builders(),
            [
                builders.LineBoxBuilder,
                builders.TextBuilder,
                builders.WordBoxBuilder,
                tesseract.CharBoxBuilder,
                builders.DigitBuilder,
                builders.DigitLineBoxBuilder,
            ]
        )

    def test_temp_dir(self):
        with tesseract.temp_dir() as tmpdir:
            with open(os.path.join(tmpdir, "example.txt"), "w") as fh:
                fh.write("test")
        self.assertFalse(os.path.exists(os.path.join(tmpdir, "example.txt")))
        self.assertFalse(os.path.exists(os.path.join(tmpdir)))

    @patch("pyocr.tesseract.get_version")
    @patch("subprocess.Popen")
    def test_run_tesseract(self, Popen, get_version):
        message = (
            "Tesseract Open Source OCR Engine v4.0.0 with Leptonica\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout

        with tesseract.temp_dir() as tmpdir:
            self.image.save(os.path.join(tmpdir, "input.bmp"))
            status, error = tesseract.run_tesseract(
                "input.bmp",
                "output",
                cwd=tmpdir,
            )
        self.assertEqual(status, 0)
        self.assertEqual(error.decode(), message)
        Popen.assert_called_once_with(
            ["tesseract", "input.bmp", "output"],
            cwd=tmpdir,
            startupinfo=None,
            creationflags=0,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        get_version.return_value = (4, 0, 0)
        builder = builders.TextBuilder()
        with tesseract.temp_dir() as tmpdir:
            self.image.save(os.path.join(tmpdir, "input2.bmp"))
            status, error = tesseract.run_tesseract(
                "input2.bmp",
                "output2",
                cwd=tmpdir,
                lang="fra",
                flags=builder.tesseract_flags,
                configs=builder.tesseract_configs,
            )
        self.assertEqual(status, 0)
        self.assertEqual(error.decode(), message)
        Popen.assert_called_with(
            ["tesseract", "input2.bmp", "output2", "-l", "fra", "--psm", "3"],
            cwd=tmpdir,
            startupinfo=None,
            creationflags=0,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        self.assertEqual(Popen.call_count, 2)

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.tesseract.temp_dir")
    @patch("subprocess.Popen")
    def test_detect_orientation_tesseract4(self, Popen, temp_dir, get_version):
        get_version.return_value = (4, 0, 0)
        message = (
            "Page number: 0\n"
            "Orientation in degrees: 90\n"
            "Rotate: 270\n"
            "Orientation confidence: 9.30\n"
            "Script: Latin\n"
            "Script confidence: 8.06\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            result = tesseract.detect_orientation(self.image)
            self.assertEqual(result["angle"], 90)
            self.assertEqual(result["confidence"], 9.30)
            Popen.assert_called_once_with(
                ["tesseract", "input.bmp", "stdout", "--psm", "0"],
                stdin=subprocess.PIPE,
                shell=False,
                startupinfo=None,
                creationflags=0,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.tesseract.temp_dir")
    @patch("subprocess.Popen")
    def test_detect_orientation_tesseract4_non_rgb_image(self, Popen,
                                                         temp_dir, get_version):
        """This tests that detect_orientation works with non RGB mode images and
        that image is converted in function."""
        image = self.image.convert("L")
        get_version.return_value = (4, 0, 0)
        message = (
            "Page number: 0\n"
            "Orientation in degrees: 90\n"
            "Rotate: 270\n"
            "Orientation confidence: 9.30\n"
            "Script: Latin\n"
            "Script confidence: 8.06\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            result = tesseract.detect_orientation(image)
            self.assertEqual(result["angle"], 90)
            self.assertEqual(result["confidence"], 9.30)
            Popen.assert_called_once_with(
                ["tesseract", "input.bmp", "stdout", "--psm", "0"],
                stdin=subprocess.PIPE,
                shell=False,
                startupinfo=None,
                creationflags=0,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )


    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.tesseract.temp_dir")
    @patch("subprocess.Popen")
    def test_detect_orientation_tesseract4_with_lang(self, Popen, temp_dir,
                                                     get_version):
        get_version.return_value = (4, 0, 0)
        message = (
            "Page number: 0\n"
            "Orientation in degrees: 90\n"
            "Rotate: 270\n"
            "Orientation confidence: 9.30\n"
            "Script: Latin\n"
            "Script confidence: 8.06\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            result = tesseract.detect_orientation(self.image, lang="fra")
            self.assertEqual(result["angle"], 90)
            self.assertEqual(result["confidence"], 9.30)
            Popen.assert_called_once_with(
                ["tesseract", "input.bmp", "stdout", "--psm", "0", "-l", "osd"],
                stdin=subprocess.PIPE,
                shell=False,
                startupinfo=None,
                creationflags=0,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.tesseract.temp_dir")
    @patch("subprocess.Popen")
    def test_detect_orientation_tesseract4_error(self, Popen, temp_dir,
                                                 get_version):
        get_version.return_value = (4, 0, 0)
        message = (
            "Could not initialize tesseract\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.detect_orientation(self.image)
            Popen.assert_called_once_with(
                ["tesseract", "input.bmp", "stdout", "--psm", "0"],
                stdin=subprocess.PIPE,
                shell=False,
                startupinfo=None,
                creationflags=0,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            self.assertEqual(te.exception.status, -1)
            self.assertIn("Error initializing tesseract", te.exception.message)

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.tesseract.temp_dir")
    @patch("subprocess.Popen")
    def test_detect_orientation_tesseract4_bad_output(self, Popen, temp_dir,
                                                      get_version):
        get_version.return_value = (4, 0, 0)
        message = (
            "Page number: 0\n"
            "Orientation in degrees: ABC\n"
            "Rotate: 270\n"
            "Orientation confidence: AB.CD\n"
            "Script: Latin\n"
            "Script confidence: 8.06\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.detect_orientation(self.image)
            Popen.assert_called_once_with(
                ["tesseract", "input.bmp", "stdout", "--psm", "0"],
                stdin=subprocess.PIPE,
                shell=False,
                startupinfo=None,
                creationflags=0,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            self.assertEqual(te.exception.status, -1)
            self.assertIn("No script found in image", te.exception.message)

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.tesseract.temp_dir")
    @patch("subprocess.Popen")
    def test_detect_orientation_tesseract3(self, Popen, temp_dir, get_version):
        get_version.return_value = (3, 5, 0)
        message = (
            "Page number: 0\n"
            "Orientation in degrees: 90\n"
            "Rotate: 270\n"
            "Orientation confidence: 9.30\n"
            "Script: Latin\n"
            "Script confidence: 8.06\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            result = tesseract.detect_orientation(self.image)
            self.assertEqual(result["angle"], 90)
            self.assertEqual(result["confidence"], 9.30)
            Popen.assert_called_once_with(
                ["tesseract", "input.bmp", "stdout", "-psm", "0"],
                stdin=subprocess.PIPE,
                shell=False,
                startupinfo=None,
                creationflags=0,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.tesseract.temp_dir")
    @patch("subprocess.Popen")
    def test_detect_orientation_tesseract3_with_lang(self, Popen, temp_dir,
                                                     get_version):
        get_version.return_value = (3, 5, 0)
        message = (
            "Page number: 0\n"
            "Orientation in degrees: 90\n"
            "Rotate: 270\n"
            "Orientation confidence: 9.30\n"
            "Script: Latin\n"
            "Script confidence: 8.06\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            result = tesseract.detect_orientation(self.image, lang="fra")
            self.assertEqual(result["angle"], 90)
            self.assertEqual(result["confidence"], 9.30)
            Popen.assert_called_once_with(
                ["tesseract", "input.bmp", "stdout", "-psm", "0", "-l", "fra"],
                stdin=subprocess.PIPE,
                shell=False,
                startupinfo=None,
                creationflags=0,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.tesseract.temp_dir")
    @patch("subprocess.Popen")
    def test_detect_orientation_tesseract3_error(self, Popen, temp_dir,
                                                 get_version):
        get_version.return_value = (3, 5, 0)
        message = (
            "Could not initialize tesseract\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.detect_orientation(self.image)
            Popen.assert_called_once_with(
                ["tesseract", "input.bmp", "stdout", "-psm", "0"],
                stdin=subprocess.PIPE,
                shell=False,
                startupinfo=None,
                creationflags=0,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            self.assertEqual(te.exception.status, -1)
            self.assertIn("Error initializing tesseract", te.exception.message)

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.tesseract.temp_dir")
    @patch("subprocess.Popen")
    def test_detect_orientation_tesseract3_bad_output(self, Popen, temp_dir,
                                                      get_version):
        get_version.return_value = (3, 5, 0)
        message = (
            "Page number: 0\n"
            "Orientation in degrees: ABC\n"
            "Rotate: 270\n"
            "Orientation confidence: AB.CD\n"
            "Script: Latin\n"
            "Script confidence: 8.06\n"
        )
        self.stdout.stdout.read.return_value = message.encode()
        Popen.return_value = self.stdout
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.detect_orientation(self.image)
            Popen.assert_called_once_with(
                ["tesseract", "input.bmp", "stdout", "-psm", "0"],
                stdin=subprocess.PIPE,
                shell=False,
                startupinfo=None,
                creationflags=0,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            self.assertEqual(te.exception.status, -1)
            self.assertIn("No script found in image", te.exception.message)


class TestTesseractTxt(BaseTest):
    """
    These tests make sure the "usual" OCR works fine. (the one generating
    a .txt file)
    """
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.builder = builders.TextBuilder()

    @patch("pyocr.tesseract.get_version")
    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_image_to_string_defaults_to_text_buidler(self, run_tesseract,
                                                      copen, temp_dir,
                                                      get_version):
        get_version.return_value = (4, 0, 0)
        run_tesseract.return_value = (0, "")
        copen.return_value = StringIO(self._get_file_content("text"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with open(os.path.join(tmpdir, "output.txt"), "w") as fh:
                fh.write("")
            result = tesseract.image_to_string(self.image)

        self.assertEqual(result, self._get_file_content("text").strip())
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_lang(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "")
        copen.return_value = StringIO(self._get_file_content("text"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with open(os.path.join(tmpdir, "output.txt"), "w") as fh:
                fh.write("")
            result = tesseract.image_to_string(self.image, lang="fra",
                                               builder=self.builder)

        self.assertEqual(result, self._get_file_content("text").strip())
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang="fra",
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_text(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "")
        copen.return_value = StringIO(self._get_file_content("text"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with open(os.path.join(tmpdir, "output.txt"), "w") as fh:
                fh.write("")
            result = tesseract.image_to_string(self.image,
                                               builder=self.builder)

        self.assertEqual(result, self._get_file_content("text").strip())
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_text_non_rgb_image(self, run_tesseract, copen, temp_dir):
        """This tests that image_to_string works with non RGB mode images and
        that image is converted in function."""
        image = self.image.convert("L")
        run_tesseract.return_value = (0, "")
        copen.return_value = StringIO(self._get_file_content("text"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with open(os.path.join(tmpdir, "output.txt"), "w") as fh:
                fh.write("")
            result = tesseract.image_to_string(image, builder=self.builder)

        self.assertEqual(result, self._get_file_content("text").strip())
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_text_error(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (1, "Error")
        copen.return_value = StringIO(self._get_file_content("text"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)
        self.assertEqual(te.exception.status, 1)
        self.assertEqual(te.exception.message, "Error")
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_text_cannot_open_file(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "")
        copen.side_effect = OSError("Error opening file")
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with open(os.path.join(tmpdir, "output.txt"), "w") as fh:
                fh.write("")
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)
        self.assertEqual(te.exception.status, -1)
        self.assertIn("Unable to find output file last name tried",
                      te.exception.message)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_text_no_output(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "No file output")
        copen.return_value = StringIO(self._get_file_content("text"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)
        self.assertEqual(te.exception.status, -1)
        self.assertIn("Unable to find output file last name tried",
                      te.exception.message)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )


class TestTesseractCharBox(BaseTest):
    """
    These tests make sure that Tesseract box handling works fine.
    """
    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.builder = tesseract.CharBoxBuilder()

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_char(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "")
        copen.return_value = StringIO(self._get_file_content("boxes"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with open(os.path.join(tmpdir, "output.box"), "w") as fh:
                fh.write("")
            result = tesseract.image_to_string(self.image,
                                               builder=self.builder)

        for box in result:
            self.assertIsInstance(box, builders.Box)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_char_error(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (1, "Error")
        copen.return_value = StringIO(self._get_file_content("boxes"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)
        self.assertEqual(te.exception.status, 1)
        self.assertEqual(te.exception.message, "Error")
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_char_no_output(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "No file output")
        copen.return_value = StringIO(self._get_file_content("boxes"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)
        self.assertEqual(te.exception.status, -1)
        self.assertIn("Unable to find output file last name tried",
                      te.exception.message)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )


class TestCharBoxBuilder(BaseTest):
    def test_init(self):
        builder = tesseract.CharBoxBuilder()
        self.assertListEqual(builder.file_extensions, ["box"])
        self.assertListEqual(builder.tesseract_flags, [])
        self.assertListEqual(
            builder.tesseract_configs,
            ["batch.nochop", "makebox"]
        )
        self.assertListEqual(builder.cuneiform_args, [])
        self.assertEqual(builder.tesseract_layout, 1)

    def test_read_file(self):
        builder = tesseract.CharBoxBuilder()
        boxes = builder.read_file(self._get_file_handle("boxes"))
        for box in boxes:
            self.assertIsInstance(box, builders.Box)

    def test_read_empty_file(self):
        builder = tesseract.CharBoxBuilder()
        output = StringIO()
        self.assertListEqual(builder.read_file(output), [])

    def test_read_file_empty_lines(self):
        builder = tesseract.CharBoxBuilder()
        boxes = builder.read_file(self._get_file_handle("boxes_empty_lines"))
        for box in boxes:
            self.assertIsInstance(box, builders.Box)
            self.assertNotEqual(box.content, "")

    def test_read_file_short_lines(self):
        builder = tesseract.CharBoxBuilder()
        boxes = builder.read_file(self._get_file_handle("boxes_short_lines"))
        for box in boxes:
            self.assertIsInstance(box, builders.Box)
            self.assertNotEqual(box.content, "#")

    def test_write_file(self):
        builder = tesseract.CharBoxBuilder()
        output = StringIO()
        boxes = [
            builders.Box("a", ((10, 11), (12, 13)), 95),
            builders.Box("b", ((11, 12), (13, 14))),
            builders.Box("c", ((12, 13), (14, 15))),
            builders.Box("d", ((13, 14), (15, 16)), 87),
            builders.Box(u"\xe9", ((14, 15), (16, 17)), 88),
        ]
        builder.write_file(output, boxes)
        output.seek(0)
        output = output.read()
        for box in boxes:
            self.assertIn(box.content, output)
            self.assertIn(u"{} {} {} {}".format(
                box.position[0][0], box.position[0][1],
                box.position[1][0], box.position[1][1],
            ), output)

    def test_str_method(self):
        self.assertEqual(str(tesseract.CharBoxBuilder()), "Character boxes")


class TestTesseractDigits(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.builder = builders.DigitBuilder()
        self.image = Image.new(mode="RGB", size=(1, 1))

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_digits(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "")
        copen.return_value = StringIO(self._get_file_content("digits"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with open(os.path.join(tmpdir, "output.txt"), "w") as fh:
                fh.write("")
            result = tesseract.image_to_string(self.image,
                                               builder=self.builder)

        for digit in result:
            self.assertIsInstance(int(digit), int)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )


class TestTesseractWordBox(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.builder = builders.WordBoxBuilder()

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_word(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "")
        copen.return_value = StringIO(self._get_file_content("words"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with open(os.path.join(tmpdir, "output.hocr"), "w") as fh:
                fh.write("")
            result = tesseract.image_to_string(self.image,
                                               builder=self.builder)

        for box in result:
            self.assertIsInstance(box, builders.Box)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_word_error(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (1, "Error")
        copen.return_value = StringIO(self._get_file_content("words"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)

        self.assertEqual(te.exception.status, 1)
        self.assertEqual(te.exception.message, "Error")
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_word_no_output(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "No file output")
        copen.return_value = StringIO(self._get_file_content("words"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)

        self.assertEqual(te.exception.status, -1)
        self.assertIn("Unable to find output file last name tried",
                      te.exception.message)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )


class TestTesseractLineBox(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.builder = builders.LineBoxBuilder()

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_line(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "")
        copen.return_value = StringIO(self._get_file_content("tesseract.lines"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with open(os.path.join(tmpdir, "output.hocr"), "w") as fh:
                fh.write("")
            result = tesseract.image_to_string(self.image,
                                               builder=self.builder)

        for line in result:
            self.assertIsInstance(line, builders.LineBox)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_line_error(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (1, "Error")
        copen.return_value = StringIO(self._get_file_content("tesseract.lines"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)

        self.assertEqual(te.exception.status, 1)
        self.assertEqual(te.exception.message, "Error")
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_line_no_output(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "No file output")
        copen.return_value = StringIO(self._get_file_content("tesseract.lines"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)

        self.assertEqual(te.exception.status, -1)
        self.assertIn("Unable to find output file last name tried",
                      te.exception.message)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )


class TestTesseractDigitsLineBox(BaseTest):

    @patch("pyocr.tesseract.get_version")
    def setUp(self, get_version):
        get_version.return_value = (4, 0, 0)
        self.image = Image.new(mode="RGB", size=(1, 1))
        self.builder = builders.DigitLineBoxBuilder()

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_line(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "")
        copen.return_value = StringIO(self._get_file_content("digits.lines"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with open(os.path.join(tmpdir, "output.hocr"), "w") as fh:
                fh.write("")
            result = tesseract.image_to_string(self.image,
                                               builder=self.builder)

        for line in result:
            self.assertIsInstance(line, builders.LineBox)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_line_error(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (1, "Error")
        copen.return_value = StringIO(self._get_file_content("digits.lines"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)

        self.assertEqual(te.exception.status, 1)
        self.assertEqual(te.exception.message, "Error")
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )

    @patch("pyocr.tesseract.temp_dir")
    @patch("codecs.open")
    @patch("pyocr.tesseract.run_tesseract")
    def test_line_no_output(self, run_tesseract, copen, temp_dir):
        run_tesseract.return_value = (0, "No file output")
        copen.return_value = StringIO(self._get_file_content("digits.lines"))
        with TemporaryDirectory(prefix="tess_") as tmpdir:
            enter = MagicMock()
            enter.__enter__.return_value = tmpdir
            temp_dir.return_value = enter
            with self.assertRaises(tesseract.TesseractError) as te:
                tesseract.image_to_string(self.image, builder=self.builder)

        self.assertEqual(te.exception.status, -1)
        self.assertIn("Unable to find output file last name tried",
                      te.exception.message)
        run_tesseract.assert_called_once_with(
            "input.bmp", "output", cwd=tmpdir, lang=None,
            flags=self.builder.tesseract_flags,
            configs=self.builder.tesseract_configs,
        )
