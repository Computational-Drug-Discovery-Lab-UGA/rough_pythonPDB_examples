cmake_minimum_required(VERSION 3.8)
project(PDBClassifier)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES main.cpp)
add_executable(PDBClassifier ${SOURCE_FILES})