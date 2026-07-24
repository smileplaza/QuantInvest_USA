"""
QuantInvest Tool - Quantitative Investment Strategy Analysis Application
Setup configuration for package distribution and PyInstaller bundling
"""

from setuptools import setup, find_packages
import os

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
def read_requirements(filename):
    """Parse requirements.txt and return list of dependencies."""
    requirements = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                # Remove inline comments
                line = line.split("#")[0].strip()
                if line:
                    requirements.append(line)
    return requirements

setup(
    name="QuantInvest-Tool",
    version="1.0.0",
    author="QuantInvest Development Team",
    author_email="sahong@kakao.com",
    description="GUI application for analyzing and backtesting quantitative investment strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smileplaza/QuantInvest_USA",
    project_urls={
        "Bug Tracker": "https://github.com/smileplaza/QuantInvest_USA/issues",
        "Documentation": "https://github.com/smileplaza/QuantInvest_USA",
        "Source Code": "https://github.com/smileplaza/QuantInvest_USA",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.12",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "pytest>=8.0,<10",
            "pytest-cov>=6.0,<8",
            "black>=25.0,<27",
            "flake8>=7.3,<8",
            "isort>=6.0,<9",
        ],
        "build": [
            "pyinstaller>=6.16,<7",
            "setuptools>=68",
            "wheel",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="quantitative trading backtesting strategies finance investment",
    entry_points={
        "console_scripts": [
            "quantinvest=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["Windows", "macOS", "Linux"],
)
