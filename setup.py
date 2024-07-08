from setuptools import setup, find_packages

setup(
    name="fastapi-cli",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer",
        "sqlmodel",
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "fastapi-cli=fastapi_cli.main:app",
        ],
    },
)