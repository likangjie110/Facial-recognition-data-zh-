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
