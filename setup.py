from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='scopus_spider',
      version='0.1',
      description='Search and scrape scopus database',
      long_description=readme(),
      url='',
      author='Robert Vesco',
      author_email='rv_spam@hotmail.com',
      license='MIT',
      packages=['scopus_spider','scopus_spider.scraping'],
      zip_safe=False,
      entry_points = {
          'console_scripts': ['scopus_spider=scopus_spider.command_line:main'],
                  },
      install_requires=[
          'sys',
      ],
)
