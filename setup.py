#!/usr/bin/env python3

import sys
from setuptools import setup


# NOTE: This file must remain Python 2 compatible for the foreseeable future,
# to ensure that we error out properly for people with outdated setuptools
# and/or pip.
if sys.version_info < (3, 4):
    error = """
Beginning with PyOCR 0.7, Python 3.4 or above is required.

This may be due to an out of date pip.

Make sure you have pip >= 9.0.1.
"""
    sys.exit(error)

setup(
    name="async-pyocr",
    description=("A Python wrapper for OCR engines (Tesseract, Cuneiform,"
                 " etc), with async"),
    keywords="tesseract cuneiform ocr",
    url="https://github.com/mlouielu/async-pyocr/",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later"
        " (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    license="GPLv3+",
    author="Louie Lu",
    author_email="me@louie.lu",
    packages=[
        'async_pyocr',
        'async_pyocr.libtesseract',
    ],
    package_dir={
        '': 'src',
    },
    data_files=[],
    scripts=[],
    zip_safe=True,
    python_requires='>=3.6',
    install_requires=[
        "Pillow",
    ],
    setup_requires=[
        'setuptools_scm',
        'setuptools_scm_git_archive',
    ],
    use_scm_version={
        'write_to': 'src/async_pyocr/_version.py',
    },
)
