# Copyright (c) Orbbec Inc. All Rights Reserved.
# Licensed under the MIT License.

cmake_minimum_required(VERSION 3.10)
project(ob_open3d)

find_package(Open3D REQUIRED)

add_executable(${PROJECT_NAME} open3d.cpp)

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)

# Prefer conda Open3D runtime libs (libstdc++/tbb/fmt) over older system copies.
if(DEFINED ENV{CONDA_PREFIX})
    set(_CONDA_LIB "$ENV{CONDA_PREFIX}/lib")
    target_link_directories(${PROJECT_NAME} PRIVATE "${_CONDA_LIB}")
    # Force conda TBB at the end of the link line (system libtbb lacks symbols embree needs).
    if(EXISTS "${_CONDA_LIB}/libtbb.so")
        set(_CONDA_TBB "${_CONDA_LIB}/libtbb.so")
    else()
        file(GLOB _CONDA_TBB "${_CONDA_LIB}/libtbb.so.*")
        list(GET _CONDA_TBB 0 _CONDA_TBB)
    endif()
endif()

target_link_libraries(${PROJECT_NAME} ob::${OB_SDK_LIB_NAME} ob::examples::utils Open3D::Open3D)
if(_CONDA_TBB)
    target_link_libraries(${PROJECT_NAME} "${_CONDA_TBB}" fmt)
    # Ensure linker searches conda first when resolving embree's TBB refs.
    target_link_options(${PROJECT_NAME} PRIVATE "LINKER:-rpath,${_CONDA_LIB}")
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES FOLDER "examples")
if(MSVC)
    set_target_properties(${PROJECT_NAME} PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
endif()

install(TARGETS ${PROJECT_NAME} RUNTIME DESTINATION bin)
