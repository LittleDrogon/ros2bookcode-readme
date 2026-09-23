# Orbbec SDK v2 示例说明

本文档对应 `examples/` 源码与编译后的 `bin/` 可执行文件。  
在 SDK 根目录下运行：

```bash
cd /home/lyzn-robot/ros2bookcode/OrbbecSDK_v2_linux_x86_64
# 首次使用建议：sudo bash setup.sh
./bin/ob_xxx
```

编译方式（已在本机编译过可跳过）：

```bash
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DOB_BUILD_LINUX=ON \
  -DCMAKE_INSTALL_PREFIX="$(pwd)/.." ../examples
cmake --build . -j$(nproc)
make install
```

可执行文件输出到：`OrbbecSDK_v2_linux_x86_64/bin/`  
源码目录：`OrbbecSDK_v2_linux_x86_64/examples/src/`

> Gemini 335L 属于 Gemini 330 系列；激光交错等部分高级示例仅支持该系列。

---

## 0. 基础（basic）

### 快速开始

获取 RGB-D 相机帧并显示，SDK 入门示例。

```bash
./bin/ob_quick_start
```

- 源码：`examples/src/0.basic.quick_start/quick_start.cpp`

### 枚举设备

枚举相机信息：型号、传感器、可用分辨率/帧率等配置。

```bash
./bin/ob_enumerate
```

- 源码：`examples/src/0.basic.enumerate/enumerate.cpp`

---

## 1. 数据流（stream）

### 深度流

获取深度流并在窗口中显示。

```bash
./bin/ob_depth
```

- 源码：`examples/src/1.stream.depth/depth.cpp`

### 彩色流

获取彩色流并在窗口中显示。

```bash
./bin/ob_color
```

- 源码：`examples/src/1.stream.color/color.cpp`

### 红外流

获取 IR 红外流并在窗口中显示。

```bash
./bin/ob_infrared
```

- 源码：`examples/src/1.stream.infrared/infrared.cpp`

### 置信度流

同时获取深度流与置信度流并显示。

```bash
./bin/ob_confidence
```

- 源码：`examples/src/1.stream.confidence/confidence.cpp`

### IMU 流

读取相机内置 IMU（加速度计 / 陀螺仪）数据并输出。

```bash
./bin/ob_imu
```

- 源码：`examples/src/1.stream.imu/imu.cpp`

### 多路数据流

同时开启并输出多路相机数据流。

```bash
./bin/ob_multi_streams
```

- 源码：`examples/src/1.stream.multi_streams/multi_streams.cpp`

### 抽稀（Decimation）

配置预设分辨率，为传感器选择 decimation profile 并显示。

```bash
./bin/ob_decimation
```

- 源码：`examples/src/1.stream.decimation/decimation.cpp`

### 回调取流

通过回调获取深度 / RGB / IR，可在回调里做采集、处理、修改。

```bash
./bin/ob_callback
```

- 源码：`examples/src/1.stream.callback/callback.cpp`

---

## 2. 设备控制（device）

### 设备参数控制

修改相机参数：激光开关、激光强度、白平衡等。

```bash
./bin/ob_device_control
```

- 源码：`examples/src/2.device.control/device_control.cpp`

### 固件升级

读取 BIN 文件对设备做固件升级。

```bash
./bin/ob_device_firmware_update
```

- 源码：`examples/src/2.device.firmware_update/device_firmware_update.cpp`

### 可选深度预设升级

读取 BIN 文件升级设备的 optional depth presets。

```bash
./bin/ob_device_optional_depth_presets_update
```

- 源码：`examples/src/2.device.optional_depth_presets_update/device.optional_depth_presets_update.cpp`

### ForceIP（网络相机）

通过 ForceIP 为网络设备配置新 IP。

```bash
./bin/ob_device_forceip
```

- 源码：`examples/src/2.device.forceip/forceip.cpp`

### 热插拔

注册设备插拔回调，处理断连 / 重连后的取流。

```bash
./bin/ob_hot_plugin
```

- 源码：`examples/src/2.device.hot_plugin/hot_plugin.cpp`

### 录制（带界面）

将相机视频流录制为 Rosbag 包（有画面预览）。

```bash
./bin/ob_device_record
```

- 源码：`examples/src/2.device.record/device_record.cpp`

### 录制（无界面）

同上，命令行录制，不渲染画面，适合无 GUI 环境。

```bash
./bin/ob_device_record_nogui
```

- 源码：`examples/src/2.device.record.nogui/device_record_nogui.cpp`

### 回放

从已录制的 Rosbag 包读取帧数据并回放。

```bash
./bin/ob_device_playback
```

