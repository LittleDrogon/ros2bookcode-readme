#include "MainWindow.h"
#include "OrbbecCamera.h"
#include "PointCloudGLWidget.h"

#include <QComboBox>
#include <QCoreApplication>
#include <QDateTime>
#include <QDir>
#include <QFileDialog>
#include <QFileInfo>
#include <QHBoxLayout>
#include <QLabel>
#include <QMessageBox>
#include <QPlainTextEdit>
#include <QPushButton>
#include <QSplitter>
#include <QStatusBar>
#include <QVBoxLayout>
#include <QWidget>

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    // 可执行文件在 qt_pointcloud_viewer/build/，输出保存到 qt_pointcloud_viewer/ 同目录
    const QDir appDir(QCoreApplication::applicationDirPath());
    outputDir_ = QFileInfo(appDir.absoluteFilePath(QStringLiteral(".."))).absoluteFilePath();

    camera_ = new OrbbecCamera(this);
    setupUi();

    connect(camera_, &OrbbecCamera::frameReady, this, &MainWindow::onFrameReady);
    connect(camera_, &OrbbecCamera::errorOccurred, this, &MainWindow::onCameraError);
    connect(camera_, &OrbbecCamera::started, this, [this]() {
        btnStart_->setEnabled(false);
        btnStop_->setEnabled(true);
        btnSave_->setEnabled(true);
        btnSaveAs_->setEnabled(true);
        setPreStartControlsEnabled(false);
        const QString sn = camera_->serialNumber();
        const QString msg = sn.isEmpty() ? QStringLiteral("相机已启动")
                                         : QStringLiteral("相机已启动  SN: %1").arg(sn);
        statusBar()->showMessage(msg);
        appendLog(msg);
    });
    connect(camera_, &OrbbecCamera::stopped, this, [this]() {
        btnStart_->setEnabled(true);
        btnStop_->setEnabled(false);
        btnSave_->setEnabled(false);
        btnSaveAs_->setEnabled(false);
        setPreStartControlsEnabled(true);
        statusBar()->showMessage(QStringLiteral("已停止"));
        appendLog(QStringLiteral("相机已停止"));
    });

    appendLog(QStringLiteral("输出目录: %1").arg(outputDir_));
    appendLog(QStringLiteral("保存 PLY 默认路径: %1").arg(defaultPlyPath()));
}

MainWindow::~MainWindow() {
    if (camera_) {
        camera_->stop();
    }
}

QString MainWindow::defaultPlyPath() const {
    const bool rgb = modeBox_
                         ? (static_cast<OrbbecCamera::CloudMode>(modeBox_->currentData().toInt()) ==
                            OrbbecCamera::CloudMode::ColorRgb)
                         : true;
    return QDir(outputDir_).filePath(rgb ? QStringLiteral("RGBPoints.ply") : QStringLiteral("DepthPoints.ply"));
}

void MainWindow::appendLog(const QString &message) {
    if (!logView_) {
        return;
    }
    const QString line =
        QStringLiteral("[%1] %2")
            .arg(QDateTime::currentDateTime().toString(QStringLiteral("hh:mm:ss.zzz")), message);
    logView_->appendPlainText(line);
}

void MainWindow::setPreStartControlsEnabled(bool enabled) {
    snBox_->setEnabled(enabled);
    btnRefreshSn_->setEnabled(enabled);
    modeBox_->setEnabled(enabled);
    densityBox_->setEnabled(enabled);
}

void MainWindow::populateDeviceList() {
    const QString prev = snBox_->currentData().toString();
    snBox_->clear();

    QString err;
    const auto devices = OrbbecCamera::listDevices(&err);
    if (!err.isEmpty()) {
        appendLog(QStringLiteral("枚举设备失败: %1").arg(err));
        statusBar()->showMessage(QStringLiteral("枚举设备失败: ") + err, 5000);
    }

    if (devices.isEmpty()) {
        snBox_->addItem(QStringLiteral("(未检测到设备)"), QString());
        btnStart_->setEnabled(false);
        appendLog(QStringLiteral("未检测到 Orbbec 设备"));
        statusBar()->showMessage(QStringLiteral("未检测到 Orbbec 设备，请插上相机后点「刷新」"));
        return;
    }

    btnStart_->setEnabled(true);
    int selectIndex = 0;
    for (int i = 0; i < devices.size(); ++i) {
        const auto &d = devices[i];
        const QString text = QStringLiteral("%1  [%2]").arg(d.serial, d.name);
        snBox_->addItem(text, d.serial);
        appendLog(QStringLiteral("发现设备: %1  name=%2  pid=%3").arg(d.serial, d.name).arg(d.pid));
        if (!prev.isEmpty() && d.serial == prev) {
            selectIndex = i;
        }
    }
    snBox_->setCurrentIndex(selectIndex);
    onSerialChanged(selectIndex);
    appendLog(QStringLiteral("共 %1 台设备").arg(devices.size()));
    statusBar()->showMessage(QStringLiteral("检测到 %1 台设备").arg(devices.size()), 4000);
}

