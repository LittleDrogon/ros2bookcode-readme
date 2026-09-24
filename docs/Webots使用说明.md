# Webots 使用说明（对话记录）

本文整理自近期三次对话：Webots 如何使用、已安装后的空世界操作、以及 Open Sample World 内容说明。  
环境假设：**Ubuntu 22.04 + ROS 2 Humble**，本机 Webots 为 **R2025a**（路径示例：`~/.ros/webotsR2025a/webots/`）。  
本仓库（`ros2bookcode`）当前无 Webots 示例代码。

---

## 一、Webots 如何使用

### 1. 安装

```bash
# 安装 Webots（任选其一）
# 官方 deb：https://cyberbotics.com/#download
# 或 snap：
sudo snap install webots

# ROS 2 接口
sudo apt install ros-humble-webots-ros2
```

若 Webots 不在默认路径，指定：

```bash
export WEBOTS_HOME=/usr/local/webots   # 按实际安装路径改
```

### 2. 先跑官方示例

```bash
source /opt/ros/humble/setup.bash
ros2 launch webots_ros2_universal_robot multirobot_launch.py
```

会打开 Webots，并带上 ROS 2 节点。也可用 TurtleBot3 等包：

```bash
ros2 launch webots_ros2_turtlebot robot_launch.py
```

### 3. 基本操作（Webots 界面）

| 操作 | 说明 |
|------|------|
| 世界文件 `.wbt` | 场景 + 机器人模型 |
| 播放 / 暂停 | 顶部仿真控制 |
| 树形 Scene Tree | 改物体、传感器、控制器 |
| 机器人 `controller` | 可设为 `<extern>`，交给 ROS 控制 |
| 键盘/鼠标 | 视角；`Ctrl+F10` 等可开传感器射线显示 |

单独打开 Webots：`webots`，再 `File → Open World` 选 `.wbt`。

### 4. 和 ROS 2 联用（推荐路径）

核心包是 `webots_ros2_driver`：

1. 准备 `worlds/xxx.wbt`（机器人 controller 用 `<extern>`）
2. 用 URDF 描述机器人，并用 `<ros2_control>` / `<plugin>` 挂传感器、驱动
3. Launch 里用 `WebotsLauncher` 开仿真、`WebotsController` 连机器人
4. 你的节点照常订阅 `/scan`、`/odom`，发布 `/cmd_vel`

官方教程：

