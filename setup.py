from setuptools import setup
import sys

tests_require = ['pytest', 'pytest-flake8', 'flake8']

if sys.version < '3':
    tests_require.append('unittest2')

setup(name='liaison',
      version='0.3.0',
      description='A small daemon that collects service health information '
                  'from consul and sends it to a TSDB',
      url='http://github.com/cruatta/liaison',
      author='Cameron Ruatta',
      packages=['liaison'],
      scripts=['bin/liaison'],
      package_data={'liaison': ['README.md', 'LICENSE.txt']},
      license='MIT',
      install_requires=['python-consul', 'statsd', 'argparse', 'six'],
      tests_require=tests_require,
      setup_requires=['pytest-runner'],
      )
