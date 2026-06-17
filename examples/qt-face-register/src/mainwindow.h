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
