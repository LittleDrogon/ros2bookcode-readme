# orbbec_camera：`examples/` 与 `src/` 说明

> 路径：`Orbbec-Gemini-335L/OrbbecSDK_ROS2/orbbec_camera/`  
> 本文说明这两个目录里「产出什么、干什么」。  
> **重要：** `src/` 里几乎**不是「一个 .cpp = 一个可执行文件」**，而是打进共享库 + 主节点；真正独立可执行文件多在 `examples/`、`tools/`、`scripts/`，由 `CMakeLists.txt` 注册。

编译安装后，可执行文件一般在：

```text
install/orbbec_camera/lib/orbbec_camera/<名字>
# 或
ros2 run orbbec_camera <名字>
```

---

## 1. 和这两个目录相关的可执行文件一览

| 可执行名 | 源码位置 | 作用（一句话） |
|----------|----------|----------------|
| **`orbbec_camera_node`** | `src/ob_camera_node_driver.cpp`（插件入口）+ 整库 `src/*` | **主相机节点**：开流、发 topic、参数与服务；日常 `ros2 launch orbbec_camera ...` 用的就是它。 |
| **`435le_example_node`** | `examples/Gemini_435Le_example_node/camera_example_node.cpp` | 交互示例：读写标定、开关流、查设备信息/状态（菜单式）。 |
| **`image_sync_example_node`** | `examples/multi_camera_time_sync/image_sync_example_node.cpp` | 多路图像时间同步示例：订阅多相机 topic，近似时间同步并统计时间差 / 可选显示。 |

`examples/` 里其余多为 **launch.py**（启动配置），本身不是 C++ 可执行文件，而是拉起 `orbbec_camera_node` 等。

同包还有工具节点（源码在 `tools/`，不在这两个目录，但常一起用）：

| 可执行名 | 作用 |
|----------|------|
| `list_devices_node` | 列出已连接设备 |
| `list_depth_work_mode_node` | 列出深度工作模式 |
| `list_camera_profile_mode_node` | 列出相机 profile |
| `firmware_update_tool` | 固件升级 |
| `ip_config_tool` / `set_device_ip` | 配置 / 设置设备 IP |
| `topic_statistics_node` | topic 统计 |
| `ob_benchmark_node` | 性能压测相关 |
| `service_benchmark_node` | 服务压测 |
| `frame_latency_node` | 指定 topic 延迟 / FPS |
| `start_benchmark_node` | 启动压测订阅端 |
| `multi_save_rgbir_node` | 多机同步存 RGB/IR |

---

## 2. `examples/` — 示例与 launch

### 2.1 总览（官方 README 摘要）

| 子目录 | 作用 | 难度 |
|--------|------|------|
| `net_camera/` | 网络相机用法（Femto Mega、Gemini 335Le 等） | ⭐ |
| `gmsl_camera/` | GMSL 相机（Gemini 335Lg） | ⭐ |
| `benchmark/` | 各种配置下的性能压测 launch | ⭐⭐ |
| `multi_camera_synced_verification_tool/` | 多机硬件同步精度验证 | ⭐⭐⭐ |
| `multi_camera_time_sync/` | 软件侧多 topic 时间同步示例节点 | — |
| `Gemini_435Le_example_node/` | 服务调用示例可执行节点 | — |

### 2.2 各文件 / 目标

#### `net_camera/`

| 文件 | 作用 |
|------|------|
| `multi_net_camera.launch.py` | 启动多台**网口相机**（示例里用 `net_device_ip` 等参数），适合 Femto Mega / Gemini 335Le 等网络设备。 |

#### `gmsl_camera/`

| 文件 | 作用 |
|------|------|
| `gemini_330_gmsl.launch.py` | 单台 GMSL 接口 Gemini 330 系列启动。 |
| `multi_gmsl_camera.launch.py` | 多台 GMSL 相机（未强调硬件同步）。 |
| `multi_gmsl_camera_synced.launch.py` | 多台 GMSL **带同步**启动。 |

#### `benchmark/`

| 文件 | 作用 |
|------|------|
| `ob_benchmark_0.launch.py` / `ob_benchmark_1.launch.py` | 基准测试场景 launch（不同配置组合）。 |
| `gemini_330_series_benchmark.launch.py` | 针对 Gemini 330 系列的压测启动。 |

配合可执行节点如 `ob_benchmark_node`、`start_benchmark_node`、`frame_latency_node` 等使用。

#### `multi_camera_synced_verification_tool/`

| 文件 / 目录 | 作用 |
|-------------|------|
| `*.launch.py`（如 `gemini_synced_verify.launch.py` 等） | 启动多机同步采集，用于验证同步。 |
| `multicamera_sync/Python/SyncFramesMain.py` | Python 主脚本：按配置做帧匹配 / 同步分析。 |
| `multicamera_sync/Python/script/config_frameMatch*.py` | 不同机型 / 时间戳方案的帧匹配配置。 |
| `multicamera_sync/output/` | 样例输出（图像、匹配结果），不是程序源码。 |

#### `multi_camera_time_sync/`

