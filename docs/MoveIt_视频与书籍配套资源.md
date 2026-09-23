# MoveIt 视频与书籍配套学习资源

> 面向 ROS 2 Humble / MoveIt 2。  
> 说明：真正「一书一课」严格配套的不多；更多是「网文/网课 + 视频跟练」。

相关本地文档：

- [MoveIt + RViz Demo 操作说明](./MoveIt_RViz_Demo操作说明.md)
- [RealMan rm_ws 编译与启动](./RealMan_rm_ws编译与启动.md)
- [ROS2 话题/服务/动作/参数选型](./ROS2_话题服务动作参数选型.md)

---

## 1. 最贴本仓库（书/网文 + 视频）

### 1.1 鱼香 ROS《动手学 ROS2》

和当前 `ros2bookcode` / 鱼香书体系最配。

| 类型 | 链接 |
|------|------|
| 图文教程（Humble，含 MoveIt2 章） | [https://fishros.com/d2lros2/](https://fishros.com/d2lros2/) |
| 仓库 / 源码参考 | [fishros/d2l-ros2](https://github.com/fishros/d2l-ros2) |
| MoveIt2 相关介绍 | [微信一文](https://mp.weixin.qq.com/s/Lx-xLO_C9NKxCcRBHj2gUw) |

教程结构中含：**Moveit2 仿真 / 进阶 / 真机控制** 等章节。  
适合：跟着章节做，和现有书本、本仓库代码结构一致。

### 1.2 古月居（书城 / 网课 + B 站）

| 类型 | 链接 |
|------|------|
| 图书 / 图文 | [https://book.guyuehome.com/](https://book.guyuehome.com/) |
| 付费课程 | [https://class.guyuehome.com/](https://class.guyuehome.com/) |
| ROS2 基础视频 | [古月·ROS2入门21讲](https://www.bilibili.com/video/BV16B4y1Q7jQ/) |
| 机械臂原理（偏 ROS1 MoveIt，概念仍值一看） | [ROS机械臂开发原理](https://www.bilibili.com/video/BV14b411p7Hm/) |

适合：要系统课、愿意付费；具体 MoveIt2 专课以官网课表为准。

---

## 2. 官方文档配套视频（英文，质量高）

### 2.1 PickNik 跟官方 Tutorials 录屏

| 类型 | 链接 |
|------|------|
| 视频系列入口 | [Getting Started With MoveIt 2](https://picknik.ai/series/Getting-Started-With-Moveit2) |
| 对应官方文档 | [Getting Started](https://moveit.picknik.ai/main/doc/tutorials/getting_started/getting_started.html) |
| Humble 文档入口（更贴本机） | [https://moveit.picknik.ai/humble/](https://moveit.picknik.ai/humble/) |

适合：对着官方英文教程一步步做。  
若已用 `apt` 安装 MoveIt，可跳过「从源码编译整仓」段落，直接看 RViz / 第一个 C++ 项目等章节。

### 2.2 Udemy 项目课（付费、系统）

| 课程 | 链接 |
|------|------|
| ROS 2 MoveIt 2 - Control a Robotic Arm | [Udemy 课程页](https://www.udemy.com/course/ros2-moveit2/) |

内容大致覆盖：URDF → Setup Assistant → MoveIt 2 → ros2_control，偏实战。  
**不是**某本中文书的官方配套，但是英文里较完整的视频课之一。

---

## 3. 中文文档补充（非视频）

| 资源 | 说明 | 链接 |
|------|------|------|
| MoveIt 中文教程（个人翻译，Noetic） | ROS1 完整译，RViz 操作可参考，命令勿照抄到 ROS2 | [decyzy.github.io](https://decyzy.github.io/moveit_tutorials/index.html) |
| 社区 MoveIt2 入门摘译 | 个人转述 Getting Started，注意版本 | 如 [博客园·Moveit2入门](https://www.cnblogs.com/ai-ldj/p/18340781) |

官方 MoveIt 2 文档**没有**完整同步中文站；以英文官方 + 上述社区材料为准。

---

## 4. 怎么选（务实）

| 目标 | 建议 |
|------|------|
| 和当前鱼香书 / 本仓库同步 | **动手学 ROS2 MoveIt 章** + 本地 `MoveIt_RViz_Demo操作说明.md` |
| 学透官方流程（英文） | **PickNik 视频 + Humble 文档** |
| 从零做自己的六轴配置 | **Udemy MoveIt2 课** 或古月付费机械臂课 |
| 只要 RViz 拖拽玩明白 | 继续 Panda / `rm_65_config demo`，不必先追长视频 |
| 睿尔曼真机 / 仿真 | 见 `RealMan_rm_ws编译与启动.md` + 厂商 README |

---

## 5. 建议学习顺序（本机）

1. 跑通 Panda：`ros2 launch moveit_resources_panda_moveit_config demo.launch.py`  
2. 对照本地操作说明练 Plan / Execute  
3. 跑通睿尔曼：`ros2 launch rm_65_config demo.launch.py`（需先 `source ~/rm_ws/install/setup.bash`）  
4. 再跟鱼香 MoveIt 章或 PickNik / Udemy 深入 Setup Assistant、C++/Python API、真机  

---

## 6. 结论

- 中文里较少「纸质书严格绑定的 MoveIt2 全套视频」。  
- 最接近书课一体的是：**鱼香《动手学ROS2》+ 其视频/公众号**，以及 **古月居网课体系**。  
- 英文则是：**官方文档 + PickNik 跟练视频** 最正统；系统项目课可选 Udemy。  

---

*文档整理日期：2026-09-23*
