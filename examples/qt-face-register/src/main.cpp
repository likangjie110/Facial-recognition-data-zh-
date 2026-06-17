#include "mainwindow.h"

#include <QApplication>

/// Qt application entry point for the face register demo.
int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    MainWindow window;
    window.resize(820, 560);
    window.show();
    return app.exec();
}
