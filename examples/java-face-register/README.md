# Java Face Register Demo

完整 Java 调用案例，演示照片注册 `0xF7` 的协议封包和发送流程。

## Run

```powershell
mvn -q package
java -jar target/java-face-register-1.0.0.jar --mock
```

## Real integration

Replace `MockTransport` with serial, TCP, USB CDC, JNA, or vendor SDK transport. Keep `FaceProtocol` unchanged.
