# Findpybind11.cmake
find_path(PYBIND11_INCLUDE_DIR NAMES pybind11/pybind11.h
          HINTS 
            ${CONDA_PREFIX}/include
          PATH_SUFFIXES pybind11)

find_package_handle_standard_args(pybind11  DEFAULT_MSG  PYBIND11_INCLUDE_DIR)

if(NOT PYBIND11_FOUND)
    message(FATAL_ERROR "pybind11 not found in current conda environment")
endif()

mark_as_advanced(PYBIND11_INCLUDE_DIR)
