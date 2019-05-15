# Copyright (c) 2019 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

exec(open('mitzasql/version.py').read())

setuptools.setup(
        name='mitzasql',
        version=__version__,
        author='Vlad Balmos',
        author_email='vladbalmos@yahoo.com',
        long_description_content_type='text/markdown',
        description='Text user interface MySQL client',
        long_description=long_description,
        license="MIT",
        url='https://github.com/vladbalmos/mitzasql',
        project_urls={
            'Bug Tracker': 'https://github.com/vladbalmos/mitzasql/issues',
            'Website': 'https://vladbalmos.github.io/mitzasql'
        },
        packages=setuptools.find_packages(),
        keywords='tui cli ncurses console mysql client',
        package_data={
            'mitzasql': ['ui/widgets/help.txt']
        },
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
        ],
        install_requires=[
            'urwid ==2.0.1',
            'mysql-connector-python ==8.0.16',
            'appdirs ==1.4.3'
        ],
        scripts=['bin/mitzasql']
)
