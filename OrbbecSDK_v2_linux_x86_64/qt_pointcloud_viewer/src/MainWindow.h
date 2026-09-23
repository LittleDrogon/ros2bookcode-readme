#pragma once

#include <QMainWindow>
#include <QString>

class OrbbecCamera;
class PointCloudGLWidget;
class QLabel;
class QPushButton;
class QComboBox;
class QPlainTextEdit;

/**
 * @brief 主窗口：设备/模式选择、点云显示、导出 PLY、底部运行日志。
 */
class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override;

private slots:
    void onStart();
    void onStop();
    void onSave();
    void onSaveAs();
    void onRefreshDevices();
    void onModeChanged(int index);
    void onDensityChanged(int index);
    void onSerialChanged(int index);
    void onFrameReady(int pointCount);
    void onCameraError(const QString &message);

private:
    void setupUi();
    void setPreStartControlsEnabled(bool enabled);
    void populateDeviceList();
    void appendLog(const QString &message);
    QString defaultPlyPath() const;

    OrbbecCamera *camera_ = nullptr;
    PointCloudGLWidget *view_ = nullptr;
    QPlainTextEdit *logView_ = nullptr;
    QPushButton *btnStart_ = nullptr;
    QPushButton *btnStop_ = nullptr;
    QPushButton *btnSave_ = nullptr;
    QPushButton *btnSaveAs_ = nullptr;
    QPushButton *btnRefreshSn_ = nullptr;
    QComboBox *snBox_ = nullptr;
    QComboBox *modeBox_ = nullptr;
    QComboBox *densityBox_ = nullptr;
    QLabel *infoLabel_ = nullptr;
    QString outputDir_;
};
