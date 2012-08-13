#!/usr/bin/env python

PROJECT = 'brainstorm'
VERSION = '0.1'

from setuptools import setup, find_packages


long_description = ''

setup(
    name=PROJECT,
    version=VERSION,
    description='cliff-based CLI for interacting with DHO.',
    long_description=long_description,
    author='Kyle Marsh',
    author_email='kyle.marsh@dreamhost.com',
    url='...',
    download_url='...',
    scripts=[],
    provides=[],
    install_requires=['boto', 'cliff'],
    test_suite="nose.collector",
    tests_require=['nose', 'unittest'],
    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'brainstorm = brainstorm.main:main'
            ],
        'brainstorm.commands': [
            'list = brainstorm.viewer:List',
            'show = brainstorm.viewer:Show',
            'delete = brainstorm.manipulator:DeleteObjects',
            'down = brainstorm.manipulator:DownloadObject',
            'up = brainstorm.manipulator:UploadFile',
            'create bucket = brainstorm.manipulator:CreateBucket',
            'remove bucket = brainstorm.manipulator:RemoveBucket',
            'set acl = brainstorm.manipulator:SetCannedACL',
            ],
        },
    zip_safe=False,
    )
