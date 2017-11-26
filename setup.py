#!/usr/bin/env python
# released under the GNU General Public License version 3.0 (GPLv3)

from setuptools import setup, find_packages

requires = [
    'six~=1.4',
    'beautifulsoup4~=4.4',
    'progressbar2~=3.1',
    'requests~=2.18',
    'docopt~=0.4',
    'python-dateutil~=2.1',
    'hues>=0.2.2,<1'
]

# SETUPTOOLS VERSION
setup(
    name='instaLooter',
    version='0.13.2',
    description="Another API-less Instagram pictures and videos downloader",
    url='https://github.com/althonos/instaLooter',
    author='Martin Larralde',
    author_email='martin.larralde@ens-paris-saclay.fr',
    license='GPLv3',
    packages=find_packages(exclude=['tests*']),
    install_requires=requires,
    entry_points={
        'console_scripts': ['instaLooter = instaLooter:main'],
    },
    test_suite='tests',
    zip_safe=False,
    keywords=['instagram', 'download', 'web', 'web scraping', 'looter']
)
