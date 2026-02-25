#!/usr/bin/env python3
"""
Setup configuration for gogs_python

Project: Python University - 분산 시스템 & 양자 보안 연구
Author: Python University
License: MIT
"""

from setuptools import setup, find_packages
from pathlib import Path

# README 읽기
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="gogs-python",
    version="9.4.0",
    author="Python University",
    author_email="python@university.edu",
    description="분산 시스템 및 양자 보안 연구 - MapReduce, Quantum Crypto, Raft Consensus, Quantum Internet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gogs.dclub.kr/kim/gogs_python.git",
    project_urls={
        "Documentation": "https://gogs.dclub.kr/kim/gogs_python",
        "Bug Tracker": "https://gogs.dclub.kr/kim/gogs_python/issues",
        "Source Code": "https://gogs.dclub.kr/kim/gogs_python.git",
    },
    packages=find_packages(exclude=["tests", "docs", "__pycache__"]),
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Distributed Computing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="distributed-systems mapreduce quantum-crypto raft-consensus quantum-internet",
    include_package_data=True,
    zip_safe=False,
)
