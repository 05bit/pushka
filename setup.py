"""Push notifications, SMS, and emails on top of asyncio
"""
import os
from setuptools import setup, find_packages

__version__ = None

dirname, realpath, join = os.path.dirname, os.path.realpath, os.path.join
init_file = join(realpath(dirname(__file__)), 'pushka', '__init__.py')

with open(init_file, 'r') as file:
    for line in file:
        if '__version__' in line:
            __version__ = line.split('=')[1].strip().strip('"').strip("'")
            break

if not __version__:
    raise ValueError("Can't read version from file %s" % init_file)

setup(
    name='pushka',
    version=__version__,
    author="Alexey Kinëv",
    author_email="rudy@05bit.com",
    url="https://github.com/05bit/pushka",
    description=__doc__,
    license='Apache-2.0',
    zip_safe=False,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
    test_suite='tests',
)
