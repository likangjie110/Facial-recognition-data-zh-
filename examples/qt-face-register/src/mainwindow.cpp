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

QString toHex(const QByteArray& bytes) {
    return bytes.toHex(' ').toUpper();
}
}  // namespace

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

void MainWindow::refreshPorts() {
    portCombo_->clear();
    for (const auto& info : QSerialPortInfo::availablePorts()) {
        portCombo_->addItem(info.portName());
    }
}

void MainWindow::chooseImage() {
    imagePath_ = QFileDialog::getOpenFileName(this, "Choose face image", QString(), "Images (*.jpg *.jpeg *.png);;All files (*.*)");
    imageLabel_->setText(imagePath_.isEmpty() ? "No image selected; demo bytes will be used." : imagePath_);
}

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

void MainWindow::readSerialData() {
    appendLog("RX " + toHex(serial_.readAll()));
}

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

QByteArray MainWindow::dataPacket(quint16 seq, const QByteArray& chunk) const {
    QByteArray data;
    data.append(static_cast<char>((seq >> 8) & 0xFF));
    data.append(static_cast<char>(seq & 0xFF));
    data.append(chunk);
    return data;
}

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

quint8 MainWindow::parity(quint8 msgId, const QByteArray& data) const {
    const quint16 size = static_cast<quint16>(data.size());
    quint8 value = msgId ^ static_cast<quint8>((size >> 8) & 0xFF) ^ static_cast<quint8>(size & 0xFF);
    for (const auto item : data) {
        value ^= static_cast<quint8>(item);
    }
    return value;
}

void MainWindow::appendLog(const QString& line) {
    log_->append(line);
}

void MainWindow::sendFrame(const QByteArray& frame) {
    appendLog("TX " + toHex(frame));
    if (mockMode_->isChecked()) {
        appendLog("RX " + toHex(buildFrame(0x00, QByteArray::fromHex("F7 00"))));
        return;
    }
    serial_.write(frame);
}
