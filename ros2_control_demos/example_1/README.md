# Example 1：RRBot（`ros2_control_demo_example_1`）

*RRBot*（Revolute-Revolute Manipulator Robot）是一个双关节、位置控制的简单机械臂示例：单一硬件接口，并演示在不同控制器之间切换。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_1/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws`（`src/` 里是指向 `example_*` 的符号链接） |
| 包名 | `ros2_control_demo_example_1` |

**注意：** apt 中**没有** `ros-humble-ros2-control-demos` 元包，必须从本仓库源码编译。系统里已有的 `ros-humble-ros2-control` / `ros-humble-ros2-controllers` 等依赖可继续用 apt 安装。

---

## 前置条件

1. 已安装 ROS 2 Humble，并能 `source /opt/ros/humble/setup.bash`。
2. 已安装常用依赖（示例）：

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

3. 仓库在 humble 分支：

```bash
cd /home/lyzn-robot/ros2bookcode/ros2_control_demos
git branch --show-current   # 应输出 humble
```

---

## 编译

每个新终端建议先把系统 `PATH` 放到前面，再 source ROS 与工作空间（避免 conda 等覆盖 `python`/`colcon`）：

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_1
source install/setup.bash
```

只改了 example_1 时可用 `--packages-select ros2_control_demo_example_1`（若依赖包已装好）。

验证包是否可见：

```bash
ros2 pkg prefix ros2_control_demo_example_1
```

---

## 运行

### 1.（可选）仅查看模型

不启动 `ros2_control`，用 RViz + `joint_state_publisher_gui` 检查 URDF：

```bash
ros2 launch ros2_control_demo_example_1 view_robot.launch.py
```

可选参数：`gui:=false`（不自动开 RViz / GUI）、`prefix:=某前缀`（关节名前缀）。

出现 `Invalid frame ID "odom"` 警告一般可忽略（GUI 启动稍慢）。

### 2. 启动 Example 1（主流程）

```bash
ros2 launch ros2_control_demo_example_1 rrbot.launch.py
```

会启动硬件模拟、`controller_manager`、默认控制器，并打开 RViz（橙/黄连杆表示正常）。

可选参数：

- `gui:=true`（默认）：自动启动 RViz
- `gui:=false`：不启动 RViz，适合无头或另开 RViz

默认激活的控制器：

- `joint_state_broadcaster`
- `forward_position_controller`

### 3. 检查硬件与控制器

另开终端（同样 `export PATH` + source Humble + source `install/setup.bash`）：

```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
```

正常时应看到 `joint1/position`、`joint2/position` 的 command 接口带 `[claimed]`，且两个控制器均为 `active`。

### 4. 发送位置命令（Forward Command Controller）

手动发布（两关节位置，单位弧度）：

```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.5, 0.5]}"
```

或用演示节点循环发目标（每约 5 秒）：

```bash
ros2 launch ros2_control_demo_example_1 test_forward_position_controller.launch.py
```

可在 RViz 中看到连杆运动；也可用：

```bash
ros2 topic echo /joint_states
```

目标序列可在 `bringup/config/rrbot_forward_position_publisher.yaml` 中修改。

### 5. 切换到 Joint Trajectory Controller

加载并配置（一步到位）：

```bash
ros2 control load_controller joint_trajectory_position_controller --set-state inactive
```

再切换（停用 forward，启用 trajectory）：

```bash
ros2 control switch_controllers \
  --activate joint_trajectory_position_controller \
  --deactivate forward_position_controller
```

然后发轨迹演示：

```bash
ros2 launch ros2_control_demo_example_1 test_joint_trajectory_controller.launch.py
```

目标可在 `bringup/config/rrbot_joint_trajectory_publisher.yaml` 中调整。

（可选）GUI 调参：

```bash
ros2 run rqt_joint_trajectory_controller rqt_joint_trajectory_controller
```

在界面中选择 `joint_trajectory_position_controller`，用滑条设目标并发送。

切回 forward 控制器示例：

```bash
ros2 control switch_controllers \
  --activate forward_position_controller \
  --deactivate joint_trajectory_position_controller
```

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF（无 control） |
| `rrbot.launch.py` | 完整 Example 1：硬件 + 控制器 + RViz |
| `test_forward_position_controller.launch.py` | 向 forward 控制器循环发位置目标 |
| `test_joint_trajectory_controller.launch.py` | 向轨迹控制器循环发轨迹目标 |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| `Package 'ros2_control_demo_example_1' not found` | 当前终端未 `source` 工作空间：`source /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws/install/setup.bash`（且先 source Humble） |
| `无法定位软件包 ros-humble-ros2-control-demos` | 正常：该 apt 包不存在，请用本仓库 + `colcon` 编译 |
| `colcon` / `python` 行为异常 | 先执行 `export PATH="/usr/bin:$PATH"`，再 source |
| 控制器切换失败 / 接口 claimed | 同一时刻只能有一个控制器占用同一 command 接口；先 `--deactivate` 旧的再 `--activate` 新的 |
| 仓库在 `master` 等分支编译失败 | Humble 请使用 `humble` 分支 |

---

## 相关文件

- 硬件插件：`hardware/rrbot.cpp`
- 控制器配置：`bringup/config/rrbot_controllers.yaml`
- URDF / `ros2_control` 标签：`description/urdf/`、`description/ros2_control/`
