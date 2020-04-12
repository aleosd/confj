from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='confj',
    version='0.2.3',
    description='Load configs from json files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/aleosd/confj',
    author='Alekey Osadchuk',
    author_email='osdalex@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='json configs loader',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.5, <4',
    extras_require={
        'validation': ['jsonschema'],
        'aws': ['boto3'],
        'test': ['pytest'],
    },

    project_urls={
        'Bug Reports': 'https://github.com/aleosd/confj/issues',
        'Say Thanks!': 'https://saythanks.io/to/aleosd',
        'Source': 'https://github.com/aleosd/confj/',
    },
)
