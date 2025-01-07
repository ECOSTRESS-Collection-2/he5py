import os
from typing import List, Union

import numpy as np

from rasters import RasterGrid, Raster

os.environ["HDF5_DISABLE_VERSION_CHECK"] = "2"

import HE5PY_CPP


def test_struct():
    return HE5PY_CPP.test_struct()


# r	Readonly, file must exist (default)
# r+	Read/write, file must exist
# w	Create file, truncate if exists
# w- or x	Create file, fail if exists
# a	Read/write if exists, create otherwise

# H5F_ACC_EXCL
# w- or x
# If file already exists, H5Fcreate fails. If file does not exist, it is created and opened with read-write access.
#
# H5F_ACC_TRUNC
# w
# If file already exists, file is opened with read-write access and new data overwrites existing data, destroying all prior content, i.e., file content is truncated upon opening. If file does not exist, it is created and opened with read-write access.
#
# H5F_ACC_RDONLY
# r
# Existing file is opened with read-only access. If file does not exist, H5Fopen fails.
#
# H5F_ACC_RDWR
# r+
# Existing file is opened with read-write access. If file does not exist, H5Fopen fails.

H5F_ACC_EXCL = HE5PY_CPP.H5F_ACC_EXCL
H5F_ACC_TRUNC = HE5PY_CPP.H5F_ACC_TRUNC
H5F_ACC_RDONLY = HE5PY_CPP.H5F_ACC_RDONLY
H5F_ACC_RDWR = HE5PY_CPP.H5F_ACC_RDWR

H5T_NATIVE_FLOAT = HE5PY_CPP.H5T_NATIVE_FLOAT


def create_grid_latlon(
        gdfid: int,
        grid_name: str,
        ul_lon: float,
        ul_lat: float,
        lr_lon: float,
        lr_lat: float,
        rows: int,
        cols: int) -> int:
    return HE5PY_CPP.create_grid_latlon(gdfid, grid_name, ul_lon, ul_lat, lr_lon, lr_lat, rows, cols)


def write_grid_field_float(gdid: int, image: np.ndarray, field_name: str) -> int:
    return HE5PY_CPP.write_grid_field_float(gdid, image, field_name)


def write_grid_field_uint8(gdid: int, image: np.ndarray, field_name: str) -> int:
    return HE5PY_CPP.write_grid_field_uint8(gdid, image, field_name)

def write_grid_field_uint16(gdid: int, image: np.ndarray, field_name: str) -> int:
    return HE5PY_CPP.write_grid_field_uint16(gdid, image, field_name)

def HE5_GDopen(filename: str, Flags: int) -> int:
    return HE5PY_CPP.HE5_GDopen(filename, Flags)


def HE5_GDattach(fid: int, grid_name: str) -> int:
    return HE5PY_CPP.HE5_GDattach(fid, grid_name)


def HE5_GDdetach(gdid: int) -> int:
    return HE5PY_CPP.HE5_GDdetach(gdid)


def HE5_EHconvAng(*args):
    return HE5PY_CPP.HE5_EHconvAng(*args)


def HE5_GDcreate(gdfid: int, grid_name: str, xdim, ydim, upleft, lowright):
    return HE5PY_CPP.HE5_GDcreate(gdfid, grid_name, xdim, ydim, upleft, lowright)


def HE5_GDdefproj(gridID, projcode, zonecode, spherecode, projparm):
    return HE5PY_CPP.HE5_GDdefproj(gridID, projcode, zonecode, spherecode, projparm)


def HE5_GDdeffield(gridID, fieldname, dimlist, maxdimlist, ntype, merge):
    return HE5PY_CPP.HE5_GDdeffield(gridID, fieldname, dimlist, maxdimlist, ntype, merge)


def HE5_GDwritefield(gridID, fieldname, start, stride, edge, data):
    return HE5PY_CPP.HE5_GDwritefield(gridID, fieldname, start, stride, edge, data)


def HE5_GDclose(fileID):
    return HE5PY_CPP.HE5_GDclose(fileID)


class GridCreationFailed(IOError):
    pass


class GridAttachmentFailed(IOError):
    pass


class FileOpenFailed(IOError):
    pass


class FieldWriteFailed(IOError):
    pass


class FieldReadFailed(IOError):
    pass


