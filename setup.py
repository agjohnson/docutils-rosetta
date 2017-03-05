"""
Docutils Rosetta Stone

Support for minor markup formats in Docutils
"""

import codecs

from setuptools import setup, find_packages


setup(
    name='docutils-rosetta',
    version='1.0',
    author='Anthony Johnson',
    author_email='aj@ohess.org',
    url='http://github.com/agjohnson/docutils-rosetta',
    license='GPL',
    description='Docutils parsers for minor markup formats',
    package_dir={'': '.'},
    packages=find_packages('.'),
    long_description=__doc__,
    include_package_data=True,
    package_data={},
    install_requires=[
        'Parsley',
        'docutils<0.14',
        'Sphinx',
    ],
)
