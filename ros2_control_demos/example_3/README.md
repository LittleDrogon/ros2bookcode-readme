# Example 3：RRBot 多接口（`ros2_control_demo_example_3`）

*RRBot* 的多命令接口示例：同一套硬件同时暴露 **position / velocity / acceleration** 命令接口，演示如何选择合法控制器，以及混用接口时激活会被拒绝。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_3/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws`（`src/` 里是指向 `example_*` 的符号链接） |
| 包名 | `ros2_control_demo_example_3` |

**注意：** apt 中**没有** `ros-humble-ros2-control-demos` 元包，必须从本仓库源码编译。

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

4. **不要与其他 demo 同时开着**：共用 `/controller_manager` 等全局名会互相抢占。

---

## 编译

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

cd /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_3
source install/setup.bash
```

验证：

```bash
ros2 pkg prefix ros2_control_demo_example_3
```

---

## 运行

### 1.（可选）仅查看模型

```bash
ros2 launch ros2_control_demo_example_3 view_robot.launch.py
```

### 2. 启动 Example 3（主流程）

默认激活 **速度** forward 控制器：

```bash
ros2 launch ros2_control_demo_example_3 rrbot_system_multi_interface.launch.py
```

可选参数：

- `gui:=true`（默认）：自动启动 RViz
- `gui:=false`：不启动 RViz
- `robot_controller:=forward_velocity_controller`（默认）
- `robot_controller:=forward_position_controller`
- `robot_controller:=forward_acceleration_controller`
- `use_mock_hardware:=true`：改用 mock 硬件
- `slowdown:=50.0`：硬件模拟减速因子

默认激活的控制器：

- `joint_state_broadcaster`
- `forward_velocity_controller`（可由 `robot_controller` 覆盖）

配置里还有故意“不合法”的控制器：`forward_illegal1_controller`、`forward_illegal2_controller`（混用不同关节的接口类型）。用它们作 `robot_controller` 时激活会失败，用于演示规则。

### 3. 检查硬件与控制器

```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
```

应能看到各关节的 position / velocity / acceleration 命令接口；当前激活的 forward 控制器对应接口为 `[claimed]`。

### 4. 发送命令

**速度模式（默认）：**

```bash
ros2 topic pub /forward_velocity_controller/commands std_msgs/msg/Float64MultiArray "{data: [5.0, 5.0]}"
```

**位置模式：** 启动时指定，或运行中切换：

```bash
ros2 launch ros2_control_demo_example_3 rrbot_system_multi_interface.launch.py \
  robot_controller:=forward_position_controller
```

```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.5, 0.5]}"
```

或循环发目标：

```bash
ros2 launch ros2_control_demo_example_3 test_forward_position_controller.launch.py
```

**加速度模式：**

```bash
ros2 launch ros2_control_demo_example_3 rrbot_system_multi_interface.launch.py \
  robot_controller:=forward_acceleration_controller
```

```bash
ros2 topic pub /forward_acceleration_controller/commands std_msgs/msg/Float64MultiArray "{data: [10.0, 10.0]}"
```

### 5. 运行中切换控制器（示例：速度 → 位置）

```bash
ros2 control load_controller forward_position_controller --set-state inactive
ros2 control switch_controllers \
  --activate forward_position_controller \
  --deactivate forward_velocity_controller
```

规则：同一时刻，所有被控关节必须占用**同一种**命令接口；混用会切换失败。

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF（无 control） |
| `rrbot_system_multi_interface.launch.py` | 完整 Example 3：多接口硬件 + 控制器 + RViz |
| `test_forward_position_controller.launch.py` | 向 forward 位置控制器循环发目标 |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| `Package '...example_3' not found` | 未 `source` 工作空间：`source /home/lyzn-robot/ros2bookcode/ros2_control_demos_ws/install/setup.bash` |
| 无法定位 apt 包 `ros-humble-ros2-control-demos` | 正常：不存在，请用本仓库 `colcon` 编译 |
| `colcon` / `python` 异常 | 先 `export PATH="/usr/bin:$PATH"`，再 source |
| 控制器激活失败 / 接口 claimed | 先停用占用同接口的旧控制器；非法混用接口的控制器无法激活 |
| 与其他 demo 冲突 | 先关掉占用 `/controller_manager` 的旧 launch |
| 仓库不在 `humble` | Humble 请切换到 `humble` 分支 |

---

## 相关文件

- 硬件插件：`hardware/rrbot_system_multi_interface.cpp`
- 控制器配置：`bringup/config/rrbot_multi_interface_forward_controllers.yaml`
- 位置发布器配置：`bringup/config/rrbot_forward_position_publisher.yaml`
- URDF / `ros2_control`：`description/urdf/`、`description/ros2_control/`
