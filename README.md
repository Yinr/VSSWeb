# VSSWeb

一个用 aardio 编写的 Windows 桌面监控客户端，用来承载老式 `IVSWeb` ActiveX 监控页面的核心能力。

## 功能

- 连接设备并预览通道画面。
- 打开/关闭全部通道，或单独控制 1 至 8 路通道。
- 支持云台方向控制。
- 提供系统设置、录像、警报、关于等常用入口。
- 支持保存连接地址、用户名和密码。

## 目录说明

- `main.aardio`: 当前主实现。
- `default.aproj`: aardio 工程文件。
- `lib/`: 配置与日志模块。
- `dlg/`: 设置窗口和辅助工具。
- `res/`: 图标、原始页面备份和接口整理资料。
- `docs/`: 项目文档。

## 运行前提

- 本机需要安装并注册 `CLSID:D639FA00-CB11-4f67-82F2-C0A87EAECD13` 对应的 `IVSWeb` ActiveX。
- aardio 进程位数需要和 ActiveX 位数一致。
- 设备连接信息默认保存在根目录 `config.ini`。

## 构建

- 使用 aardio 打开 `default.aproj`。
- 主入口为 `main.aardio`。
- 发布输出目录为 `dist/`。

## 验证方式

- 这个仓库没有自动化测试。
- 修改后通过运行 aardio 工程手动验证：控件创建、设备登录、通道开关、云台控制、设置保存和退出断开。

## Changelog

- 版本发布记录见 [CHANGELOG.md](CHANGELOG.md)。
