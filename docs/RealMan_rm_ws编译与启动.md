# 睿尔曼 RealMan ROS2 工作空间（~/rm_ws）

本机已将 `real-man_ros2_rm_robot` 链入并编译到：

```text
/home/lyzn-robot/rm_ws
```

源码：`/home/lyzn-robot/real-man_ros2_rm_robot`（symlink → `~/rm_ws/src/ros2_rm_robot`）

---

## 已编译包（摘要）

| 包 | 作用 |
|----|------|
| `rm_description` | URDF / meshes（含 `rm_65.urdf`） |
| `rm_65_config` 等 | 各机型 MoveIt2 配置（63/65/75/eco/gen72） |
| `rm_ros_interfaces` | 自定义消息 / 服务 |
| `rm_driver` / `rm_control` / `rm_bringup` 等 | 驱动、控制、启动相关 |

---

## 每次使用前（新终端）

```bash
# 建议先退出 conda，避免 Python/工具链干扰
conda deactivate 2>/dev/null

source /opt/ros/humble/setup.bash
source /home/lyzn-robot/rm_ws/install/setup.bash

# 自检
ros2 pkg prefix rm_description
ros2 pkg prefix rm_65_config
```

---

## 跑 RM65 MoveIt 虚拟臂 demo

```bash
source /opt/ros/humble/setup.bash
source /home/lyzn-robot/rm_ws/install/setup.bash

ros2 launch rm_65_config demo.launch.py
```

六维力等变体见同包 launch：`demo_6f.launch.py`、`demo_6fb.launch.py`。  
真机见：`real_moveit_demo.launch.py`（需驱动与网络配置正确）。

---

## MoveIt Setup Assistant 加载 URDF

必须先 source `~/rm_ws`，再启动助手，并选择：

```text
…/rm_description/share/rm_description/urdf/rm_65.urdf
```

注意：没有 `rml_65.urdf`；65 用 **`rm_65.urdf`**，63 用 `rml_63.urdf`。

```bash
source /opt/ros/humble/setup.bash
source /home/lyzn-robot/rm_ws/install/setup.bash
ros2 run moveit_setup_assistant moveit_setup_assistant
```

一般 **不必** 再为 65 跑 Setup Assistant，官方已提供 `rm_65_config`。

---

## 重新编译

```bash
cd /home/lyzn-robot/rm_ws
source /opt/ros/humble/setup.bash
# 避开 conda Python
export PATH="/usr/bin:$PATH"

colcon build --symlink-install \
  --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash
```

只编部分包示例：

```bash
colcon build --packages-select rm_description rm_65_config --symlink-install \
  --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
```

---

*整理日期：2026-09-23*
