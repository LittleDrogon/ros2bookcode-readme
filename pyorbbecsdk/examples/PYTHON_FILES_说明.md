# pyorbbecsdk/examples — 各 Python 文件说明

> 目录：`/home/lyzn-robot/ros2bookcode/pyorbbecsdk/examples`  
> 本文按路径列出每个 `.py` 文件的作用。更完整的学习路径与依赖见同目录 [README.md](README.md)。

---

## 根目录

| 文件 | 作用 |
|------|------|
| `quick_start.py` | **最快上手**：零配置启动 Pipeline，并排显示彩色 + 深度（带 3D 浮雕着色），约 30 行验证相机能通。 |
| `utils.py` | **公共工具库**：帧转 BGR、格式转换、分辨率适配，以及 Astra Mini / Gemini 305 / LiDAR 等机型判断函数，供其它示例 import。 |
| `run_all_examples.py` | **批量冒烟测试**：子进程依次跑各示例，带超时与模拟 stdin；超时视为 PASS（GUI 循环正常），非零退出视为 FAIL。 |

---

## beginner/ — 入门教程（建议按编号顺序）

| 文件 | 作用 |
|------|------|
| `01_hello_camera.py` | 发现设备；打印名称、固件、序列号；枚举默认流配置；读取当前 / 可用深度 preset。不下发画面显示。 |
| `02_depth_visualization.py` | 开深度流；uint16→毫米；裁剪范围；伽马 + Scharr 浮雕着色；按 **C** 切换多种伪彩色。 |
| `03_color_and_depth_aligned.py` | 同时开彩色 + 深度；软件 `AlignFilter` 对齐（默认）或 `--hw` 硬件 D2C；叠加显示，可调方向与透明度。 |
| `04_camera_calibration.py` | 读取内外参：fx/fy/cx/cy、畸变、depth→color 外参 (R\|t)；便于对接 OpenCV / ROS / Open3D。 |
| `05_point_cloud.py` | `PointCloudFilter` + `AlignFilter` 生成彩色点云；可保存 `.ply`；装好 Open3D 后可实时 3D 查看（见下文）。 |
| `06_multi_streams.py` | 多路同时开（彩色 / 深度 / IR / IMU），异步回调收帧，动态网格拼图显示。 |
| `07_imu.py` | 开加速度计 + 陀螺仪；实时打印时间戳、温度与三轴数值。 |
| `08_net_device.py` | 连接网络相机（如 Gemini 335Le / 435Le）；用 PyAV 解 H.264/MJPG，pygame 显示。 |
| `09_device_firmware_update.py` | 从 `.bin` 做 OTA 固件升级；进度回调；强调升级中勿断电/拔线。 |
| `10_logger.py` | 配置 SDK 日志：控制台级别、写文件路径等。细节见 `LOG_CONFIGURATION.md`。 |

---

## advanced/ — 单点深入

### 录制 / 回放 / 存盘

| 文件 | 作用 |
|------|------|
| `01_recorder.py` | 用 `RecordDevice` 把多路流录成 `.bag`；可 GUI 预览或 `--no-gui`；可暂停/恢复；可导出 sidecar JSON preset。 |
| `02_playback.py` | 回放 `.bag`；自动循环；多流网格显示；可加载录制时的 JSON preset，并补上部分后处理滤波。 |
| `03_save_image_to_disk.py` | 抓取固定帧数：彩色存 PNG，深度存 16-bit PNG（含 depth scale）。 |

### 设备与系统

| 文件 | 作用 |
|------|------|
| `04_enumerate.py` | 交互枚举：设备 → 传感器 → 所有 stream profile（格式 / 分辨率 / FPS）。 |
| `05_hot_plug.py` | 注册设备插拔回调，运行时检测相机连接 / 断开。 |
| `06_control.py` | 枚举设备属性（bool/int/float）及范围、读写权限，演示 get/set。 |
| `07_metadata.py` | 读每帧 metadata：曝光、增益、时间戳等，并可与深度画面一起看。 |

### 深度处理与对齐

| 文件 | 作用 |
|------|------|
| `08_custom_filter_chain.py` | 自建滤波链：Temporal → Spatial → HoleFilling → Threshold；键盘实时调参。 |
| `09_post_processing.py` | 完整后处理栈；原始深度 vs 滤波深度并排对比（偏 Gemini 330 等）。 |
| `10_hdr.py` | 开启 HDR / 交错曝光，用 `HdrMergeFilter` 合成一帧，扩展深度动态范围。 |
| `11_preset.py` | 查询并切换命名深度 preset（如 Default / Hand / High Accuracy）。 |
| `12_depth_work_mode.py` | 列出并切换 depth work mode（High Accuracy、High Density 等，偏 Gemini 2 系列）。 |
| `13_confidence.py` | 开深度置信度图；伪彩可视化；按阈值过滤低置信像素。 |

### 多机 / 网络 / 性能

| 文件 | 作用 |
|------|------|
| `14_two_devices_sync.py` | 同时开两台相机；结合 JSON 做硬件帧同步；并排显示。 |
| `15_high_performance_pipeline.py` | 异步回调 + 有界队列；统计 FPS / 延迟；避免主线程长时间阻塞。 |
| `16_coordinate_transform.py` | 标定 API 做 2D↔2D、2D↔3D、3D↔3D、3D↔2D 变换；按键 1–4 切换。 |
| `17_laser_interleave.py` | 激光交错模式，减轻多机红外互相干扰（需设备支持）。 |
| `18_forceip.py` | 给网络相机强制设置静态 IP（如 Femto Mega、Gemini 2 XL）。 |
| `19_device_optional_depth_presets_update.py` | 把可选深度 preset 的 `.bin` 写入设备，并显示进度。 |

