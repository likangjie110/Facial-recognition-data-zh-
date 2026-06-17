package com.aegis.face;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

/**
 * Command-line entry point for running the photo registration example.
 */
public final class Main {
    /**
     * Transport abstraction used to swap mock, serial, TCP, or vendor SDK calls.
     */
    interface Transport {
        /**
         * Sends one protocol frame and returns the raw reply frame.
         */
        byte[] exchange(byte[] frame) throws IOException;
    }

    /**
     * Offline transport that prints outgoing frames and returns a successful mock reply.
     */
    static final class MockTransport implements Transport {
        private int count = 0;

        /**
         * Logs the frame and returns a simulated MID_REPLY payload.
         */
        @Override
        public byte[] exchange(byte[] frame) {
            count++;
            System.out.println("TX[" + count + "] " + FaceProtocol.hex(frame));
            return FaceProtocol.buildFrame(0x00, new byte[] {(byte) FaceProtocol.MID_ENROLL_WITH_PHOTO, 0x00});
        }
    }

    private Main() {
    }

    /**
     * Parses options, prepares photo bytes, builds frames, and sends them through a transport.
     */
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

    /**
     * Reads the value that follows a named command-line option.
     */
    private static Path optionValue(String[] args, String name) {
        for (int i = 0; i + 1 < args.length; i++) {
            if (name.equals(args[i])) {
                return Paths.get(args[i + 1]);
            }
        }
        return null;
    }

    /**
     * Produces deterministic demo image bytes for mock runs without a real file.
     */
    private static byte[] demoPhoto() {
        byte[] bytes = new byte[512];
        for (int i = 0; i < bytes.length; i++) {
            bytes[i] = (byte) (i & 0xFF);
        }
        return bytes;
    }
}
