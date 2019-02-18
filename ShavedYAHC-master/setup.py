# vim: set tw=99:

from setuptools import setup

setup(name='shaved_yahc',
      version='0.1',
      description='Streamlined version of the YAHC web crawler',
      url='http://github.com/PLSysSec/ShavedYAHC',
      author='Michael Smith',
      author_email='michael@spinda.net',
      license='GPLv2',
      packages=['shaved_yahc'],
      install_requires=['selenium'],
      scripts=['scripts/syahc'],
      zip_safe=False)
