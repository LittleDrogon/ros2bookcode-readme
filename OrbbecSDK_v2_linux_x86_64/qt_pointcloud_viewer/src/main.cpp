#include "MainWindow.h"

#include <QApplication>
#include <QSurfaceFormat>

int main(int argc, char *argv[]) {
    QSurfaceFormat fmt;
    fmt.setDepthBufferSize(24);
    fmt.setSwapBehavior(QSurfaceFormat::DoubleBuffer);
    QSurfaceFormat::setDefaultFormat(fmt);

    QApplication app(argc, argv);
    app.setApplicationName(QStringLiteral("qt_pointcloud_viewer"));
    app.setOrganizationName(QStringLiteral("OrbbecDemo"));

    MainWindow window;
    window.show();
    return app.exec();
}
