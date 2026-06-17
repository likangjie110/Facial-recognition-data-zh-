# Cpp项目文件预览

CMake + C++17 示例，展示协议函数拆分、文件读取和离线 mock 发送。

工程位置：`examples/cpp-face-register`

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

## 文件内容

### `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.16)
project(face_register_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(face_register_demo
  src/main.cpp
  src/face_protocol.cpp
)

target_include_directories(face_register_demo PRIVATE src)
```

### `README.md`

````markdown
# C++ Face Register Demo

C++17 demo for building face photo register frames.

## Build

```powershell
cmake -S . -B build
cmake --build build
.\build\face_register_demo.exe --mock
```

Replace `MockTransport` in `src/main.cpp` with UART, TCP, USB, or vendor SDK transport for real devices.
````

### `src/face_protocol.cpp`

```cpp
#include "face_protocol.hpp"

#include <algorithm>
#include <iomanip>
#include <sstream>

namespace aegis::face {

// Builds one complete protocol frame.
Bytes buildFrame(std::uint8_t msgId, const Bytes& data) {
    const auto size = static_cast<std::uint16_t>(data.size());
    Bytes frame;
    frame.reserve(2 + 1 + 2 + data.size() + 1);
    frame.push_back(Sync0);
    frame.push_back(Sync1);
    frame.push_back(msgId);
    frame.push_back(static_cast<std::uint8_t>((size >> 8) & 0xFF));
    frame.push_back(static_cast<std::uint8_t>(size & 0xFF));
    frame.insert(frame.end(), data.begin(), data.end());
    frame.push_back(parity(msgId, size, data));
    return frame;
}

// Builds the sequence-0 metadata packet for photo registration.
Bytes firstPacket(std::uint32_t photoLength) {
    return Bytes{
        0x00,
        0x00,
        static_cast<std::uint8_t>((photoLength >> 24) & 0xFF),
        static_cast<std::uint8_t>((photoLength >> 16) & 0xFF),
        static_cast<std::uint8_t>((photoLength >> 8) & 0xFF),
        static_cast<std::uint8_t>(photoLength & 0xFF),
        BioTypeNormalPhoto,
    };
}

// Builds one sequenced photo data packet.
Bytes dataPacket(std::uint16_t seq, const Bytes& photoChunk) {
    Bytes data;
    data.reserve(2 + photoChunk.size());
    data.push_back(static_cast<std::uint8_t>((seq >> 8) & 0xFF));
    data.push_back(static_cast<std::uint8_t>(seq & 0xFF));
    data.insert(data.end(), photoChunk.begin(), photoChunk.end());
    return data;
}

// Splits a photo into the first packet and all data packets.
std::vector<Bytes> buildPhotoRegisterFrames(const Bytes& photo) {
    std::vector<Bytes> frames;
    frames.push_back(buildFrame(MidEnrollWithPhoto, firstPacket(static_cast<std::uint32_t>(photo.size()))));

    std::size_t offset = 0;
    std::uint16_t seq = 1;
    while (offset < photo.size()) {
        const auto length = std::min(MaxPhotoChunk, photo.size() - offset);
        Bytes chunk(photo.begin() + static_cast<std::ptrdiff_t>(offset),
                    photo.begin() + static_cast<std::ptrdiff_t>(offset + length));
        frames.push_back(buildFrame(MidEnrollWithPhoto, dataPacket(seq, chunk)));
        offset += length;
        seq++;
    }
    return frames;
}

// Calculates XOR parity for one frame.
std::uint8_t parity(std::uint8_t msgId, std::uint16_t size, const Bytes& data) {
    std::uint8_t value = msgId;
    value ^= static_cast<std::uint8_t>((size >> 8) & 0xFF);
    value ^= static_cast<std::uint8_t>(size & 0xFF);
    for (auto item : data) {
        value ^= item;
    }
    return value;
}

// Formats bytes as uppercase hexadecimal text.
std::string toHex(const Bytes& bytes) {
    std::ostringstream stream;
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        if (i != 0) {
            stream << ' ';
        }
        stream << std::uppercase << std::hex << std::setw(2) << std::setfill('0')
               << static_cast<int>(bytes[i]);
    }
    return stream.str();
}

}  // namespace aegis::face
```

### `src/face_protocol.hpp`

```cpp
#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace aegis::face {

