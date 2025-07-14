from setuptools import setup, find_packages
import os

setup(
    name="foxit-pdf-cloudapi",  
    version="1.0.2", 
    author="Foxit Software Inc.",
    author_email="support@foxitsoftware.com",  
    description="A Python library for PDF manipulation using cloud APIs",  
    long_description=open("README.md", "r", encoding="utf-8").read(), 
    long_description_content_type="text/markdown", 
    packages=find_packages(include=["config", "server", "tools", "*"], exclude=["__pycache__", "tests", "output"]),  
    include_package_data=True,  
    py_modules=["main"],  # Explicitly include main.py
    install_requires=open(os.path.join(os.path.dirname(__file__), "requirements.txt"), "r", encoding="utf-8").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'foxit-cloudapi-mcp-service=main:main',  # Entry point for the MCP service
        ],
    },
    python_requires=">=3.6",
)
