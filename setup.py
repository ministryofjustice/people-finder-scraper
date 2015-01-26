import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='people-finder-scraper',
    version='0.1',
    packages=['people_finder_scraper'],
    include_package_data=True,
    license='BSD License',
    description='converts people finder urls in to python objects',
    long_description=README,
    author='Sym Roe',
    author_email='sym.roe@digital.justice.gov.uk',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
