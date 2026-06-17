# C++ 完整项目

标签：#项目案例 #C++ #CMake #照片下发

## 工程位置

`examples/cpp-face-register`

## 项目结构

```text
cpp-face-register
  - src/
    - face_protocol.cpp
    - face_protocol.hpp
    - main.cpp
  - CMakeLists.txt
  - README.md
```

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

## 文件内容预览

源码预览页包含 `README.md`、`CMakeLists.txt`、`face_protocol.hpp`、`face_protocol.cpp`、`main.cpp` 的完整文件内容。

- [查看 C++ 项目全部文件内容](/50-项目案例/源码预览/Cpp项目文件预览.md)

## 参考

- [项目案例总览](/50-项目案例/项目案例总览.md)
- [项目文件预览索引](/50-项目案例/源码预览/项目文件预览索引.md)
