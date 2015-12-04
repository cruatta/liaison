from distutils.core import setup

setup(name='liaison',
    version='0.1.0-alpha',
    description='A small daemon that collects service health information from consul and sends it to a TSDB',
    author='Cameron Ruatta',
    packages=['liaison'],
    scripts=['bin/liaison'],
    package_data={'liaison': ['README.md', 'LICENSE.txt']}
)