/// Byte container used by the protocol helpers.
using Bytes = std::vector<std::uint8_t>;

constexpr std::uint8_t Sync0 = 0xEF;
constexpr std::uint8_t Sync1 = 0xAA;
constexpr std::uint8_t MidEnrollWithPhoto = 0xF7;
constexpr std::uint8_t BioTypeNormalPhoto = 0x00;
constexpr std::size_t MaxPhotoChunk = 246;

/// Builds a complete protocol frame with SyncWord, message id, payload size,
/// payload bytes, and XOR parity.
Bytes buildFrame(std::uint8_t msgId, const Bytes& data);

/// Builds the first photo registration packet with sequence 0 and image length.
Bytes firstPacket(std::uint32_t photoLength);

/// Builds a sequenced packet for one photo chunk.
Bytes dataPacket(std::uint16_t seq, const Bytes& photoChunk);

/// Builds photo registration frames for the first packet and all photo chunks.
std::vector<Bytes> buildPhotoRegisterFrames(const Bytes& photo);

/// Calculates XOR parity over all bytes after the SyncWord.
std::uint8_t parity(std::uint8_t msgId, std::uint16_t size, const Bytes& data);

/// Formats bytes as uppercase hexadecimal text for logs.
std::string toHex(const Bytes& bytes);

}  // namespace aegis::face
```

### `src/main.cpp`

```cpp
#include "face_protocol.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

/// Mock transport that prints outgoing frames and returns a successful reply.
class MockTransport {
public:
    /// Sends one frame through the offline mock channel.
    aegis::face::Bytes exchange(const aegis::face::Bytes& frame) {
        ++count_;
        std::cout << "TX[" << count_ << "] " << aegis::face::toHex(frame) << '\n';
        return aegis::face::buildFrame(0x00, aegis::face::Bytes{aegis::face::MidEnrollWithPhoto, 0x00});
    }

private:
    int count_ = 0;
};

/// Creates deterministic demo image bytes for mock runs.
aegis::face::Bytes demoPhoto() {
    aegis::face::Bytes bytes(512);
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        bytes[i] = static_cast<std::uint8_t>(i & 0xFF);
    }
    return bytes;
}

/// Reads an image file as raw bytes.
aegis::face::Bytes readFile(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot open image file");
    }
    return aegis::face::Bytes(std::istreambuf_iterator<char>(input), {});
}

/// Reads the value following a named command-line option.
std::filesystem::path optionValue(int argc, char** argv, const std::string& name) {
    for (int i = 1; i + 1 < argc; ++i) {
        if (argv[i] == name) {
            return argv[i + 1];
        }
    }
    return {};
}

}  // namespace

/// Command-line entry point for the photo registration demo.
int main(int argc, char** argv) {
    try {
        const auto imagePath = optionValue(argc, argv, "--image");
        const auto photo = imagePath.empty() ? demoPhoto() : readFile(imagePath);
        const auto frames = aegis::face::buildPhotoRegisterFrames(photo);
        MockTransport transport;

        std::cout << "photo bytes=" << photo.size() << ", frames=" << frames.size() << '\n';
        for (const auto& frame : frames) {
            const auto reply = transport.exchange(frame);
            std::cout << "RX " << aegis::face::toHex(reply) << '\n';
        }
        std::cout << "done\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
```

## 返回

- [项目文件预览索引](/50-项目案例/源码预览/项目文件预览索引.md)
- [项目案例总览](/50-项目案例/项目案例总览.md)
