# C++ Face Register Demo

C++17 demo for building face photo register frames.

## Build

```powershell
cmake -S . -B build
cmake --build build
.\build\face_register_demo.exe --mock
```

Replace `MockTransport` in `src/main.cpp` with UART, TCP, USB, or vendor SDK transport for real devices.
