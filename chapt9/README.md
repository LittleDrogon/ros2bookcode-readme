# 第 9 章：真机 Bringup（FishBot）

本章把仿真栈迁移到真实 FishBot：里程计转 TF、micro-ROS、激光雷达与导航。

> 真机部分依赖外部硬件与未收录在本仓库的包（`micro_ros_agent`、`ydlidar`、`ros_serial2wifi`）。无真机时仍可编译本仓库代码，并单独验证 `odom2tf` / URDF 相关节点。

## 环境要求

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

sudo apt install \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-nav2-bringup \
  ros-humble-tf2-ros
```

另需按书中/厂商文档安装：

- `micro_ros_agent`（UDP 8888）
- `ydlidar`（`ydlidar_launch.py`）
- `ros_serial2wifi`（串口/WiFi 桥接）

## 目录说明

```
chapt9/fishbot_ws/src/
├── fishbot_description/    # 真机简化 URDF
├── fishbot_bringup/        # odom2tf、bringup / urdf2tf launch
└── fishbot_navigation2/    # 真机地图与导航配置
```

## 编译

```bash
cd /home/lyzn-robot/ros2bookcode/chapt9/fishbot_ws
colcon build
source install/setup.bash
```

## 启动真机驱动栈

```bash
ros2 launch fishbot_bringup bringup.launch.py
```

`bringup.launch.py` 会启动：

1. `urdf2tf`：机器人模型 TF
2. `odom2tf`：订阅 `odom`，广播里程计 TF（SensorData QoS）
3. `micro_ros_agent`：`udp4 --port 8888`
4. `ros_serial2wifi`：`tcp_server`，串口 `/tmp/tty_laser`
5. 延时约 5 秒后启动 `ydlidar`

仅测 URDF TF：

```bash
ros2 launch fishbot_bringup urdf2tf.launch.py
```

## 真机导航

```bash
ros2 launch fishbot_navigation2 navigation2.launch.py use_sim_time:=false
```

注意：默认 launch 可能仍带仿真时间参数，真机务必显式关闭 `use_sim_time`。

## 修复说明

本仓库已修正 `bringup.launch.py` 中变量名笔误：`ros_serail2wifi` → `ros_serial2wifi`，否则 Launch 会因未定义名称失败。

## 要点

1. 真机与仿真的差异主要在驱动层；上层 Nav2/应用可复用。
2. micro-ROS 适合 MCU 侧发布里程计等数据。
3. `odom` → TF 是导航定位链路的关键一环。
