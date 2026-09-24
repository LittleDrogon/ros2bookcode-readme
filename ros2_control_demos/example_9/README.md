# Example 9：RRBot 仿真 / 硬件切换（`ros2_control_demo_example_9`）

演示同一套 RRBot 描述在 **自定义硬件插件** 与 **Gazebo（`gz_ros2_control`）** 之间切换：控制接口与话题保持一致，便于理解 sim↔real。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_9/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_9` |

**注意：** apt 中**没有** `ros-humble-ros2-control-demos` 元包，必须从本仓库源码编译。

---

## 前置条件

基础依赖：

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

若要跑 Gazebo 版本，还需（包名随 Humble/Gazebo 发行版可能略有差异）：

```bash
sudo apt install -y \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-gz-ros2-control
```

仓库在 `humble` 分支；不要与其他 demo 同时运行。

---

## 编译

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_9
source install/setup.bash
```

若 Gazebo 相关依赖缺失，`rrbot_gazebo.launch.py` 可能无法启动，但 `rrbot.launch.py`（纯硬件插件）通常仍可用。

```bash
ros2 pkg prefix ros2_control_demo_example_9
```

---

## 运行

### 1.（可选）仅查看模型

```bash
ros2 launch ros2_control_demo_example_9 view_robot.launch.py
```

### 2a. 自定义硬件（主流程，无 Gazebo）

```bash
ros2 launch ros2_control_demo_example_9 rrbot.launch.py
```

可选：`gui:=true|false`。

### 2b. Gazebo 仿真

```bash
ros2 launch ros2_control_demo_example_9 rrbot_gazebo.launch.py
```

- `gui:=true`（默认）：Gazebo + RViz
- `gui:=false`：无头 Gazebo

两种启动默认激活：

- `joint_state_broadcaster`
- `forward_position_controller`

### 3. 检查

```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
```

### 4. 发送位置命令（两种启动方式相同）

```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.5, 0.5]}"
```

或：

```bash
ros2 launch ros2_control_demo_example_9 test_forward_position_controller.launch.py
```

反馈：

```bash
ros2 topic echo /joint_states
ros2 topic echo /dynamic_joint_states
```

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF |
| `rrbot.launch.py` | 自定义硬件 + 控制器 + RViz |
| `rrbot_gazebo.launch.py` | Gazebo + `gz_ros2_control` |
| `test_forward_position_controller.launch.py` | 循环发位置目标 |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| 包找不到 | source Humble + 工作空间 |
| Gazebo launch 失败 / 缺包 | 安装 `ros-gz-*`、`gz-ros2-control`；或先用 `rrbot.launch.py` |
| apt 无 demos 元包 | 本仓库 `colcon` 编译 |
| 与其他 demo 冲突 | 关掉旧 `/controller_manager` |

---

## 相关文件

- 硬件：`hardware/rrbot.cpp`
- 控制器配置：`bringup/config/rrbot_controllers.yaml`
- Gazebo launch：`bringup/launch/rrbot_gazebo.launch.py`
