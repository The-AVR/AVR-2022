cmake_minimum_required (VERSION 2.8.11)
project (avrapriltags)

set(CMAKE_CXX_STANDARD 11)

set (THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

add_subdirectory(./libraries/json)

include_directories("/usr/include/opencv4/")
include_directories("/usr/local/cuda-10.2/include")
include_directories("/opt/nvidia/vpi1/include")
include_directories("../libraries/json/include")

link_directories("./libraries/lib_aarch64_jetpack44")
link_directories("/usr/local/cuda-10.2/lib64")
link_directories("/opt/nvidia/vpi1/lib64")

link_libraries(april_tagging cudart cuda cublas opencv_core opencv_videoio opencv_imgproc opencv_highgui nvvpi paho-mqttpp3 paho-mqtt3as)

set(SOURCE_FILES src/avrapriltags.cpp src/apriltags.cpp src/undistort.cpp src/cam_properties.cpp)

add_executable (avrapriltags ${SOURCE_FILES})
target_link_libraries(avrapriltags PRIVATE nlohmann_json::nlohmann_json)
# target_link_libraries(avrapriltags paho-mqttpp3)