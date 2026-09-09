# 第 2 章：第一个 ROS 2 节点与现代 C++ / 多线程基础

本章学习创建 ROS 2 节点，以及 C++ 新特性、面向对象与多线程基础。

## 环境要求

- Ubuntu 22.04 + ROS 2 Humble
- 若系统装了 conda，请优先使用系统 Python 3.10，避免与 Humble 的 `rclpy` 冲突：

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
```

## 目录说明

```
chapt2/
├── ros2_cpp_node.cpp / ros2_python_node.py   # 工作空间外的独立示例
└── chapt2_ws/src/
    ├── demo_cpp_pkg/      # C++ 节点与现代 C++ 示例
    └── demo_python_pkg/   # Python 节点与多线程示例
```

工作空间根目录下的 `novel1.txt`、`novel2.txt`、`novel3.txt` 供多线程下载示例使用。

## 编译

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
cd /home/lyzn-robot/ros2bookcode/chapt2/chapt2_ws
colcon build
source install/setup.bash
```

## 运行节点

### C++ / Python 基础节点

```bash
ros2 run demo_cpp_pkg cpp_node
ros2 run demo_python_pkg python_node
```

### 面向对象节点（PersonNode）

```bash
ros2 run demo_cpp_pkg person_node
ros2 run demo_python_pkg person_node
ros2 run demo_python_pkg writer_node
```

### 现代 C++ 示例

```bash
ros2 run demo_cpp_pkg learn_auto
ros2 run demo_cpp_pkg learn_shared_ptr
ros2 run demo_cpp_pkg learn_lambda
ros2 run demo_cpp_pkg learn_function
```

### 多线程下载小说（需本地 HTTP 服务）

在**另一个终端**启动静态文件服务（工作目录需能访问 novel 文本）：

```bash
cd /home/lyzn-robot/ros2bookcode/chapt2/chapt2_ws
python3 -m http.server 8000
```

然后运行：

```bash
source /opt/ros/humble/setup.bash
source /home/lyzn-robot/ros2bookcode/chapt2/chapt2_ws/install/setup.bash
ros2 run demo_cpp_pkg learn_thread
ros2 run demo_python_pkg learn_thread
```

Python 版依赖 `requests`（Ubuntu 可用 `sudo apt install python3-requests`）。

## 可执行文件一览

| 包名 | 可执行文件 |
|------|------------|
| `demo_cpp_pkg` | `cpp_node`, `person_node`, `learn_auto`, `learn_shared_ptr`, `learn_lambda`, `learn_function`, `learn_thread` |
| `demo_python_pkg` | `python_node`, `person_node`, `writer_node`, `learn_thread` |

## 要点

1. `rclcpp::Node` / `rclpy.node.Node` 是 ROS 2 程序入口。
2. `spin` 保持节点存活并处理回调。
3. 本章尚无话题/服务，重点是节点生命周期与语言基础。
