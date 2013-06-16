import os
from setuptools import setup, find_packages, Extension

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
    name = "kaa",
    version = "0.0.1",
    description='kaa - console text editor.',
    author='Atsuo Ishimoto',
    author_email='ishimoto@gembook.org',
    long_description=read('README.rst'),
    classifiers=[
            "Programming Language :: Python :: 3",
            "Development Status :: 2 - Pre-Alpha",
            "Topic :: Text Editors",
            "Environment :: Console :: Curses",
            "License :: OSI Approved :: BSD License", ],

    install_requires=['curses_ex'],
    packages=find_packages(),
    ext_modules = [ext],
    entry_points = {
        'console_scripts': [
            'kaa = kaa.cui.main:run',
        ],}
)
