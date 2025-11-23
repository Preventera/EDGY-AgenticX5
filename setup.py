"""
EDGY-AgenticX5 Setup
"""

from setuptools import setup, find_packages

setup(
    name="edgy-agentic",
    version="0.1.0",
    description="Advanced Agentic AI Platform for Occupational Health & Safety",
    author="GenAISafety | Preventera",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "rdflib>=7.0.0",
        "pydantic>=2.0.0",
        "pyshacl>=0.25.0",
        "owlrl>=6.0.2",
        "pytest>=7.4.0",
        "langgraph>=0.2.28",
        "langchain-core>=0.3.80",
        "langchain-anthropic>=0.3.3",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)