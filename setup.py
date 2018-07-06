from setuptools import setup, find_packages
import modpacker

setup(name='modpacker',
      version=modpacker.version,
      description='Generate and maintain Minecraft modpacks',
      url='https://gitlab.com/MetaDark/modpacker',
      author='MetaDark',
      author_email='kira.bruneau@gmail.com',
      license='GPL3',
      packages=find_packages(),
      entry_points= {
          'console_scripts': [
              'modpacker = modpacker:main'
          ],
      },
      install_requires=[
          'bs4',
          'docopt',
          'requests',
          'unshortenit',
      ],
      zip_safe=True)
