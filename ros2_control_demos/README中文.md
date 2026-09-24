# ros2_control_demos（中文说明）

> 本文为同目录 [README.md](README.md) 的中文翻译。本机若使用 **ROS 2 Humble**，请对照仓库的 `humble` 分支与 [Humble 文档](https://control.ros.org/humble/doc/ros2_control_demos/doc/index.html)。

本仓库提供 `ros2_control` 框架各类功能与能力的示例，包含若干简洁实现，用于演示不同概念。请选择与你的 ROS 2 发行版匹配的分支，并参阅 [control.ros.org](https://control.ros.org) 上的完整文档，参见下方「构建状态」表。

若希望按步骤动手练习 `ros2_control`，可参考 [ros-control/roscon2022_workshop](https://github.com/ros-controls/roscon2022_workshop) 仓库（本仓库旁亦有本地拷贝与中文说明）。

许可证：[Apache 2.0](https://opensource.org/licenses/Apache-2.0)

## 参与贡献

作为开源项目，我们欢迎每位贡献者，不论背景与经验。可挑选 [PR](https://github.com/ros-controls/ros2_control_demos/pulls) 进行评审，或 [创建自己的贡献](https://github.com/ros-controls/ros2_control_demos/contribute)！

若刚接触本项目，请阅读 [贡献指南](https://control.ros.org/rolling/doc/contributing/contributing.html) 了解如何入门。我们乐于协助你完成第一次贡献。

## 入门

请按 [Humble 文档中的安装说明](https://control.ros.org/humble/doc/ros2_control_demos/doc/index.html#installation) 安装。

**注意：** apt 中**没有** `ros-humble-ros2-control-demos` 这个元包（会报「无法定位软件包」）。请用本仓库源码编译。本机需使用 **`humble` 分支**（`master` 面向更新的 ROS 2，与 Humble 不兼容）。

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

# 若尚未切到 humble 分支：
cd ~/ros2bookcode/ros2_control_demos
git fetch upstream humble   # 或：git fetch origin humble
git checkout humble

# 工作空间（已建好可用现成的）
cd ~/ros2bookcode/ros2_control_demos_ws
colcon build --packages-up-to ros2_control_demo_example_1
source install/setup.bash

ros2 launch ros2_control_demo_example_1 rrbot.launch.py
```

## 内容

本演示仓库包含以下示例：

### Example 1: [RRBot](example_1)

*RRBot*（Revolute-Revolute Manipulator Robot）——简单的位置控制机器人，仅一个硬件接口。该示例也演示如何在不同控制器之间切换。

### Example 2: [DiffBot](example_2)

*DiffBot*（Differential Mobile Robot）——简单的差速移动底盘。机器人本质上是一个按差速运动学运动的盒子。

### Example 3: [带多种接口的 RRBot](example_3)

具有多种接口的 *RRBot*。

### Example 4: [集成传感器的工业机器人](example_4)

带集成传感器的 *RRBot*。

### Example 5: [外接传感器的工业机器人](example_5)

带外部连接传感器的 *RRBot*。

### Example 6: [各执行器独立通信的模块化机器人](example_6)

演示如何实现与每个执行器分别通信的机器人硬件。

### Example 7: [六自由度机器人](example_7)

面向中级 ROS 2 用户的 6 自由度机器人完整教程。

### Example 8: [使用传动（transmissions）](example_8)

暴露传动接口的 *RRBot*。

### Example 9: [Gazebo 仿真](example_9)

演示如何在仿真与真实硬件之间切换。

### Example 10: [带 GPIO 接口的工业机器人](example_10)

带 GPIO 接口的 *RRBot*。

### Example 11: [使用转向控制器库的类车机器人](example_11)

类车结构，使用转向控制器库。

### Example 12: [控制器链式（chaining）](example_12)

演示一个简单的可链式控制器，以及如何组成控制器链来控制 *RRBot* 的关节。

### Example 13: [多机器人系统与硬件生命周期管理](example_13)

演示如何在**同一个** controller manager 实例中管理多台机器人。

### Example 14: [执行器不提供状态、并带额外传感器的模块化机器人](example_14)

演示如何实现：执行器不提供状态反馈、且带有额外传感器的机器人硬件。

### Example 15: [使用多个 controller manager](example_15)

演示如何在不同 controller manager 实例下集成多台机器人。

### Example 16: [带链式控制器的 DiffBot](example_16)

演示如何用 `diff_drive_controller` 与两个 `pid_controller` 组成链式控制器，控制差速机器人。

### Example 17: [硬件组件发布诊断信息的 RRBot](example_17)

演示如何在硬件组件中，使用 Controller Manager 传入的 Executor 发布诊断（diagnostics）。

## 目录结构

仓库按 `example_XY` 文件夹组织，每个文件夹是一个完整的包，包名形如 `ros2_control_demos_example_XY`（运行时常见包名也可能是 `ros2_control_demo_example_XY`，以本地 `package.xml` 为准）。

各包内子目录结构如下：

- `bringup`：存放演示机器人的 launch 文件与运行时配置
- `description`：存放示例机器人的 URDF（及 XACRO）、RViz 配置与网格模型
- `hardware`：存放示例硬件组件（接口）的实现
- `controllers`（可选）：存放示例控制器实现

每个示例中建议重点查看的文件：

- `bringup/launch/示例名.launch.py`：该示例的 launch 文件
- `bringup/config/示例名_controllers.yaml`：该示例的控制器参数配置
- `description/示例名.ros2_control.xacro`：含 ros2_control URDF 标签的硬件与参数 XACRO
- `description/示例名.urdf.xacro`：示例主描述文件，用于即时生成 URDF，并发布到 `/robot_description`
- `hardware/示例名.hpp`：示例硬件组件头文件
- `hardware/示例名.cpp`：示例硬件组件源文件
- `controllers/示例名.hpp`：示例控制器头文件
- `controllers/示例名.cpp`：示例控制器源文件

**注意**：本仓库给出的包/目录/文件结构**不推荐**直接用于你的真实机器人项目。通常应将上述目录拆成独立包，命名约定为 `机器人名或类型/bringup`、`description`、`hardware`、`controllers`。

更标准的结构可参考 Dave Coleman 的 [ros_control_boilerplate](https://github.com/PickNikRobotics/ros_control_boilerplate)，或 Stogl Robotics 的 [ros_team_workspace 文档](https://rtw.stoglrobotics.de/master/guidelines/robot_package_structure.html)。

本包中的概念主要通过虚构的 *RRBot* 与 *DiffBot* 演示；二者是用于展示并测试 `ros2_control` 概念的简易仿真机器人。

## 构建状态

| ROS 2 发行版 | 分支 | 文档 |
| --- | --- | --- |
| Rolling | [master](https://github.com/ros-controls/ros2_control_demos/tree/master) | [文档](https://control.ros.org/rolling/doc/ros2_control_demos/doc/index.html) |
| Lyrical | [master](https://github.com/ros-controls/ros2_control_demos/tree/master) | [文档](https://control.ros.org/lyrical/doc/ros2_control_demos/doc/index.html) |
| Kilted | [master](https://github.com/ros-controls/ros2_control_demos/tree/master) | [文档](https://control.ros.org/kilted/doc/ros2_control_demos/doc/index.html) |
| Jazzy | [jazzy](https://github.com/ros-controls/ros2_control_demos/tree/jazzy) | [文档](https://control.ros.org/jazzy/doc/ros2_control_demos/doc/index.html) |
| Humble | [humble](https://github.com/ros-controls/ros2_control_demos/tree/humble) | [文档](https://control.ros.org/humble/doc/ros2_control_demos/doc/index.html) |

构建徽章与 CI 细节见英文 [README.md](README.md)。

## 致谢

本项目得到多家公司与机构的重要贡献，名单见 [control.ros.org 致谢页](https://control.ros.org/rolling/doc/acknowledgements/acknowledgements.html)。
