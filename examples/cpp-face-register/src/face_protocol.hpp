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
