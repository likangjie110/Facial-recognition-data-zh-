# Qt项目文件预览

Qt 6 Widgets + SerialPort 示例，展示图形界面、串口发送和 mock 模式。

工程位置：`examples/qt-face-register`

## 项目结构

```text
qt-face-register
  - src/
    - main.cpp
    - mainwindow.cpp
    - mainwindow.h
  - CMakeLists.txt
  - README.md
```

## 文件内容

### `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.16)
project(qt_face_register LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets SerialPort)

add_executable(qt_face_register
  src/main.cpp
  src/mainwindow.h
  src/mainwindow.cpp
)

target_link_libraries(qt_face_register PRIVATE Qt6::Widgets Qt6::SerialPort)
```

### `README.md`

````markdown
# Qt Face Register Demo

Qt 6 Widgets demo for photo registration.

## Build

```powershell
cmake -S . -B build -DCMAKE_PREFIX_PATH=C:\Qt\6.6.0\msvc2019_64
cmake --build build
.\build\qt_face_register.exe
```

Use mock mode first. Disable mock mode after selecting a real serial port.
````

### `src/main.cpp`

```cpp
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
```

### `src/mainwindow.cpp`

```cpp
#include "mainwindow.h"

#include <QCheckBox>
#include <QComboBox>
#include <QFile>
#include <QFileDialog>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QSerialPortInfo>
#include <QTextEdit>
#include <QVBoxLayout>
#include <QtEndian>

namespace {
constexpr quint8 Sync0 = 0xEF;
constexpr quint8 Sync1 = 0xAA;
constexpr quint8 MidEnrollWithPhoto = 0xF7;
constexpr quint8 BioTypeNormalPhoto = 0x00;
constexpr int MaxPhotoChunk = 246;

/// Formats a byte array as uppercase hexadecimal text.
QString toHex(const QByteArray& bytes) {
    return bytes.toHex(' ').toUpper();
}
}  // namespace

/// Builds the main window and wires the UI controls.
MainWindow::MainWindow(QWidget* parent) : QMainWindow(parent) {
    auto* central = new QWidget(this);
    auto* layout = new QVBoxLayout(central);
    auto* topRow = new QHBoxLayout();

    portCombo_ = new QComboBox(central);
    auto* refreshButton = new QPushButton("Refresh Ports", central);
    mockMode_ = new QCheckBox("Mock mode", central);
    mockMode_->setChecked(true);
    auto* chooseButton = new QPushButton("Choose Image", central);
    sendButton_ = new QPushButton("Send Photo Register", central);
    imageLabel_ = new QLabel("No image selected; demo bytes will be used.", central);
    log_ = new QTextEdit(central);
    log_->setReadOnly(true);

    topRow->addWidget(portCombo_);
    topRow->addWidget(refreshButton);
    topRow->addWidget(mockMode_);
    topRow->addWidget(chooseButton);
    topRow->addWidget(sendButton_);
    layout->addLayout(topRow);
    layout->addWidget(imageLabel_);
    layout->addWidget(log_);
    setCentralWidget(central);
    setWindowTitle("Face Register Demo");

    connect(refreshButton, &QPushButton::clicked, this, &MainWindow::refreshPorts);
    connect(chooseButton, &QPushButton::clicked, this, &MainWindow::chooseImage);
    connect(sendButton_, &QPushButton::clicked, this, &MainWindow::sendPhotoRegister);
    connect(&serial_, &QSerialPort::readyRead, this, &MainWindow::readSerialData);
    refreshPorts();
}

/// Refreshes the serial port combobox with currently available ports.
void MainWindow::refreshPorts() {
    portCombo_->clear();
    for (const auto& info : QSerialPortInfo::availablePorts()) {
        portCombo_->addItem(info.portName());
    }
}

/// Lets the user choose a local image file.
void MainWindow::chooseImage() {
    imagePath_ = QFileDialog::getOpenFileName(this, "Choose face image", QString(), "Images (*.jpg *.jpeg *.png);;All files (*.*)");
    imageLabel_->setText(imagePath_.isEmpty() ? "No image selected; demo bytes will be used." : imagePath_);
}

/// Builds the photo registration frames and sends them through the active transport.
void MainWindow::sendPhotoRegister() {
    QByteArray photo;
    if (imagePath_.isEmpty()) {
        photo.resize(512);
        for (int i = 0; i < photo.size(); ++i) {
            photo[i] = static_cast<char>(i & 0xFF);
        }
    } else {
        QFile file(imagePath_);
        if (!file.open(QIODevice::ReadOnly)) {
            appendLog("cannot open image file");
            return;
        }
        photo = file.readAll();
    }

    if (!mockMode_->isChecked() && !serial_.isOpen()) {
        serial_.setPortName(portCombo_->currentText());
        serial_.setBaudRate(QSerialPort::Baud115200);
        if (!serial_.open(QIODevice::ReadWrite)) {
            appendLog("open serial failed: " + serial_.errorString());
            return;
        }
    }

    const auto frames = buildPhotoRegisterFrames(photo);
    appendLog(QString("photo bytes=%1, frames=%2").arg(photo.size()).arg(frames.size()));
    for (const auto& frame : frames) {
        sendFrame(frame);
    }
}

/// Appends serial replies to the on-screen log.
void MainWindow::readSerialData() {
    appendLog("RX " + toHex(serial_.readAll()));
}

