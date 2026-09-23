#include "OrbbecCamera.h"

#include <libobsensor/ObSensor.hpp>
#include "libobsensor/hpp/Utils.hpp"

#include <QMetaObject>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <iostream>

OrbbecCamera::OrbbecCamera(QObject *parent)
    : QObject(parent), cloud_(std::make_shared<PointCloudData>()) {}

OrbbecCamera::~OrbbecCamera() {
    stop();
}

QVector<OrbbecCamera::DeviceInfo> OrbbecCamera::listDevices(QString *errorMessage) {
    QVector<DeviceInfo> result;
    try {
        ob::Context ctx;
        auto list = ctx.queryDeviceList();
        const uint32_t n = list->getCount();
        result.reserve(static_cast<int>(n));
        for (uint32_t i = 0; i < n; ++i) {
            DeviceInfo info;
            info.serial = QString::fromUtf8(list->getSerialNumber(i));
            info.name = QString::fromUtf8(list->getName(i));
            info.pid = static_cast<int>(list->getPid(i));
            result.push_back(info);
        }
    } catch (ob::Error &e) {
        if (errorMessage) {
            *errorMessage = QString::fromStdString(e.what());
        }
    } catch (const std::exception &e) {
        if (errorMessage) {
            *errorMessage = QString::fromStdString(e.what());
        }
    }
    return result;
}

bool OrbbecCamera::start(CloudMode mode) {
    if (running_.load()) {
        return true;
    }

    mode_ = mode;
    try {
        auto config = std::make_shared<ob::Config>();
        config->enableVideoStream(OB_STREAM_DEPTH, OB_WIDTH_ANY, OB_HEIGHT_ANY, OB_FPS_ANY, OB_FORMAT_ANY);
        config->enableVideoStream(OB_STREAM_COLOR, OB_WIDTH_ANY, OB_HEIGHT_ANY, OB_FPS_ANY, OB_FORMAT_RGB);
        config->setFrameAggregateOutputMode(OB_FRAME_AGGREGATE_OUTPUT_ALL_TYPE_FRAME_REQUIRE);

        if (!serialNumber_.isEmpty()) {
            ob::Context ctx;
            auto list = ctx.queryDeviceList();
            device_ = list->getDeviceBySN(serialNumber_.toUtf8().constData());
            if (!device_) {
                emit errorOccurred(QStringLiteral("未找到序列号: ") + serialNumber_);
                return false;
            }
            pipeline_ = std::make_shared<ob::Pipeline>(device_);
        } else {
            pipeline_ = std::make_shared<ob::Pipeline>();
        }

        pipeline_->enableFrameSync();
        pipeline_->start(config);

        pointCloudFilter_ = std::make_shared<ob::PointCloudFilter>();
        align_ = std::make_shared<ob::Align>(OB_STREAM_COLOR);

        stopRequested_ = false;
        running_ = true;
        worker_ = std::thread(&OrbbecCamera::captureLoop, this);
        emit started();
        return true;
    } catch (ob::Error &e) {
        emit errorOccurred(QString::fromStdString(std::string("Orbbec: ") + e.what()));
        pipeline_.reset();
        device_.reset();
        running_ = false;
        return false;
    } catch (const std::exception &e) {
        emit errorOccurred(QString::fromStdString(e.what()));
        pipeline_.reset();
        device_.reset();
        running_ = false;
        return false;
    }
}

void OrbbecCamera::stop() {
    stopRequested_ = true;
    if (worker_.joinable()) {
        worker_.join();
    }
    if (pipeline_) {
        try {
            pipeline_->stop();
        } catch (...) {
        }
        pipeline_.reset();
    }
    pointCloudFilter_.reset();
    align_.reset();
    device_.reset();
    if (running_.exchange(false)) {
        emit stopped();
    }
}

void OrbbecCamera::setMode(CloudMode mode) {
    mode_ = mode;
}

void OrbbecCamera::setDisplayStride(int stride) {
    displayStride_ = std::max(1, stride);
}

void OrbbecCamera::setSerialNumber(const QString &sn) {
    serialNumber_ = sn.trimmed();
}

bool OrbbecCamera::savePly(const QString &path, QString *errorMessage) {
    if (!pipeline_ || !pointCloudFilter_ || !align_) {
        if (errorMessage) {
            *errorMessage = QStringLiteral("相机未启动");
        }
        return false;
    }

    try {
        std::shared_ptr<ob::Frame> frame;
        QString err;
        if (!buildOneCloud(&frame, &err) || !frame) {
            if (errorMessage) {
                *errorMessage = err.isEmpty() ? QStringLiteral("取帧失败") : err;
            }
            return false;
        }
        const bool colored = (mode_ == CloudMode::ColorRgb);
        ob::PointCloudHelper::savePointcloudToPly(path.toStdString().c_str(), frame, false, false, 50);
        (void)colored;
        return true;
    } catch (ob::Error &e) {
        if (errorMessage) {
            *errorMessage = QString::fromStdString(e.what());
        }
        return false;
    }
}

