from distutils.core import setup

setup(name='liaison',
      version='0.1.0',
      description='A small daemon that collects service health information '
                  'from consul and sends it to a TSDB',
      url='http://github.com/cruatta/liaison',
      author='Cameron Ruatta',
      packages=['liaison'],
      scripts=['bin/liaison'],
      package_data={'liaison': ['README.md', 'LICENSE.txt']},
      license='MIT',
      install_requires=['consul', 'statsd', 'argparse'],
      )
