# Java项目文件预览

Maven CLI 示例，展示照片注册协议封包和 mock transport 调用链。

工程位置：`examples/java-face-register`

## 项目结构

```text
java-face-register
  - src/
    - main/
      - java/
        - com/
          - aegis/
            - face/
              - FaceProtocol.java
              - Main.java
  - pom.xml
  - README.md
```

## 文件内容

### `pom.xml`

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.aegis.face</groupId>
  <artifactId>java-face-register</artifactId>
  <version>1.0.0</version>
  <properties>
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.4.2</version>
        <configuration>
          <archive>
            <manifest>
              <mainClass>com.aegis.face.Main</mainClass>
            </manifest>
          </archive>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
```

### `README.md`

````markdown
# Java Face Register Demo

完整 Java 调用案例，演示照片注册 `0xF7` 的协议封包和发送流程。

## Run

```powershell
mvn -q package
java -jar target/java-face-register-1.0.0.jar --mock
```

## Real integration

Replace `MockTransport` with serial, TCP, USB CDC, JNA, or vendor SDK transport. Keep `FaceProtocol` unchanged.
````

### `src/main/java/com/aegis/face/FaceProtocol.java`

```java
package com.aegis.face;

import java.io.ByteArrayOutputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Utility methods for the face module photo registration protocol.
 */
public final class FaceProtocol {
    public static final int SYNC_0 = 0xEF;
    public static final int SYNC_1 = 0xAA;
    public static final int MID_ENROLL_WITH_PHOTO = 0xF7;
    public static final int BIO_TYPE_NORMAL_PHOTO = 0x00;
    public static final int MAX_PHOTO_CHUNK = 246;

    /**
     * Prevents instantiation because this class only exposes static helpers.
     */
    private FaceProtocol() {
    }

    /**
     * Builds a complete protocol frame with SyncWord, message id, payload size,
     * payload bytes, and XOR parity.
     */
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

    /**
     * Builds all frames required by photo registration, including the first
     * metadata packet and all 246-byte photo chunks.
     */
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

    /**
     * Builds the first photo registration packet with sequence 0, photo length,
     * and biometric type.
     */
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

    /**
     * Builds a sequenced photo data packet for one image chunk.
     */
    public static byte[] dataPacket(int seq, byte[] photoChunk) {
        byte[] data = new byte[2 + photoChunk.length];
        data[0] = (byte) ((seq >>> 8) & 0xFF);
        data[1] = (byte) (seq & 0xFF);
        System.arraycopy(photoChunk, 0, data, 2, photoChunk.length);
        return data;
    }

    /**
     * Calculates the XOR parity over all bytes after the SyncWord.
     */
    public static int parity(int msgId, int size, byte[] data) {
        int value = msgId & 0xFF;
        value ^= (size >>> 8) & 0xFF;
        value ^= size & 0xFF;
        for (byte item : data) {
            value ^= item & 0xFF;
        }
        return value & 0xFF;
    }

    /**
     * Formats a byte array as uppercase hexadecimal text for logging.
     */
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
```

### `src/main/java/com/aegis/face/Main.java`

```java
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

    /**
     * Prevents instantiation because this class only exposes the CLI entry point.
     */
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
```

## 返回

- [项目文件预览索引](/50-项目案例/源码预览/项目文件预览索引.md)
- [项目案例总览](/50-项目案例/项目案例总览.md)
