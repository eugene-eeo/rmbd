import sys
from setuptools import setup


setup(
    name='rmbd',
    version='0.1.0',
    description='remember stuff',
    author='Eeo Jun',
    author_email='141bytes@gmail.com',
    url='https://github.com/eugene-eeo/rmbd/',
    packages=['rmbd'],
    tests_require=['nose', 'coverage'],
    install_requires=[
        'gevent==1.1.2',
        'fnvhash==0.1.0',
    ],
)
