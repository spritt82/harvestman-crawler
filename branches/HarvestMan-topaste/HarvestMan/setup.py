from setuptools import setup, find_packages
import sys, os

version = '2.0.2'

setup(name='HarvestMan',
      version=version,
      description="HarvestMan is a web crawler application and framework.",
      long_description="""\
HarvestMan is a modular, extensible and flexible web crawler program cum framework written in pure Python. HarvestMan? can be used to download files from websites according to a number of customized rules and constraints. It can be used to find information from websites matching keywords or regular expressions.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='crawler spider web-crawler web-bot robot data-mining python',
      author='Anand B Pillai',
      author_email='abpillai at gmail dot com',
      url='http://code.google.com/p/harvestman-crawler/',
      license='GPLv2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      "sgmlop >= 1.1.1",
      "pyparsing >= 1.4.8",
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
