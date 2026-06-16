# Qt Face Register Demo

Qt 6 Widgets demo for photo registration.

## Build

```powershell
cmake -S . -B build -DCMAKE_PREFIX_PATH=C:\Qt\6.6.0\msvc2019_64
cmake --build build
.\build\qt_face_register.exe
```

Use mock mode first. Disable mock mode after selecting a real serial port.
