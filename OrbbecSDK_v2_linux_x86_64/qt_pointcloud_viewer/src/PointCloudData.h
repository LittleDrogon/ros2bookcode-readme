#pragma once

#include <QVector>
#include <QVector3D>
#include <QColor>
#include <mutex>
#include <vector>

/**
 * @brief 线程安全的彩色点云数据模型（相机坐标系，单位：毫米）。
 */
class PointCloudData {
public:
    struct Point {
        float x = 0.f;
        float y = 0.f;
        float z = 0.f;
        float r = 1.f;
        float g = 1.f;
        float b = 1.f;
    };

    void clear();
    void setPoints(std::vector<Point> &&points);
    std::vector<Point> snapshot() const;
    size_t size() const;

private:
    mutable std::mutex mutex_;
    std::vector<Point> points_;
};
