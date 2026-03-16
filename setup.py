"""Setup script for SignBridge."""

from setuptools import setup, find_packages

from signbridge import __version__

setup(
    name="signbridge",
    version=__version__,
    description="Real-time sign language interpretation via camera",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SignBridge Team",
    url="https://github.com/yeager/SignBridge",
    license="GPL-3.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PyGObject>=3.42",
        "opencv-python>=4.8",
        "mediapipe>=0.10",
        "numpy>=1.24",
    ],
    entry_points={
        "console_scripts": [
            "signbridge=signbridge.main:main",
        ],
    },
    data_files=[
        ("share/applications", ["data/se.signbridge.app.desktop"]),
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Topic :: Accessibility",
    ],
)
