from __future__ import annotations

import argparse
from pathlib import Path

from face_protocol import MID_ENROLL_WITH_PHOTO, build_frame, build_photo_register_frames, to_hex


class MockTransport:
    def __init__(self) -> None:
        self.count = 0

    def exchange(self, frame: bytes) -> bytes:
        self.count += 1
        print(f"TX[{self.count}] {to_hex(frame)}")
        return build_frame(0x00, bytes([MID_ENROLL_WITH_PHOTO, 0x00]))


class SerialTransport:
    def __init__(self, port: str, baud: int, timeout: float = 2.0) -> None:
        import serial

        self.serial = serial.Serial(port=port, baudrate=baud, timeout=timeout)

    def exchange(self, frame: bytes) -> bytes:
        self.serial.write(frame)
        self.serial.flush()
        return self.serial.read(64)


def demo_photo() -> bytes:
    return bytes(item & 0xFF for item in range(512))


def main() -> int:
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
