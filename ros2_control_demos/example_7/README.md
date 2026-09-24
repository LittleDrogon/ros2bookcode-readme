# Example 7：六自由度 R6Bot（`ros2_control_demo_example_7`）

面向中级用户的完整 6-DOF 教程：自定义 URDF、`SystemInterface` 硬件、自定义 `RobotController`，以及基于 KDL 的参考轨迹生成器。

包结构：

- `bringup`：launch 与控制器配置
- `controller`：六自由度自定义控制器
- `description`：机器人描述
- `hardware`：硬件接口
- `reference_generator`：KDL 固定轨迹参考

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_7/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_7` |

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
  ros-humble-kdl-parser \
  ros-humble-realtime-tools \
  python3-colcon-common-extensions
```

仓库在 `humble` 分支；不要与其他 demo 同时运行。

---

## 编译

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_7
source install/setup.bash
```

若缺 `kdl_parser` / `orocos_kdl` 等依赖导致编译失败，用 `rosdep` 或上述 apt 包补齐后再编。

```bash
ros2 pkg prefix ros2_control_demo_example_7
```

---

## 运行

### 1.（可选）仅查看模型

注意 launch 名是 `view_r6bot`（不是 `view_robot`）：

```bash
ros2 launch ros2_control_demo_example_7 view_r6bot.launch.py
```

### 2. 启动 Example 7（主流程）

```bash
ros2 launch ros2_control_demo_example_7 r6bot_controller.launch.py
```

可选：`gui:=true`（默认）/ `gui:=false`。

默认激活：

- `joint_state_broadcaster`
- `r6bot_controller`（类型 `ros2_control_demo_example_7/RobotController`）

### 3. 检查

```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
```

应看到 `joint_1` … `joint_6` 的 position / velocity 接口，以及 `r6bot_controller` 为 `active`。

### 4. 发送轨迹（演示圆形运动）

另开终端（同样 export PATH + source）：

```bash
ros2 launch ros2_control_demo_example_7 send_trajectory.launch.py
```

该节点向 `/r6bot_controller/joint_trajectory` 发布 `trajectory_msgs/msg/JointTrajectory`。可在 RViz 中观察六轴运动。

查看状态：

```bash
ros2 topic echo /joint_states
```

本示例**没有** `test_forward_position_controller` 一类 launch；控制主要靠 `send_trajectory`。

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_r6bot.launch.py` | 仅可视化 URDF |
| `r6bot_controller.launch.py` | 硬件 + 自定义控制器 + RViz |
| `send_trajectory.launch.py` | KDL 参考轨迹生成器 |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| 包找不到 | source Humble + 工作空间 |
| 编译缺 kdl / realtime_tools | 安装对应 `ros-humble-*` 依赖后重编 |
| apt 无 demos 元包 | 本仓库 `colcon` 编译 |
| 与其他 demo 冲突 | 关掉占用 `/controller_manager` 的旧进程 |
| 找不到 `view_robot.launch.py` | 本包用的是 `view_r6bot.launch.py` |

---

## 相关文件

- 硬件：`hardware/r6bot_hardware.cpp`
- 控制器：`controller/r6bot_controller.cpp`
- 轨迹生成：`reference_generator/send_trajectory.cpp`
- 配置：`bringup/config/r6bot_controller.yaml`