---

## applications/ — 完整小应用

| 文件 | 作用 |
|------|------|
| `ruler.py` | **深度直尺**：彩色图上拖线，用对齐深度反投影算两点真实 3D 距离（mm）；**C** 清除。 |
| `object_detection/object_detection.py` | **YOLO 检测**：彩色流跑 YOLOv5s（ONNX），叠加每目标中位深度（软件 D2C 对齐）。 |
| `object_detection/setup_model.py` | 一键准备模型：装依赖、下载/导出 `models/yolov5s.onnx`（可用 `--force` / `--export`）。 |

---

## lidar_examples/ — 激光雷达专用

| 文件 | 作用 |
|------|------|
| `lidar_quick_start.py` | LiDAR 最小示例：连设备、开点云流、可存 `.ply`。 |
| `lidar_stream.py` | 持续流式显示 / 统计 LiDAR 点云。 |
| `lidar_device_control.py` | 枚举并读写 LiDAR 属性；可同时开扫描 + IMU。 |
| `lidar_record.py` | 将 LiDAR 数据录到 `.bag`。 |
| `lidar_playback.py` | 回放 LiDAR `.bag` 点云（可不接真机）。 |

---

## 环境安装与常见问题

本仓库 `examples/` 面向 **Orbbec SDK v2**。

### 正确安装（务必用「当前 python」）

```bash
# 推荐：装到当前 python 所在环境（conda / venv 都行）
python -m pip install pyorbbecsdk2
python -m pip install open3d          # 点云实时查看需要
# 其它示例依赖见 requirements.txt
python -m pip install -r examples/requirements.txt
```

注意：

| 错误做法 | 后果 |
|----------|------|
| `pip install pyorbbecsdk` | 装的是 **v1** 旧包，且常装到别的 Python（如 3.10） |
| `pip` 与 `python` 不是同一环境 | 出现 `ModuleNotFoundError: No module named 'pyorbbecsdk'` |
| 正确包名 | PyPI 上是 **`pyorbbecsdk2`**，代码里仍 `import pyorbbecsdk` |

检查是否一致：

```bash
which python
python -V
python -m pip -V
python -c "import pyorbbecsdk; print(pyorbbecsdk.__file__)"
```

### `undefined symbol: ob_application_config_set_struct`

若已能 `import` 包名但加载 `.so` 失败，多半是 **`LD_LIBRARY_PATH` 里 ROS / 其它目录的旧 `libOrbbecSDK.so` 抢先被加载**（例如 `ros2_ws/install/orbbec_camera/lib`），与 pip 自带的新库冲突。

**推荐：用包装脚本（自动把 pip 自带库放到最前）：**

```bash
cd ~/ros2bookcode/pyorbbecsdk
./examples/run.sh examples/beginner/05_point_cloud.py
```

或手动：

```bash
cd ~/ros2bookcode/pyorbbecsdk

# 注意：必须先 export，再 python；只 pip install 不够
export LD_LIBRARY_PATH="$(python -c 'from pathlib import Path; import sys; print(next(Path(p)/"pyorbbecsdk" for p in sys.path if (Path(p)/"pyorbbecsdk"/"libOrbbecSDK.so.2").exists()))'):$LD_LIBRARY_PATH"

python examples/beginner/05_point_cloud.py
```

> Linux 上 **`LD_LIBRARY_PATH` 优先于** `.so` 自带的 `$ORIGIN` RUNPATH，所以 ROS 里的旧 `libOrbbecSDK` 会抢走链接。

可用下面命令确认链接到的是 pip 自带库：

```bash
ldd "$(python -c 'import pyorbbecsdk, os, glob; print(glob.glob(os.path.dirname(pyorbbecsdk.__file__)+"/pyorbbecsdk*.so")[0])')" | grep Orbbec
# 应指向 .../site-packages/pyorbbecsdk/libOrbbecSDK.so.2
```

---

## `05_point_cloud.py`：用 Open3D 实时查看

脚本已内置 Open3D 窗口；**装好 `open3d` 后直接跑就会弹出**，无需另开软件。

```bash
python -m pip install open3d

cd ~/ros2bookcode/pyorbbecsdk
./examples/run.sh examples/beginner/05_point_cloud.py
```

- **已安装 Open3D**：打开实时点云窗口，每帧刷新。  
- **未安装**：打印 WARN，退化为只保存一帧 `.ply` 后退出（`./point_clouds/`）。

窗口操作：

| 按键 / 操作 | 作用 |
|-------------|------|
| 鼠标拖动 | 旋转 / 平移 / 缩放 |
| **C** | 在「RGB 真彩」与「按深度伪彩」之间切换 |
| **S** | 当前帧保存为 `./point_clouds/point_cloud_XXXX.ply` |
| **Q / ESC** | 退出 |

有彩色传感器时优先显示彩色点云；否则用深度伪彩。

---

## 建议阅读顺序（简表）

```
quick_start.py
  → beginner/01 … 05
  → 按需 advanced/* 或 applications/*
  → 若是 LiDAR → lidar_examples/lidar_quick_start.py
```

常用命令（在 `pyorbbecsdk` 仓库根目录）：

```bash
# 建议先处理 LD_LIBRARY_PATH（见上文），再运行
python examples/quick_start.py
python examples/beginner/01_hello_camera.py
python examples/beginner/05_point_cloud.py
python examples/applications/ruler.py
```
