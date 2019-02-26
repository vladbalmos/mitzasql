import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
        name='mitzasql',
        version='0.1dev',
        author='Vlad Balmos',
        author_email='vladbalmos@yahoo.com',
        description='Ncurses MySQL client',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/vladbalmos/mitzasql',
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
        ],
        install_requires=[
            'urwid >=2.0.1, <3',
            'mysql-connector-python >=8.0.15, <9',
            'appdirs >=1.4.3, <1.5'
        ],
        scripts=['bin/mitzasql']
)
