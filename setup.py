# coding: utf-8

"""
    Deci Dataset Analyzer
"""

from setuptools import setup
from setuptools import find_packages

README_LOCATION = "README.md"
REQ_LOCATION = "requirements.txt"
INIT_FILE = "src/data_gradients/__init__.py"
VERSION_FILE = "version.txt"


def readme():
    """print long description"""
    with open(README_LOCATION, encoding="utf-8") as f:
        return f.read()


def get_requirements():
    with open(REQ_LOCATION, encoding="utf-8") as f:
        requirements = f.read().splitlines()
        return [r for r in requirements if not r.startswith("--") and not r.startswith("#")]


def get_version():
    with open(VERSION_FILE, encoding="utf-8") as f:
        ver = f.readline()

    if ver.startswith("for"):
        with open(INIT_FILE, encoding="utf-8") as f:
            for line in f.readlines():
                if line.startswith("__version__"):
                    ver = line.split()[-1].strip('"') + "+master"

    return ver


setup(
    name="data-gradients",
    description="DataGradients",
    version=get_version(),
    author="Deci AI",
    author_email="rnd@deci.ai",
    url="https://github.com/Deci-AI/data-gradients",
    keywords=["Deci", "AI", "Data", "Deep Learning", "Computer Vision", "PyTorch"],
    install_requires=get_requirements(),
    packages=find_packages(where="./src"),
    package_dir={"": "src"},
    package_data={
        "data_gradients.config": ["*.yaml", "**/*.yaml"],
        "data_gradients": ["example.ipynb", "requirements.txt"],
        "data_gradients.assets": ["images/*.png", "html/*.html", "css/*.css", "text/*.txt"],
    },
    long_description=readme(),
    long_description_content_type="text/markdown",
)
