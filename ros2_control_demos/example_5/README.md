# Example 5：RRBot + 外部力/力矩传感器（`ros2_control_demo_example_5`）

*RRBot* 关节由一个 `SystemInterface` 驱动，末端 3D 力/力矩传感器由**独立的** `SensorInterface` 提供。与 Example 4 不同：关节与传感器是两个硬件组件，数据交换相互独立。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_5/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_5` |

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

仓库需在 `humble` 分支；不要与其他 demo 同时占用 `/controller_manager`。

---

## 编译

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_5
source install/setup.bash
```

```bash
ros2 pkg prefix ros2_control_demo_example_5
```

---

## 运行

### 1.（可选）仅查看模型

```bash
ros2 launch ros2_control_demo_example_5 view_robot.launch.py
```

### 2. 启动 Example 5（主流程）

```bash
ros2 launch ros2_control_demo_example_5 rrbot_system_with_external_sensor.launch.py
```

可选参数：

- `gui:=true|false`
- `use_mock_hardware:=true`
- `mock_sensor_commands:=true`
- `slowdown:=50.0`
- `use_wrench_transformer:=true`：启动 wrench 坐标变换节点

默认激活：

- `joint_state_broadcaster`
- `forward_position_controller`
- `fts_broadcaster`

### 3. 检查

```bash
ros2 control list_hardware_interfaces
ros2 control list_hardware_components
ros2 control list_controllers
```

应看到两个硬件组件（系统 + 外部传感器），控制器均为 `active`。

### 4. 控制关节

```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.5, 0.5]}"
```

或：

```bash
ros2 launch ros2_control_demo_example_5 test_forward_position_controller.launch.py
```

### 5. 查看力/力矩

```bash
ros2 topic echo /fts_broadcaster/wrench
```

带坐标变换时：

```bash
ros2 launch ros2_control_demo_example_5 rrbot_system_with_external_sensor.launch.py \
  use_wrench_transformer:=true
```

然后：

```bash
ros2 topic list | rg wrench
ros2 topic echo /fts_wrench_transformer/base_link/wrench
ros2 topic echo /fts_wrench_transformer/link1/wrench
```

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF |
| `rrbot_system_with_external_sensor.launch.py` | 完整 Example 5 |
| `test_forward_position_controller.launch.py` | 循环发位置目标 |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| 包找不到 | source Humble + 工作空间 |
| apt 无 demos 元包 | 本仓库 `colcon` 编译 |
| PATH 异常 | `export PATH="/usr/bin:$PATH"` |
| 与其他 demo 冲突 | 关掉旧的 `/controller_manager` |
| 变换话题不存在 | 确认启动时加了 `use_wrench_transformer:=true` |

---

## 相关文件

- 硬件：`hardware/rrbot.cpp`、`hardware/external_rrbot_force_torque_sensor.cpp`
- 控制器配置：`bringup/config/rrbot_with_external_sensor_controllers.yaml`
- 变换参数：`bringup/config/wrench_transformer_params.yaml`
