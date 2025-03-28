from setuptools import setup, find_packages

setup(
    name="questgit",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "questgit = cli.main:main",
        ]
    },
)
