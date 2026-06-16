#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace aegis::face {

using Bytes = std::vector<std::uint8_t>;

constexpr std::uint8_t Sync0 = 0xEF;
constexpr std::uint8_t Sync1 = 0xAA;
constexpr std::uint8_t MidEnrollWithPhoto = 0xF7;
constexpr std::uint8_t BioTypeNormalPhoto = 0x00;
constexpr std::size_t MaxPhotoChunk = 246;

Bytes buildFrame(std::uint8_t msgId, const Bytes& data);
Bytes firstPacket(std::uint32_t photoLength);
Bytes dataPacket(std::uint16_t seq, const Bytes& photoChunk);
std::vector<Bytes> buildPhotoRegisterFrames(const Bytes& photo);
std::uint8_t parity(std::uint8_t msgId, std::uint16_t size, const Bytes& data);
std::string toHex(const Bytes& bytes);

}  // namespace aegis::face
