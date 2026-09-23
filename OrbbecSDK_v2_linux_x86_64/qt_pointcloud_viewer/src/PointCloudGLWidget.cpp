#include "PointCloudGLWidget.h"

#include <QMouseEvent>
#include <QWheelEvent>
#include <cmath>

PointCloudGLWidget::PointCloudGLWidget(QWidget *parent) : QOpenGLWidget(parent) {
    setMinimumSize(640, 480);
}

void PointCloudGLWidget::setCloud(const std::shared_ptr<PointCloudData> &cloud) {
    cloud_ = cloud;
}

void PointCloudGLWidget::reloadFromCloud() {
    if (!cloud_) {
        return;
    }
    auto pts = cloud_->snapshot();
    uploadBuffer(pts);
    update();
}

void PointCloudGLWidget::uploadBuffer(const std::vector<PointCloudData::Point> &points) {
    vertexBuffer_.resize(points.size() * 6);
    for (size_t i = 0; i < points.size(); ++i) {
        const auto &p = points[i];
        // Orbbec: x right, y down, z forward(mm). Flip Y for typical OpenGL up-axis view.
        vertexBuffer_[i * 6 + 0] = p.x;
        vertexBuffer_[i * 6 + 1] = -p.y;
        vertexBuffer_[i * 6 + 2] = -p.z;
        vertexBuffer_[i * 6 + 3] = p.r;
        vertexBuffer_[i * 6 + 4] = p.g;
        vertexBuffer_[i * 6 + 5] = p.b;
    }
    pointCount_ = static_cast<int>(points.size());
}

void PointCloudGLWidget::initializeGL() {
    initializeOpenGLFunctions();
    glClearColor(0.08f, 0.09f, 0.12f, 1.f);
    glEnable(GL_DEPTH_TEST);
    glPointSize(2.0f);
}

void PointCloudGLWidget::resizeGL(int w, int h) {
    glViewport(0, 0, w, h);
}

void PointCloudGLWidget::paintGL() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    QMatrix4x4 projection;
    projection.perspective(45.f, width() / std::max(1.f, float(height())), 1.f, 20000.f);

    QMatrix4x4 view;
    view.translate(0.f, 0.f, -distance_);
    view.rotate(pitch_, 1.f, 0.f, 0.f);
    view.rotate(yaw_, 0.f, 1.f, 0.f);

    QMatrix4x4 mvp = projection * view;
    glMatrixMode(GL_PROJECTION);
    glLoadMatrixf(mvp.constData());
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    if (pointCount_ <= 0 || vertexBuffer_.empty()) {
        return;
    }

    glEnableClientState(GL_VERTEX_ARRAY);
    glEnableClientState(GL_COLOR_ARRAY);
    glVertexPointer(3, GL_FLOAT, 6 * sizeof(float), vertexBuffer_.data());
    glColorPointer(3, GL_FLOAT, 6 * sizeof(float), vertexBuffer_.data() + 3);
    glDrawArrays(GL_POINTS, 0, pointCount_);
    glDisableClientState(GL_COLOR_ARRAY);
    glDisableClientState(GL_VERTEX_ARRAY);
}

void PointCloudGLWidget::mousePressEvent(QMouseEvent *event) {
    lastPos_ = event->pos();
}

void PointCloudGLWidget::mouseMoveEvent(QMouseEvent *event) {
    const int dx = event->x() - lastPos_.x();
    const int dy = event->y() - lastPos_.y();
    if (event->buttons() & Qt::LeftButton) {
        yaw_ += dx * 0.3f;
        pitch_ += dy * 0.3f;
        pitch_ = std::max(-89.f, std::min(89.f, pitch_));
        update();
    }
    lastPos_ = event->pos();
}

void PointCloudGLWidget::wheelEvent(QWheelEvent *event) {
    const float delta = event->angleDelta().y() > 0 ? 0.9f : 1.1f;
    distance_ = std::max(200.f, std::min(8000.f, distance_ * delta));
    update();
}
