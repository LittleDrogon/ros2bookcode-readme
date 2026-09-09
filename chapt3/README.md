# 第 3 章：话题通信（Topic）与自定义消息

本章学习发布者/订阅者、turtlesim 控制，以及自定义消息 + Qt 状态显示。包含两个独立工作空间。

## 环境要求

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
```

可选依赖：

```bash
sudo apt install ros-humble-turtlesim python3-psutil qtbase5-dev
# 小说朗读示例（可选）
sudo apt install espeak-ng
sudo pip3 install espeakng   # 或使用系统包管理方式安装
```

---

## 一、`topic_ws`：turtlesim 与小说话题

### 编译

```bash
cd /home/lyzn-robot/ros2bookcode/chapt3/topic_ws
colcon build
source install/setup.bash
```

### 小海龟画圆 / 闭环控制

终端 1：

```bash
ros2 run turtlesim turtlesim_node
```

终端 2（画圆，发布 `/turtle1/cmd_vel`）：

```bash
ros2 run demo_cpp_topic turtle_circle
```

或闭环到点控制（订阅 `/turtle1/pose`，发布 `/turtle1/cmd_vel`）：

```bash
ros2 run demo_cpp_topic turtle_control
```

### 小说发布 / 订阅

小说发布节点会通过 HTTP 拉取文本并发布到话题 `novel`。可先在工作空间目录起 HTTP 服务（若代码指向本地文件/URL，按书中说明调整），然后：

```bash
ros2 run demo_python_topic novel_pub_node
ros2 run demo_python_topic novel_sub_node
```

订阅端可将收到的字符串送给 `espeak-ng` 朗读。

| 节点 | 话题 | 消息类型 |
|------|------|----------|
| `turtle_circle` | pub `/turtle1/cmd_vel` | `geometry_msgs/Twist` |
| `turtle_control` | sub `/turtle1/pose`, pub `/turtle1/cmd_vel` | `turtlesim/Pose`, `Twist` |
| `novel_pub_node` | pub `novel` | `example_interfaces/String` |
| `novel_sub_node` | sub `novel` | String |

---

## 二、`topic_practice_ws`：自定义消息与系统监控

### 包结构

| 包名 | 作用 |
|------|------|
| `status_interfaces` | 自定义消息 `SystemStatus.msg` |
| `status_publisher` | Python 发布系统状态（`psutil`） |
| `status_display` | C++ Qt 界面订阅并显示 |

### 编译与运行

```bash
cd /home/lyzn-robot/ros2bookcode/chapt3/topic_practice_ws
colcon build
source install/setup.bash

# 终端 1
ros2 run status_publisher sys_status_pub

# 终端 2（需图形界面）
ros2 run status_display sys_status_display
```

可用命令查看话题：

```bash
ros2 topic echo /sys_status
ros2 interface show status_interfaces/msg/SystemStatus
```

纯 Qt 示例（不依赖 ROS）：

```bash
ros2 run status_display hello_qt
```

## 要点

1. Topic 是一对多异步通信。
2. 自定义消息需独立接口包，并用 `rosidl` 生成。
3. 实践：采集数据发布 + GUI/工具订阅可视化。