class Grid:
    def __init__(self, filename: str, fid: int, gid: int, grid_name: str, geometry: RasterGrid):
        self.filename = filename
        self._fid = fid
        self._gid = gid
        self.grid_name = grid_name
        self.geometry = geometry

    def __repr__(self) -> str:
        return f'Grid(filename="{self.filename},mode={self.grid_name}")'

    @classmethod
    def create(cls,
               filename: str,
               fid: int,
               grid_name: str,
               geometry: RasterGrid):
        # print(f"creating grid: {grid_name} fid: {fid} file: {filename}")
        # print("geometry:")
        # print(geometry)
        # print("affine:")
        # print(geometry.affine)
        ul_lon = geometry.x_min
        ul_lat = geometry.y_max
        lr_lon = geometry.x_max
        lr_lat = geometry.y_min
        rows = geometry.rows
        cols = geometry.cols
        # print(f"ul_lon: {ul_lon} ul_lat: {ul_lat} lr_lon: {lr_lon} lr_lat: {lr_lat} rows: {rows} cols: {cols}")

        gid = create_grid_latlon(
            gdfid=fid,
            grid_name=grid_name,
            ul_lon=ul_lon,
            ul_lat=ul_lat,
            lr_lon=lr_lon,
            lr_lat=lr_lat,
            rows=rows,
            cols=cols
        )

        if gid == -1:
            raise GridCreationFailed(f"unable to create grid {grid_name} in file {filename} ({fid})")

        grid = Grid(
            filename=filename,
            fid=fid,
            gid=gid,
            grid_name=grid_name,
            geometry=geometry
        )

        return grid

    @classmethod
    def attach(
            cls,
            filename: str,
            fid: int,
            grid_name: str):
        # print(f"attaching grid: {grid_name} fid: {fid} file: {filename}")
        gid = HE5_GDattach(fid, grid_name)
        # print(f"gid: {gid}")

        if gid == -1:
            raise GridAttachmentFailed(f"unable to attach to grid {grid_name} in file {filename} ({fid})")

        grid_boundaries = HE5PY_CPP.read_grid(gid)
        cols = grid_boundaries.xdim
        rows = grid_boundaries.ydim
        x_min = grid_boundaries.ul_x
        y_max = grid_boundaries.ul_y
        x_max = grid_boundaries.lr_x
        y_min = grid_boundaries.lr_y
        bbox = (x_min, y_min, x_max, y_max)
        shape = (rows, cols)
        geometry = RasterGrid.from_bbox(bbox=bbox, shape=shape)

        grid = Grid(
            filename=filename,
            fid=fid,
            gid=gid,
            grid_name=grid_name,
            geometry=geometry
        )

        return grid

    def __enter__(self):
        return self

    def write_float(self, field_name: str, image: Union[Raster, np.ndarray]):
        # print( f"writing float field {field_name} ({image.dtype}) ({image.shape}) to grid {self.grid_name} ({self._gid}) in file {self.filename} ({self._fid})")

        status = write_grid_field_float(
            gdid=self._gid,
            image=image,
            field_name=field_name
        )

        if status == -1:
            raise FieldWriteFailed(
                f"unable to write field {field_name} to grid {self.grid_name} ({self._gid}) in file {self.filename} ({self._fid})")

    def write_uint8(self, field_name: str, image: Union[Raster, np.ndarray]):
        status = write_grid_field_uint8(
            gdid=self._gid,
            image=image,
            field_name=field_name
        )

        if status == -1:
            raise FieldWriteFailed(
                f"unable to write field {field_name} to grid {self.grid_name} ({self._gid}) in file {self.filename} ({self._fid})")

    def write_uint16(self, field_name: str, image: Union[Raster, np.ndarray]):
        status = write_grid_field_uint16(
            gdid=self._gid,
            image=image,
            field_name=field_name
        )

        if status == -1:
            raise FieldWriteFailed(
                f"unable to write field {field_name} to grid {self.grid_name} ({self._gid}) in file {self.filename} ({self._fid})")

    @property
    def _grid_boundaries(self):
        return HE5PY_CPP.read_grid(self._gid)

    def read_float(self, field_name: str) -> Raster:
        # print(f"reading field {field_name} to grid {self.grid_name} ({self._gid}) in file {self.filename} ({self._fid})")
        rows, cols = self.geometry.shape
        array = np.full((rows, cols), np.nan, dtype=np.float32)

        status = HE5PY_CPP.read_grid_field_float(
            self._gid,
            array,
            field_name
        )

        if status == -1:
            raise FieldReadFailed(
                f"unable to read field {field_name} from grid {self.grid_name} ({self._gid}) in file {self.filename} ({self._fid})")

        image = Raster(array, geometry=self.geometry)

        return image

    def close(self):
        # print(f"closing grid: {self.filename} gid: {self._gid}")
        HE5_GDdetach(self._gid)

    def __exit__(self, type, value, traceback):
        self.close()


class File:
    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode
        # print(f"opening file: {self.filename} mode: {self.mode}")

        if mode == "w-" or mode == "x":
            flags = H5F_ACC_EXCL
        elif mode == "w":
            flags = H5F_ACC_TRUNC
        elif mode == "r":
            flags = H5F_ACC_RDONLY
        elif mode == "r+" or mode == "rw":
            flags = H5F_ACC_RDWR
        else:
            raise ValueError(f"unsupported file mode: {mode}")

        self._fid = HE5_GDopen(filename, Flags=flags)

        if self._fid == -1:
            raise FileOpenFailed()

        self._open_grids = []

    def __repr__(self) -> str:
        return f'File(filename="{self.filename},mode={self.mode}")'

    def __enter__(self):
        return self

    @property
    def open_grids(self) -> List[Grid]:
        return self._open_grids

    def create_grid(
            self,
            grid_name: str,
            geometry: RasterGrid) -> Grid:

        grid = Grid.create(
            filename=self.filename,
            fid=self._fid,
            grid_name=grid_name,
            geometry=geometry
        )

        self.open_grids.append(grid)

        return grid

    def attach_grid(self, grid_name: str) -> Grid:
        grid = Grid.attach(
            filename=self.filename,
            fid=self._fid,
            grid_name=grid_name
        )

        self.open_grids.append(grid)

        return grid

    def close(self):
        # print(f"closing file: {self.filename} fid: {self._fid}")
        HE5_GDclose(self._fid)

    def __exit__(self, type, value, traceback):
        for open_grid in self.open_grids:
            # print("closing open grid:")
            # print(open_grid)
            open_grid.close()

        self.close()
