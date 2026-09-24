# ROSCon 2022 ros2_control 工作坊中文说明

本文根据同目录 [`README.md`](README.md) 整理，面向 **ROS 2 Humble**。

原仓库用于 2022 年京都 ROSCon 的 *ros2_control* 工作坊，按「从描述 → Mock → 仿真 → 真机驱动 → 自定义控制器」的顺序讲解框架。本地代码目录：

```text
/home/lyzn-robot/ros2bookcode/roscon2022_workshop/   # 源码
/home/lyzn-robot/ros2bookcode/roscon2022_ws/         # 推荐编译工作空间
```

---

## 什么是 ros2_control

简言之，`ros2_control` 是 ROS 2 的控制框架；更进一步说，它是控制系统的「内核」：

- 为 MoveIt2、Nav2 等高层框架抽象硬件与底层控制
- 管理硬件资源访问
- 管理控制器与硬件组件的生命周期

更多介绍见：[ROS World 2021 相关资料](https://control.ros.org/master/doc/resources/resources.html#ros-world-2021)

Humble 官方文档入口：[https://control.ros.org/humble/](https://control.ros.org/humble/)

---

## 环境准备与依赖安装

### 推荐：本机工作空间 `roscon2022_ws`

```bash
export PATH="/usr/bin:$PATH"   # 避开 conda，优先系统 Python 3.10
source /opt/ros/humble/setup.bash

# 若尚未创建工作空间，可将本目录下的包链到 src：
mkdir -p ~/ros2bookcode/roscon2022_ws/src
cd ~/ros2bookcode/roscon2022_ws/src
for p in controlko_description controlko_bringup \
         controlko_hardware_interface controlko_controllers \
         roscon2022_control_workshop; do
  ln -sfn ../../roscon2022_workshop/$p $p
done

cd ~/ros2bookcode/roscon2022_ws
colcon build
source install/setup.bash
```

每次新开终端启动前都要重新 `source`：

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
source ~/ros2bookcode/roscon2022_ws/install/setup.bash
```

> 报错 `Package 'controlko_xxx' not found`：说明该包还没编译，或当前终端没有 source `roscon2022_ws/install/setup.bash`。

### 系统依赖（apt）

```bash
sudo apt install \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-ros2-controllers-test-nodes \
  ros-humble-ros2controlcli \
  ros-humble-xacro \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros2-control \
  ros-humble-ros-ign-gazebo \
  ros-humble-ign-ros2-control \
  ros-humble-controller-manager
```

说明：

- **`ros-humble-ros2-controllers-test-nodes`**：轨迹/位置测试发布节点（见专节）
- **`ros-humble-gazebo-ros-pkgs` + `gazebo-ros2-control`**：Gazebo Classic（`rrbot_sim_gazebo_classic.launch.py`）
- **`ros-humble-ros-ign-gazebo` + `ign-ros2-control`**：新版 Gazebo / Ignition（`rrbot_sim_gazebo.launch.py` 需要 `ros_ign_gazebo`；该包为指向 `ros_gz_sim` 的兼容包）

也可用 `vcs` + `rosdep`（在含本仓库的 `src` 下）：

```bash
vcs import --input roscon2022_workshop/roscon2022_workshop.humble.repos .
rosdep update
rosdep install -y -i --from-paths .
```

---

## 工作坊结构（共 8 步）

| 步骤 | 主题 |
|------|------|
| 1 | 为 ros2_control 准备硬件描述（URDF / Xacro + `<ros2_control>`） |
| 2 | 用 Mock Hardware 快速验证控制器配置 |
| 3 | 理解四大组件：Controller Manager / Controllers / Resource Manager / Hardware Interface |
| 4 | 系统自省（CLI / 服务 / rqt） |
| 5 | Gazebo Classic / Gazebo 仿真 |
| 6 | 控制器与硬件的生命周期 |
| 7 | 编写机器人 Hardware Interface |
| 8 | 编写自定义 Controller |

原 README 中部分步骤对应 git **分支**（如 `1-robot-description/task`）。你本地拷贝可能已包含较完整的解答文件，可直接对照包内源码学习。

---

## 第 1 步：用 Xacro 写机器人描述

### 目标

- 用 Xacro 宏组织机器人 URDF
- 了解接入 `ros2_control` 时 URDF 需要哪些改动

### 任务概要（RRBot）

在包 `controlko_description` 中描述 **RRBot**：

**运动学**

- 2 自由度
- 第 1 关节装在底座（30×30×30 cm 方盒）上，离地 30 cm，绕竖直轴旋转
- 第 1 连杆长 50 cm（直径 20 cm 圆柱）
- 第 2 关节旋转轴垂直于第 1 连杆长度方向
- 第 2 连杆长 60 cm（截面约 10×10 cm，文中亦写 5×5 cm 量级细节，以宏文件为准）

**硬件**

- TCP 处 6 维力/力矩传感器
- 2 路数字输入、2 路数字输出（输出可测）

**关键文件**

| 文件 | 作用 |
|------|------|
| `rrbot_macro.xacro` | 运动学与几何宏 |
| `rrbot.urdf.xacro` | 实例化宏的主文件 |
| `view_rrbot.launch.py` | 在 RViz2 中显示 |

参考：[URDF](https://wiki.ros.org/urdf)、[URDF XML](https://wiki.ros.org/urdf/XML)

### 运行（查看模型）

```bash
ros2 launch controlko_description view_rrbot.launch.py
```

可用 Joint State Publisher GUI 拖动关节。

辅助工具（可选）：[RosTeamWS 机器人描述相关指南](https://stoglrobotics.github.io/ros_team_workspace/master/use-cases/ros_packages/setup_robot_description_package.html)

---

## 第 2 步：Mock Hardware 快速测试

### 目标

- 理解 Mock Hardware 是什么、怎么用
- 在上仿真/真机之前，先验证控制器与参数

### 概念

Mock Hardware 根据 `<ros2_control>` 标签「假装」一层硬件接口，启动快、行为理想，适合先调控制器。  
**注意**：功能刻意受限——通常只是把同名 command 接口的值反映到 state 接口；对多数联调已够用。

建议：**新控制器或新配置先 Mock，再仿真，最后真机。**

### 配置要点

1. 在 `<ros2_control>` 下加 `hardware`，插件用 `mock_components/GenericSystem`，并设置 `mock_sensor_commands` 等参数（可为传感器造假命令接口）。
2. 编写 `rrbot.launch.py`，用正确的 robot description 启动 `ros2_control` 节点。

目前主要是 `GenericSystem`；传感器 / 执行器也可被它「降配」模拟。

### 现成控制器练习

为 RRBot 配置：

- `Joint State Broadcaster`：产生 `/joint_states`
- `Forward Command Controller`：直接发关节位置命令
- `Joint Trajectory Controller`：在目标点之间插值轨迹

Launch 中加载并激活控制器，然后测试。

### 运行示例

```bash
ros2 launch controlko_bringup rrbot.launch.py
```

向 forward 控制器发命令：

```bash
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "
layout:
 dim: []
 data_offset: 0
data:
 - 0.7
 - 0.7"
```

改用关节轨迹控制器：

```bash
ros2 launch controlko_bringup rrbot.launch.py robot_controller:=joint_trajectory_controller
```

另一终端发测试轨迹（依赖 `ros2_controllers_test_nodes`，见下一节）：

```bash
ros2 launch controlko_bringup test_joint_trajectory_controller.launch.py
```

复杂系统可对控制器启动加短暂延时，按场景调整。

---

## 如何使用 `ros2_controllers_test_nodes`

该包提供**测试用命令发布节点**：按 YAML 中的目标，周期性向控制器话题发指令。  
**本身不启动仿真/机器人**，必须先把 RRBot（或其它已激活对应控制器的系统）跑起来。

### 安装

```bash
sudo apt install ros-humble-ros2-controllers-test-nodes
```

安装后确认：

```bash
ros2 pkg prefix ros2_controllers_test_nodes
ros2 pkg executables ros2_controllers_test_nodes
```

### 配合本工作坊（推荐）

**终端 1：启动机器人并指定控制器**

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
source ~/ros2bookcode/roscon2022_ws/install/setup.bash

# 轨迹控制器
ros2 launch controlko_bringup rrbot.launch.py \
  robot_controller:=joint_trajectory_controller
```

**终端 2：启动测试发布节点**

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
source ~/ros2bookcode/roscon2022_ws/install/setup.bash

ros2 launch controlko_bringup test_joint_trajectory_controller.launch.py
```

RViz 中应看到两关节在多个目标位姿间往返。

**Forward 控制器版本：**

```bash
# 终端 1
ros2 launch controlko_bringup rrbot.launch.py \
  robot_controller:=forward_position_controller

# 终端 2
ros2 launch controlko_bringup test_forward_position_controller.launch.py
```

### 包内可执行文件

| 可执行文件 | 作用 |
|------------|------|
| `publisher_joint_trajectory_controller` | 向 `/joint_trajectory_controller/joint_trajectory` 发轨迹点 |
| `publisher_forward_position_controller` | 向 forward 控制器发位置数组 |

### 目标配置文件

路径：`controlko_bringup/config/test_goal_publishers_config.yaml`

- JTC：每隔约 6 秒依次发布 `pos1` → `pos2` → `pos3` → `pos4`（约 ±0.785 rad）
- Forward：每隔约 5 秒发布同样几组位置

### 不通过 launch、直接运行节点

```bash
ros2 run ros2_controllers_test_nodes publisher_joint_trajectory_controller \
  --ros-args --params-file \
  $(ros2 pkg prefix controlko_bringup)/share/controlko_bringup/config/test_goal_publishers_config.yaml
```

### 排查

```bash
ros2 topic echo /joint_trajectory_controller/joint_trajectory
ros2 control list_controllers
```

对应控制器（如 `joint_trajectory_controller`）必须为 **`active`**，否则发布了也不会动。

若报错 `package 'ros2_controllers_test_nodes' not found`：先 `sudo apt install ros-humble-ros2-controllers-test-nodes`，再重新 `source /opt/ros/humble/setup.bash`。

---

## 第 3 步：四大组件角色

再启动第 2 步示例，思考：

1. **Controller Manager** 是什么？在哪里？
2. **Controllers** 是什么？在 ROS 2 里如何体现？
3. **Resource Manager** 是什么？在哪看到？如何访问？
4. **Hardware Interface** 是什么？存放在哪？如何交互？

架构图：[ros2_control Overview](https://control.ros.org/master/_images/ros2_control_overview.png)

简要对应关系：

| 组件 | 作用 |
|------|------|
| Controller Manager | 加载/切换/管理控制器与硬件组件生命周期 |
| Controllers | 算法与 ROS 接口（话题、服务）；激活后直接读写硬件导出的接口 |
| Resource Manager | 登记并管理硬件导出的接口资源，防止冲突占用 |
| Hardware Interface | 驱动层，对接 Mock / 仿真 / 真机 |

---

## 第 4 步：系统自省（Introspection）

可用两种方式：

1. CLI：`ros2 control <命令>`（包 `ros2controlcli`）
2. 直接调用 Controller Manager 的服务

### 练习问题与参考命令

| 问题 | 参考做法 |
|------|----------|
| 加载了哪些控制器？ | `ros2 control list_controllers` |
| 控制器状态？ | 同上 |
| 有哪些硬件组件、状态如何？ | `ros2 service call /controller_manager/list_hardware_components controller_manager_msgs/srv/ListHardwareComponents {}` |
| 有哪些硬件接口？ | `ros2 control list_hardware_interfaces` |
| 如何在 forward 与 JTC 间切换？ | 见下方切换示例 |
| 并行跑所有控制器会怎样？ | 尝试激活冲突控制器，看 `ros2_control_node` 终端报错 |
| 控制器用了哪些接口？ | `ros2 control list_controllers -v` |

切换示例：

```bash
ros2 run controller_manager spawner forward_position_controller --inactive
ros2 control switch_controllers \
  --deactivate joint_trajectory_controller \
  --activate forward_position_controller
```

图形工具：`rqt_controller_manager`、`rqt_joint_trajectory_controller`。

---

## 第 5 步：Gazebo Classic / Gazebo 仿真

仿真器通过专用插件扩展 Controller Manager，并按 `<ros2_control>` 中的接口名（常见 `position` / `velocity` / `effort`）接到仿真内部状态。

| 仿真器 | 包 | 仿真插件 | 硬件插件 |
|--------|----|----------|----------|
| Gazebo Classic | `gazebo_ros2_control` | `libgazebo_ros2_control.so` | `gazebo_ros2_control/GazeboSystem` |
| Gazebo (Ign/Gz) | `ign_ros2_control` / `gz_ros2_control` | `libign_ros2_control-system.so` 等 | `ign_ros2_control/IgnitionSystem` |

### 本机依赖（解决 `ros_ign_gazebo` not found）

`rrbot_sim_gazebo.launch.py` 会查找包 **`ros_ign_gazebo`**。Humble 上请安装：

```bash
sudo apt install ros-humble-ros-ign-gazebo ros-humble-ign-ros2-control
# 或新命名：
# sudo apt install ros-humble-ros-gz-sim ros-humble-gz-ros2-control
```

装完后重新 source：

```bash
source /opt/ros/humble/setup.bash
source ~/ros2bookcode/roscon2022_ws/install/setup.bash
```

若暂时不想装新 Gazebo，可改用 **Classic**（本机通常已有 `gazebo_ros`）：

```bash
ros2 launch controlko_bringup rrbot_sim_gazebo_classic.launch.py
```

### 任务要点

1. 在 `rrbot.urdf.xacro` 增加 `<gazebo>`，声明仿真插件与参数  
2. 在 `rrbot_macro.ros2_control.xacro` 的 `<ros2_control>` 中填写对应 HW 插件  
3. 增加 Classic / Gazebo 启动文件  

### 运行

```bash
# 方式 A：Gazebo Classic（推荐先试这个）
ros2 launch controlko_bringup rrbot_sim_gazebo_classic.launch.py

# 方式 B：Gazebo / Ignition（需已安装 ros-ign-gazebo）
ros2 launch controlko_bringup rrbot_sim_gazebo.launch.py

# 另一终端发轨迹测试
ros2 launch controlko_bringup test_joint_trajectory_controller.launch.py
```

仿真时注意宏文件中定义的关节限位。

---

## 第 6 步：控制器与硬件生命周期

生命周期状态与 **Lifecycle Node** 一致。硬件接口生命周期图：

[Hardware Interface Lifecycle](https://control.ros.org/master/_images/hardware_interface_lifecycle.png)

### 练习

1. 用 Mock 启动 RRBot  
2. 查看控制器与硬件组件状态  
3. 激活 `joint_trajectory_controller`（可能需先停掉占用相同接口的控制器）  
4. 将硬件设为 `inactive`，观察系统内部状态  
5. 试用 RQT Controller Manager  

### 参考命令

```bash
ros2 launch controlko_bringup rrbot.launch.py

# 另开终端
ros2 control list_controllers
ros2 service call /controller_manager/list_hardware_components \
  controller_manager_msgs/srv/ListHardwareComponents {}
```

切换到 JTC（多种写法之一）：

```bash
ros2 control load_controller joint_trajectory_controller
ros2 control set_controller_state joint_trajectory_controller inactive
ros2 control switch_controllers \
  --deactivate forward_position_controller \
  --activate joint_trajectory_controller
```

将硬件设为 inactive：

```bash
ros2 control switch_controllers --deactivate joint_trajectory_controller

ros2 service call /controller_manager/list_hardware_components \
  controller_manager_msgs/srv/ListHardwareComponents {}

ros2 service call /controller_manager/set_hardware_component_state \
  controller_manager_msgs/srv/SetHardwareComponentState "
name: rrbot
target_state:
 id: 0
 label: inactive"

ros2 control list_controllers
ros2 control list_hardware_interfaces
```

---

## 第 7 步：编写 Hardware Interface

Hardware Interface 是对接真实硬件的最底层驱动，向框架导出接口供控制器读写。生命周期各阶段调用哪些方法，见第 6 步图与官方文档。

### 任务要点

包名：`controlko_hardware_interface`

1. 使用头文件库 `dr_denis_rrbot_comms.hpp` 与 RRBot「通信」  
2. 按官方手册实现：[Writing a new hardware interface](https://control.ros.org/master/doc/ros2_control/hardware_interface/doc/writing_new_hardware_interface.html)  
3. 修改 URDF，指向该硬件插件  

实现时注意：

- 支持哪些控制模式？  
- 激活不兼容的控制器时会发生什么？  
- 能力（capabilities）如何声明？  

### 运行与验证

```bash
ros2 launch controlko_bringup rrbot.launch.py use_mock_hardware:=false
```

分别用 `forward_position_controller`、`joint_trajectory_controller` 测试；再尝试激活不兼容控制器：

```bash
ros2 control load_controller incompatible_joint_trajectory_controller
ros2 control set_controller_state incompatible_joint_trajectory_controller inactive
ros2 control switch_controllers \
  --deactivate forward_position_controller \
  --activate incompatible_joint_trajectory_controller
```

---

## 第 8 步：编写 Controller

控制器一方面对接 ROS 话题/服务，另一方面实现控制算法。激活后通过「借出」的硬件接口直接读写内存中的命令/状态，保证确定性数据流。

### 任务要点

包：`controlko_controllers`

编写位移（displacement）控制器：输入关节位移，更新新的关节位置。

关注：

- 回调与 `update()` 之间如何交换数据  
- 状态如何发到 ROS 话题  
- **慢速模式**：位移减半  
- **命令只接受一次**（不持续复用旧命令）  
- 输入消息类型：`control_msgs/msg/JointJog`  

查看消息定义：

```bash
ros2 interface show control_msgs/msg/JointJog
```

官方手册：[Writing a new controller](https://control.ros.org/master/doc/ros2_controllers/doc/writing_new_controller.html)

参数可用 [generate_parameter_library](https://github.com/PickNikRobotics/generate_parameter_library) 生成；本仓库示例见：

- `controlko_controllers/src/displacement_controller.yaml`
- `controlko_controllers/test/displacement_controller_params.yaml`
- `controlko_controllers/test/displacement_controller_preceeding_params.yaml`（链路最前端时用）

### 运行

```bash
ros2 launch controlko_bringup rrbot.launch.py
```

然后按 bringup 配置加载/切换到 displacement 控制器，并向 `JointJog` 话题发命令（具体话题名以 YAML / `ros2 topic list` 为准）。

---

## 本地包一览

| 包 | 作用 |
|----|------|
| `controlko_description` | RRBot URDF/Xacro、RViz |
| `controlko_bringup` | Launch、控制器 YAML、仿真启动 |
| `controlko_hardware_interface` | RRBot 硬件插件示例 |
| `controlko_controllers` | Displacement 控制器示例 |
| `roscon2022_control_workshop` | 工作坊元包（若存在） |

主要 launch（`controlko_bringup`）：

- `rrbot.launch.py` — Mock / 真机硬件参数切换  
- `rrbot_sim_gazebo_classic.launch.py`  
- `rrbot_sim_gazebo.launch.py`  
- `test_joint_trajectory_controller.launch.py`  
- `test_forward_position_controller.launch.py`  

---

## 推荐学习顺序（结合本仓库）

1. 先读 [docs/ros2_control学习资料.md](../docs/ros2_control学习资料.md) 与 [chapt6/README.md](../chapt6/README.md)（FishBot 差速）  
2. 再按本工作坊第 1→2→4→6 步跑通 Mock 与生命周期  
3. 第 5 步接仿真；第 7→8 步深入驱动与自定义控制器  
4. 对照官方 [ros2_control_demos](https://control.ros.org/humble/doc/ros2_control_demos/doc/index.html)

---

## 参考链接

- 原英文 README：[`README.md`](README.md)
- 上游仓库：https://github.com/ros-controls/roscon2022_workshop
- Humble 文档：https://control.ros.org/humble/
- RosTeamWS 辅助脚本说明：https://stoglrobotics.github.io/ros_team_workspace/
