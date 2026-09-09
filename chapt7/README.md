# 第 7 章：建图、导航与自动巡检

本章在仿真中完成 SLAM、Navigation2，以及自动巡检（到点播报 + 拍照）。

## 环境要求

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

sudo apt install \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-ros2-controllers \
  ros-humble-xacro \
  ros-humble-tf-transformations \
  espeak-ng

sudo pip3 install espeakng transforms3d
```

更完整说明见工作空间内 [chapt7_ws/README.md](chapt7_ws/README.md)。

## 功能包

| 包名 | 作用 |
|------|------|
| `fishbot_description` | 仿真模型与 Gazebo launch |
| `fishbot_navigation2` | Nav2 参数、地图、导航 launch |
| `fishbot_application` | Python 导航应用（Simple Commander） |
| `fishbot_application_cpp` | C++ `navigate_to_pose` Action 客户端 |
| `autopatrol_interfaces` | `SpeachText.srv` |
| `autopatrol_robot` | 自动巡检节点与语音 |

## 编译

```bash
cd /home/lyzn-robot/ros2bookcode/chapt7/chapt7_ws
colcon build
source install/setup.bash
```

## 运行仿真 + 导航 + 巡检

终端 1 — 仿真：

```bash
ros2 launch fishbot_description gazebo_sim.launch.py
```

终端 2 — 导航（使用包内已有地图）：

```bash
ros2 launch fishbot_navigation2 navigation2.launch.py
```

终端 3 — 自动巡检：

```bash
ros2 launch autopatrol_robot autopatrol.launch.py
```

初始化位姿（若需要）：

```bash
ros2 run fishbot_application init_robot_pose
```

C++ 导航到点示例：

```bash
ros2 run fishbot_application_cpp nav2pose
```

## 自行建图（可选）

仿真启动后：

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
# 遥控跑完环境后保存地图，放到 fishbot_navigation2/maps/
```

## Python 应用脚本说明

`setup.py` 中已注册入口：`init_robot_pose`。

同目录还有 `nav_to_pose.py`、`waypoint_follower.py`、`get_robot_pose.py`，可用模块方式运行，例如：

```bash
ros2 run fishbot_application init_robot_pose
# 或：
python3 -m fishbot_application.nav_to_pose
```

（需已 `source install/setup.bash`，且仿真 + Nav2 已启动。）

## 巡检逻辑概要

- 按配置在多个目标点循环导航
- 到达后调用 `speech_text` 服务播报
- 订阅摄像头图像并保存到本地

## 要点

1. Nav2 通过 Action（如 `navigate_to_pose`）完成导航请求。
2. 仿真时间需 `use_sim_time:=true` 与 `/clock` 对齐。
3. 应用层把导航、语音、视觉串成业务闭环。
