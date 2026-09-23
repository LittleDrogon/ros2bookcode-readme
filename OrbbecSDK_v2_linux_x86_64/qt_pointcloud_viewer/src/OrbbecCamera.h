#pragma once

#include "PointCloudData.h"

#include <QObject>
#include <QString>
#include <QStringList>
#include <QVector>
#include <atomic>
#include <memory>
#include <mutex>
#include <thread>

namespace ob {
class Pipeline;
class Config;
class PointCloudFilter;
class Align;
class Frame;
class Device;
}  // namespace ob

/**
 * @brief Orbbec 相机封装：开流、对齐、生成点云，在后台线程中运行。
 */
class OrbbecCamera : public QObject {
    Q_OBJECT
public:
    enum class CloudMode { DepthOnly, ColorRgb };

    struct DeviceInfo {
        QString serial;
        QString name;
        int pid = 0;
    };

    explicit OrbbecCamera(QObject *parent = nullptr);
    ~OrbbecCamera() override;

    /** 枚举当前连接的设备（不占用设备）。 */
    static QVector<DeviceInfo> listDevices(QString *errorMessage = nullptr);

    bool start(CloudMode mode = CloudMode::ColorRgb);
    void stop();
    bool isRunning() const { return running_.load(); }

    CloudMode mode() const { return mode_; }
    void setMode(CloudMode mode);

    int displayStride() const { return displayStride_; }
    void setDisplayStride(int stride);

    QString serialNumber() const { return serialNumber_; }
    void setSerialNumber(const QString &sn);

    /** 保存当前一帧点云为 PLY（阻塞，在调用线程执行）。 */
    bool savePly(const QString &path, QString *errorMessage = nullptr);

    std::shared_ptr<PointCloudData> cloud() const { return cloud_; }

signals:
    void started();
    void stopped();
    void frameReady(int pointCount);
    void errorOccurred(const QString &message);

private:
    void captureLoop();
    bool buildOneCloud(std::shared_ptr<ob::Frame> *outFrame, QString *errorMessage);
    static std::vector<PointCloudData::Point> frameToPoints(const std::shared_ptr<ob::Frame> &frame,
                                                            CloudMode mode,
                                                            int stride);

    std::shared_ptr<PointCloudData> cloud_;
    std::shared_ptr<ob::Device> device_;
    std::shared_ptr<ob::Pipeline> pipeline_;
    std::shared_ptr<ob::PointCloudFilter> pointCloudFilter_;
    std::shared_ptr<ob::Align> align_;

    std::thread worker_;
    std::mutex pipelineMutex_;
    std::atomic<bool> running_{false};
    std::atomic<bool> stopRequested_{false};
    CloudMode mode_ = CloudMode::ColorRgb;
    int displayStride_ = 4;
    QString serialNumber_;
};
