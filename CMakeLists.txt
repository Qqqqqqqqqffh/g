cmake_minimum_required(VERSION 3.14)
project(BenchmarkProject)

set(CMAKE_CXX_STANDARD 17)

# Загрузка библиотеки JSON
include(FetchContent)
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.2
)
FetchContent_MakeAvailable(nlohmann_json)

add_executable(main main.cpp)
target_link_libraries(main PRIVATE nlohmann_json::nlohmann_json)
