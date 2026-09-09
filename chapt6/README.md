# 第 6 章：机器人建模、仿真与 ros2_control

本章用 URDF/Xacro 描述 FishBot，在 RViz 中显示，并在 Gazebo 中仿真差速控制。

## 环境要求

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

sudo apt install \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-ros2-controllers \
  ros-humble-controller-manager \
  ros-humble-diff-drive-controller \
  ros-humble-joint-state-broadcaster \
  ros-humble-teleop-twist-keyboard
```

## 目录说明

```
chapt6/chapt6_ws/src/fishbot_description/
├── urdf/                 # first_robot、fishbot 模块化 xacro
├── config/               # ros2_control 控制器配置
├── world/                # Gazebo 房间世界
└── launch/
    ├── display_robot.launch.py   # RViz 显示
    └── gazebo_sim.launch.py      # Gazebo 仿真
```

## 编译

```bash
cd /home/lyzn-robot/ros2bookcode/chapt6/chapt6_ws
colcon build
source install/setup.bash
```

## 在 RViz 中显示模型

```bash
ros2 launch fishbot_description display_robot.launch.py \
  model:=$(ros2 pkg prefix fishbot_description)/share/fishbot_description/urdf/fishbot/fishbot.urdf.xacro
```

也可使用包内更简单的 `first_robot.urdf` / `.xacro` 做入门练习。

## 启动 Gazebo 仿真

```bash
ros2 launch fishbot_description gazebo_sim.launch.py
```

启动流程概要：

1. `robot_state_publisher` 发布机器人描述与 TF
2. 加载 `custom_room.world`
3. `spawn_entity` 生成机器人
4. 加载 `joint_state_broadcaster` 与 `fishbot_diff_drive_controller`

## 键盘遥控

仿真起来后：

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r /cmd_vel:=/diff_drive_controller/cmd_vel_unstamped
```

若重映射无效，先用下面命令确认实际 cmd_vel 话题名后再改 remapping：

```bash
ros2 topic list | grep cmd_vel
```

常见名称也可能是 `/fishbot_diff_drive_controller/cmd_vel_unstamped`。

## 控制器说明

配置见 `config/fishbot_ros2_controller.yaml`：

- `fishbot_joint_state_broadcaster`：关节状态
- `fishbot_diff_drive_controller`：差速驱动，发布里程计，广播 `odom` → `base_footprint`

## 要点

1. URDF/Xacro 描述连杆、关节与传感器。
2. Gazebo + 插件实现物理仿真与传感器数据。
3. `ros2_control` 把仿真/真机控制接口统一起来。
