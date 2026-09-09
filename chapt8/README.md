# 第 8 章：pluginlib 与自定义 Nav2 规划器 / 控制器

本章先学习 `pluginlib`，再实现并接入自定义全局规划器与局部控制器。

## 环境要求

同第 7 章，额外需要：

```bash
sudo apt install ros-humble-pluginlib ros-humble-nav2-core ros-humble-nav2-costmap-2d
```

## 目录说明

```
chapt8/
├── learn_pluginlib/          # pluginlib 入门示例
│   └── src/motion_control_system/
└── chapt8_ws/                # 含自定义 Nav2 插件的完整仿真导航栈
    └── src/
        ├── nav2_custom_planner/
        ├── nav2_custom_controller/
        ├── fishbot_description/
        ├── fishbot_navigation2/   # nav2_params.yaml 已指向自定义插件
        └── ...
```

---

## 一、pluginlib 入门（`learn_pluginlib`）

### 编译与运行

```bash
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
cd /home/lyzn-robot/ros2bookcode/chapt8/learn_pluginlib
colcon build
source install/setup.bash

ros2 run motion_control_system test_plugin motion_control_system/SpinMotionController
```

接口 `MotionController`，插件实现 `SpinMotionController`，由 XML 注册后动态加载。

---

## 二、自定义 Nav2 插件（`chapt8_ws`）

| 包名 | 插件类 | 作用 |
|------|--------|------|
| `nav2_custom_planner` | `nav2_custom_planner/CustomPlanner` | 直线插值全局路径 |
| `nav2_custom_controller` | `nav2_custom_controller::CustomController` | 先转向再前进的局部控制 |

在 `fishbot_navigation2/config/nav2_params.yaml` 中已配置：

- `planner_server` → `CustomPlanner`
- `controller_server` → `CustomController`

### 编译

```bash
cd /home/lyzn-robot/ros2bookcode/chapt8/chapt8_ws
colcon build
source install/setup.bash
```

### 运行

```bash
# 终端 1
ros2 launch fishbot_description gazebo_sim.launch.py

# 终端 2
ros2 launch fishbot_navigation2 navigation2.launch.py
```

在 RViz 中设置初始位姿并给出导航目标，即可验证自定义规划/控制。

也可继续启动巡检：

```bash
ros2 launch autopatrol_robot autopatrol.launch.py
```

## 要点

1. `pluginlib` 支持在不改主程序的情况下替换算法实现。
2. Nav2 的 Planner / Controller 均为插件接口，便于定制。
3. 通过参数文件切换插件，便于对比默认算法与自定义算法。
