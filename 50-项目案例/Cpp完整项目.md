# C++ 完整项目

标签：#项目案例 #C++ #CMake #照片下发

## 工程位置

`examples/cpp-face-register`

## 功能

- 使用 C++17 实现协议帧构造。
- 支持照片首包和 `246 byte` 分包。
- 提供 `MockTransport`，用于离线验证发送顺序。
- CMake 工程可迁移到 Windows、Linux 或嵌入式交叉编译环境。

## 构建运行

```powershell
cd examples/cpp-face-register
cmake -S . -B build
cmake --build build
.\build\face_register_demo.exe --mock
```

Linux 或 MinGW 环境下可运行：

```bash
./build/face_register_demo --mock --image ./face.jpg
```

## 接入真实设备

替换 `main.cpp` 中的 `MockTransport`：

- Windows：可使用 Win32 Serial API。
- Linux：可使用 termios。
- 嵌入式：将 `FaceProtocol::buildFrame` 生成的字节写入 UART 驱动。

## 关键文件

| 文件 | 说明 |
| --- | --- |
| `CMakeLists.txt` | CMake 构建入口 |
| `src/face_protocol.hpp` | 协议类型和函数声明 |
| `src/face_protocol.cpp` | 帧构造、校验、分包实现 |
| `src/main.cpp` | CLI 入口、mock transport 和调用流程 |

## 源码入口

| 文件 | 在线打开 |
| --- | --- |
| README | <a href="examples/cpp-face-register/README.md" target="_blank" rel="noopener">打开</a> |
| CMake 配置 | <a href="examples/cpp-face-register/CMakeLists.txt" target="_blank" rel="noopener">打开</a> |
| 协议头文件 | <a href="examples/cpp-face-register/src/face_protocol.hpp" target="_blank" rel="noopener">打开</a> |
| 协议实现 | <a href="examples/cpp-face-register/src/face_protocol.cpp" target="_blank" rel="noopener">打开</a> |
| 调用入口 | <a href="examples/cpp-face-register/src/main.cpp" target="_blank" rel="noopener">打开</a> |
