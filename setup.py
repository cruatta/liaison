from setuptools import setup
import sys

tests_require = ['pytest', 'pytest-flake8', 'flake8']

if sys.version < '3.3':
    tests_require.append('mock>=1.3.0')
if sys.version < '3':
    tests_require.append('unittest2>=1.1.0')

setup(name='liaison',
      version='0.4.0_rc1',
      description='A small daemon that collects service health information '
                  'from consul and sends it to a TSDB',
      url='http://github.com/cruatta/liaison',
      author='Cameron Ruatta',
      packages=['liaison'],
      scripts=['bin/liaison'],
      package_data={'liaison': ['README.md', 'LICENSE.txt']},
      license='MIT',
      install_requires=['python-consul>=0.4.7', 'statsd>=3.2.1', 'argparse',
                        'six'],
      tests_require=tests_require,
      setup_requires=['pytest-runner'],
      )
