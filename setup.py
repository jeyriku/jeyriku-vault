#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
setup.py for Jeyriku Vault
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = [
    'cryptography>=41.0.0',
]

# Optional dependencies
extras_require = {
    'sqlcipher': ['pysqlcipher3>=1.1.0'],
    'all': ['pysqlcipher3>=1.1.0'],
}

setup(
    name='jeyriku-vault',
    version='1.0.0',
    author='Jeremie Rouzet',
    author_email='contact@jeyriku.net',
    description='Secure credential management system for Jeyriku network automation tools',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jeyriku/jeyriku-vault',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Topic :: System :: Systems Administration',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'jeyriku-vault=jeyriku_vault.cli:main',
        ],
    },
    include_package_data=True,
    keywords='vault credentials security encryption network automation',
    project_urls={
        'Bug Reports': 'https://github.com/jeyriku/jeyriku-vault/issues',
        'Source': 'https://github.com/jeyriku/jeyriku-vault',
        'Documentation': 'https://github.com/jeyriku/jeyriku-vault#readme',
    },
)
