cmake_minimum_required(VERSION 3.16)
project(qt_face_register LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets SerialPort)

add_executable(qt_face_register
  src/main.cpp
  src/mainwindow.h
  src/mainwindow.cpp
)

target_link_libraries(qt_face_register PRIVATE Qt6::Widgets Qt6::SerialPort)
