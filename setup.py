# setup.py
"""
Setup script for ComplianceCompass package.

Gestisce l'installazione del pacchetto e le sue dipendenze.
"""
import os
from setuptools import setup, find_packages
from typing import List

def read(fname: str) -> str:
    """Legge il contenuto di un file."""
    with open(os.path.join(os.path.dirname(__file__), fname), "r", encoding="utf-8") as f:
        return f.read()

def read_requirements(fname: str) -> List[str]:
    """
    Legge i requisiti da un file, ignorando commenti e righe vuote.
    
    Args:
        fname: Nome del file dei requisiti
        
    Returns:
        Lista di requisiti
    """
    requirements = []
    for line in read(fname).splitlines():
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('//'):
            requirements.append(line)
    return requirements

setup(
    name="compliance-compass",
    version="0.1.0",
    author="Compliance Compass Team",
    author_email="team@compliancecompass.example.com",
    description="Piattaforma wiki collaborativa per normative tecniche e di sicurezza",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/orgname/compliance-compass",
    project_urls={
        "Bug Tracker": "https://github.com/orgname/compliance-compass/issues",
        "Documentation": "https://compliance-compass.readthedocs.io/",
        "Source Code": "https://github.com/orgname/compliance-compass",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={
        "compliance_compass": [
            "templates/*.html",
            "static/*",
            "alembic.ini",
            "logging.conf",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Framework :: FastAPI",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements("requirements.txt"),
    tests_require=read_requirements("requirements-test.txt"),
    extras_require={
        "dev": [
            "black",
            "flake8",
            "bandit",
            "isort",
            "pre-commit",
            "mypy",
            "pylint",
        ],
        "test": read_requirements("requirements-test.txt"),
        "docs": [
            "sphinx",
            "sphinx_rtd_theme",
            "sphinx-autodoc-typehints",
            "myst-parser",
        ],
        "prod": [
            "gunicorn",
            "uvicorn[standard]",
            "python-json-logger",
        ],
    },
    entry_points={
        "console_scripts": [
            "cc_seed=scripts.seed_db:main",
            "cc_elasticsearch=scripts.elasticsearch_init:main",
            "cc_test=scripts.run_tests:main",
            "cc_migrate=scripts.db_migrate:main",
            "cc_dev=scripts.dev_server:main",
        ],
    },
    zip_safe=False,
)