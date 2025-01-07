cmake_minimum_required(VERSION 3.18)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake/;${CMAKE_MODULE_PATH}")
message("CMAKE_MODULE_PATH: ${CMAKE_MODULE_PATH}")

message("CONDA_PREFIX: $ENV{CONDA_PREFIX}")

# check for conda environment
if(DEFINED ENV{CONDA_PREFIX})
    set(CMAKE_PREFIX_PATH $ENV{CONDA_PREFIX})
endif()

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS "-O3")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

message("CMAKE_PREFIX_PATH: ${CMAKE_PREFIX_PATH}")

find_package(HDF5 REQUIRED COMPONENTS C HL)
message("HDF5_INCLUDE_DIRS: ${HDF5_INCLUDE_DIRS}")
message("HDF5_C_LIBRARIES: ${HDF5_C_LIBRARIES}")
message("HDF5_C_HL_LIBRARIES: ${HDF5_C_HL_LIBRARIES}")
include_directories(${HDF5_INCLUDE_DIRS})

set(HDFEOS5_INCLUDE_DIRS ${CMAKE_PREFIX_PATH}/include)
set(HDFEOS5_C_LIBRARIES ${CMAKE_PREFIX_PATH}/lib/libhe5_hdfeos.a;${CMAKE_PREFIX_PATH}/lib/libGctp.a)

# find_package(HDFEOS5 REQUIRED)
# set(HDFEOS5_INCLUDE_DIRS "${CMAKE_PREFIX_PATH}/include")
# set(HDFEOS5_C_LIBRARIES "${CMAKE_PREFIX_PATH}/lib/libhe5_hdfeos.a;${CMAKE_PREFIX_PATH}/lib/libGctp.a")
message("HDFEOS5_INCLUDE_DIRS: ${HDFEOS5_INCLUDE_DIRS}")
message("HDFEOS5_C_LIBRARIES: ${HDFEOS5_C_LIBRARIES}")
include_directories(${HDFEOS5_INCLUDE_DIRS})

find_package(ZLIB REQUIRED)
message("ZLIB_INCLUDE_DIRS: ${ZLIB_INCLUDE_DIRS}")
message("ZLIB_LIBRARIES: ${ZLIB_LIBRARIES}")
include_directories(${ZLIB_INCLUDE_DIRS})

# # Pybind11
# find_package(pybind11 REQUIRED)
# add_subdirectory(pybind11)

# find_package(Python3 REQUIRED)
# message("Python3_INCLUDE_DIRS: ${Python3_INCLUDE_DIRS}")
include_directories(${Python3_INCLUDE_DIRS})

find_package(NumPy REQUIRED)
message("PYTHON_NUMPY_INCLUDE_DIR: ${PYTHON_NUMPY_INCLUDE_DIR}")
include_directories(${PYTHON_NUMPY_INCLUDE_DIR})

# add_executable(grid_1_2d grid_1_2d.c)
# target_include_directories(grid_1_2d PRIVATE ${HDF5_INCLUDE_DIRS} ${ZLIB_INCLUDE_DIRS} ${HDFEOS5_INCLUDE_DIRS})
# target_link_libraries(grid_1_2d PRIVATE ${HDF5_C_LIBRARIES} ${HDF5_C_HL_LIBRARIES} ${ZLIB_LIBRARIES} ${HDFEOS5_C_LIBRARIES})

include_directories(/usr/local/include)
include_directories("${CMAKE_SOURCE_DIR}/include")
include_directories("${CMAKE_SOURCE_DIR}/src")

file (GLOB SOURCE_FILES "*.cpp" "*.c")
file (GLOB PYTHON_FILES "*.cpp" "*.hpp")

# Set up such that XCode organizes the files
source_group(TREE ${CMAKE_CURRENT_SOURCE_DIR} FILES ${SOURCE_FILES} ${HEADER_FILES} ${PYTHON_FILES} )

include_directories("../include")
include_directories(".")
file (GLOB HEADER_FILES "../include/*.hpp" "../include/*.h")

pybind11_add_module(HE5PY_CPP
	${SOURCE_FILES}
	${HEADER_FILES}
	${PYTHON_FILES}
)

target_link_libraries(HE5PY_CPP PUBLIC ${HDF5_C_LIBRARIES} ${HDF5_C_HL_LIBRARIES} ${ZLIB_LIBRARIES} ${HDFEOS5_C_LIBRARIES})

message("CMAKE_LIBRARY_OUTPUT_DIRECTORY: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
message("CMAKE_INSTALL_LIBDIR: ${CMAKE_INSTALL_LIBDIR}")

install(TARGETS HE5PY_CPP
  COMPONENT python
  LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  )

