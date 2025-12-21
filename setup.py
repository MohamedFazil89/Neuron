from setuptools import setup, find_packages

setup(
    name="neuron-cli",
    version="1.0.0",
    description="AI-powered full-stack code generation CLI",
    author="Your Name",
    author_email="nmohammedfazil790@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "neuron=neuron_cli.cli:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)