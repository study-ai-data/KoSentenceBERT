# !/usr/bin/env python

from setuptools import setup, find_packages
import KoSentenceBERT


def install():
    setup(name=KoSentenceBERT.__name__,
          install_requires=KoSentenceBERT.__install_requires__,
          long_description=open('KoSentenceBERT/README.md', 'r', encoding='utf-8').read(),
          packages=find_packages(),
          classifiers=[
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.2',
              'Programming Language :: Python :: 3.3',
              'Programming Language :: Python :: 3.4',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3.6',
              'Programming Language :: Python :: 3.7',
              'Programming Language :: Python :: 3.8',
              'Programming Language :: Python :: 3.9',
          ]
          )


if __name__ == "__main__":
    install()
