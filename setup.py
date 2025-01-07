from setuptools import setup, find_packages

try:
    import pybind11_cmake
except ImportError:
    print("pybind11-cmake must be installed."
          "Try \n \t pip install pybind11_cmake")
    import sys
    sys.exit()

from pybind11_cmake import CMakeExtension, CMakeBuild

from os.path import join, abspath, dirname

__author__ = "Gregory Halverson"
AUTHOR_EMAIL = "Gregory.H.Halverson@jpl.nasa.gov"

def version():
    with open(join(abspath(dirname(__file__)), "he5py", "version.txt"), "r") as file:
        return file.read()

setup(
    version=version(),
    author=__author__,
    author_email=AUTHOR_EMAIL,
    long_description='',
    setup_requires=['pybind11_cmake'],
    ext_modules=[CMakeExtension('HE5PY_CPP')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
    packages=find_packages() + ["he5py", "he5py.src"],
    package_data={'': ["*", "he5py/*", "he5py/src/*"]}
)
