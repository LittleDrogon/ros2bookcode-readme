# Example 13：多机器人单 Controller Manager（`ros2_control_demo_example_13`）

在**同一个** `controller_manager` 实例中加载多台机器人 / 多个硬件组件，并演示硬件生命周期（configure / activate / deactivate）与控制器启停的配合。

本包**无本地 hardware 源码**，复用 example_4 / example_5 等插件与 mock 组件。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_13/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_13` |

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
  ros-humble-rqt-controller-manager \
  python3-colcon-common-extensions
```

仓库在 `humble` 分支；不要与其他 demo 同时运行。

---

## 编译

`--packages-up-to` 会一并编译依赖的 example_4 / example_5 等：

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_13
source install/setup.bash
```

```bash
ros2 pkg prefix ros2_control_demo_example_13
```

---

## 运行

### 1. 启动 Example 13（主流程）

本包**没有**单独的 `view_robot.launch.py`。

```bash
ros2 launch ros2_control_demo_example_13 three_robots.launch.py
```

可选参数：

- `gui:=true`（默认）：RViz
- `rqt:=true`（默认）：自动开 `rqt_controller_manager`
- `rqt:=false`：不开 rqt
- `slowdown:=50.0`

启动后会有多组控制器与命令发布器；部分硬件一开始是 inactive / unconfigured。

### 2. 查看硬件与控制器

```bash
ros2 control list_hardware_components
ros2 control list_controllers
```

典型组件名包括：`RRBotSystemPositionOnly`、`RRBotSystemWithSensor`、`FakeThreeDofBot` 以及外部 FTS 等（以实际输出为准）。

### 3. 控制与生命周期实验（官方教程要点）

命令话题（bringup 会起 publisher；也可手动 pub）：

- `/rrbot_position_controller/commands`
- `/rrbot_with_sensor_position_controller/commands`
- `/threedofbot_position_controller/commands`

激活带传感器的 RRBot 并启用其位置控制器示例：

```bash
ros2 control set_hardware_component_state RRBotSystemWithSensor active
ros2 control switch_controllers --activate rrbot_with_sensor_position_controller
```

配置并启用 ThreeDofBot（先 inactive 再开 broadcaster / PID，再 active + position）：

```bash
ros2 control set_hardware_component_state FakeThreeDofBot inactive
ros2 control switch_controllers --activate threedofbot_joint_state_broadcaster threedofbot_pid_gain_controller
ros2 control set_hardware_component_state FakeThreeDofBot active
ros2 control switch_controllers --activate threedofbot_position_controller
```

**注意：** 停硬件前先停依赖它的控制器。全局 `joint_state_broadcaster` 不会自动捡起后来才出现的接口，必要时：

```bash
ros2 control switch_controllers --deactivate joint_state_broadcaster
ros2 control switch_controllers --activate joint_state_broadcaster
```

查看：

```bash
ros2 topic echo /joint_states --once
```

也可用 GUI：

```bash
ros2 run rqt_controller_manager rqt_controller_manager
```

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `three_robots.launch.py` | 三机器人 / 多硬件 + 控制器 + RViz（可选 rqt） |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| 包找不到 / 缺插件 | 用 `--packages-up-to`，确保 example_4/5 已编进工作空间 |
| 切换硬件失败 | 先 deactivate 相关控制器再改硬件状态 |
| joint_states 缺关节 | 重启 `joint_state_broadcaster` |
| 与其他 demo 冲突 | 关掉旧 `/controller_manager` |

---

## 相关文件

- 配置：`bringup/config/three_robots_controllers.yaml`
- 命令发布器：`bringup/config/three_robots_position_command_publishers.yaml`
- URDF：`description/urdf/three_robots.urdf.xacro`
