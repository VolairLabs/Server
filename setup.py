#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup

# find packages
import setuptools


def find_packages():
    packages = []
    for package in setuptools.find_packages():
        if package.startswith("volair_on_PREM"):
            packages.append(package)
    return packages


with open("requirements.txt") as fp:
    install_requires = fp.read()
setup(
    name="volair_on_PREM",
    version="0.34.3",
    description="""Magic Cloud Layer""",
    long_description="".join(open("README.md", encoding="utf-8").readlines()),
    long_description_content_type="text/markdown",
    url="https://github.com/Volair/Server",
    author="Volair",
    author_email="onur.atakan.ulusoy@volair.co",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    # install_requires=install_requires,
    entry_points={
        "console_scripts": ["volair_on_PREM=volair_on_PREM.main:cli"],
    },
    python_requires=">= 3",
    zip_safe=False,
)
