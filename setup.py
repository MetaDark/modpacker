from setuptools import setup, find_packages

setup(name='modpacker',
      version='1.0',
      description='Generate and maintain Minecraft modpacks',
      url='https://gitlab.com/MetaDark/modpacker',
      author='MetaDark',
      author_email='kira.bruneau@gmail.com',
      license='GPL3',
      packages=find_packages(),
      install_requires=[
          'bs4'
          'docopt',
          'requests',
      ],
      zip_safe=True)
