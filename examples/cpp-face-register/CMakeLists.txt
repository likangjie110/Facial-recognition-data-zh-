cmake_minimum_required(VERSION 3.16)
project(face_register_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(face_register_demo
  src/main.cpp
  src/face_protocol.cpp
)

target_include_directories(face_register_demo PRIVATE src)
