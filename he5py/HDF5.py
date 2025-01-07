import logging
from typing import List

import h5py
import numpy as np
# from memory_profiler import profile

from rasters import Raster


def decode_HDF5_attribute(value):
    if isinstance(value, bytes):
        value = value.decode()
    elif isinstance(value, np.ndarray):
        if len(value) == 1:
            value = value[0].item()
        else:
            value = list(value)
    # else:
        # raise ValueError(f"unknown HDF5 attribute type: {type(value).__name__}")

    return value


class HDF5(h5py.File):
    logger = logging.getLogger()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self):
        super().__enter__()
        return self

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)

    def metadata(self, dataset_name: str) -> dict:
        try:
            raw_metadata = self[dataset_name].attrs.items()
        except Exception as e:
            self.logger.error(e)
            raise IOError(f"unable to read attributes for dataset {dataset_name} from file {self.filename}")

        metadata = dict([
            (key, decode_HDF5_attribute(value))
            for key, value
            in raw_metadata
        ])

        return metadata

    def listing(self, dataset_name: str) -> List[str]:
        try:
            return list(self[dataset_name].keys())
        except Exception as e:
            self.logger.error(e)
            raise IOError(f"unable to open dataset {dataset_name} in file: {self.filename}")

    # @profile
    def write(
            self,
            name: str,
            data: Raster or np.ndarray,
            compression: str = None,
            fillvalue: float or int = None,
            group: h5py.Group = None,
            **kwargs):
        if group is None:
            group = self

        dataset = group.create_dataset(
            name=name,
            data=data,
            shape=data.shape,
            dtype=data.dtype,
            compression=compression,
            fillvalue=fillvalue,
            **kwargs
        )

        return dataset

    def inspect(self):
        listing = []

        self.visit(listing.append)

        for name in listing:
            if isinstance(self[name], h5py.Group):
                print(name)
            elif isinstance(self[name], h5py.Dataset):
                print(f"{name} ({self[name].dtype})")

                if str(self[name].dtype).startswith("|S"):
                    string_value = self[name][()].decode()

                    for line in string_value.split("\n"):
                        print(f"\t{line}")

            for key, value in self.metadata(name).items():
                print(f"* {key}: {value} ({type(value).__name__})")


def inspect_hdf5(filename: str):
    with HDF5(filename, "r") as file:
        file.inspect()
