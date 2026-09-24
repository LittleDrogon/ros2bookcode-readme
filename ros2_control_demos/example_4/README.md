# Example 4：RRBot + 集成力/力矩传感器（`ros2_control_demo_example_4`）

工业风格 *RRBot*：在**同一个** `SystemInterface` 硬件组件里同时提供关节位置接口与集成式 2D 力/力矩传感器（`force.x`、`torque.z`），关节与传感器数据在一次通信中交换。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_4/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_4` |

**注意：** apt 中**没有** `ros-humble-ros2-control-demos` 元包，必须从本仓库源码编译。

---

## 前置条件

1. 已安装 ROS 2 Humble，并能 `source /opt/ros/humble/setup.bash`。
2. 常用依赖：

```bash
sudo apt update
sudo apt install -y \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-ros2-controllers-test-nodes \
  ros-humble-xacro \
  ros-humble-rviz2 \
  python3-colcon-common-extensions
```

3. 仓库在 humble 分支；**不要与其他 demo 同时运行**（共用 `/controller_manager`）。

---

## 编译

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_4
source install/setup.bash
```

```bash
ros2 pkg prefix ros2_control_demo_example_4
```

---

## 运行

### 1.（可选）仅查看模型

```bash
ros2 launch ros2_control_demo_example_4 view_robot.launch.py
```

### 2. 启动 Example 4（主流程）

```bash
ros2 launch ros2_control_demo_example_4 rrbot_system_with_sensor.launch.py
```

可选参数：`gui:=true|false`、`use_mock_hardware:=true`、`mock_sensor_commands:=true`、`slowdown:=50.0`、`prefix:=...`

默认激活的控制器：

- `joint_state_broadcaster`
- `forward_position_controller`
- `fts_broadcaster`（力/力矩）

### 3. 检查

```bash
ros2 control list_hardware_interfaces
ros2 control list_hardware_components -v
ros2 control list_controllers
```

应看到单一硬件组件（含关节 + 传感器接口），三个控制器均为 `active`。

### 4. 控制关节

```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.5, 0.5]}"
```

或：

```bash
ros2 launch ros2_control_demo_example_4 test_forward_position_controller.launch.py
```

目标序列见 `bringup/config/rrbot_forward_position_publisher.yaml`。

### 5. 查看力/力矩

```bash
ros2 topic echo /fts_broadcaster/wrench
```

类型为 `geometry_msgs/msg/WrenchStamped`，`frame_id` 一般为 `tool_link`。若出现 NaN，RViz 里可能显示不佳，以 CLI echo 为准。

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF |
| `rrbot_system_with_sensor.launch.py` | 完整 Example 4 |
| `test_forward_position_controller.launch.py` | 循环发位置目标 |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| 包找不到 | `source` Humble + `demos_ws/install/setup.bash` |
| apt 无 demos 元包 | 用本仓库 `colcon` 编译 |
| PATH / conda 干扰 | `export PATH="/usr/bin:$PATH"` |
| 与其他 demo 冲突 | 关掉占用 `/controller_manager` 的旧进程 |
| wrench 在 RViz 异常 | 可能是 NaN；用 `ros2 topic echo` 查看 |

---

## 相关文件

- 硬件：`hardware/rrbot_system_with_sensor.cpp`
- 控制器配置：`bringup/config/rrbot_with_sensor_controllers.yaml`
- URDF / `ros2_control`：`description/urdf/`、`description/ros2_control/`
