from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='freq_table',
    version='0.2.1',
    license='MIT',
    description='Make printable tables using http://radioscanner.ru frequency db',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/snowwm/freq_table',
    author='Pavel Andreyev',
    author_email='snowwontmelt@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Telecommunications Industry',
        'Topic :: Printing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='radio radio-frequency html-table html-generation',

    packages=['freq_table'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'freq_table=freq_table.__main__:main',
        ],
    },

    python_requires='>=3',
    install_requires=[
        'beautifulsoup4',
        'mako',
        'pyphen',
        'pyyaml',
        'requests',
    ],
)