void MainWindow::setupUi() {
    setWindowTitle(QStringLiteral("Orbbec 点云查看器 (Qt)"));
    resize(1200, 800);

    auto *central = new QWidget(this);
    setCentralWidget(central);

    auto *root = new QVBoxLayout(central);
    auto *toolbar = new QHBoxLayout();

    snBox_ = new QComboBox(this);
    snBox_->setMinimumWidth(260);
    snBox_->setToolTip(QStringLiteral("启动前选择设备序列号"));

    btnRefreshSn_ = new QPushButton(QStringLiteral("刷新"), this);
    btnRefreshSn_->setToolTip(QStringLiteral("重新枚举已连接设备"));

    modeBox_ = new QComboBox(this);
    modeBox_->addItem(QStringLiteral("彩色点云 RGBD"), static_cast<int>(OrbbecCamera::CloudMode::ColorRgb));
    modeBox_->addItem(QStringLiteral("深度点云"), static_cast<int>(OrbbecCamera::CloudMode::DepthOnly));
    modeBox_->setToolTip(QStringLiteral("启动前选择点云类型"));

    densityBox_ = new QComboBox(this);
    densityBox_->addItem(QStringLiteral("精细 (抽稀 2)"), 2);
    densityBox_->addItem(QStringLiteral("标准 (抽稀 4)"), 4);
    densityBox_->addItem(QStringLiteral("流畅 (抽稀 8)"), 8);
    densityBox_->addItem(QStringLiteral("极速 (抽稀 16)"), 16);
    densityBox_->setCurrentIndex(1);
    densityBox_->setToolTip(QStringLiteral("启动前选择显示密度"));

    btnStart_ = new QPushButton(QStringLiteral("启动"), this);
    btnStop_ = new QPushButton(QStringLiteral("停止"), this);
    btnSave_ = new QPushButton(QStringLiteral("保存 PLY"), this);
    btnSaveAs_ = new QPushButton(QStringLiteral("另存为…"), this);
    btnSave_->setToolTip(QStringLiteral("保存到 qt_pointcloud_viewer/RGBPoints.ply 或 DepthPoints.ply"));
    btnStop_->setEnabled(false);
    btnSave_->setEnabled(false);
    btnSaveAs_->setEnabled(false);

    infoLabel_ = new QLabel(QStringLiteral("点数: 0"), this);

    toolbar->addWidget(new QLabel(QStringLiteral("序列号:"), this));
    toolbar->addWidget(snBox_);
    toolbar->addWidget(btnRefreshSn_);
    toolbar->addWidget(new QLabel(QStringLiteral("模式:"), this));
    toolbar->addWidget(modeBox_);
    toolbar->addWidget(new QLabel(QStringLiteral("密度:"), this));
    toolbar->addWidget(densityBox_);
    toolbar->addSpacing(12);
    toolbar->addWidget(btnStart_);
    toolbar->addWidget(btnStop_);
    toolbar->addWidget(btnSave_);
    toolbar->addWidget(btnSaveAs_);
    toolbar->addStretch();
    toolbar->addWidget(infoLabel_);

    view_ = new PointCloudGLWidget(this);
    view_->setCloud(camera_->cloud());

    logView_ = new QPlainTextEdit(this);
    logView_->setReadOnly(true);
    logView_->setMaximumBlockCount(2000);
    logView_->setPlaceholderText(QStringLiteral("运行日志…"));
    logView_->setMinimumHeight(140);
    QFont logFont = logView_->font();
    logFont.setFamily(QStringLiteral("Monospace"));
    logFont.setPointSize(10);
    logView_->setFont(logFont);

    auto *splitter = new QSplitter(Qt::Vertical, this);
    splitter->addWidget(view_);
    splitter->addWidget(logView_);
    splitter->setStretchFactor(0, 4);
    splitter->setStretchFactor(1, 1);

    root->addLayout(toolbar);
    root->addWidget(splitter, 1);

    statusBar()->showMessage(QStringLiteral("请选择设备序列号后点「启动」"));

    connect(btnStart_, &QPushButton::clicked, this, &MainWindow::onStart);
    connect(btnStop_, &QPushButton::clicked, this, &MainWindow::onStop);
    connect(btnSave_, &QPushButton::clicked, this, &MainWindow::onSave);
    connect(btnSaveAs_, &QPushButton::clicked, this, &MainWindow::onSaveAs);
    connect(btnRefreshSn_, &QPushButton::clicked, this, &MainWindow::onRefreshDevices);
    connect(snBox_, QOverload<int>::of(&QComboBox::currentIndexChanged), this, &MainWindow::onSerialChanged);
    connect(modeBox_, QOverload<int>::of(&QComboBox::currentIndexChanged), this, &MainWindow::onModeChanged);
    connect(densityBox_, QOverload<int>::of(&QComboBox::currentIndexChanged), this, &MainWindow::onDensityChanged);

    onModeChanged(modeBox_->currentIndex());
    onDensityChanged(densityBox_->currentIndex());
    populateDeviceList();
}