/// Builds a complete protocol frame.
QByteArray MainWindow::buildFrame(quint8 msgId, const QByteArray& data) const {
    const quint16 size = static_cast<quint16>(data.size());
    QByteArray frame;
    frame.reserve(2 + 1 + 2 + data.size() + 1);
    frame.append(static_cast<char>(Sync0));
    frame.append(static_cast<char>(Sync1));
    frame.append(static_cast<char>(msgId));
    frame.append(static_cast<char>((size >> 8) & 0xFF));
    frame.append(static_cast<char>(size & 0xFF));
    frame.append(data);
    frame.append(static_cast<char>(parity(msgId, data)));
    return frame;
}

/// Builds the first photo registration packet.
QByteArray MainWindow::firstPacket(qint64 photoLength) const {
    QByteArray data;
    data.append('\0');
    data.append('\0');
    data.append(static_cast<char>((photoLength >> 24) & 0xFF));
    data.append(static_cast<char>((photoLength >> 16) & 0xFF));
    data.append(static_cast<char>((photoLength >> 8) & 0xFF));
    data.append(static_cast<char>(photoLength & 0xFF));
    data.append(static_cast<char>(BioTypeNormalPhoto));
    return data;
}

/// Builds one data packet for a photo chunk.
QByteArray MainWindow::dataPacket(quint16 seq, const QByteArray& chunk) const {
    QByteArray data;
    data.append(static_cast<char>((seq >> 8) & 0xFF));
    data.append(static_cast<char>(seq & 0xFF));
    data.append(chunk);
    return data;
}

/// Builds all frames required by photo registration.
QList<QByteArray> MainWindow::buildPhotoRegisterFrames(const QByteArray& photo) const {
    QList<QByteArray> frames;
    frames.append(buildFrame(MidEnrollWithPhoto, firstPacket(photo.size())));
    quint16 seq = 1;
    for (int offset = 0; offset < photo.size(); offset += MaxPhotoChunk) {
        frames.append(buildFrame(MidEnrollWithPhoto, dataPacket(seq, photo.mid(offset, MaxPhotoChunk))));
        ++seq;
    }
    return frames;
}

/// Calculates XOR parity for the payload bytes after the SyncWord.
quint8 MainWindow::parity(quint8 msgId, const QByteArray& data) const {
    const quint16 size = static_cast<quint16>(data.size());
    quint8 value = msgId ^ static_cast<quint8>((size >> 8) & 0xFF) ^ static_cast<quint8>(size & 0xFF);
    for (const auto item : data) {
        value ^= static_cast<quint8>(item);
    }
    return value;
}

/// Appends one line to the log view.
void MainWindow::appendLog(const QString& line) {
    log_->append(line);
}

/// Sends one frame in mock mode or through the serial port.
void MainWindow::sendFrame(const QByteArray& frame) {
    appendLog("TX " + toHex(frame));
    if (mockMode_->isChecked()) {
        appendLog("RX " + toHex(buildFrame(0x00, QByteArray::fromHex("F7 00"))));
        return;
    }
    serial_.write(frame);
}
```

### `src/mainwindow.h`

```cpp
#pragma once

#include <QByteArray>
#include <QMainWindow>
#include <QSerialPort>

class QCheckBox;
class QComboBox;
class QLabel;
class QPushButton;
class QTextEdit;

/// Main Qt window for choosing an image, sending frames, and showing replies.
class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    /// Builds the main window and initializes the UI.
    explicit MainWindow(QWidget* parent = nullptr);

private slots:
    /// Lets the user choose a face image from disk.
    void chooseImage();
    /// Builds and sends the photo registration frames.
    void sendPhotoRegister();
    /// Refreshes the available serial ports.
    void refreshPorts();
    /// Reads and logs serial data from the device.
    void readSerialData();

private:
    /// Builds one complete protocol frame.
    QByteArray buildFrame(quint8 msgId, const QByteArray& data) const;
    /// Builds the first packet for a photo registration sequence.
    QByteArray firstPacket(qint64 photoLength) const;
    /// Builds a single data packet for one photo chunk.
    QByteArray dataPacket(quint16 seq, const QByteArray& chunk) const;
    /// Builds all frames needed for photo registration.
    QList<QByteArray> buildPhotoRegisterFrames(const QByteArray& photo) const;
    /// Calculates XOR parity for one frame.
    quint8 parity(quint8 msgId, const QByteArray& data) const;
    /// Appends a message to the on-screen log.
    void appendLog(const QString& line);
    /// Sends a single frame through mock mode or serial mode.
    void sendFrame(const QByteArray& frame);

    /// Serial port selector.
    QComboBox* portCombo_ = nullptr;
    /// Displays the selected image path.
    QLabel* imageLabel_ = nullptr;
    /// Enables offline mock mode.
    QCheckBox* mockMode_ = nullptr;
    /// Shows sent frames and replies.
    QTextEdit* log_ = nullptr;
    /// Starts the registration flow.
    QPushButton* sendButton_ = nullptr;
    /// Underlying serial port handle.
    QSerialPort serial_;
    /// Selected image file path.
    QString imagePath_;
};
```

## 返回

- [项目文件预览索引](/50-项目案例/源码预览/项目文件预览索引.md)
- [项目案例总览](/50-项目案例/项目案例总览.md)
