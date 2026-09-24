# Example 8：RRBot + Transmission（`ros2_control_demo_example_8`）

演示带 **transmission（传动）接口** 的 RRBot：关节空间与执行器空间通过传动比映射（日志中可见不同减速比）。适合理解 `transmission_interface` 与位置-only 系统。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_8/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_8` |

**注意：** apt 中**没有** `ros-humble-ros2-control-demos` 元包，必须从本仓库源码编译。

---

## 前置条件

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

仓库在 `humble` 分支；不要与其他 demo 同时运行。

---

## 编译

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_8
source install/setup.bash
```

```bash
ros2 pkg prefix ros2_control_demo_example_8
```

---

## 运行

### 1.（可选）仅查看模型

```bash
ros2 launch ros2_control_demo_example_8 view_robot.launch.py
```

### 2. 启动 Example 8（主流程）

```bash
ros2 launch ros2_control_demo_example_8 rrbot_transmissions_system_position_only.launch.py
```

可选参数：`gui:=true|false`、`slowdown:=50.0`、`robot_controller:=forward_position_controller`（默认）、`prefix:=...`  
（本 launch **无** `use_mock_hardware` 参数。）

默认激活：

- `joint_state_broadcaster`
- `forward_position_controller`

启动终端里可观察传动映射相关日志（关节命令与执行器侧数值不同）。

### 3. 检查

```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
```

### 4. 发送位置命令

```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.5, 0.5]}"
```

或循环：

```bash
ros2 launch ros2_control_demo_example_8 test_forward_position_controller.launch.py
```

```bash
ros2 topic echo /joint_states
```

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF |
| `rrbot_transmissions_system_position_only.launch.py` | 完整 Example 8 |
| `test_forward_position_controller.launch.py` | 循环发位置目标 |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| 包找不到 | source Humble + 工作空间 |
| apt 无 demos 元包 | 本仓库 `colcon` 编译 |
| PATH 异常 | `export PATH="/usr/bin:$PATH"` |
| 与其他 demo 冲突 | 关掉旧 `/controller_manager` |

---

## 相关文件

- 硬件：`hardware/rrbot_transmissions_system_position_only.cpp`
- 控制器配置：`bringup/config/rrbot_controllers.yaml`
- 位置发布器：`bringup/config/rrbot_forward_position_publisher.yaml`
