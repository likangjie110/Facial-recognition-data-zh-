#pragma once

#include <QByteArray>
#include <QMainWindow>
#include <QSerialPort>

class QCheckBox;
class QComboBox;
class QLabel;
class QPushButton;
class QTextEdit;

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget* parent = nullptr);

private slots:
    void chooseImage();
    void sendPhotoRegister();
    void refreshPorts();
    void readSerialData();

private:
    QByteArray buildFrame(quint8 msgId, const QByteArray& data) const;
    QByteArray firstPacket(qint64 photoLength) const;
    QByteArray dataPacket(quint16 seq, const QByteArray& chunk) const;
    QList<QByteArray> buildPhotoRegisterFrames(const QByteArray& photo) const;
    quint8 parity(quint8 msgId, const QByteArray& data) const;
    void appendLog(const QString& line);
    void sendFrame(const QByteArray& frame);

    QComboBox* portCombo_ = nullptr;
    QLabel* imageLabel_ = nullptr;
    QCheckBox* mockMode_ = nullptr;
    QTextEdit* log_ = nullptr;
    QPushButton* sendButton_ = nullptr;
    QSerialPort serial_;
    QString imagePath_;
};
