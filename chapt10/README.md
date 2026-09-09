# 第 10 章：ROS 2 进阶（Executor、Lifecycle、QoS、组合节点、消息过滤、DDS）

本章覆盖运行时与中间件层面的进阶用法，示例以 C++ / Python 成对提供。

## 环境要求

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash

sudo apt install \
  ros-humble-rclcpp-lifecycle \
  ros-humble-rclcpp-components \
  ros-humble-message-filters \
  ros-humble-example-interfaces
```

## 目录说明

```
chapt10/
├── chapt10_ws/
│   ├── src/
│   │   ├── learn_executor_cpp / learn_executor_py
│   │   ├── learn_lifecyclenode_cpp / learn_lifecyclenode_py
│   │   ├── learn_qos_cpp / learn_qos_py
│   │   ├── learn_compose
│   │   ├── learn_message_filter_cpp / learn_message_filter_py
│   │   └── learn_dds_cpp
│   ├── shm.xml                 # FastDDS 共享内存配置
│   └── topic_sub_limit.xml     # 限制订阅者数量示例
└── rosbag2_message_filter/     # 供 message_filters 回放
```

## 编译

```bash
cd /home/lyzn-robot/ros2bookcode/chapt10/chapt10_ws
colcon build
source install/setup.bash
```

---

## 1. Executor 与回调组

```bash
ros2 run learn_executor_cpp learn_executor
# 或
ros2 run learn_executor_py learn_executor
```

另开终端调用会故意耗时的服务，观察多线程执行器行为：

```bash
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 1, b: 2}"
```

---

## 2. Lifecycle Node

```bash
ros2 run learn_lifecyclenode_cpp learn_lifecyclenode
# 或 learn_lifecyclenode_py

ros2 lifecycle set /lifecyclenode configure
ros2 lifecycle set /lifecyclenode activate
ros2 lifecycle get /lifecyclenode
ros2 lifecycle set /lifecyclenode deactivate
ros2 lifecycle set /lifecyclenode shutdown
```

---

## 3. QoS

```bash
ros2 run learn_qos_cpp reliability_test
# 或
ros2 run learn_qos_py reliability_test
```

观察不同 Reliability / Durability / Deadline 对 `odom` 等话题匹配的影响。

---

## 4. 组件与进程内通信

```bash
ros2 run learn_compose intra_process_pubsub
```

或通过组件容器加载（若环境支持）：

```bash
ros2 run rclcpp_components component_container
# 另开终端 load talker/listener 组件
```

话题示例：`count`。

---

## 5. Message Filters 时间同步

```bash
# 终端 1：回放含 imu / odom 的 bag
cd /home/lyzn-robot/ros2bookcode/chapt10
ros2 bag play rosbag2_message_filter

# 终端 2
source /home/lyzn-robot/ros2bookcode/chapt10/chapt10_ws/install/setup.bash
ros2 run learn_message_filter_cpp timesync_test
# 或 learn_message_filter_py
```

---

## 6. DDS 共享内存 / Loaned Message

```bash
cd /home/lyzn-robot/ros2bookcode/chapt10/chapt10_ws
export FASTRTPS_DEFAULT_PROFILES_FILE=$(pwd)/shm.xml
ros2 run learn_dds_cpp shm_pub
```

`topic_sub_limit.xml` 可用于限制 `/chatter` 匹配订阅者数量等 DDS 实验。

---

## 要点

1. Executor 决定回调如何调度；回调组影响并行与互斥。
2. Lifecycle 适合需要明确启动/关闭流程的节点（如导航服务器）。
3. QoS 不匹配会导致“看起来有话题却收不到”。
4. 组合节点与零拷贝可降低进程间通信开销。
5. Message Filters 解决多传感器时间对齐问题。
