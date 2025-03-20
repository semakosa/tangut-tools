from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tgtortho",
    version="0.1.0",
    author="Tangut Tools Team",
    author_email="xun.gong@univie.ac.at",  # Updated email
    description="A library for handling Tangut orthography and phonological vectors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/semakosa/tangut-tools",  # Updated URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pynini>=2.1.3",
    ],
    extras_require={
        "full": [
            "PyICU>=2.8",
            "numpy>=1.19.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "sphinx>=4.0.0",
        ],
    },
) 