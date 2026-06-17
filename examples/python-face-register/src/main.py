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
