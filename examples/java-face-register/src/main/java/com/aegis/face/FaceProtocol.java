package com.aegis.face;

import java.io.ByteArrayOutputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public final class FaceProtocol {
    public static final int SYNC_0 = 0xEF;
    public static final int SYNC_1 = 0xAA;
    public static final int MID_ENROLL_WITH_PHOTO = 0xF7;
    public static final int BIO_TYPE_NORMAL_PHOTO = 0x00;
    public static final int MAX_PHOTO_CHUNK = 246;

    private FaceProtocol() {
    }

    public static byte[] buildFrame(int msgId, byte[] data) {
        int size = data.length;
        ByteArrayOutputStream out = new ByteArrayOutputStream(2 + 1 + 2 + size + 1);
        out.write(SYNC_0);
        out.write(SYNC_1);
        out.write(msgId & 0xFF);
        out.write((size >>> 8) & 0xFF);
        out.write(size & 0xFF);
        out.write(data, 0, data.length);
        out.write(parity(msgId, size, data));
        return out.toByteArray();
    }

    public static List<byte[]> buildPhotoRegisterFrames(byte[] photo) {
        List<byte[]> frames = new ArrayList<>();
        frames.add(buildFrame(MID_ENROLL_WITH_PHOTO, firstPacket(photo.length)));

        int offset = 0;
        int seq = 1;
        while (offset < photo.length) {
            int length = Math.min(MAX_PHOTO_CHUNK, photo.length - offset);
            byte[] chunk = Arrays.copyOfRange(photo, offset, offset + length);
            frames.add(buildFrame(MID_ENROLL_WITH_PHOTO, dataPacket(seq, chunk)));
            offset += length;
            seq++;
        }

        return frames;
    }

    public static byte[] firstPacket(int photoLength) {
        return new byte[] {
            0x00,
            0x00,
            (byte) ((photoLength >>> 24) & 0xFF),
            (byte) ((photoLength >>> 16) & 0xFF),
            (byte) ((photoLength >>> 8) & 0xFF),
            (byte) (photoLength & 0xFF),
            (byte) BIO_TYPE_NORMAL_PHOTO
        };
    }

    public static byte[] dataPacket(int seq, byte[] photoChunk) {
        byte[] data = new byte[2 + photoChunk.length];
        data[0] = (byte) ((seq >>> 8) & 0xFF);
        data[1] = (byte) (seq & 0xFF);
        System.arraycopy(photoChunk, 0, data, 2, photoChunk.length);
        return data;
    }

    public static int parity(int msgId, int size, byte[] data) {
        int value = msgId & 0xFF;
        value ^= (size >>> 8) & 0xFF;
        value ^= size & 0xFF;
        for (byte item : data) {
            value ^= item & 0xFF;
        }
        return value & 0xFF;
    }

    public static String hex(byte[] bytes) {
        StringBuilder builder = new StringBuilder();
        for (byte item : bytes) {
            if (builder.length() > 0) {
                builder.append(' ');
            }
            builder.append(String.format("%02X", item & 0xFF));
        }
        return builder.toString();
    }
}
