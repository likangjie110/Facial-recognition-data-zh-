# Python 完整项目

标签：#项目案例 #Python #脚本 #照片下发

## 工程位置

`examples/python-face-register`

## 项目结构

```text
python-face-register
  - src/
    - face_protocol.py
    - main.py
  - README.md
  - requirements.txt
```

## 功能

- 使用标准库实现协议封包和照片分包。
- 默认 mock 运行，不需要安装串口依赖。
- 指定 `--port` 后可通过 pyserial 连接真实串口。
- 适合作为产线脚本、协议排查脚本或跨语言对照实现。

## 运行

```powershell
cd examples/python-face-register
python src/main.py --mock
```

指定照片：

```powershell
python src/main.py --mock --image C:\path\face.jpg
```

真实串口：

```powershell
pip install -r requirements.txt
python src/main.py --port COM3 --baud 115200 --image C:\path\face.jpg
```

## 关键文件

| 文件 | 说明 |
| --- | --- |
| `src/face_protocol.py` | 协议封包、校验、分包 |
| `src/main.py` | CLI、mock transport、pyserial transport |
| `requirements.txt` | 真实串口模式所需 pyserial |

## 文件内容预览

源码预览页包含 `README.md`、`requirements.txt`、`face_protocol.py`、`main.py` 的完整文件内容。

- [查看 Python 项目全部文件内容](/50-项目案例/源码预览/Python项目文件预览.md)

## 接入提示

没有真实设备时先使用 `--mock`，确认输出帧和分包数量；接设备后再打开串口模式，并根据模组返回的 `MID_REPLY` 检查 `result`。

## 参考

- [项目案例总览](/50-项目案例/项目案例总览.md)
- [项目文件预览索引](/50-项目案例/源码预览/项目文件预览索引.md)
