# 第 5 章：TF 坐标变换、Git 与 Rosbag

本章学习静态/动态 TF 广播与监听，并附带 Git 练习包与示例 rosbag。

## 环境要求

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
sudo apt install ros-humble-tf2-ros ros-humble-tf2-tools ros-humble-tf-transformations
sudo pip3 install transforms3d   # Python TF 示例常用
```

## 目录说明

```
chapt5/
├── chapt5_ws/src/
│   ├── demo_cpp_tf/      # C++ static / dynamic / listener
│   └── demo_python_tf/   # Python 对应实现
├── learn_git/            # Git 练习用空包
├── rosbag2_2023_12_11-01_57_18/   # 示例 bag
└── rviz_tf.rviz          # TF 可视化配置（若存在）
```

## 编译

```bash
cd /home/lyzn-robot/ros2bookcode/chapt5/chapt5_ws
colcon build
source install/setup.bash
```

## 运行 C++ TF 示例

三个终端分别启动：

```bash
ros2 run demo_cpp_tf static_tf_broadcaster    # map → target_point
ros2 run demo_cpp_tf dynamic_tf_broadcaster   # map → base_link（周期性）
ros2 run demo_cpp_tf tf_listener              # 查询 base_link → target_point
```

查看坐标系树：

```bash
ros2 run tf2_tools view_frames
# 生成 frames.pdf
```

RViz：

```bash
rviz2
# Fixed Frame 设为 map，添加 TF 显示
```

## 运行 Python TF 示例

```bash
ros2 run demo_python_tf static_tf_broadcaster   # base_link → camera_link
ros2 run demo_python_tf dynamic_tf_broadcaster  # camera_link → bottle_link
ros2 run demo_python_tf tf_listener             # base_link → bottle_link
```

注意：C++ 与 Python 示例的坐标系命名不完全相同，请按语言成套运行。

## Rosbag

```bash
cd /home/lyzn-robot/ros2bookcode/chapt5
ros2 bag info rosbag2_2023_12_11-01_57_18
ros2 bag play rosbag2_2023_12_11-01_57_18
```

## Git 练习

```bash
cd /home/lyzn-robot/ros2bookcode/chapt5/learn_git
# 按书中步骤练习 git init / add / commit / branch 等
```

## 要点

1. TF 描述坐标系之间的变换，是机器人感知与控制的基础。
2. 静态 TF 适合固定安装关系；动态 TF 适合运动关节/里程计。
3. Listener 通过 `lookupTransform` 查询任意两帧关系。
