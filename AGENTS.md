# VSSWeb Agent Notes

## 项目入口
- 主入口是 `main.aardio`。
- 工程文件是 `default.aproj`，输出配置是 `dist/VSSWeb.exe`。

## 先看哪里
- 先读 `main.aardio`、`default.aproj`、`res/README.md`。
- aardio 语法或标准库用法不确定时，查官方文档：`https://www.aardio.com/zh-cn/doc/`。

## 参考资料
- `res/README.md` 用来理解 ActiveX 接口、原始页面生命周期和当前接线方式。
- `res/VSSWebBackup/` 是原始设备页面备份，用来核对原始调用方式。
- `res/IVSWeb_typeinfo.txt` 是 `dlg/exportOCX.aardio` 导出的 ActiveX 类型信息，用来查接口名和签名线索。

## 目录分工
- `dlg/native.aardio` 是纯 `createEmbed()` 对照实现。
- `dlg/exportOCX.aardio` 用来重新导出 ActiveX 类型信息。

## 集成方式
- 通过 `web.form.emulation(11001)` + `wb.write(makeHtml())` 创建 ActiveX。
- 在 `<object>` 创建阶段通过 `<param>` 传入初始化参数，重点保留 `lVideoWindNum=4`。
- aardio 调 JS 统一走 `wb.doScript(...)`。
- ActiveX 事件通过 HTML 里的 `for="ocx" event="..."` 脚本桥接到 `wb.external`。
- `ConnectAllChannle` 是 ActiveX 真实方法名，按原拼写调用。

## 配置与日志
- 配置与日志相关实现先以当前代码为准。
- 配置项调整时，同步查看 `lib/config.aardio` 和 `main.aardio`。
- 日志输出位置同时查看 `logger.aardio` 和调用方初始化代码。

## 验证
- 运行前确认本机已安装并注册 `CLSID:D639FA00-CB11-4f67-82F2-C0A87EAECD13` 对应的 IVSWeb ActiveX，且 aardio 进程位数与控件一致。
- 修改后运行 aardio 工程，手动检查：控件创建、登录、自动打开全部通道、单通道开关、云台按钮、设置弹窗回写 `config.ini`、退出时断开。
- 验证 ActiveX 方法或签名时，运行 `dlg/exportOCX.aardio` 重新导出类型信息，再和原始页面调用交叉确认。
