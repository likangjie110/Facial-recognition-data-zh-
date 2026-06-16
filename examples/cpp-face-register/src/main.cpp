#include "face_protocol.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

class MockTransport {
public:
    aegis::face::Bytes exchange(const aegis::face::Bytes& frame) {
        ++count_;
        std::cout << "TX[" << count_ << "] " << aegis::face::toHex(frame) << '\n';
        return aegis::face::buildFrame(0x00, aegis::face::Bytes{aegis::face::MidEnrollWithPhoto, 0x00});
    }

private:
    int count_ = 0;
};

aegis::face::Bytes demoPhoto() {
    aegis::face::Bytes bytes(512);
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        bytes[i] = static_cast<std::uint8_t>(i & 0xFF);
    }
    return bytes;
}

aegis::face::Bytes readFile(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot open image file");
    }
    return aegis::face::Bytes(std::istreambuf_iterator<char>(input), {});
}

std::filesystem::path optionValue(int argc, char** argv, const std::string& name) {
    for (int i = 1; i + 1 < argc; ++i) {
        if (argv[i] == name) {
            return argv[i + 1];
        }
    }
    return {};
}

}  // namespace

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
