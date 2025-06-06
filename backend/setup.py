from setuptools import setup, find_packages

setup(
    name="easytalk",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "pydantic",
        "firebase-admin",
        "pytest",
        "httpx",
    ],
)
