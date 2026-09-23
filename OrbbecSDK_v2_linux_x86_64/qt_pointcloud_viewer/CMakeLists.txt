cmake_minimum_required(VERSION 3.14)
project(qt_pointcloud_viewer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

set(ORBBEC_SDK_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." CACHE PATH "Orbbec SDK root")
set(OrbbecSDK_DIR "${ORBBEC_SDK_ROOT}/lib")
find_package(OrbbecSDK REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Widgets OpenGL)

set(SOURCES
    src/main.cpp
    src/PointCloudData.cpp
    src/OrbbecCamera.cpp
    src/PointCloudGLWidget.cpp
    src/MainWindow.cpp
)

set(HEADERS
    src/PointCloudData.h
    src/OrbbecCamera.h
    src/PointCloudGLWidget.h
    src/MainWindow.h
)

add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${ORBBEC_SDK_ROOT}/include
)

target_link_libraries(${PROJECT_NAME} PRIVATE
    ob::OrbbecSDK
    Qt5::Widgets
    Qt5::OpenGL
    GL
)

set_target_properties(${PROJECT_NAME} PROPERTIES
    BUILD_RPATH "$ORIGIN/../../lib"
    INSTALL_RPATH "$ORIGIN/../lib"
)

install(TARGETS ${PROJECT_NAME} RUNTIME DESTINATION bin)

message(STATUS "Orbbec SDK: ${ORBBEC_SDK_ROOT}")
message(STATUS "Build: ${CMAKE_BINARY_DIR}/${PROJECT_NAME}")
