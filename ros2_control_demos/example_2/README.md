# Example 2：DiffBot（`ros2_control_demo_example_2`）

*DiffBot*（Differential Mobile Robot）是一个简单的差速驱动移动底盘：单一硬件接口，左右轮用 **速度（velocity）** 命令接口，默认通过 `diff_drive_controller` 订阅 `/cmd_vel` 做运动学解算。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_2/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws`（`src/` 里是指向 `example_*` 的符号链接） |
| 包名 | `ros2_control_demo_example_2` |

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
  ros-humble-xacro \
  ros-humble-rviz2 \
  ros-humble-teleop-twist-keyboard \
  python3-colcon-common-extensions
```

可选（键盘发 `Twist`、控制器要 `TwistStamped` 时做桥接）：

```bash
sudo apt install -y ros-humble-twist-stamper
```

3. 仓库在 humble 分支：

```bash
cd /home/lyzn-robot/ros2bookcode/ros2_control_demos
git branch --show-current   # 应输出 humble
```

4. **不要与 Example 1 等其他 demo 同时开着**：它们共用 `/controller_manager`、`/robot_description` 等全局名，会互相抢占。启动 DiffBot 前请先关掉其他 `ros2_control` 示例。

---

## 编译

每个新终端建议先把系统 `PATH` 放到前面，再 source ROS 与工作空间（避免 conda 等覆盖 `python`/`colcon`）：

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_2
source install/setup.bash
```

只改了 example_2 时可用 `--packages-select ros2_control_demo_example_2`（若依赖包已装好）。

验证包是否可见：

```bash
ros2 pkg prefix ros2_control_demo_example_2
```

---

## 运行

### 1.（可选）仅查看模型

不启动 `ros2_control`，用 RViz + `joint_state_publisher_gui` 检查 URDF：

```bash
ros2 launch ros2_control_demo_example_2 view_robot.launch.py
```

可选参数：`gui:=false`（不自动开 RViz / GUI）、`prefix:=某前缀`（关节名前缀）。

出现 `Invalid frame ID "odom"` 警告一般可忽略（GUI 启动稍慢）。

### 2. 启动 Example 2（主流程）

```bash
ros2 launch ros2_control_demo_example_2 diffbot.launch.py
```

会启动硬件模拟、`controller_manager`、默认控制器，并打开 RViz（橙色盒子表示正常）。终端里硬件接口会打印内部状态，仅作演示。

可选参数：

- `gui:=true`（默认）：自动启动 RViz
- `gui:=false`：不启动 RViz，适合无头或另开 RViz
- `use_mock_hardware:=true`：改用 `mock_components/GenericSystem`（见下文）
- `disable_commands:=true`：仅在 mock 硬件下有效，模拟驱动断开（命令不回写状态）

默认激活的控制器：

- `joint_state_broadcaster`
- `diffbot_base_controller`（`diff_drive_controller/DiffDriveController`）

Launch 里把控制器的命令话题 remap 到了根命名空间：

- `/diffbot_base_controller/cmd_vel` → `/cmd_vel`

因此直接往 **`/cmd_vel`** 发速度即可。

### 3. 检查硬件与控制器

另开终端（同样 `export PATH` + source Humble + source `install/setup.bash`）：

```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
ros2 control list_hardware_components
```

正常时应类似：

- command：`left_wheel_joint/velocity`、`right_wheel_joint/velocity` 带 `[claimed]`
- state：左右轮的 `position` / `velocity`
- 控制器：`diffbot_base_controller`、`joint_state_broadcaster` 均为 `active`
- 硬件组件名：`DiffBot`，插件为 `ros2_control_demo_example_2/DiffBotSystemHardware`（或 mock 时为 `mock_components/GenericSystem`）

也可看话题：

```bash
ros2 topic list | rg "cmd_vel|odom|joint_states"
ros2 topic info /cmd_vel -v
```

Humble 下默认 `use_stamped_vel:=true`，`/cmd_vel` 类型为 **`geometry_msgs/msg/TwistStamped`**。

---

## 如何控制 DiffBot

### 4. 用 CLI 发速度（推荐，与官方教程一致）

以约 10 Hz 发布（`cmd_vel_timeout` 默认 0.5 s，停发后底盘会停）：

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/TwistStamped "
header: auto
twist:
  linear:
    x: 0.7
    y: 0.0
    z: 0.0
  angular:
    x: 0.0
    y: 0.0
    z: 1.0"
```

