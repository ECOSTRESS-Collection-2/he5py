from skbuild import setup

setup(
    name="he5py",
    version="1.0.0",
    description="Utilities for working with the HDF-EOS-5 remote sensing data format",
    author="Gregory H. Halverson",
    license="Apache Software License",
    packages=["he5py"],
    cmake_install_dir="he5py",
    include_package_data=True,
    install_requires=[
        "affine",
        "colored-logging",
        "numpy",
        "h5py",
        "rasters"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)