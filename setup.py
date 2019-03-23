#!/usr/bin/env python

import sys
from setuptools import setup

setup(
    name="pyocr",
    description=("A Python wrapper for OCR engines (Tesseract, Cuneiform,"
                 " etc)"),
    keywords="tesseract cuneiform ocr",
    url="https://gitlab.gnome.org/World/OpenPaperwork/pyocr",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later"
        " (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    license="GPLv3+",
    author="Jerome Flesch",
    author_email="jflesch@openpaper.work",
    packages=[
        'pyocr',
        'pyocr.libtesseract',
    ],
    package_dir={
        '': 'src',
    },
    data_files=[],
    scripts=[],
    zip_safe=True,
    install_requires=[
        "Pillow",
        "six",
    ],
    setup_requires=[
        'setuptools_scm',
        'setuptools_scm_git_archive',
    ],
    use_scm_version={
        'write_to': 'src/pyocr/_version.py',
    },
)
