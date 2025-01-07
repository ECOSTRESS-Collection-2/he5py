import logging
from time import process_time

import h5py
import numpy as np
from affine import Affine

import he5py

import rasters

from rasters import RasterGrid, Raster, RasterGeometry
import logging
import colored_logging as cl

from .HDF5 import HDF5

HDFEOS_INFORMATION_GROUP_NAME = "HDFEOS INFORMATION"

logger = logging.getLogger(__name__)

def crawl(input_group: h5py.Group, output_group: h5py.Group = None, compression="gzip"):
    for key, value in input_group.items():
        if isinstance(value, h5py.Group):
            logger.info(f"crawling group: {key}")

            if output_group is None:
                output_subgroup = None
            else:
                output_subgroup = output_group.create_group(key)

            for attr_key, attr_value in value.attrs.items():
                logger.info(f"copying attribute {attr_key}: {attr_value}")
                output_subgroup.attrs[attr_key] = attr_value

            crawl(value, output_subgroup, compression=compression)
        elif isinstance(value, h5py.Dataset):
            if output_group is None:
                logger.info(f"found dataset: {key} ({value.size}, {value.dtype})")
            else:
                if "QC" in key or "quality" in key:
                    value_array = np.array(value).astype(np.uint16)
                else:
                    value_array = np.array(value)

                logger.info(f"copying dataset: {key} ({value.size}, {value.dtype})")

                if value.size > 1:
                    dataset = output_group.create_dataset(key, data=value_array, compression=compression)
                else:
                    dataset = output_group.create_dataset(key, data=value_array)

                for attr_key, attr_value in value.attrs.items():
                    logger.info(f"copying attribute {attr_key}: {attr_value}")
                    dataset.attrs[attr_key] = attr_value

        else:
            print(f"something weird happened: {key} ({type(key)}")

def h5py_copy(input_filename: str, output_filename: str):
    with h5py.File(input_filename, "r") as input_file, h5py.File(output_filename, "w") as output_file:
        crawl(input_file, output_file)