void MainWindow::onRefreshDevices() {
    appendLog(QStringLiteral("刷新设备列表…"));
    populateDeviceList();
}

void MainWindow::onStart() {
    const QString sn = snBox_->currentData().toString();
    if (sn.isEmpty()) {
        appendLog(QStringLiteral("启动失败: 未选择设备"));
        QMessageBox::warning(this, QStringLiteral("未选择设备"),
                             QStringLiteral("请先选择有效的设备序列号，或点「刷新」重新枚举。"));
        return;
    }

    const auto mode = static_cast<OrbbecCamera::CloudMode>(modeBox_->currentData().toInt());
    appendLog(QStringLiteral("正在启动 SN=%1  模式=%2  密度=%3")
                  .arg(sn)
                  .arg(mode == OrbbecCamera::CloudMode::ColorRgb ? QStringLiteral("RGBD")
                                                                 : QStringLiteral("Depth"))
                  .arg(densityBox_->currentData().toInt()));

    camera_->setSerialNumber(sn);
    camera_->setDisplayStride(densityBox_->currentData().toInt());
    if (!camera_->start(mode)) {
        appendLog(QStringLiteral("启动失败: 无法打开设备"));
        QMessageBox::warning(this, QStringLiteral("启动失败"),
                             QStringLiteral("无法打开设备 SN=%1。\n请确认未被 ROS 占用，可点「刷新」后重试。").arg(sn));
    }
}

void MainWindow::onStop() {
    appendLog(QStringLiteral("正在停止相机…"));
    camera_->stop();
}

void MainWindow::onSave() {
    const QString path = defaultPlyPath();
    appendLog(QStringLiteral("开始保存点云 → %1").arg(path));
    QString err;
    if (camera_->savePly(path, &err)) {
        const QFileInfo fi(path);
        appendLog(QStringLiteral("保存成功: %1  (%2 KB)")
                      .arg(path)
                      .arg(fi.size() / 1024));
        statusBar()->showMessage(QStringLiteral("已保存: ") + path, 5000);
    } else {
        appendLog(QStringLiteral("保存失败: %1").arg(err));
        QMessageBox::warning(this, QStringLiteral("保存失败"), err);
    }
}

void MainWindow::onSaveAs() {
    const QString path = QFileDialog::getSaveFileName(this, QStringLiteral("另存点云"),
                                                      defaultPlyPath(),
                                                      QStringLiteral("PLY (*.ply)"));
    if (path.isEmpty()) {
        appendLog(QStringLiteral("取消另存为"));
        return;
    }
    appendLog(QStringLiteral("开始另存点云 → %1").arg(path));
    QString err;
    if (camera_->savePly(path, &err)) {
        const QFileInfo fi(path);
        appendLog(QStringLiteral("另存成功: %1  (%2 KB)")
                      .arg(path)
                      .arg(fi.size() / 1024));
        statusBar()->showMessage(QStringLiteral("已保存: ") + path, 5000);
    } else {
        appendLog(QStringLiteral("另存失败: %1").arg(err));
        QMessageBox::warning(this, QStringLiteral("保存失败"), err);
    }
}

void MainWindow::onSerialChanged(int) {
    camera_->setSerialNumber(snBox_->currentData().toString());
}

void MainWindow::onModeChanged(int) {
    camera_->setMode(static_cast<OrbbecCamera::CloudMode>(modeBox_->currentData().toInt()));
    if (logView_) {
        appendLog(QStringLiteral("默认保存文件改为: %1").arg(defaultPlyPath()));
    }
}

void MainWindow::onDensityChanged(int) {
    camera_->setDisplayStride(densityBox_->currentData().toInt());
}

void MainWindow::onFrameReady(int pointCount) {
    infoLabel_->setText(QStringLiteral("点数: %1").arg(pointCount));
    view_->reloadFromCloud();
}

void MainWindow::onCameraError(const QString &message) {
    appendLog(QStringLiteral("错误: %1").arg(message));
    statusBar()->showMessage(message, 8000);
}