- 源码：`examples/src/2.device.playback/device_playback.cpp`

---

## 3. 高级功能（advanced）

### 同步与对齐

演示多传感器数据流同步与对齐，并显示对齐后的图像。

```bash
./bin/ob_sync_align
```

- 源码：`examples/src/3.advanced.sync_align/sync_align.cpp`

### 硬件 D2C 对齐

演示硬件深度到彩色（Depth-to-Color）对齐。

```bash
./bin/ob_hw_d2c_align
```

- 源码：`examples/src/3.advanced.hw_d2c_align/hw_d2c_align.cpp`

### 后处理

演示深度后处理滤波等操作，并显示处理后的图像。

```bash
./bin/ob_post_processing
```

- 源码：`examples/src/3.advanced.post_processing/post_processing.cpp`

### 点云

开流后生成深度点云或 RGBD 点云，保存为 PLY。

```bash
./bin/ob_point_cloud
```

- 源码：`examples/src/3.advanced.point_cloud/point_cloud.cpp`

### 预设（Preset）

设置 / 获取设备 preset。

```bash
./bin/ob_preset
```

- 源码：`examples/src/3.advanced.preset/preset.cpp`

### 坐标变换

演示不同坐标系之间的坐标转换。

```bash
./bin/ob_coordinate_transform
```

- 源码：`examples/src/3.advanced.coordinate_transform/coordinate_transform.cpp`

### HDR

获取 HDR 融合图像；可开关 HDR merge，以及切换显示原始帧。

```bash
./bin/ob_hdr
```

- 源码：`examples/src/3.advanced.hdr/hdr.cpp`

### 激光帧交错

开启 / 关闭激光帧交错（laser frame interleave）与 SequenceId 滤波。  
**仅支持 Gemini 330 系列（含 335L）。**

```bash
./bin/ob_laser_interleave
```

- 源码：`examples/src/3.advanced.laser_interleave/laser_interleave.cpp`

### 多设备

连接多台相机，分别获取彩色与深度图。

```bash
./bin/ob_multi_device
```

- 源码：`examples/src/3.advanced.multi_devices/multi_device.cpp`

### 多设备同步

连接多台设备，结合 JSON 配置做多机同步。  
配置文件：`bin/MultiDeviceSyncConfig.json`

```bash
./bin/ob_multi_devices_sync
```

- 源码：`examples/src/3.advanced.multi_devices_sync/`  
  （主文件 `ob_multi_devices_sync.cpp`，以及 `PipelineHolder` / `FramePairingManager` 等）

### GMSL 触发同步

GMSL 设备发送 PWM 触发，通常与 `ob_multi_devices_sync` 配合使用。

```bash
./bin/ob_multi_devices_sync_gmsltrigger
```

- 源码：`examples/src/3.advanced.multi_devices_sync_gmsltrigger/ob_multi_devices_sync_gmsltrigger.cpp`

### 增强深度滤波

对对齐后的深度做 `EnhancedDepthFilter` 增强，并对比显示。  
**主要面向 NVIDIA Jetson（ARM64），且需有效 license；x86 上通常不可用。**

```bash
./bin/ob_enhanced_depth_filter
```

- 源码：`examples/src/3.advanced.enhanced_depth_filter/enhanced_depth_filter.cpp`

### 常用用法综合

查看相机信息、设置参数并显示视频流；包含设备插拔回调等常用流程。

```bash
./bin/ob_common_usages
```

- 源码：`examples/src/3.advanced.common_usages/common_usages.cpp`

---

## 4. 杂项（misc）

### 日志

设置日志输出级别与自定义输出路径。

```bash
./bin/ob_logger
```

- 源码：`examples/src/4.misc.logger/logger.cpp`

### 元数据

读取各路数据流的 metadata。

```bash
./bin/ob_metadata
```

- 源码：`examples/src/4.misc.metadata/metadata.cpp`

### 保存到磁盘

采集彩色 / 深度帧，转换格式后将前若干有效帧保存为 PNG。

```bash
./bin/ob_save_to_disk
```

- 源码：`examples/src/4.misc.save_to_disk/save_to_disk.cpp`

---

## 5. 第三方包装（wrapper）

### OpenCV 显示

用 OpenCV `imshow` 显示相机画面（深度伪彩等）。

```bash
./bin/ob_imshow
```

- 源码：`examples/src/5.wrapper.opencv/imshow/imshow.cpp`

### PCL / Open3D

本机已编译。依赖 PCL（系统 `libpcl-dev`）与 Open3D（conda-forge）。

