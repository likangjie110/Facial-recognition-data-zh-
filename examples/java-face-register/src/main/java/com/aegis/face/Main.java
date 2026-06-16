package com.aegis.face;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public final class Main {
    interface Transport {
        byte[] exchange(byte[] frame) throws IOException;
    }

    static final class MockTransport implements Transport {
        private int count = 0;

        @Override
        public byte[] exchange(byte[] frame) {
            count++;
            System.out.println("TX[" + count + "] " + FaceProtocol.hex(frame));
            return FaceProtocol.buildFrame(0x00, new byte[] {(byte) FaceProtocol.MID_ENROLL_WITH_PHOTO, 0x00});
        }
    }

    private Main() {
    }

    public static void main(String[] args) throws Exception {
        Path imagePath = optionValue(args, "--image");
        byte[] photo = imagePath == null ? demoPhoto() : Files.readAllBytes(imagePath);
        Transport transport = new MockTransport();

        List<byte[]> frames = FaceProtocol.buildPhotoRegisterFrames(photo);
        System.out.println("photo bytes=" + photo.length + ", frames=" + frames.size());
        for (byte[] frame : frames) {
            byte[] reply = transport.exchange(frame);
            System.out.println("RX " + FaceProtocol.hex(reply));
        }
        System.out.println("done");
    }

    private static Path optionValue(String[] args, String name) {
        for (int i = 0; i + 1 < args.length; i++) {
            if (name.equals(args[i])) {
                return Paths.get(args[i + 1]);
            }
        }
        return null;
    }

    private static byte[] demoPhoto() {
        byte[] bytes = new byte[512];
        for (int i = 0; i < bytes.length; i++) {
            bytes[i] = (byte) (i & 0xFF);
        }
        return bytes;
    }
}
