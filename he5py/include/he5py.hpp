#include <HE5_HdfEosDef.h>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <xtensor/xmath.hpp>
#include <xtensor/xarray.hpp>
#include <xtensor/xadapt.hpp>
#include <xtensor/xcsv.hpp>

#define FORCE_IMPORT_ARRAY
#include <xtensor-python/pyarray.hpp>
#include <xtensor-python/pyvectorize.hpp>

#include <iostream>
#include <fstream>
#include <numeric>
#include <cmath>

#ifndef HE5PY_H
#define HE5PY_H

using namespace std;

namespace py = pybind11;

namespace he5py
{
    hid_t create_grid_latlon(hid_t gdfid, string grid_name, float ul_lon, float ul_lat, float lr_lon, float lr_lat, int rows, int cols);

    template<class T> herr_t write_grid_field(hid_t gdid, xt::pyarray<T> &image, string field_name, hid_t H5Type);

    herr_t write_grid_field_float(hid_t gdid, xt::pyarray<float> &image, string field_name);

    herr_t write_grid_field_uint8(hid_t gdid, xt::pyarray<unsigned char> &image, string field_name);

    herr_t write_grid_field_uint16(hid_t gdid, xt::pyarray<unsigned char> &image, string field_name);

//    template<class T> xt::xarray<T> read_grid_field(hid_t gdid, string field_name, int rows, int cols);
    template<class T> herr_t read_grid_field(hid_t gdid, xt::pyarray<T> &image, string field_name);

//    xt::xarray<float> read_grid_field_float(hid_t gdid, string field_name, int rows, int cols);

    herr_t read_grid_field_float(hid_t gdid, xt::pyarray<float> &image, string field_name);

    herr_t write_attr(hid_t gdid, char* field_name, char* attr_name, char* value);

    struct GridBoundaries
    {
        long xdim;
        long ydim;
        double ul_x;
        double ul_y;
        double lr_x;
        double lr_y;
    };

    GridBoundaries test_struct();

    GridBoundaries read_grid(hid_t gdid);
}

#endif
