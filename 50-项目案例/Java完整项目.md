# Java 完整项目

标签：#项目案例 #Java #照片下发 #协议封包

## 工程位置

`examples/java-face-register`

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

## 源码入口

| 文件 | 在线打开 |
| --- | --- |
| README | <a href="examples/java-face-register/README.md" target="_blank" rel="noopener">打开</a> |
| Maven 配置 | <a href="examples/java-face-register/pom.xml" target="_blank" rel="noopener">打开</a> |
| 协议实现 | <a href="examples/java-face-register/src/main/java/com/aegis/face/FaceProtocol.java" target="_blank" rel="noopener">打开</a> |
| 调用入口 | <a href="examples/java-face-register/src/main/java/com/aegis/face/Main.java" target="_blank" rel="noopener">打开</a> |

## 参考

- [项目案例总览](项目案例总览.md)
- [软件开发手册](/20-软件开发/软件开发手册.md)
