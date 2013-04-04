#!/usr/bin/env python
from setuptools import setup


setup(
    name='sqlalchemy-manager',
    version='0.0.2',
    description='Manager for SQLAlchemy',
    long_description=open('README.rst').read(),
    author='Roman Gladkov',
    author_email='d1fffuz0r@gmail.com',
    url='https://github.com/d1ffuz0r/sqlalchemy-manager',
    install_requires=['sqlalchemy'],
    py_modules=['alchmanager'],
    zip_safe=False,
    test_suite='tests',
    classifiers=(
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    )
)
