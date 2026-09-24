# Example 10：RRBot + GPIO（`ros2_control_demo_example_10`）

工业风格 *RRBot*：在关节位置接口之外增加 **GPIO** 接口（模拟量 IO、真空开关等），通过 `gpio_controllers/GpioCommandController` 读写。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_10/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_10` |

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
colcon build --packages-up-to ros2_control_demo_example_10
source install/setup.bash
```

```bash
ros2 pkg prefix ros2_control_demo_example_10
```

---

## 运行

### 1.（可选）仅查看模型

```bash
ros2 launch ros2_control_demo_example_10 view_robot.launch.py
```

### 2. 启动 Example 10（主流程）

```bash
ros2 launch ros2_control_demo_example_10 rrbot.launch.py
```

可选：`use_mock_hardware:=true`（本 bringup **无** `gui` 参数；RViz 行为以 launch 实现为准）。

默认激活：

- `joint_state_broadcaster`
- `gpio_controller`
- `forward_position_controller`

### 3. 检查

```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
ros2 control list_hardware_components -v
```

除 `joint1/position`、`joint2/position` 外，还应看到例如：

- `flange_analog_IOs/analog_output1`（及对应 state）
- `flange_vacuum/vacuum`

### 4. 查看 GPIO / 关节状态

```bash
ros2 topic echo /dynamic_joint_states --once
ros2 topic echo /gpio_controller/gpio_states
```

### 5. 发送 GPIO 命令

模拟量输出：

```bash
ros2 topic pub /gpio_controller/commands control_msgs/msg/DynamicInterfaceGroupValues \
  "{interface_groups: [flange_analog_IOs], interface_values: [{interface_names: [analog_output1], values: [0.5]}]}"
```

真空：

```bash
ros2 topic pub /gpio_controller/commands control_msgs/msg/DynamicInterfaceGroupValues \
  "{interface_groups: [flange_vacuum], interface_values: [{interface_names: [vacuum], values: [0.27]}]}"
```

同时设置两组：

```bash
ros2 topic pub /gpio_controller/commands control_msgs/msg/DynamicInterfaceGroupValues \
  "{interface_groups: [flange_vacuum, flange_analog_IOs], interface_values: [{interface_names: [vacuum], values: [0.27]}, {interface_names: [analog_output1], values: [0.5]}]}"
```

启动终端的硬件日志应打印 Writing commands；`/gpio_controller/gpio_states` 会变化。

### 6. 关节位置（可选）

```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.5, 0.5]}"
```

也有 `test_forward_position_controller.launch.py`，但其配置路径指向 **example_1** 的 publisher yaml。若已编译 example_1 可直接用；否则请用上面的手动 `topic pub`，或先：

```bash
colcon build --packages-up-to ros2_control_demo_example_1
```

### 7.（可选）Mock 硬件

```bash
ros2 launch ros2_control_demo_example_10 rrbot.launch.py use_mock_hardware:=true
```

Mock 下 GPIO 命令通常会镜像到状态接口。

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF |
| `rrbot.launch.py` | 完整 Example 10（含 GPIO） |
| `test_forward_position_controller.launch.py` | 循环发位置（依赖 example_1 的 yaml） |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| 包找不到 | source Humble + 工作空间 |
| test_forward 找不到配置 | 先编 example_1，或改用手动 `topic pub` |
| GPIO 无变化 | 确认消息类型为 `DynamicInterfaceGroupValues`，组名/接口名与配置一致 |
| 与其他 demo 冲突 | 关掉旧 `/controller_manager` |

---

## 相关文件

- 硬件：`hardware/rrbot.cpp`
- 控制器配置：`bringup/config/rrbot_controllers.yaml`
