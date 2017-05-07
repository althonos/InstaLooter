#!/usr/bin/env python
# released under the GNU General Public License version 3.0 (GPLv3)

from setuptools import setup, find_packages

import instaLooter

def format_for_setup(requirement_file):
    """Build a list of requirements out of requirements.txt files.
    """
    requirements = []
    with open(requirement_file) as rq:
        for line in rq:
            line = line.strip()
            if line.startswith('-r'):
                other_requirement_file = line.split(' ', 1)[-1]
                requirements.extend(format_for_setup(other_requirement_file))
            elif line:
                requirements.append(line)
    return requirements


## SETUPTOOLS VERSION
setup(
    name='instaLooter',
    version=instaLooter.__version__,

    packages=find_packages(),

    py_modules=['instaLooter'],

    author= instaLooter.__author__,
    author_email= instaLooter.__author_email__,

    description="Another API-less Instagram pictures and videos downloader.",
    long_description=open('README.rst').read(),

    install_requires = format_for_setup('requirements.txt'),
    extras_require = { extra:format_for_setup('requirements-{}.txt'.format(extra))
                        for extra in ['metadata'] },

    entry_points=dict(
        console_scripts=[
            'instaLooter = instaLooter:main',
        ],
    ),

    include_package_data=True,

    url='http://github.com/althonos/InstaLooter',

    #test_suite="tests",

    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],

    license="GPLv3",

    keywords = ['instagram', 'download', 'web', 'web scraping'],

)