```bash
# 重新编译时：
export CONDA_PREFIX=/home/lyzn-robot/miniconda3
cmake -DCMAKE_BUILD_TYPE=Release -DOB_BUILD_LINUX=ON \
  -DOB_BUILD_PCL_EXAMPLES=ON -DOB_BUILD_OPEN3D_EXAMPLES=ON \
  -DOpen3D_DIR=$CONDA_PREFIX/lib/cmake/Open3D \
  -DCMAKE_EXE_LINKER_FLAGS="-L$CONDA_PREFIX/lib -Wl,-rpath,$CONDA_PREFIX/lib" \
  -DCMAKE_INSTALL_PREFIX="$(pwd)/.." ../examples
```

| 可执行文件 | 源码 | 说明 |
|------------|------|------|
| `ob_pcl` | `5.wrapper.pcl/pcl/pcl.cpp` | PCL 深度点云可视化 |
| `ob_pcl_color` | `5.wrapper.pcl/pcl_color/pcl_color.cpp` | PCL 彩色点云可视化 |
| `ob_open3d` | `5.wrapper.open3d/open3d.cpp` | Open3D 实时显示彩色/深度 |

运行 Open3D 示例时需能找到 conda 库：

```bash
export LD_LIBRARY_PATH=/home/lyzn-robot/miniconda3/lib:$LD_LIBRARY_PATH
./bin/ob_open3d
```

---

## C 语言示例

### C 快速开始

用 C API 快速开流。

```bash
./bin/ob_quick_start_c
```

- 源码：`examples/src/c_examples/0.c_quick_start/quick_start.c`

### C 枚举

用 C API 枚举设备与流配置。

```bash
./bin/ob_enumerate_c
```

- 源码：`examples/src/c_examples/1.c_enumerate/enumerate.c`

### C 深度流

用 C API 获取深度流并显示。

```bash
./bin/ob_depth_c
```

- 源码：`examples/src/c_examples/2.c_depth/depth.c`

---

## LiDAR 示例

> 面向 Orbbec LiDAR 设备；Gemini 335L 深度相机一般不需要这些。

### LiDAR 快速开始

快速获取 LiDAR 点云，按键触发后保存为 PLY。

```bash
./bin/ob_lidar_quick_start
```

- 源码：`examples/src/lidar_examples/0.lidar_quick_start/lidar_quick_start.cpp`

### LiDAR 取流

配置并启动 LiDAR / IMU 流，回调处理并显示传感器信息。

```bash
./bin/ob_lidar_stream
```

- 源码：`examples/src/lidar_examples/1.lidar_stream/lidar_stream.cpp`

### LiDAR 设备控制

命令行交互式读写 LiDAR 设备属性。

```bash
./bin/ob_lidar_device_control
```

- 源码：`examples/src/lidar_examples/2.lidar_device_control/lidar_device_control.cpp`

### LiDAR 录制

将 LiDAR / IMU 数据录制到 bag，支持暂停 / 继续。

```bash
./bin/ob_lidar_record
```

- 源码：`examples/src/lidar_examples/3.lidar_record/lidar_record.cpp`

### LiDAR 回放

从 bag 回放 LiDAR / IMU，支持暂停与循环播放。

```bash
./bin/ob_lidar_playback
```

- 源码：`examples/src/lidar_examples/4.lidar_playback/lidar_playback.cpp`

### C：LiDAR 快速开始 / 取流

```bash
./bin/ob_lidar_quick_start_c
./bin/ob_lidar_stream_c
```

- 源码：
  - `lidar_examples/0.c_lidar_quick_start/lidar_quick_start.c`
  - `lidar_examples/1.c_lidar_stream/lidar_stream.c`

---

## SDK 自带、非 examples 编译产物

`bin/` 里还有部分随 SDK 预置的工具（不是本次 `examples` 编译出来的）：

| 可执行文件 | 说明 |
|------------|------|
| `ob_benchmark` | 性能基准测试 |
| `ob_timestamp_tracker` | 时间戳跟踪 / 调试 |
| `ob_multi_devices_firmware_update` | 多设备固件批量升级 |
| `MultiDeviceSyncConfig.json` | 多机同步配置（给 `ob_multi_devices_sync` 用） |

---

## Gemini 335L 建议试用顺序

```bash
./bin/ob_enumerate          # 确认设备能被识别
./bin/ob_quick_start        # 彩色+深度快速预览
./bin/ob_color              # 仅彩色
./bin/ob_depth              # 仅深度
./bin/ob_point_cloud        # 点云导出 PLY
./bin/ob_sync_align         # 深度彩色对齐
./bin/ob_device_control     # 调激光/白平衡等参数
```

窗口中一般按 `ESC` 或按提示键退出；具体以各程序终端提示为准。
