cmake_minimum_required(VERSION 3.20)
project(PCDA LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(MPI REQUIRED COMPONENTS CXX)

add_executable(PCDA
    main.cpp
    lab1.h
    lab2_matrix.h
    lab2_matrix.cpp
    lab2.cpp
    lab2.h
    lab3.h
    lab3.cpp
    lab4.h
    lab4.cpp
    lab5.h
    lab5.cpp
    lz4_parallel.h
    lz4_parallel.cpp
    lz4.h
    lz4.c
    compressor.h
    compressor.cpp
)

target_link_libraries(PCDA PRIVATE MPI::MPI_CXX)

set(LZ4_ROOT "" CACHE PATH "Path to LZ4 installation")

find_path(LZ4_INCLUDE_DIR
    NAMES lz4.h
    HINTS "${LZ4_ROOT}/include"
    REQUIRED
)

find_library(LZ4_LIBRARY
    NAMES lz4 liblz4
    HINTS
        "${LZ4_ROOT}/lib"
        "${LZ4_ROOT}/dll"
        "${LZ4_ROOT}/example"
    REQUIRED
)

target_include_directories(PCDA PRIVATE "${LZ4_INCLUDE_DIR}")
target_link_libraries(PCDA PRIVATE "${LZ4_LIBRARY}")