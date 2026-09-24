# Example 15：命名空间 / 多 Controller Manager（`ros2_control_demo_example_15`）

演示如何把机器人放进 **ROS 命名空间**，以及如何同时运行 **多个** `controller_manager` 实例（两台 RRBot）。本包无本地 hardware，复用 example_1 / example_5 的插件与描述。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_15/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_15` |

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

仓库在 `humble` 分支。本示例自己带命名空间 / 多 CM，一般不要再叠开 example_1 等同名全局 CM。

---

## 编译

会拉取 example_1 / example_5 等依赖：

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_15
source install/setup.bash
```

```bash
ros2 pkg prefix ros2_control_demo_example_15
```

---

## 场景 A：单机器人命名空间

### 启动

```bash
ros2 launch ros2_control_demo_example_15 rrbot_namespace.launch.py
```

可选：`start_rviz:=true`（默认）/ `false`。

- Controller Manager：`/rrbot/controller_manager`
- 默认激活：`joint_state_broadcaster`、`forward_position_controller`
- 预加载未激活：`position_trajectory_controller`
- 位置命令 remap 到：`/position_commands`

### 检查与控制

命名空间下请始终指定 `-c`：

```bash
ros2 control list_controllers -c /rrbot/controller_manager
ros2 control list_hardware_interfaces -c /rrbot/controller_manager
```

发位置（注意话题是 remap 后的根命名空间名）：

```bash
ros2 topic pub /position_commands std_msgs/msg/Float64MultiArray "{data: [0.5, 0.5]}"
```

或用测试 launch（覆盖本包配置名）：

```bash
ros2 launch ros2_control_demo_example_15 test_forward_position_controller.launch.py \
  publisher_config:=rrbot_namespace_forward_position_publisher.yaml
```

切换到轨迹控制器：

```bash
ros2 control switch_controllers -c /rrbot/controller_manager \
  --deactivate forward_position_controller \
  --activate position_trajectory_controller
```

```bash
ros2 launch ros2_control_demo_example_15 test_joint_trajectory_controller.launch.py \
  publisher_config:=rrbot_namespace_joint_trajectory_publisher.yaml
```

---

## 场景 B：两台机器人 / 两个 Controller Manager（主多 CM 流程）

### 启动

```bash
ros2 launch ros2_control_demo_example_15 multi_controller_manager_example_two_rrbots.launch.py
```

可选：`start_rviz_multi:=true`（默认）、`robot_controller:=forward_position_controller`（默认）或 `position_trajectory_controller`、`use_mock_hardware:=true` 等。

- CM：`/rrbot_1/controller_manager`、`/rrbot_2/controller_manager`
- 内部通过 `rrbot_base.launch.py` 分别拉起两台机器人

### 检查与控制

```bash
ros2 control list_controllers -c /rrbot_1/controller_manager
ros2 control list_controllers -c /rrbot_2/controller_manager
```

同时给两台发 forward 位置：

```bash
ros2 launch ros2_control_demo_example_15 \
  test_multi_controller_manager_forward_position_controller.launch.py
```

有效话题类似：

- `/rrbot_1/forward_position_controller/commands`
- `/rrbot_2/forward_position_controller/commands`

切换到轨迹控制器（两台都要切）：

```bash
ros2 control switch_controllers -c /rrbot_1/controller_manager \
  --deactivate forward_position_controller \
  --activate position_trajectory_controller
ros2 control switch_controllers -c /rrbot_2/controller_manager \
  --deactivate forward_position_controller \
  --activate position_trajectory_controller
```

```bash
ros2 launch ros2_control_demo_example_15 \
  test_multi_controller_manager_joint_trajectory_controller.launch.py
```

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `rrbot_namespace.launch.py` | 单 RRBot + 命名空间 CM |
| `multi_controller_manager_example_two_rrbots.launch.py` | 双 RRBot + 双 CM |
| `rrbot_base.launch.py` | 被多 CM launch include 的底层启动（一般不单独当主入口） |
| `test_forward_position_controller.launch.py` | forward 位置测试（配合 `publisher_config`） |
| `test_joint_trajectory_controller.launch.py` | 轨迹测试（配合 `publisher_config`） |
| `test_multi_controller_manager_forward_position_controller.launch.py` | 双机 forward 测试 |
| `test_multi_controller_manager_joint_trajectory_controller.launch.py` | 双机轨迹测试 |

本包**没有** `description/launch/view_robot.launch.py`。

---

## 常见问题

| 现象 | 处理 |
|---|---|
| `list_controllers` 空 / 失败 | 必须加 `-c /rrbot/...` 或 `/rrbot_1/...` |
| test_forward 找不到默认 yaml | 本包默认文件名不同，用上面的 `publisher_config:=...` |
| 缺硬件插件 | 确保 example_1 / example_5 已随 `--packages-up-to` 编译 |
| 与全局 demo 冲突 | 不要同时开 example_1 等占用根 `/controller_manager` 的进程 |

---

## 相关文件

- 命名空间配置：`bringup/config/rrbot_namespace_*.yaml`
- 双 CM 配置：`bringup/config/multi_controller_manager_*.yaml`
