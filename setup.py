from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='appengine-monkey',
      version=version,
      description="Monkeypatches for Google App Engine",
      long_description="""\
This project is a set of replacement modules and monkeypatches to
existing modules in the App Engine environment, to make it more like a
normal Python environment. This is to facilitate the use of existing
libraries.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='appengine',
      author='Ian Bicking',
      author_email='google-appengine@googlegroups.com',
      url='http://code.google.com/p/appengine-monkey/',
      license='MIT',
      py_modules=['pth_relpath_fixup', 'appengine_monkey'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      entry_points="""
      """,
      )
