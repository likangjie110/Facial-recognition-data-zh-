# Python项目文件预览

Python CLI 示例，展示标准库封包、mock transport 和 pyserial transport。

工程位置：`examples/python-face-register`

## 项目结构

```text
python-face-register
  - src/
    - face_protocol.py
    - main.py
  - README.md
  - requirements.txt
```

## 文件内容

### `README.md`

````markdown
# Python Face Register Demo

Python demo for `0xF7` photo registration.

## Mock run

```powershell
python src/main.py --mock
```

## Serial run

```powershell
pip install -r requirements.txt
python src/main.py --port COM3 --baud 115200 --image C:\path\face.jpg
```
````

### `requirements.txt`

```text
pyserial>=3.5
```

### `src/face_protocol.py`

```python
"""Protocol helpers for the face photo registration command."""

from __future__ import annotations

from dataclasses import dataclass

SYNC = bytes([0xEF, 0xAA])
MID_ENROLL_WITH_PHOTO = 0xF7
BIO_TYPE_NORMAL_PHOTO = 0x00
MAX_PHOTO_CHUNK = 246


def parity(msg_id: int, data: bytes) -> int:
    """Calculate XOR parity over all bytes after the SyncWord."""
    size = len(data)
    value = msg_id ^ ((size >> 8) & 0xFF) ^ (size & 0xFF)
    for item in data:
        value ^= item
    return value & 0xFF


def build_frame(msg_id: int, data: bytes = b"") -> bytes:
    """Build one complete protocol frame with SyncWord, size, data, and parity."""
    size = len(data)
    return SYNC + bytes([msg_id, (size >> 8) & 0xFF, size & 0xFF]) + data + bytes([parity(msg_id, data)])


def first_packet(photo_length: int, bio_type: int = BIO_TYPE_NORMAL_PHOTO) -> bytes:
    """Build the first photo registration packet with sequence 0 and image length."""
    return bytes([0x00, 0x00]) + photo_length.to_bytes(4, "big") + bytes([bio_type])


def data_packet(seq: int, chunk: bytes) -> bytes:
    """Build one sequenced photo data packet."""
    return seq.to_bytes(2, "big") + chunk


def build_photo_register_frames(photo: bytes) -> list[bytes]:
    """Build all frames required by photo registration, including every chunk."""
    frames = [build_frame(MID_ENROLL_WITH_PHOTO, first_packet(len(photo)))]
    for index, offset in enumerate(range(0, len(photo), MAX_PHOTO_CHUNK), start=1):
        chunk = photo[offset : offset + MAX_PHOTO_CHUNK]
        frames.append(build_frame(MID_ENROLL_WITH_PHOTO, data_packet(index, chunk)))
    return frames


def to_hex(data: bytes) -> str:
    """Format bytes as uppercase hexadecimal text for logs."""
    return " ".join(f"{item:02X}" for item in data)


@dataclass(frozen=True)
class Reply:
    """Parsed mock reply payload."""

    msg_id: int
    result: int
    data: bytes


def parse_mock_reply(frame: bytes) -> Reply:
    """Parse a mock reply frame into message id, result, and extra data."""
    payload = frame[5:-1]
    return Reply(msg_id=payload[0], result=payload[1], data=payload[2:])
```

### `src/main.py`

```python
"""Command-line photo registration demo for mock or serial transport."""

from __future__ import annotations

import argparse
from pathlib import Path

from face_protocol import MID_ENROLL_WITH_PHOTO, build_frame, build_photo_register_frames, to_hex


class MockTransport:
    """Mock transport that prints outgoing frames and returns a successful reply."""

    def __init__(self) -> None:
        """Initialize the sent-frame counter."""
        self.count = 0

    def exchange(self, frame: bytes) -> bytes:
        """Send one frame through the offline mock channel."""
        self.count += 1
        print(f"TX[{self.count}] {to_hex(frame)}")
        return build_frame(0x00, bytes([MID_ENROLL_WITH_PHOTO, 0x00]))


class SerialTransport:
    """Serial transport backed by pyserial for real device communication."""

    def __init__(self, port: str, baud: int, timeout: float = 2.0) -> None:
        """Open a serial port with the requested baud rate and timeout."""
        import serial

        self.serial = serial.Serial(port=port, baudrate=baud, timeout=timeout)

    def exchange(self, frame: bytes) -> bytes:
        """Write one frame and read a bounded reply from the serial port."""
        self.serial.write(frame)
        self.serial.flush()
        return self.serial.read(64)


def demo_photo() -> bytes:
    """Produce deterministic demo image bytes for mock runs."""
    return bytes(item & 0xFF for item in range(512))


def main() -> int:
    """Parse arguments, build photo registration frames, and send them."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="use mock transport")
    parser.add_argument("--port", help="serial port, for example COM3 or /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--image", type=Path)
    args = parser.parse_args()

    photo = args.image.read_bytes() if args.image else demo_photo()
    transport = MockTransport() if args.mock or not args.port else SerialTransport(args.port, args.baud)
    frames = build_photo_register_frames(photo)

    print(f"photo bytes={len(photo)}, frames={len(frames)}")
    for frame in frames:
        reply = transport.exchange(frame)
        print(f"RX {to_hex(reply)}")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 返回

- [项目文件预览索引](/50-项目案例/源码预览/项目文件预览索引.md)
- [项目案例总览](/50-项目案例/项目案例总览.md)
