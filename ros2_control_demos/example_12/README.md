# Example 12：可链式控制器（`ros2_control_demo_example_12`）

演示如何编写简单的 **chainable（可链式）** 控制器（本包的 `passthrough_controller`），并把它接到 RRBot 上，形成控制器链：

`forward_position_controller` → `position_controller` → `joint1/2_position_controller` → 硬件

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_12/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_12` |

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
colcon build --packages-up-to ros2_control_demo_example_12
source install/setup.bash
```

本包同时编译自定义控制器插件 `passthrough_controller`。

```bash
ros2 pkg prefix ros2_control_demo_example_12
```

---

## 运行

### 1.（可选）仅查看模型

```bash
ros2 launch ros2_control_demo_example_12 view_robot.launch.py
```

### 2. 启动底层硬件与一级 passthrough（主流程第一步）

```bash
ros2 launch ros2_control_demo_example_12 rrbot.launch.py
```

可选：`gui:=true|false`。

此时默认激活：

- `joint_state_broadcaster`
- `joint1_position_controller`
- `joint2_position_controller`

（均为 passthrough 链的底层。）

可用：

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

未接到上级前，部分 reference 接口可能显示 `[unavailable]` / `[unclaimed]`。

### 3. 启动链式上层控制器（第二步）

**另开终端**（同样 source）：

```bash
ros2 launch ros2_control_demo_example_12 launch_chained_controllers.launch.py
```

会激活链路上的 `position_controller` 与 `forward_position_controller`。

再检查：

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

### 4. 发送位置命令

整条链就绪后，向最上层发命令：

```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.5, 0.5]}"
```

```bash
ros2 topic echo /joint_states
ros2 topic echo /dynamic_joint_states
```

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF |
| `rrbot.launch.py` | 硬件 + 底层 passthrough 控制器 |
| `launch_chained_controllers.launch.py` | 加载/激活链式上层控制器 |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| 包找不到 | source Humble + 工作空间 |
| 发命令无动作 | 确认已先 `rrbot.launch.py` 再 `launch_chained_controllers.launch.py` |
| 接口 unavailable | 链未接好；完成第二步后再查 `list_hardware_interfaces` |
| 与其他 demo 冲突 | 关掉旧 `/controller_manager` |

---

## 相关文件

- 硬件：`hardware/rrbot.cpp`
- 链式控制器：`controllers/src/passthrough_controller.cpp`
- 配置：`bringup/config/rrbot_chained_controllers.yaml`
