# 第 1 章：环境准备与 Hello World

本章对应《ROS 2 机器人开发：从入门到实践》入门准备，用最简单的 C++ / Python 程序和 CMake 熟悉编译流程。**本章不涉及 ROS 2 节点。**

## 环境要求

- Ubuntu 22.04
- `cmake`、`g++`、`python3`

## 目录说明

```
chapt1/
├── hello_world.cpp   # C++ Hello World
├── hello_world.py    # Python Hello World
└── CMakeLists.txt    # 生成可执行文件 learn_cmake
```

## 运行 Python 示例

```bash
cd /home/lyzn-robot/ros2bookcode/chapt1
python3 hello_world.py
```

期望输出：

```
Hello World !
```

## 编译并运行 C++ 示例

```bash
cd /home/lyzn-robot/ros2bookcode/chapt1
cmake .
make
./learn_cmake
```

期望输出：

```
Hello World !
```

`CMakeLists.txt` 核心内容：

- `project(HelloWorld)`：工程名
- `add_executable(learn_cmake hello_world.cpp)`：用 `hello_world.cpp` 生成可执行文件 `learn_cmake`

## 要点

1. 先能独立编译/运行 C++ 与 Python，再进入 ROS 2。
2. CMake 是后续 `ament_cmake` 功能包的基础。