bool OrbbecCamera::buildOneCloud(std::shared_ptr<ob::Frame> *outFrame, QString *errorMessage) {
    try {
        std::lock_guard<std::mutex> lock(pipelineMutex_);
        if (!pipeline_ || !align_ || !pointCloudFilter_) {
            if (errorMessage) {
                *errorMessage = QStringLiteral("相机未就绪");
            }
            return false;
        }

        std::shared_ptr<ob::FrameSet> frameset;
        for (int i = 0; i < 30; ++i) {
            frameset = pipeline_->waitForFrameset(200);
            if (frameset) {
                break;
            }
        }
        if (!frameset) {
            if (errorMessage) {
                *errorMessage = QStringLiteral("等待帧超时");
            }
            return false;
        }

        auto aligned = align_->process(frameset);
        if (mode_ == CloudMode::ColorRgb) {
            pointCloudFilter_->setCreatePointFormat(OB_FORMAT_RGB_POINT);
        } else {
            pointCloudFilter_->setCreatePointFormat(OB_FORMAT_POINT);
        }
        *outFrame = pointCloudFilter_->process(aligned);
        return static_cast<bool>(*outFrame);
    } catch (ob::Error &e) {
        if (errorMessage) {
            *errorMessage = QString::fromStdString(e.what());
        }
        return false;
    }
}

std::vector<PointCloudData::Point> OrbbecCamera::frameToPoints(const std::shared_ptr<ob::Frame> &frame,
                                                               CloudMode mode,
                                                               int stride) {
    std::vector<PointCloudData::Point> out;
    if (!frame) {
        return out;
    }

    auto pointsFrame = frame->as<ob::PointsFrame>();
    if (!pointsFrame) {
        return out;
    }

    const auto *data = static_cast<const uint8_t *>(pointsFrame->data());
    const uint32_t dataSize = pointsFrame->dataSize();
    stride = std::max(1, stride);

    if (mode == CloudMode::ColorRgb) {
        const size_t count = dataSize / sizeof(OBColorPoint);
        const auto *pts = reinterpret_cast<const OBColorPoint *>(data);
        out.reserve(count / static_cast<size_t>(stride) + 1);
        for (size_t i = 0; i < count; i += static_cast<size_t>(stride)) {
            const auto &p = pts[i];
            if (p.z <= 0.f || !std::isfinite(p.z)) {
                continue;
            }
            PointCloudData::Point q;
            q.x = p.x;
            q.y = p.y;
            q.z = p.z;
            // SDK 中 RGB 常为 0~255 浮点
            q.r = std::min(1.f, std::max(0.f, p.r / 255.f));
            q.g = std::min(1.f, std::max(0.f, p.g / 255.f));
            q.b = std::min(1.f, std::max(0.f, p.b / 255.f));
            out.push_back(q);
        }
    } else {
        const size_t count = dataSize / sizeof(OBPoint);
        const auto *pts = reinterpret_cast<const OBPoint *>(data);
        out.reserve(count / static_cast<size_t>(stride) + 1);
        for (size_t i = 0; i < count; i += static_cast<size_t>(stride)) {
            const auto &p = pts[i];
            if (p.z <= 0.f || !std::isfinite(p.z)) {
                continue;
            }
            // 按深度伪彩：近蓝远红（简单映射）
            const float t = std::min(1.f, std::max(0.f, (p.z - 200.f) / 2000.f));
            PointCloudData::Point q;
            q.x = p.x;
            q.y = p.y;
            q.z = p.z;
            q.r = t;
            q.g = 0.2f;
            q.b = 1.f - t;
            out.push_back(q);
        }
    }
    return out;
}

void OrbbecCamera::captureLoop() {
    using namespace std::chrono_literals;
    while (!stopRequested_.load()) {
        try {
            std::shared_ptr<ob::Frame> frame;
            QString err;
            if (!buildOneCloud(&frame, &err)) {
                std::this_thread::sleep_for(50ms);
                continue;
            }
            auto points = frameToPoints(frame, mode_, displayStride_);
            const int n = static_cast<int>(points.size());
            cloud_->setPoints(std::move(points));
            emit frameReady(n);
        } catch (ob::Error &e) {
            emit errorOccurred(QString::fromStdString(e.what()));
            std::this_thread::sleep_for(200ms);
        } catch (...) {
            emit errorOccurred(QStringLiteral("未知取流错误"));
            std::this_thread::sleep_for(200ms);
        }
    }
    running_ = false;
}
