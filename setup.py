import os, sys
from setuptools import setup, find_packages, Extension


if sys.version_info[:2] < (3, 3):
    raise RuntimeError('Kaa requires Python 3.3 or later.')

try:
    from Cython.Distutils import build_ext
    cmdclass = {'build_ext': build_ext}

    ext = Extension("_gappedbuf", 
        ["_gappedbuf/_gappedbuf.pyx",
         "_gappedbufre/_sre.c"])

except ImportError:
    cmdclass = {}
    ext = Extension("_gappedbuf", 
        ["_gappedbuf/_gappedbuf.c",
         "_gappedbufre/_sre.c"])

def read(fname):
    return open(
            os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    cmdclass = cmdclass,
    name = "kaaedit",
    version = "0.10.0",
    description='kaa - console text editor.',
    url='https://github.com/kaaedit/kaa',
    author='Atsuo Ishimoto',
    author_email='ishimoto@gembook.org',
    long_description=read('README.rst'),
    classifiers=[
            "Programming Language :: Python :: 3",
            "Development Status :: 2 - Pre-Alpha",
            "Topic :: Text Editors",
            "Environment :: Console :: Curses",
            "License :: OSI Approved :: MIT License", ],
    license='MIT License',
    install_requires=['curses_ex', 'pyjf3', 'setproctitle'],
    packages = find_packages(),
    ext_modules = [ext],
    entry_points = {
        'console_scripts': [
            'kaa = kaa.cui.main:run',
        ],}
)
