# Example 11：CarlikeBot（`ros2_control_demo_example_11`）

*CarlikeBot* 是类汽车底盘示例：前轮转向、后轮驱动，控制上按 **自行车模型**（两个虚拟关节：转向位置 + 驱动速度），默认用 `bicycle_steering_controller`。

详细原理与官方教程见 [doc/userdoc.rst](doc/userdoc.rst) 或 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/example_11/doc/userdoc.html)。

---

## 本机环境

| 项 | 值 |
|---|---|
| 系统 | Ubuntu + ROS 2 Humble（`/opt/ros/humble`） |
| 源码仓库 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos`（需在 **humble** 分支） |
| 编译工作空间 | `/home/lyzn-robot/ros2bookcode/ros2_control_demos_ws` |
| 包名 | `ros2_control_demo_example_11` |

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
colcon build --packages-up-to ros2_control_demo_example_11
source install/setup.bash
```

```bash
ros2 pkg prefix ros2_control_demo_example_11
```

---

## 运行

### 1.（可选）仅查看模型

```bash
ros2 launch ros2_control_demo_example_11 view_robot.launch.py
```

### 2. 启动 Example 11（主流程）

官方推荐打开里程计 TF remap（否则 RViz 里移动底盘可能“飘”或固定基座感）：

```bash
ros2 launch ros2_control_demo_example_11 carlikebot.launch.py remap_odometry_tf:=true
```

可选参数：

- `gui:=true`（默认）/ `gui:=false`
- `remap_odometry_tf:=true`：把 `/bicycle_steering_controller/tf_odometry` remap 到 `/tf`

默认激活：

- `joint_state_broadcaster`
- `bicycle_steering_controller`

### 3. 检查

```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
```

应看到虚拟关节相关接口被 claimed，例如转向（position）与驱动（velocity）。

### 4. 发送速度 / 转向命令

控制器订阅 **`geometry_msgs/msg/TwistStamped`**（`use_stamped_vel: true`），话题为：

```bash
ros2 topic pub --rate 30 /bicycle_steering_controller/reference geometry_msgs/msg/TwistStamped "
header: auto
twist:
  linear:
    x: 1.0
    y: 0.0
    z: 0.0
  angular:
    x: 0.0
    y: 0.0
    z: 0.1"
```

停发后，参考超时（配置里 `reference_timeout`）会让机器人停下。

查看状态：

```bash
ros2 topic echo /joint_states
```

本示例**没有** `test_*_controller.launch.py`；控制靠上述 topic。

---

## Launch 文件一览

| Launch | 作用 |
|---|---|
| `view_robot.launch.py` | 仅可视化 URDF |
| `carlikebot.launch.py` | 完整 Example 11 |

---

## 常见问题

| 现象 | 处理 |
|---|---|
| 包找不到 | source Humble + 工作空间 |
| 发了速度不动 / 类型错误 | 必须用 `TwistStamped`，话题是 `/bicycle_steering_controller/reference`（不是 `/cmd_vel`） |
| RViz 位姿异常 | 加 `remap_odometry_tf:=true` |
| 与其他 demo 冲突 | 关掉旧 `/controller_manager` |

---

## 相关文件

- 硬件：`hardware/carlikebot_system.cpp`
- 控制器配置：`bringup/config/carlikebot_controllers.yaml`
- Launch：`bringup/launch/carlikebot.launch.py`
