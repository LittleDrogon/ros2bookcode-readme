# Example 14：无状态反馈执行器 + 位置传感器（`ros2_control_demo_example_14`）

模块化机器人：执行器（`ActuatorInterface`）**只接收速度命令、不提供状态**；位置由独立的传感器组件（`SensorInterface`）提供。共四个硬件组件（两执行器 + 两传感器）。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_14/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_14` |

**注意：** apt 中**没有** `ros-humble-ros2-control-demos` 元包，必须从本仓库源码编译。

---

## 前置条件

```bash
sudo apt update
sudo apt install -y \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-xacro \
  ros-humble-rviz2 \
  python3-colcon-common-extensions
```

仓库在 `humble` 分支；不要与其他 demo 同时运行。

---

## 编译

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_14
source install/setup.bash
```

```bash
ros2 pkg prefix ros2_control_demo_example_14
```

---

## 运行

### 1.（可选）仅查看模型

```bash
ros2 launch ros2_control_demo_example_14 view_robot.launch.py
```

### 2. 启动 Example 14（主流程）

```bash
ros2 launch ros2_control_demo_example_14 \
  rrbot_modular_actuators_without_feedback_sensors_for_position_feedback.launch.py
```

可选参数：

- `gui:=true|false`
- `slowdown:=50.0`
- `robot_controller:=forward_velocity_controller`（默认）
- `prefix:=...`

默认激活：

- `joint_state_broadcaster`
- `forward_velocity_controller`

### 3. 检查

```bash
ros2 control list_hardware_interfaces
ros2 control list_hardware_components
ros2 control list_controllers
```

应看到执行器侧主要为 velocity **command**，位置 **state** 来自传感器组件。

### 4. 发送速度命令

本示例默认是 **速度** forward 控制器（不是位置）：

```bash
ros2 topic pub /forward_velocity_controller/commands std_msgs/msg/Float64MultiArray "{data: [5.0, 5.0]}"
```

```bash
ros2 topic echo /joint_states
```

无 `test_*_controller.launch.py`；用 CLI 发命令即可。

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF |
| `rrbot_modular_actuators_without_feedback_sensors_for_position_feedback.launch.py` | 完整 Example 14 |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| 包找不到 | source Humble + 工作空间 |
| 发位置话题无反应 | 默认控制器是 **velocity**，话题为 `/forward_velocity_controller/commands` |
| 与其他 demo 冲突 | 关掉旧 `/controller_manager` |

---

## 相关文件

- 执行器：`hardware/rrbot_actuator_without_feedback.cpp`
- 传感器：`hardware/rrbot_sensor_for_position_feedback.cpp`
- 配置：`bringup/config/rrbot_modular_actuators_without_feedback_sensors_for_position_feedback.yaml`