RViz 中橙色盒子应绕圈移动；启动终端里可见左右轮速度命令在变化。只前进可把 `angular.z` 设为 `0.0`。

查看反馈：

```bash
ros2 topic echo /joint_states
ros2 topic echo /diffbot_base_controller/odom
```

### 5. 键盘遥控（`teleop_twist_keyboard`）

`teleop_twist_keyboard` 发的是 **`geometry_msgs/msg/Twist`**（无 stamp），与默认 `/cmd_vel`（`TwistStamped`）类型不匹配。任选其一：

**做法 A：用 twist_stamper 桥接（不改配置）**

终端 1（DiffBot 已启动）：

```bash
ros2 run twist_stamper twist_stamper --ros-args \
  -r cmd_vel_in:=/teleop_cmd_vel \
  -r cmd_vel_out:=/cmd_vel
```

终端 2：

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
  -r /cmd_vel:=/teleop_cmd_vel
```

**做法 B：改配置接受无 stamp 的 Twist**

在 `bringup/config/diffbot_controllers.yaml` 的 `diffbot_base_controller.ros__parameters` 下增加：

```yaml
use_stamped_vel: false
```

然后重新 launch（若改了安装空间里的文件需先 `colcon build` 再 source）。之后可直接：

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

（它默认发到 `/cmd_vel`，与 launch remap 一致。）

键位以终端内提示为准（常见：`i`/`j`/`l`/`，` 等控制前进与转向，`k` 停车）。

### 6.（可选）Mock 硬件

不加载自定义 `DiffBotSystemHardware`，改用通用 mock：

```bash
ros2 launch ros2_control_demo_example_2 diffbot.launch.py use_mock_hardware:=true
```

`calculate_dynamics:=true` 时，速度命令会积分到位置状态；可用 `ros2 topic echo /joint_states` 看到位置随运动增大。

模拟“命令发出但无反馈”（如编码器断开）：

```bash
ros2 launch ros2_control_demo_example_2 diffbot.launch.py \
  use_mock_hardware:=true disable_commands:=true
```

再发 `/cmd_vel` 时，`/joint_states` 中位置/速度应基本不变。

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF（无 control） |
| `diffbot.launch.py` | 完整 Example 2：硬件 + 差速控制器 + RViz |

本示例**没有**类似 example_1 的 `test_*_controller.launch.py`；控制主要靠 `/cmd_vel` 或键盘遥控。

---

## 常用 ros2 control CLI

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
ros2 control list_hardware_components
```

差速控制器参数与限速见 `bringup/config/diffbot_controllers.yaml`（轮距、轮半径、`linear.x` / `angular.z` 限幅、`cmd_vel_timeout` 等）。

---

## 常见问题

| 现象 | 处理 |
|---|---|
| `Package 'ros2_control_demo_example_2' not found` | 当前终端未 `source` 工作空间：`source /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws/install/setup.bash`（且先 source Humble） |
| `无法定位软件包 ros-humble-ros2-control-demos` | 正常：该 apt 包不存在，请用本仓库 + `colcon` 编译 |
| `colcon` / `python` 行为异常 | 先执行 `export PATH="/usr/bin:$PATH"`，再 source |
| 启动后加载成 RRBot / spawner 失败 | 已有其他 demo（如 example_1）占用 `/controller_manager`；先关掉旧 launch 再启 DiffBot |
| 发了速度但不动 | 确认类型是 `TwistStamped`（或已设 `use_stamped_vel: false`）；用 `--rate` 持续发布，超时约 0.5 s 会停 |
| 键盘遥控无反应 | `teleop` 发 `Twist`，默认控制器要 `TwistStamped`；用 twist_stamper 或改 `use_stamped_vel: false` |
| 仓库在 `master` 等分支编译失败 | Humble 请使用 `humble` 分支 |

---

## 相关文件

- 硬件插件：`hardware/diffbot_system.cpp`
- 控制器配置：`bringup/config/diffbot_controllers.yaml`
- Launch：`bringup/launch/diffbot.launch.py`
- URDF / `ros2_control` 标签：`description/urdf/`、`description/ros2_control/`
