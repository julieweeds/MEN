__author__ = 'juliewe'
from setuptools import setup

# Import this to prevent spurious error: info('process shutting down')
from multiprocessing import util

setup(name='mencc',
      version='0.1',
      description='Experiments using MEN dataset',
      #url='http://github.com/storborg/funniest',
      author='Julie Weeds',
      #author_email='flyingcircus@example.com',
      license='MIT',
      packages=['src/mencc'],
      #cmdclass = {'test': test},
      #options = {'test' : {'test_dir':['test']}}
      #zip_safe=False
      )