- [安装与跑示例](https://docs.ros.org/en/humble/Tutorials/Advanced/Simulators/Webots/Installation-Ubuntu.html)
- [基础仿真搭建](https://docs.ros.org/en/humble/Tutorials/Advanced/Simulators/Webots/Setting-Up-Simulation-Webots-Basic.html)
- [传感器与避障进阶](https://docs.ros.org/en/humble/Tutorials/Advanced/Simulators/Webots/Setting-Up-Simulation-Webots-Advanced.html)

### 5. 和书里 Gazebo 流程的对应关系

| 你熟悉的 | Webots |
|----------|--------|
| `.world` / Gazebo | `.wbt` |
| URDF + gazebo 插件 | URDF + `webots_ros2` 插件 |
| `ros2_control` + Gazebo | `ros2_control` + Webots 驱动 |
| `gz sim` / `gazebo` | `webots` / `WebotsLauncher` |

---

## 二、已经安装了 Webots（空世界怎么走）

打开空世界 `empty.wbt` 时，中间黑屏是正常的（场景里还没有物体）。

### 马上能看到东西

**方法 A：打开自带示例世界**

菜单 `File → Open Sample World...`，例如：

- `robots/gctronic/e-puck/e-puck.wbt`
- `robots/universal_robots/ure.wbt`

打开后点工具栏绿色 **播放**，机器人就会动。

**方法 B：在空世界里加东西**

1. 左侧 Scene Tree 点上方 **+**（Add）
2. 加 `Floor` → 再加机器人（如 `E-puck` / `TurtleBot3Burger`）
3. 选中机器人，在右侧属性里看 `controller`（示例控制器或 `<extern>` 给 ROS 用）
4. 点 **播放**

### 和 ROS 2 一起用（Humble）

另开终端：

```bash
source /opt/ros/humble/setup.bash
# 若 snap/自定义路径安装，按实际改：
# export WEBOTS_HOME=/usr/local/webots

sudo apt install ros-humble-webots-ros2   # 若还没装接口包
ros2 launch webots_ros2_turtlebot robot_launch.py
```

这会自己起 Webots + ROS 节点；不必先手动开这个空世界。

### 界面分区说明

| 区域 | 作用 |
|------|------|
| 左侧 Scene Tree | 世界里的节点（`WorldInfo`、`Viewpoint`…） |
| 中间 3D 视图 | 仿真画面（空世界所以是黑的） |
| 顶部 ▶ ⏸ | 运行 / 暂停 / 单步 |
| 右侧 Text Editor | 写控制器代码 |
| 底部 Console | 日志（刚启动时常只有 Welcome） |

---

## 三、Open Sample World 里面有哪些东西

`Open Sample World` 打开的是本机 Webots 自带示例，路径大约在：

`~/.ros/webotsR2025a/webots/projects/`

一共大约 **300 个 `.wbt` 世界**，对话框里大致按这些目录分。

### 顶层分类

| 目录 | 内容 |
|------|------|
| **robots/** | 各品牌现成机器人场景（最多、最常用） |
| **samples/** | 教程、演示、传感器用法、竞赛场景 |
| **vehicles/** | 汽车 / 城市 / 公路驾驶仿真 |
| **humans/** | 行人、骨骼动画等 |
| **objects/** | 家具、建筑、障碍物等（多为可插入节点，不全是完整世界） |
| **devices/** | 传感器/电机设备示例 |
| **default/** | 默认空世界等 |

### robots/（品牌示例）

常见、和书本/ROS 相关的例如：

- **移动机器人**：`robotis/turtlebot`（TurtleBot3）、`gctronic/e-puck`、`adept/pioneer3`、`irobot/create`、`husarion/rosbot`、`mir/mir100`
- **机械臂**：`franka_emika/panda`、`universal_robots/ure`、`abb/irb`、`kuka/youbot`、`niryo/ned`
- **人形/四足**：`softbank/nao`、`robotis/darwin-op`、`boston_dynamics/spot`、`boston_dynamics/atlas`
- **无人机**：`dji/mavic`、`bitcraze/crazyflie`
- **其他**：`pal_robotics/tiago`、`nvidia/jetbot`、`clearpath/*` 等

### samples/（学功能用）

| 子目录 | 用途 |
|--------|------|
| **tutorials/** | 入门：`my_first_simulation`、`4_wheels_robot`、避障等 |
| **demos/** | 展示：足球、六足、月球车等 |
| **devices/** | 激光、距离传感器、电机、GPS、力传感器等 |
| **howto/** | 进阶技巧：倒立摆、全向轮、视觉、OpenAI Gym 等 |
| **contests/** | RoboCup、Rat’s Life 等竞赛世界 |
| **mybot/** | 自定义小车示例 |

### vehicles/

城市、村庄、高速公路、夜间、超车等自动驾驶相关场景（`city.wbt`、`highway.wbt` 等）。

### 建议先开这几个

1. `samples/tutorials/worlds/my_first_simulation.wbt` — 入门  
2. `robots/gctronic/e-puck/worlds/e-puck.wbt` — 经典小车  
3. `robots/robotis/turtlebot/worlds/turtlebot3_burger.wbt` — 和 ROS 导航接近  
4. `robots/franka_emika/panda/worlds/panda.wbt` — 和 MoveIt Panda 对应  

打开后点顶部 **播放** 即可跑仿真。
