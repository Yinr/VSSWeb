# VSSWeb

一个用 aardio 编写的 Windows 桌面监控客户端，用来承载老式 `IVSWeb` ActiveX 监控页面的核心能力。

## 项目概述
- 主程序入口是 `main.aardio`。
- 当前实现使用 `web.form` 承载一段极简 HTML，在 IE 内核里创建 `IVSWeb` ActiveX，并通过 `window.external` 与 aardio 互相调用。
- 目标不是完整复刻原网页，而是保留最常用的监控能力：连接设备、打开/关闭通道、打开全部通道、云台控制，以及几个常用菜单入口。

## 目录说明
- `main.aardio`: 当前主实现。
- `dlg/native.aardio`: 纯 `createEmbed()` 的备用实验版。
- `dlg/exportOCX.aardio`: 导出 ActiveX 类型信息的小工具。
- `lib/`: 配置与日志模块。
- `res/VSSWebBackup/`: 从设备下载下来的原始 Web 页面备份。
- `res/IVSWeb_typeinfo.txt`: 导出的 ActiveX 接口信息。
- `res/README.md`: 对原始页面、接口和流程的整理说明。

## 运行前提
- 本机需要安装并注册 `CLSID:D639FA00-CB11-4f67-82F2-C0A87EAECD13` 对应的 `IVSWeb` ActiveX。
- aardio 进程位数需要和 ActiveX 位数一致。
- 设备连接信息默认保存在根目录 `config.ini`。

## 验证方式
- 这个仓库没有自动化测试。
- 修改后通常通过运行 aardio 工程手动验证：控件是否创建成功、是否能登录、是否能自动打开全部通道、单通道开关是否正常、云台按钮是否生效。
