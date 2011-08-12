# bootstrap easy_install
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup( 
    name = 'authorities',
    version = '0.1',
    author = 'Ed Summers',
    author_email = 'ehs@pobox.com',
    license = 'http://creativecommons.org/licenses/publicdomain/',
    packages = find_packages(),
    install_requires = ['django', 'pymarc', 'webob', 'MySQLdb',
        'rdflib==2.4.0'],
    description = 'A linked data web application for MARC Authority data',
)
