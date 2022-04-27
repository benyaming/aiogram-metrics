import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aiogram-metrics",
    version="0.0.10",
    author="Benyamin Ginzburg",
    author_email="benyomin.94@gmail.com",
    description="Message metrics exporter for aiogram framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/benyaming/aiogram-metrics",
    project_urls={
        "Bug Tracker": "https://github.com/benyaming/aiogram-metrics/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=[
        'aiogram',
        'aiopg'
    ]
)
