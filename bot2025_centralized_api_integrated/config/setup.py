"""
🌟 Trading Bot Setup Script
Easy installation and setup for the cosmic trading bot
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Cosmic Trading Bot - A sophisticated cryptocurrency trading system"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="cosmic-trading-bot",
    version="1.0.0",
    author="Trading Bot Developer",
    author_email="developer@example.com",
    description="A sophisticated cryptocurrency trading bot with machine learning capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cosmic-trading-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.12.1",
            "flake8>=6.1.0",
        ],
        "optional": [
            "pygame>=2.5.2",
            "websockets>=12.0",
            "redis>=5.0.1",
            "prometheus-client>=0.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cosmic-bot=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="trading, cryptocurrency, bot, machine learning, binance, bybit",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/cosmic-trading-bot/issues",
        "Source": "https://github.com/yourusername/cosmic-trading-bot",
        "Documentation": "https://github.com/yourusername/cosmic-trading-bot/blob/main/README.md",
    },
)
