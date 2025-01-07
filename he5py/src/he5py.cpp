#include "../include/he5py.hpp"

using namespace std;
using namespace he5py;

namespace py = pybind11;

namespace he5py
{
    /* Write a local attribute. See HDF-EOS5 testdrivers/grid/TestGrid.c.  */
    herr_t write_attr(hid_t gdid, char* field_name, char* attr_name, char* value)
    {
        hsize_t count[1];
        count[0] = strlen(value);
        return HE5_GDwritelocattr(gdid, field_name, attr_name, H5T_NATIVE_CHAR,
                                  count, value);


    }

    template<class T> herr_t write_grid_field(hid_t gdid, xt::pyarray<T> &image, string field_name, hid_t H5Type)
    {
        herr_t status;
        auto shape = image.shape();
        int rows = shape[0];
        int cols = shape[1];

        hsize_t edge[2];
        hssize_t start[2];
        start[0] = 0;
        start[1] = 0;
        edge[0] = rows; /* latitude-ydim first */
        edge[1] = cols;

        /* Create a field. */
        // set compression
        int compparm[1];
        compparm[0] = 9;
        int tilerank = 2;
        hsize_t tiledims[2];
        tiledims[0] = rows;
        tiledims[1] = cols;
//        status = HE5_GDdefcomp(gdid, HE5_HDFE_COMP_DEFLATE, compparm);
//        cout << "HE5_GDdefcomtile" << endl;
        status = HE5_GDdefcomtile(gdid, HE5_HDFE_COMP_DEFLATE, compparm, tilerank, tiledims);
//        cout << "status: " << status << endl;
//        cout << "HE5_GDdeffield" << endl;
        status = HE5_GDdeffield(gdid, field_name.c_str(), (char *)"YDim,XDim", NULL, H5Type, HE5_HDFE_NOMERGE);
//        cout << "status: " << status << endl;
//        cout << "HE5_GDwritefield" << endl;
//        status = HE5_GDwritefield(gdid, field_name.c_str(), start, NULL, edge, buffer);
        status = HE5_GDwritefield(gdid, field_name.c_str(), start, NULL, edge, image.data());
//        cout << "status: " << status << endl;

        return status;
    }

    hid_t create_grid_latlon(hid_t gdfid, string grid_name, float ul_lon, float ul_lat, float lr_lon, float lr_lat, int rows, int cols)
    {
        double upleft[2];
        double lowright[2];
        herr_t status = FAIL;
        hid_t gdid = FAIL;
        int dummy = 0;

        /* Set corner points. */
        upleft[0] = HE5_EHconvAng(ul_lon,  HE5_HDFE_DEG_DMS); /* left */
        upleft[1]  = HE5_EHconvAng(ul_lat, HE5_HDFE_DEG_DMS); /* up */

        lowright[0] = HE5_EHconvAng(lr_lon, HE5_HDFE_DEG_DMS); /* right */
        lowright[1] = HE5_EHconvAng(lr_lat, HE5_HDFE_DEG_DMS);          /* low */

        /* Create Grids. */
        gdid  = HE5_GDcreate(gdfid, grid_name.c_str(), cols, rows, upleft, lowright);

        /* Set projection. */
        status = HE5_GDdefproj(gdid, HE5_GCTP_GEO, dummy, dummy, NULL);

//        // set compression
//        int compparm[1];
//        compparm[0] = 9;
//        int tilerank = 1;
//        hsize_t tiledims[2];
//        tiledims[0] = rows;
//        tiledims[1] = cols;
////        status = HE5_GDdefcomp(gdid, HE5_HDFE_COMP_DEFLATE, compparm);
//        HE5_GDdefcomtile(gdid, HE5_HDFE_COMP_DEFLATE, compparm, tilerank, tiledims);

        return gdid;
    }

    herr_t write_grid_field_float(hid_t gdid, xt::pyarray<float> &image, string field_name)
    {
        return he5py::write_grid_field<float>(gdid, image, field_name, H5T_NATIVE_FLOAT);
    }

    herr_t write_grid_field_uint8(hid_t gdid, xt::pyarray<unsigned char> &image, string field_name)
    {
        return he5py::write_grid_field<unsigned char>(gdid, image, field_name, H5T_NATIVE_UCHAR);
    }

    herr_t write_grid_field_uint16(hid_t gdid, xt::pyarray<unsigned char> &image, string field_name)
    {
        return he5py::write_grid_field<unsigned char>(gdid, image, field_name, H5T_NATIVE_USHORT);
    }

