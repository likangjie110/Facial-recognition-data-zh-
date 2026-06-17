# Qt 完整项目

标签：#项目案例 #Qt #QSerialPort #图形工具

## 工程位置

`examples/qt-face-register`

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

## 功能

- Qt 6 Widgets 图形界面。
- 可选择串口并发送照片注册帧。
- 支持 mock 模式，方便先检查封包结果。
- 日志窗口显示发送帧、分包序号和串口返回数据。

## 构建运行

```powershell
cd examples/qt-face-register
cmake -S . -B build -DCMAKE_PREFIX_PATH=C:\Qt\6.6.0\msvc2019_64
cmake --build build
.\build\qt_face_register.exe
```

`CMAKE_PREFIX_PATH` 请替换为本机 Qt 安装目录。

## 接入真实设备

1. 在界面中选择串口。
2. 取消勾选 `Mock mode`。
3. 选择照片文件。
4. 点击 `Send Photo Register`。

Qt SerialPort 模块提供串口配置、读写和 RS-232 控制信号能力；示例使用 `QSerialPort::write` 发送帧，并通过 `readyRead` + `readAll` 接收返回数据。

## 关键文件

| 文件 | 说明 |
| --- | --- |
| `CMakeLists.txt` | Qt 6 Widgets + SerialPort 构建 |
| `src/main.cpp` | Qt 应用入口 |
| `src/mainwindow.h` | 主窗口声明 |
| `src/mainwindow.cpp` | UI、协议封包、串口调用 |

## 文件内容预览

源码预览页包含 `README.md`、`CMakeLists.txt`、`main.cpp`、`mainwindow.h`、`mainwindow.cpp` 的完整文件内容。

- [查看 Qt 项目全部文件内容](/50-项目案例/源码预览/Qt项目文件预览.md)

## 参考

- [项目案例总览](/50-项目案例/项目案例总览.md)
- [项目文件预览索引](/50-项目案例/源码预览/项目文件预览索引.md)
- [Qt Serial Port 官方文档](https://doc.qt.io/qt-6/qtserialport-index.html)
- [QSerialPort 官方文档](https://doc.qt.io/qt-6/qserialport.html)
