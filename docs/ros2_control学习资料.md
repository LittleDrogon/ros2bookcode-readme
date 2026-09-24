# ros2_control 学习资料（Humble）

环境：Ubuntu 22.04 + ROS 2 Humble。本机已安装 `ros-humble-ros2-control`、`ros-humble-ros2-controllers` 等包。

---

## 一、本仓库实践（上手最快）

| 路径 | 说明 |
|------|------|
| [chapt6/README.md](../chapt6/README.md) | 第 6 章：URDF / Gazebo / ros2_control（FishBot 差速） |
| `chapt6/.../urdf/fishbot/fishbot.ros2_control.xacro` | 硬件接口描述 |
| `chapt6/.../config/fishbot_ros2_controller.yaml` | 控制器配置 |
| `chapt6/.../launch/gazebo_sim.launch.py` | Gazebo + controller_manager 启动 |

快速跑通：

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
cd /home/lyzn-robot/ros2bookcode/chapt6/chapt6_ws
colcon build && source install/setup.bash
ros2 launch fishbot_description gazebo_sim.launch.py
```

键盘遥控（话题名以 `ros2 topic list | grep cmd_vel` 为准）：

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r /cmd_vel:=/diff_drive_controller/cmd_vel_unstamped
```

---

## 二、官方文档（Humble）

| 资源 | 链接 | 说明 |
|------|------|------|
| 文档首页 | https://control.ros.org/humble/ | 总入口 |
| Getting Started | https://control.ros.org/humble/doc/getting_started/getting_started.html | 安装、架构、Controller Manager |
| Demos 索引 | https://control.ros.org/humble/doc/ros2_control_demos/doc/index.html | 官方示例总目录 |
| Example 1 RRBot | https://control.ros.org/humble/doc/ros2_control_demos/example_1/doc/userdoc.html | 最简单：加载/切换控制器 |
| Example 7 六轴 | https://control.ros.org/humble/doc/ros2_control_demos/example_7/doc/userdoc.html | URDF + Hardware + Controller 全流程 |
| Controllers 列表 | https://control.ros.org/humble/doc/ros2_controllers/doc/controllers_index.html | 差速、轨迹、关节状态广播等参数 |

源码仓库（选 `humble` 分支）：

- https://github.com/ros-controls/ros2_control_demos
- https://github.com/ros-controls/ros2_control
- https://github.com/ros-controls/ros2_controllers

---

## 三、官方演示包（本机可装）

```bash
sudo apt install ros-humble-ros2-control-demos
source /opt/ros/humble/setup.bash

# Example 1：两关节 RRBot
ros2 launch ros2_control_demo_example_1 rrbot.launch.py
```

其他常用示例包名形如 `ros2_control_demo_example_N`，详见 [Demos 索引](https://control.ros.org/humble/doc/ros2_control_demos/doc/index.html)。

---

## 四、推荐学习顺序

1. **本仓库 chapt6** — 差速底盘 + Gazebo，与书一致  
2. **官方 Example 1 RRBot** — 理解 controller 加载 / 切换  
3. **Example 2 DiffBot** — 移动底盘，与 FishBot 接近  
4. **Example 7** — 自己写 hardware interface / controller  
5. **可选工作坊** — [roscon2022_workshop](https://github.com/ros-controls/roscon2022_workshop)（步骤更细）

---

## 五、核心概念速记

| 概念 | 作用 |
|------|------|
| `ros2_control`（URDF 标签） | 声明关节接口：position / velocity / effort |
| Hardware Interface | 对接仿真或真机硬件 |
| Controller Manager | 加载、激活、切换控制器 |
| Controllers | 如 `diff_drive_controller`、`joint_trajectory_controller`、`joint_state_broadcaster` |
| YAML 配置 | 指定控制器类型、关节名、话题与限幅 |

仿真与真机尽量共用同一套 URDF + YAML，只替换 hardware 插件，这是 `ros2_control` 的主要价值。
