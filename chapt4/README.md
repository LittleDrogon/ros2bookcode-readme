# 第 4 章：服务、参数与 Launch

本章学习 Service 通信、参数动态配置，以及 Launch 文件一键启动多节点。

## 环境要求

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
sudo apt install ros-humble-turtlesim ros-humble-cv-bridge
```

人脸检测示例额外需要（可选，未安装时仍可跑 turtlesim 巡逻）：

```bash
# face_recognition / dlib 等，按书中或官方文档安装
```

## 目录说明

```
chapt4/chapt4_ws/src/
├── chapt4_interfaces/     # FaceDetector.srv、Patrol.srv
├── demo_cpp_service/      # 海龟巡逻服务端/客户端 + launch
└── demo_python_service/   # 人脸检测服务端/客户端 + launch
```

## 编译

```bash
cd /home/lyzn-robot/ros2bookcode/chapt4/chapt4_ws
colcon build
source install/setup.bash
```

## 运行：海龟巡逻（推荐先跑通）

一键启动：

```bash
ros2 launch demo_cpp_service demo.launch.py launch_max_speed:=2.0
```

或分终端：

```bash
ros2 run turtlesim turtlesim_node
ros2 run demo_cpp_service turtle_control --ros-args -p max_speed:=2.0
ros2 run demo_cpp_service patrol_client
```

说明：

- 服务 `patrol`：请求目标坐标 `target_x/y`，返回成功/失败
- 参数 `k`、`max_speed`：控制增益与限速
- 客户端周期性请求随机目标，并可通过 `set_parameters` 改参数

手动调用服务示例：

```bash
ros2 service call /patrol chapt4_interfaces/srv/Patrol "{target_x: 5.0, target_y: 5.0}"
```

## 运行：人脸检测服务（可选）

```bash
ros2 run demo_python_service face_detect_node
ros2 run demo_python_service face_detect_client_node
# 或先体验非服务版本：
ros2 run demo_python_service learn_face_detect
```

| 节点 | 接口 |
|------|------|
| `face_detect_node` | 服务 `/face_detect`，参数模型/上采样次数 |
| `face_detect_client_node` | 客户端，可动态改参数 |

也可：

```bash
ros2 launch demo_python_service demo.launch.py
```

## 接口一览

- `chapt4_interfaces/srv/Patrol`
- `chapt4_interfaces/srv/FaceDetector`（请求含 `sensor_msgs/Image`）

## 要点

1. Service 是一对一、请求-响应同步通信。
2. 参数可用 `--ros-args -p` 或运行时 `set_parameters` 修改。
3. Launch 适合把 turtlesim、控制节点、客户端编成一组启动。
