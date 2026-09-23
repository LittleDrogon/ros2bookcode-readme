# MoveIt + RViz Demo 操作说明（ROS 2 Humble / Panda）

> 适用环境：Ubuntu 22.04 + ROS 2 Humble + MoveIt 2  
> 示例配置：`moveit_resources_panda_moveit_config`（Franka Emika Panda 仿真 demo）

---

## 1. 安装（若尚未安装）

```bash
sudo apt update
sudo apt install -y \
  ros-humble-moveit \
  ros-humble-moveit-setup-assistant \
  ros-humble-moveit-resources \
  ros-humble-moveit-resources-panda-moveit-config \
  ros-humble-moveit-visual-tools \
  ros-humble-moveit-configs-utils \
  ros-humble-moveit-py
```

验证：

```bash
source /opt/ros/humble/setup.bash
ros2 pkg list | grep moveit | head
```

---

## 2. 启动 Demo

```bash
source /opt/ros/humble/setup.bash
ros2 launch moveit_resources_panda_moveit_config demo.launch.py
```

正常会出现：

- **RViz2** 窗口（Panda 模型）
- **`move_group`**（规划）
- **`ros2_control`** 假控制器（仿真执行，不是真机）

---

## 3. RViz 界面认识

| 区域 | 作用 |
|------|------|
| 中间 3D 视图 | 看机械臂、轨迹、障碍物 |
| 左侧 **Displays** | 勾选 `MotionPlanning`、Planning Scene、Trajectory 等 |
| 右侧 **MotionPlanning** 面板 | 规划 / 执行 / 场景的主控台 |
| 末端 **交互标记**（坐标轴/圆环） | 拖目标位姿 |

若没有右侧面板：菜单 **Panels → MotionPlanning**。  
若没有交互球：在 MotionPlanning 里勾选 / 选中 **Query Goal State**。

常见颜色约定（以实际主题为准）：

- **当前 / Start（常偏橙）**：规划起点  
- **目标 / Goal（常偏绿）**：规划终点  

---

## 4. 基本操作：拖目标 → Plan → Execute

### 4.1 设定目标

1. 拖 **Goal（绿色）** 臂的末端箭头（平移）或圆环（旋转）。  
2. 也可打开面板 **Joints**，用滑条改关节角。  
3. Planning Group 一般选 **`panda_arm`**（夹爪另见下文）。

### 4.2 规划（Plan）

在 **MotionPlanning → Planning**：

1. 确认 Group = `panda_arm`  
2. 点击 **Plan**  
3. 成功：出现轨迹预览动画/彩线  
4. 失败：看 **Status** 与启动终端的报错（目标超限、自碰、撞障碍物等）

### 4.3 执行（Execute）

1. 点击 **Execute**，或使用 **Plan & Execute**  
2. 仿真中实体臂应运动到目标  

说明：demo 使用假控制器，流程与真机一致，但不会驱动真实硬件。

---

## 5. 建议第一次上手顺序

1. 只把 Goal 挪开一点 → **Plan** → 看轨迹  
2. **Execute** → 看臂跟上  
3. 再拖一个更远的目标 → Plan / Execute  
4. 在 **Scene Objects** 加一个 Box → 目标放到另一侧 → Plan，观察绕障  
5. 把 **Velocity Scaling**、**Acceleration Scaling** 调到 `0.2`～`0.5`，动作更慢、更好观察  

---

## 6. MotionPlanning 面板常用项

| 页签 / 选项 | 作用 |
|-------------|------|
| **Context** | 选择 Planning Pipeline / 规划库（如 OMPL） |
| **Planning** | Plan、Execute；速度/加速度缩放；重试等 |
| **Joints** | 按关节设定 Start / Goal |
| **Scene Objects** | 添加/移动盒子等碰撞物，测避障 |
| **Status** | 规划成功与否、错误信息 |

---

## 7. 夹爪（Hand）