    template<class T> herr_t read_grid_field(hid_t gdid, xt::pyarray<T> &image, string field_name)
    {
        auto shape = image.shape();
        unsigned long rows = shape[0];
        unsigned long cols = shape[1];
        hssize_t start[2] ={0, 0};
        hsize_t edge[2] = {rows, cols};
        T buffer[rows][cols];
        herr_t status;

//        herr_t status = HE5_GDreadfield(gdid, field_name, start, NULL, edge, buffer);
        status = HE5_GDreadfield(gdid, field_name.c_str(), start, NULL, edge, buffer);

        for (int row = 0; row < rows; row++)
        {
            for (int col = 0; col < cols; col++)
            {
                T value = buffer[row][col];
//                cout << "row: " << row << " col: " << col << " value: " << value << endl;
                image(row, col) = value;
            }
        }

        return status;
    }

    herr_t read_grid_field_float(hid_t gdid, xt::pyarray<float> &image, string field_name)
    {
        return he5py::read_grid_field<float>(gdid, image, field_name);
    }

    GridBoundaries test_struct()
    {
        GridBoundaries grid_boundaries = {
            12,
            6,
            -180,
            90,
            180,
            -90
        };

        return grid_boundaries;
    }

    GridBoundaries read_grid(hid_t gdid)
    {
        long xdim;
        long ydim;
        double upleft[2];
        double ul_x;
        double ul_y;
        double lowright[2];
        double lr_x;
        double lr_y;
        herr_t status;

        status = HE5_GDgridinfo(gdid, &xdim, &ydim, upleft, lowright);
        ul_x = HE5_EHconvAng(upleft[0],  HE5_HDFE_DMS_DEG);
        ul_y = HE5_EHconvAng(upleft[1],  HE5_HDFE_DMS_DEG);
        lr_x = HE5_EHconvAng(lowright[0],  HE5_HDFE_DMS_DEG);
        lr_y = HE5_EHconvAng(lowright[1],  HE5_HDFE_DMS_DEG);

        GridBoundaries grid_boundaries = {
            xdim,
            ydim,
            ul_x,
            ul_y,
            lr_x,
            lr_y
        };

        return grid_boundaries;
    }
}

// Python Module and Docstrings

PYBIND11_MODULE(HE5PY_CPP, m)
{
    xt::import_numpy();

    m.doc() = R"pbdoc(
        xtensor numpy experiment

        .. currentmodule:: he5py

        .. autosummary::
           :toctree: _generate

           test_xt_element
           test_xt_transform
           readme_test_xt_element
           vectorize_test_xt_element
    )pbdoc";

    m.def("create_grid_latlon", create_grid_latlon, "create HDF-EOS5 geographic grid");
    m.def("write_grid_field_float", write_grid_field_float, "write HDF-EOS5 float grid field");
    m.def("write_grid_field_uint8", write_grid_field_uint8, "write HDF-EOS5 uint8 grid field");
    m.def("write_grid_field_uint16", write_grid_field_uint16, "write HDF-EOS5 uint16 grid field");
    m.def("read_grid_field_float", read_grid_field_float, "read HDF-EOS5 float grid field");
    m.def("read_grid", read_grid, "read HDF-EOS5 grid dimensions and corners");

    m.attr("H5F_ACC_EXCL") = H5F_ACC_EXCL;
    m.attr("H5F_ACC_TRUNC") = H5F_ACC_TRUNC;
    m.attr("H5F_ACC_RDONLY") = H5F_ACC_RDONLY;
    m.attr("H5F_ACC_RDWR") = H5F_ACC_RDWR;

    m.attr("H5T_NATIVE_FLOAT") = H5T_NATIVE_FLOAT;
    m.attr("H5T_IEEE_F32LE") = H5T_IEEE_F32LE;

    m.def("HE5_GDopen", HE5_GDopen, "HDF-EOS5 file open");
    m.def("HE5_GDattach", HE5_GDattach, "HDF-EOS5 attach grid");
    m.def("HE5_EHconvAng", HE5_EHconvAng, "HDF-EOS5 angle conversion");
    m.def("HE5_GDcreate", HE5_GDcreate, "HDF-EOS5 grid creation");
    m.def("HE5_GDdefproj", HE5_GDdefproj, "HDF-EOS5 projection definition");
    m.def("HE5_GDdeffield", HE5_GDdeffield, "HDF-EOS5 field definition");
    m.def("HE5_GDwritefield", HE5_GDwritefield, "HDF-EOS5 write field");
    m.def("HE5_GDreadfield", HE5_GDreadfield, "HDF-EOS5 read field");
    m.def("HE5_GDdetach", HE5_GDdetach, "HDF-EOS5 detach grid");
    m.def("HE5_GDclose", HE5_GDclose, "HDF-EOS5 file close");

    m.def("test_struct", test_struct, "testing struct passing");

    py::class_<GridBoundaries>(m, "GridBoundaries")
        .def_readwrite("xdim", &GridBoundaries::xdim)
        .def_readwrite("ydim", &GridBoundaries::ydim)
        .def_readwrite("ul_x", &GridBoundaries::ul_x)
        .def_readwrite("ul_y", &GridBoundaries::ul_y)
        .def_readwrite("lr_x", &GridBoundaries::lr_x)
        .def_readwrite("lr_y", &GridBoundaries::lr_y);
}