| 文件 | 编译产物 | 作用 |
|------|----------|------|
| `image_sync_example_node.cpp` | **`image_sync_example_node`** | 用 `message_filters` 近似时间同步多路 `sensor_msgs/Image`；可自动发现 topic、统计时间差、可选 OpenCV 显示。用于验证多机/多流**软件时间对齐**效果。 |

#### `Gemini_435Le_example_node/`

| 文件 | 编译产物 | 作用 |
|------|----------|------|
| `camera_example_node.cpp` | **`435le_example_node`** | 菜单示例：写/读用户标定、`set_streams_enable`、查 `GetDeviceInfo`、看设备状态等。演示如何调相机 ROS 服务（不限只能 435Le 概念，菜单面向服务接口）。 |
| `README.MD` | — | 运行说明与菜单说明。 |

运行示例：

```bash
ros2 run orbbec_camera 435le_example_node
ros2 run orbbec_camera image_sync_example_node
```

---

## 3. `src/` — 库源码（组成 `liborbbec_camera` + 主节点）

这些 `.cpp` 编进共享库 **`liborbbec_camera.so`**。  
通过 `rclcpp_components` 注册插件后，对外主可执行名是：

**`orbbec_camera_node`** ← 插件类 `orbbec_camera::OBCameraNodeDriver`

日常用法：

```bash
ros2 launch orbbec_camera gemini_330_series.launch.py
# 内部起的就是 orbbec_camera_node
```

### 3.1 每个源文件干什么

| 源文件 | 角色 |
|--------|------|
| **`ob_camera_node_driver.cpp`** | **节点驱动入口**：创建/管理设备、生命周期、热插拔/重连、加载扩展与配置；封装并持有 `OBCameraNode`。**对应可执行 `orbbec_camera_node`。** |
| **`ob_camera_node.cpp`** | **核心业务（体量最大）**：开停流、发布彩色/深度/IR/点云等、对齐与滤波、参数应用、帧回调主逻辑。 |
| **`ob_lidar_node.cpp`** | **LiDAR 节点逻辑**：雷达设备开流、点云与相关属性（库内模块，供雷达产品路径使用）。 |
| **`ros_service.cpp`** | **ROS 服务实现**：设备信息、标定读写、开关流、AE ROI、各类控制服务等。 |
| **`ros_param_backend.cpp`** | 参数后端：与 ROS 参数服务器对接的底层封装。 |
| **`dynamic_params.cpp`** | 动态参数：运行时参数声明、回调、类型安全读写（`Parameters`）。 |
| **`image_publisher.cpp`** | 图像发布封装：直接 `rclcpp` 发布或经 `image_transport` 发布。 |
| **`synced_imu_publisher.cpp`** | IMU 同步发布：加速度计/陀螺仪数据按策略合成发布。 |
| **`d2c_viewer.cpp`** | D2C 可视化辅助：深度对齐到彩色相关的查看/叠加逻辑。 |
| **`jpeg_decoder.cpp`** | JPEG 解码基类实现（软解路径）。 |
| **`jetson_nv_decoder.cpp`** | Jetson 平台硬件 JPEG/多媒体解码（依赖 Jetson Multimedia API 时编入）。 |
| **`rk_mpp_decoder.cpp`** | Rockchip MPP 硬件解码路径。 |
| **`frame_timestamp_csv_logger.cpp`** | 帧时间戳 CSV 记录：便于分析同步/延迟（color/depth 等）。 |
| **`utils.cpp`** | 工具函数：错误格式化、图像/格式转换、设备辅助等公共代码。 |

### 3.2 数据流（简化）

```text
设备 (USB/Net/GMSL)
    → OBCameraNodeDriver（创建设备、重连）
        → OBCameraNode（开流、处理、发布 topic）
            → image_publisher / synced_imu_publisher / …
            → ros_service（对外服务）
            → 可选 jpeg/jetson/rk 解码器
```

---

## 4. 怎么对应「我想跑什么」

| 需求 | 用什么 |
|------|--------|
| 正常开相机出图 | launch + **`orbbec_camera_node`**（`src` 整库） |
| 网口相机 | `examples/net_camera/*.launch.py` |
| GMSL 相机 | `examples/gmsl_camera/*.launch.py` |
| 压测 FPS/延迟 | `examples/benchmark/` + `frame_latency_node` / `ob_benchmark_node` 等 |
| 验证多机硬件同步 | `examples/multi_camera_synced_verification_tool/` |
| 软件时间同步多路图 | **`image_sync_example_node`** |
| 学怎么调服务/标定 | **`435le_example_node`** |
| 改驱动逻辑本身 | 改 `src/ob_camera_node*.cpp` 等，再 `colcon build` |

---

## 5. 参考

- `examples/README.MD` — 官方示例列表与文档链接  
- `examples/Gemini_435Le_example_node/README.MD` — 435Le 示例菜单说明  
- 包根目录 `CMakeLists.txt` — `add_executable` / `rclcpp_components_register_node` 与安装目标定义  

*整理日期：2026-09-23*
