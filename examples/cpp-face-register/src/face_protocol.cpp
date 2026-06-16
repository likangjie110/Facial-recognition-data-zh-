#include "face_protocol.hpp"

#include <algorithm>
#include <iomanip>
#include <sstream>

namespace aegis::face {

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

Bytes dataPacket(std::uint16_t seq, const Bytes& photoChunk) {
    Bytes data;
    data.reserve(2 + photoChunk.size());
    data.push_back(static_cast<std::uint8_t>((seq >> 8) & 0xFF));
    data.push_back(static_cast<std::uint8_t>(seq & 0xFF));
    data.insert(data.end(), photoChunk.begin(), photoChunk.end());
    return data;
}

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

std::uint8_t parity(std::uint8_t msgId, std::uint16_t size, const Bytes& data) {
    std::uint8_t value = msgId;
    value ^= static_cast<std::uint8_t>((size >> 8) & 0xFF);
    value ^= static_cast<std::uint8_t>(size & 0xFF);
    for (auto item : data) {
        value ^= item;
    }
    return value;
}

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
