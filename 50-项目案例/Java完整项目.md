# Java 完整项目

标签：#项目案例 #Java #照片下发 #协议封包

## 工程位置

`examples/java-face-register`

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

## 功能

- 生成 `0xEF 0xAA` 协议帧。
- 计算去掉 `SyncWord` 后的 XOR 校验。
- 按 `0xF7` 照片注册流程发送首包和照片分包。
- 默认使用 mock transport，可在没有设备时跑通调用链。

## 运行

```powershell
cd examples/java-face-register
mvn -q package
java -jar target/java-face-register-1.0.0.jar --mock
```

如需指定照片：

```powershell
java -jar target/java-face-register-1.0.0.jar --mock --image C:\path\face.jpg
```

## 接入真实设备

替换 `Main.java` 中的 `MockTransport`：

- 串口：使用 jSerialComm、RXTX 或 JavaComm 写入 `byte[]`。
- JNA：把 `frame` 传给厂商 DLL/SO 的发送接口。
- TCP/USB：实现同样的 `Transport.exchange(byte[])` 方法。

## 关键文件

| 文件 | 说明 |
| --- | --- |
| `pom.xml` | Maven 工程定义 |
| `src/main/java/com/aegis/face/FaceProtocol.java` | 协议封包、校验、照片分包 |
| `src/main/java/com/aegis/face/Main.java` | CLI 入口和 mock 调用链 |

## 文件内容预览

源码预览页包含 `README.md`、`pom.xml`、`FaceProtocol.java`、`Main.java` 的完整文件内容。

- [查看 Java 项目全部文件内容](/50-项目案例/源码预览/Java项目文件预览.md)

## 参考

- [项目案例总览](/50-项目案例/项目案例总览.md)
- [项目文件预览索引](/50-项目案例/源码预览/项目文件预览索引.md)
- [软件开发手册](/20-软件开发/软件开发手册.md)