1. Planning Group 切换为 **`hand`**（或面板中显示的 hand / panda_hand 名称）  
2. 用 Joints 或预设改开合  
3. **Plan** → **Execute**  

手臂规划时再切回 **`panda_arm`**。

---

## 8. 逐步自检清单（跟着做）

### 第 1 步：Plan

- [ ] 能看到 MotionPlanning 面板  
- [ ] 能拖动 Goal 末端  
- [ ] Group = `panda_arm`  
- [ ] 点击 **Plan** 出现轨迹  

若失败：记录 Status 文字，或保存启动终端最后 20 行日志。

### 第 2 步：Execute

- [ ] 点击 **Execute**  
- [ ] 实体臂移动到 Goal  

若不动：确认已 Plan 成功；看终端是否有 controller 报错。

### 第 3 步：避障（可选）

- [ ] Scene Objects → 添加 Box  
- [ ] Goal 放到箱子另一侧  
- [ ] Plan 得到绕行轨迹  

---

## 9. 常见问题

| 现象 | 处理 |
|------|------|
| 没有 MotionPlanning 面板 | **Panels → MotionPlanning** |
| 没有交互坐标轴 | 勾选 Query Goal；Displays 中启用 MotionPlanning |
| Plan 失败 | 目标不可达或碰撞；换姿态；检查是否穿模进桌子/箱子 |
| Execute 后不动 | 先确认 Plan 成功；查看 `ros2_control` / `move_group` 终端日志 |
| 动太快看不清 | Planning 里降低 Velocity / Acceleration Scaling |
| 想重新开干净环境 | 终端 `Ctrl+C` 停掉 launch，再重新 `ros2 launch ...` |

---

## 10. 常用命令速查

```bash
# 启动 Panda demo
source /opt/ros/humble/setup.bash
ros2 launch moveit_resources_panda_moveit_config demo.launch.py

# 查看 moveit 相关包
ros2 pkg list | grep moveit

# 查看当前机器人描述是否在发布（另开终端）
source /opt/ros/humble/setup.bash
ros2 topic list | grep -E 'joint_states|robot_description|display_planned'
```

---

## 11. 用 Python / MoveIt 程序控制仿真

仿真 `demo.launch.py` 已启动后，另开终端运行：

```bash
conda deactivate
export PATH="/usr/bin:$PATH"
bash /home/lyzn-robot/ros2bookcode/moveit_demos/panda_control/run_panda_moveit_demo.sh
```

脚本通过 `/move_action`（MoveGroup）驱动 RViz 里的 Panda，会依次：

1. 到命名位姿 `ready` → `extended`
2. 规划两个末端位姿目标
3. 开合夹爪
4. 回到 `ready`

源码：`moveit_demos/panda_control/panda_moveit_demo.py`。可改 `NAMED_JOINT_STATES` 或 `make_pose(...)` 自定义目标。

### Tkinter 控制面板（关节 / xyz / rpy / 速度）

```bash
bash /home/lyzn-robot/ros2bookcode/moveit_demos/panda_control/run_panda_moveit_gui.sh
```

面板提供：

- **J1–J7** 关节角（度）
- **X Y Z**、**Rx Ry Rz**（米 / 度）
- **Speed** 速度比例（同时缩放速度与加速度）
- 按钮：从机器人同步、执行关节运动、执行位姿运动、Ready / Extended、开合夹爪

源码：`moveit_demos/panda_control/panda_moveit_gui.py`。

---

## 12. 下一步可以做什么

- 用 **MoveIt Setup Assistant** 为自己的机械臂生成 config  
- 在自己的包里继续扩展本 demo（加障碍物、笛卡尔路径、视觉伺服等）  
- 把真机 `ros2_control` / 驱动换成真实控制器，替换 demo 的假控制器  

官方入口可参考：[MoveIt 2 文档](https://moveit.picknik.ai/)

---

*文档整理日期：2026-09-23*
