"""
Flask-PicoCMS
--------------

Lightweight CMS backend for Flask apps.
"""
import re
from setuptools import setup

with open('flask_picocms/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

setup(
    name='Flask-PicoCMS',
    version=version,
    url='https://github.com/johnwilson/picocms',
    license='MIT',
    author='John K.E. Wilson',
    author_email='wilsonfiifi@gmail.com',
    description='Lightweight CMS backend for Flask apps',
    long_description=__doc__,
    py_modules=['flask_picocms'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    download_url='https://github.com/johnwilson/picocms/archive/v0.0.1.tar.gz',
    keywords=['flask', 'cms'],
    install_requires=[
        "Flask",
        "peewee==2.10.2",
        "toml==0.9.2"
    ],
    test_suite="tests",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
