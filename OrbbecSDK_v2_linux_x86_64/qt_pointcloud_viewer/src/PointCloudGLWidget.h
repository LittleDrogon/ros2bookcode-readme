#pragma once

#include "PointCloudData.h"

#include <QOpenGLWidget>
#include <QOpenGLFunctions>
#include <QMatrix4x4>
#include <QPoint>
#include <memory>
#include <vector>

/**
 * @brief 用 OpenGL 渲染点云，支持鼠标旋转 / 滚轮缩放。
 */
class PointCloudGLWidget : public QOpenGLWidget, protected QOpenGLFunctions {
    Q_OBJECT
public:
    explicit PointCloudGLWidget(QWidget *parent = nullptr);

    void setCloud(const std::shared_ptr<PointCloudData> &cloud);
    void reloadFromCloud();

protected:
    void initializeGL() override;
    void resizeGL(int w, int h) override;
    void paintGL() override;

    void mousePressEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void wheelEvent(QWheelEvent *event) override;

private:
    void uploadBuffer(const std::vector<PointCloudData::Point> &points);

    std::shared_ptr<PointCloudData> cloud_;
    std::vector<float> vertexBuffer_;  // xyzrgb interleaved
    int pointCount_ = 0;

    float distance_ = 1500.f;  // mm
    float yaw_ = 30.f;
    float pitch_ = -20.f;
    QPoint lastPos_;
};
