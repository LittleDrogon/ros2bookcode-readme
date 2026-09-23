# Qt 点云查看器

面向对象的 Orbbec 实时点云界面（Qt5 + CMake + C++17 + OpenGL）。

相关说明见上级目录：[POINTCLOUD.md](../POINTCLOUD.md)

## 类结构

| 类 | 职责 |
|----|------|
| `PointCloudData` | 线程安全的点云数据模型 |
| `OrbbecCamera` | 开流、D2C 对齐、生成点云（后台线程） |
| `PointCloudGLWidget` | OpenGL 渲染，鼠标旋转 / 滚轮缩放 |
| `MainWindow` | 启动/停止/保存 PLY、模式切换 |

## 编译

```bash
cd /home/lyzn-robot/ros2bookcode/OrbbecSDK_v2_linux_x86_64/qt_pointcloud_viewer
mkdir -p build && cd build
cmake ..
cmake --build . -j$(nproc)
```

## 运行

```bash
# 若正在跑 ROS orbbec_camera，请先停掉
cd /home/lyzn-robot/ros2bookcode/OrbbecSDK_v2_linux_x86_64/qt_pointcloud_viewer/build
./qt_pointcloud_viewer
```

- **启动**：开始取流并刷新点云
- **模式**：彩色点云 / 深度伪彩点云（启动前选择）
- **保存 PLY**：导出到本工程目录 `qt_pointcloud_viewer/RGBPoints.ply` 或 `DepthPoints.ply`
- **另存为…**：自定义路径
- **鼠标左键拖动**：旋转；**滚轮**：缩放
- 窗口下方为运行日志