class HDFEOS5(HDF5):
    logger = logging.getLogger()

    FILL_VALUE_ATTRIBUTE = "_Fillvalue"
    OFFSET_ATTRIBUTE = "add_offset"
    SCALE_ATTRIBUTE = "scale_factor"
    LONG_NAME_ATTRIBUTE = "long_name"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self):
        super().__enter__()
        return self

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)

    def metadata(self, dataset_name: str, strict=False) -> dict:
        variable_name = dataset_name.split('/')[-1]

        metadata = super().metadata(dataset_name)

        if len(metadata) == 0:
            return metadata

        if strict and self.FILL_VALUE_ATTRIBUTE not in metadata:
            raise IOError(f"HDFEOS5 attribute {self.FILL_VALUE_ATTRIBUTE} not found for dataset {dataset_name}")

        if "_FillValue" in metadata:
            fill_value = metadata.pop("_FillValue")
        elif "nodata" in metadata:
            fill_value = metadata.pop("nodata")
        else:
            fill_value = np.nan

        metadata["nodata"] = fill_value

        if strict and self.OFFSET_ATTRIBUTE not in metadata:
            raise IOError(f"HDFEOS5 attribute {self.OFFSET_ATTRIBUTE} not found for dataset {dataset_name}")

        if "_Offset" in metadata:
            offset = metadata.pop("_Offset")
        elif "add_offset" in metadata:
            offset = metadata.pop("add_offset")
        elif "offset" in metadata:
            offset = metadata.pop("offset")
        else:
            offset = 0.0

        metadata["offset"] = offset

        if strict and self.SCALE_ATTRIBUTE not in metadata:
            raise IOError(f"HDFEOS5 attribute {self.SCALE_ATTRIBUTE} not found for dataset {dataset_name}")

        if "_Scale" in metadata:
            scale = metadata.pop("_Scale")
        elif "scale_factor" in metadata:
            scale = metadata.pop("scale_factor")
        elif "scale" in metadata:
            scale = metadata.pop("scale")
        else:
            scale = 1.0

        metadata["scale"] = scale

        if strict and self.LONG_NAME_ATTRIBUTE not in metadata:
            raise IOError(f"HDFEOS5 attribute {self.LONG_NAME_ATTRIBUTE} not found for dataset {dataset_name}")

        if "long_name" in metadata:
            name = metadata.pop("long_name")
        elif "name" in metadata:
            name = metadata.pop("name")
        else:
            name = variable_name

        metadata["name"] = name

        if 'units' in metadata:
            units = metadata.pop('units')
        elif 'Units' in metadata:
            units = metadata.pop('Units')
        else:
            units = ""

        metadata["units"] = units

        return metadata

    @property
    def HDFEOS_information_group_name(self):
        return HDFEOS_INFORMATION_GROUP_NAME

    @property
    def HDFEOS_information_group(self):
        group_name = self.HDFEOS_information_group_name

        if group_name in self:
            group = self[group_name]
        else:
            self.logger.info(f"creating HDFEOS INFORMATION group: {group_name}")
            group = self.create_group(group_name)

        return group

    def write_geometry(
            self,
            target_geometry: RasterGrid,
            geometry_name: str) -> h5py.Group:
        target_proj4 = target_geometry.crs.proj4
        target_geotransform = target_geometry.affine.to_gdal()
        rows = target_geometry.rows
        cols = target_geometry.cols

        HDFEOS_information_group = self.HDFEOS_information_group
        HDFEOS_information_group["StructMetadata.0"] = "need to implement HDF-EOS5"

        # FIXME temporary CRS and affine representation until we get HDF-EOS5 StructMetadata.0 working
        geometry_group_name = f"{HDFEOS_INFORMATION_GROUP_NAME}/{geometry_name}"
        self.logger.info(f"creating ad-hoc geometry group: {geometry_group_name}")
        adhoc_geometry_group = HDFEOS_information_group.create_group(geometry_name)
        self.logger.info(f"using ad-hoc proj4 metadata: {target_proj4}")
        adhoc_geometry_group["proj4"] = target_proj4.encode()
        self.logger.info(f"using ad-hoc geotransform metadata: {target_geotransform}")
        adhoc_geometry_group["geotransform"] = target_geotransform
        self.logger.info(f"using ad-hoc rows metadata: {rows}")
        adhoc_geometry_group["rows"] = rows
        self.logger.info(f"using ad-hoc cols metadata: {cols}")
        adhoc_geometry_group["cols"] = cols

        return HDFEOS_information_group

    @classmethod
    def data_group_name(cls, grid_name: str) -> str:
        return f"HDFEOS/GRIDS/{grid_name}/Data Fields"

    def data_group(self, grid_name: str) -> h5py.Group:
        data_group_name = self.data_group_name(grid_name)

        if data_group_name in self:
            group = self[data_group_name]
        else:
            self.logger.info(f"creating HDFEOS5 data group: {data_group_name}")
            group = self.create_group(data_group_name)

        return group

    def dataset(self, dataset_name: str, grid_name: str) -> h5py.Dataset:
        return self[f"{self.data_group_name(grid_name)}/{dataset_name}"]

    def scale(self, dataset_name: str, grid_name: str) -> (float or int, float or int, float or int):
        dataset = self.dataset(dataset_name, grid_name)

        if self.FILL_VALUE_ATTRIBUTE in dataset.attrs:
            fill_value = float(dataset.attrs[self.FILL_VALUE_ATTRIBUTE])
        else:
            fill_value = np.nan

        if self.OFFSET_ATTRIBUTE in dataset.attrs:
            offset = float(dataset.attrs[self.OFFSET_ATTRIBUTE])
        else:
            offset = 0

        if self.SCALE_ATTRIBUTE in dataset.attrs:
            scale = float(dataset.attrs[self.SCALE_ATTRIBUTE])
        else:
            scale = 1

        return fill_value, offset, scale

    def geometry(self, geometry_name: str) -> RasterGeometry:
        with he5py.File(self.filename, "r") as file:
            grid = file.attach_grid(geometry_name)
            geometry = grid.geometry

        return geometry

    def grid(self, grid_name: str) -> RasterGrid:
        return self.geometry(grid_name)

    def read(self, full_dataset_name):
        dataset = self[full_dataset_name]
        dataset = np.array(dataset)

        return dataset

    def variable(
            self,
            dataset_name: str,
            grid_name: str,
            apply_scale: bool = True,
            geometry: RasterGeometry = None) -> Raster:
        data_group_name = self.data_group_name(grid_name)
        full_dataset_name = f"{data_group_name}/{dataset_name}"
        source_geometry = self.geometry(grid_name)

        if geometry is None:
            self.logger.info(
                f"reading HDFEOS5 raster {full_dataset_name}: {self.filename}")

            try:
                dataset = self[full_dataset_name]
            except Exception as e:
                self.logger.error(e)
                raise IOError(f"unable to read dataset {full_dataset_name} from file {self.filename}")

            array = np.array(dataset)
            image = Raster(array, geometry=source_geometry)
        else:
            index = source_geometry.index(geometry)
            self.logger.info(f"reading HDFEOS5 subset {full_dataset_name} ({index[0].start}:{index[0].stop},{index[1].start}:{index[1].stop}): {self.filename}")

            try:
                dataset = self[full_dataset_name]
            except Exception as e:
                self.logger.error(e)
                raise IOError(f"unable to read dataset {full_dataset_name} from file {self.filename}")

            image = Raster(dataset, geometry=source_geometry)
            logger.info(f"source {dataset_name} min: {np.nanmin(image.array)} mean: {np.nanmean(image.array)} max: {np.nanmax(image.array)}")
            image = image[index]
            image = image.to_geometry(geometry)
            logger.info(
                f"target {dataset_name} min: {np.nanmin(image.array)} mean: {np.nanmean(image.array)} max: {np.nanmax(image.array)}")

        if apply_scale:
            fill_value, offset, scale = self.scale(dataset_name, grid_name=grid_name)
            image = rasters.where(image == fill_value, np.nan, image * scale + offset).astype(np.float32)

        return image
