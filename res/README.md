# IVSWeb ActiveX 控件接口整理文档

## 1. 控件基本信息

### 1.1 ActiveX CLSID

```text
CLSID:D639FA00-CB11-4f67-82F2-C0A87EAECD13
```

原始 `olp.js` 通过 `document.write()` 写入 `<object>` 标签加载该 ActiveX 控件，并指定 `codebase="IVSWeb.cab#version=1,0,2,5"`。

原始创建方式：

```html
<object id="ocx"
        width="100%"
        height="100%"
        border="0"
        classid="CLSID:D639FA00-CB11-4f67-82F2-C0A87EAECD13"
        codebase="IVSWeb.cab#version=1,0,2,5">
</object>
```

---

## 2. 初始化参数

原始网页不是先创建控件再设置属性，而是在 `<object>` 创建阶段通过 `<param>` 传入初始化参数。我们测试发现，这一点很关键，尤其是 `lVideoWindNum=4`，它影响默认 4 窗格初始化。

| 参数名                  |                    原始值 | 作用                                              |
| -------------------- | ---------------------: | ----------------------------------------------- |
| `lVideoWindNum`      |                    `4` | 初始化视频窗口数量。实际测试中，用 HTML `<param>` 创建时能正常默认 4 窗格。 |
| `VideoWindBGColor`   |                   `""` | 视频窗口背景色。原始网页为空。                                 |
| `VideoWindBarColor`  |                   `""` | 视频窗口栏颜色。原始网页为空。                                 |
| `VideoWindTextColor` |                   `""` | 视频窗口文字颜色。原始网页为空。                                |
| `SetLangFromIP`      | `window.location.href` | 传入当前页面地址，推测用于语言包或设备地址上下文。                       |
| `SetHostPort`        |                 `8000` | 主机服务端口。                                         |
| `SetUpnpPort`        |                 `8000` | UPnP 或设备相关端口。                                   |
| `SetLanguage`        |                  `101` | 语言 ID。具体枚举未确认。                                  |

推荐最小 HTML 初始化模板：

```html
<object id="ocx"
        width="100%"
        height="100%"
        border="0"
        classid="CLSID:D639FA00-CB11-4f67-82F2-C0A87EAECD13"
        codebase="IVSWeb.cab#version=1,0,2,5">
    <param name="lVideoWindNum" value="4">
    <param name="VideoWindBGColor" value="">
    <param name="VideoWindBarColor" value="">
    <param name="VideoWindTextColor" value="">
    <param name="SetLangFromIP" value="http://设备IP/">
    <param name="SetHostPort" value="8000">
    <param name="SetUpnpPort" value="8000">
    <param name="SetLanguage" value="101">
</object>
```

---

# 3. 生命周期工作流程

## 3.1 原始网页生命周期

原始网页的主要启动流程如下：

1. 页面加载 `oem_t.js`、`m.js`、`m.css`。
2. `olp.js` 写入 ActiveX `<object>`。
3. 页面 `domready` 后执行语言初始化、读取设置、填充用户名、获取通道列表。
4. 用户登录时调用 `ocx.LoginDeviceEx(...)`。
5. 登录成功后调用 `getDevSetting()`、`getChnList()`、`resize()`，隐藏登录层，显示主界面。
6. 通道按钮由 `StateChanged(ci, ps, wid)` 事件更新状态。
7. 当前窗口、回放控制条、码率刷新等由 `ReturnWindInfo(wid, cid, ps, sit)` 和 `StateChanged(...)` 协同处理。

原始登录逻辑大致是：

```js
var r = ocx.LoginDeviceEx(ip, 0, username, password, logintype);
if (r) {
    getDevSetting();
    getChnList();
    resize();
    $('password').value = "";
    $('l').style.display = "none";
    $('m').style.top = "0px";
}
```

`getDevSetting()` 通过 `GetDevConfig(1)` 判断是否支持主码流 / 子码流；`getChnList()` 通过 `GetChannelName()` 生成通道列表。

---

## 3.2 当前 aardio 简化版生命周期

当前最终方案不加载原始网页 UI，而是使用 `web.form` 承载一个极简 HTML：

1. aardio 创建主窗口。
2. `web.form(mainForm.videoHost)` 创建 IE WebBrowser 宿主。
3. `wb.write(makeHtml())` 写入极简 HTML。
4. 极简 HTML 创建 ActiveX `<object>`，并用 `<param>` 传入初始化参数。
5. aardio 通过 `wb.doScript("函数名();")` 调用页面内 JS。
6. JS 再调用 `ocx.LoginDeviceEx()`、`ocx.ConnectAllChannle()` 等 ActiveX 方法。
7. ActiveX 事件通过：

```html
<script language="javascript" for="ocx" event="StateChanged(ci,ps,wid)">
    window.external.StateChanged(ci,ps,wid);
</script>
```

回传到 aardio。

当前代码已经验证 `wb.doScript(...)` 方式可用，而 `wb.document.script.xxx(...)` 在本环境中无法可靠调用 JS。当前代码的极简 HTML、`window.external` 回调、`LoginDeviceEx`、`ConnectAllChannle` 等封装都来自最终实现。

---

# 4. 接口分类总览

根据类型信息导出，ActiveX 主要暴露以下方法。

## 4.1 登录与会话

| 方法                   | 返回值    | 作用               |
| -------------------- | ------ | ---------------- |
| `LoginDevice(...)`   | `bool` | 旧登录接口。           |
| `LoginDeviceEx(...)` | `bool` | 扩展登录接口，原始网页实际使用。 |
| `LogoutDevice()`     | `bool` | 登出设备。            |
| `Restart()`          | `bool` | 重启设备。            |

## 4.2 实时预览

| 方法                                          | 返回值    | 作用                               |
| ------------------------------------------- | ------ | -------------------------------- |
| `ConnectRealVideo(lChannelNo, lStreamType)` | `bool` | 打开指定实时通道。                        |
| `DisConnectRealVideo(lChannelNo)`           | `bool` | 关闭指定实时通道。                        |
| `ConnectAllChannle()`                       | `bool` | 打开全部通道。注意原控件拼写是 `Channle`。       |
| `DisConnectAllChannel()`                    | `bool` | 关闭全部通道。                          |
| `GetCurPlayChan()`                          | `word` | 获取当前播放通道，测试中经常返回 `<null>`，可靠性有限。 |

## 4.3 回放 / 本地播放

| 方法                          | 返回值    | 作用                                             |
| --------------------------- | ------ | ---------------------------------------------- |
| `ShowPlayback()`            | `bool` | 打开录像查询 / 回放窗口。                                 |
| `PlayVideo(operationType)`  | `bool` | 控制回放播放状态。                                      |
| `SetPlayPos(posValue)`      | `bool` | 设置回放进度位置。                                      |
| `CloseLocalPlay()`          | `bool` | 关闭本地播放 / 回放。                                   |
| `QuickOperation(operation)` | `bool` | 快速操作，原网页用 `QuickOperation(0)` 对应本地播放 / 录像相关入口。 |

## 4.4 配置 / 菜单窗口

| 方法                   | 返回值       | 作用        |
| -------------------- | --------- | --------- |
| `ShowDeviceConfig()` | `bool`    | 打开系统设置窗口。 |
| `ShowAlarm()`        | `bool`    | 打开报警设置窗口。 |
| `AboutBox()`         | `pointer` | 打开关于窗口。   |
| `ShowNetUpgrade()`   | `bool`    | 网络升级窗口。   |
| `ShowBurning()`      | `bool`    | 刻录相关窗口。   |

原始 HTML 顶部菜单就是直接调用 `ShowDeviceConfig()`、`ShowPlayback()`、`ShowAlarm()`，关于按钮最终调用 `AboutBox()`。

## 4.5 云台控制

| 方法                                                    | 返回值                        | 作用                            |
| ----------------------------------------------------- | -------------------------- | ----------------------------- |
| `ControlPtz(lCommand, lParm1, lParm2, lParm3, iStop)` | `bool`                     | 云台控制，方向、预置点、巡航、辅助开关等都通过此接口完成。 |
| `ShowSetptz()`                                        | 未在当前 typeinfo 片段中列出，但原网页调用 | 云台设置。实际可用性未单独验证。              |

原始 HTML 中方向键和按钮都调用 `ControlPtz`，例如上、下、左、右分别使用命令 `0 / 1 / 2 / 3`，并在鼠标按下时传 `iStop=0`、松开时传 `iStop=1`。

## 4.6 图像颜色与码率

| 方法                                                                | 返回值      | 作用                     |
| ----------------------------------------------------------------- | -------- | ---------------------- |
| `GetColor()`                                                      | `string` | 获取亮度、对比度、饱和度、色调。       |
| `SetColor(lRegionNum, lBrightness, lContrast, lSaturation, lHue)` | `bool`   | 设置图像参数。                |
| `GetCurChanFulx()`                                                | `int`    | 获取当前通道码率。              |
| `GetTatolFulx()`                                                  | `int`    | 获取总码率。原方法名拼写为 `Tatol`。 |
| `GetPlaySpeed()`                                                  | `string` | 获取回放速度 / 播放速度显示字符串。    |

原网页 `ReturnWindInfo` 和 `StateChanged` 中会根据 `ps` 值调用 `flushData()`、`flushData1()`、`flushSpeed()`，分别显示实时码率、空闲码率、回放速度。

## 4.7 设备能力与通道信息

| 方法                     | 返回值      | 作用                                           |
| ---------------------- | -------- | -------------------------------------------- |
| `GetDevConfig(type)`   | `string` | 获取设备能力配置。原网页用 `GetDevConfig(1)` 判断主码流 / 子码流。 |
| `GetChannelName()`     | `string` | 获取通道列表和通道名称。                                 |
| `Translate(sourceStr)` | `string` | 从 ActiveX 获取翻译文本。                            |

原网页 `getDevSetting()` 调用 `GetDevConfig(1)`，并根据返回字符串判断是否显示子码流菜单；`getChnList()` 调用 `GetChannelName()`，用 TAB 和 `char(16)` 拆分通道 ID 与名称。

---

# 5. 详细接口说明

## 5.1 `LoginDeviceEx`

### 定义

```text
bool LoginDeviceEx(
    string lpstrDeviceIp,
    int lPort,
    string lpstrUsername,
    string lpstrPassword,
    word lSpecCap
)
```

类型信息中返回值为 `bool`。参数包括设备 IP、端口、用户名、密码、扩展能力标志。

### 原始网页调用

```js
var r = ocx.LoginDeviceEx(ip, 0, username, password, logintype);
```

其中 `ip = location.hostname`，`logintype = 0`。登录成功后会初始化设备能力、通道列表、界面尺寸，并隐藏登录层。

### 当前 aardio 调用

```js
var r = ocx.LoginDeviceEx(ip, 0, username, password, 0);
window.external.LoginResult(r);
return r;
```

### 参数说明

| 参数              | 类型       | 说明                      |
| --------------- | -------- | ----------------------- |
| `lpstrDeviceIp` | `string` | 设备 IP，例如 `192.168.0.5`。 |
| `lPort`         | `int`    | 登录端口。原网页使用 `0`。         |
| `lpstrUsername` | `string` | 用户名。                    |
| `lpstrPassword` | `string` | 密码。                     |
| `lSpecCap`      | `word`   | 登录类型或扩展能力。原网页使用 `0`。    |

### 返回值

| 返回值     | 含义    |
| ------- | ----- |
| `true`  | 登录成功。 |
| `false` | 登录失败。 |

### 注意事项

当前 aardio 方案不直接依赖 `doScript` 返回值，而是让 JS 主动调用 `window.external.LoginResult(r)` 回调，避免返回值转换不稳定。最终实现中就是这样处理的。

---

## 5.2 `LogoutDevice`

### 定义

```text
bool LogoutDevice()
```

用于退出设备登录。

### 原始网页逻辑

原网页 `lo()` 调用 `ocx.LogoutDevice()`，然后执行 `loeft()`。`loeft()` 会隐藏主界面、显示登录层、关闭菜单、复位打开全部状态，并调用 `ocx.CloseLocalPlay()`。

### 当前推荐调用

```js
try { ocx.DisConnectAllChannel(); } catch(e) {}
try { ocx.LogoutDevice(); } catch(e) {}
try { ocx.CloseLocalPlay(); } catch(e) {}
```

### 返回值

| 返回值     | 含义            |
| ------- | ------------- |
| `true`  | 登出成功。         |
| `false` | 登出失败或当前状态不支持。 |

---

## 5.3 `ConnectRealVideo`

### 定义

```text
bool ConnectRealVideo(
    int lChannelNo,
    int lStreamType
)
```

类型信息中返回 `bool`。

### 作用

打开指定通道的实时视频。

### 参数说明

| 参数            | 类型    | 说明                                      |
| ------------- | ----- | --------------------------------------- |
| `lChannelNo`  | `int` | 通道 ID，0-base。通道 01 对应 `0`，通道 08 对应 `7`。 |
| `lStreamType` | `int` | 码流类型。原网页 `1` 为主码流，`2` 为子码流。             |

### 原始网页调用

通道列表点击逻辑：

```js
if ($(o).hasClass('cl1')) {
    ocx.ConnectRealVideo(ch, 1);
} else {
    ocx.DisConnectRealVideo(ch);
}
```

通道右侧码流菜单调用：

```js
ocx.ConnectRealVideo(parseInt(cid), f)
```

其中 `f=1` 表示主码流，`f=2` 表示子码流。

### 状态变化

打开通道后，ActiveX 会触发：

```text
StateChanged(ci, ps, wid)
```

测试中，打开通道 01 时触发 `ci=0, ps=1`；在同一个窗口打开通道 02 时，会先触发通道 01 的 `ps=0`，再触发通道 02 的 `ps=1`。这说明同窗口切换通道时，旧通道会被控件内部自动关闭。

### 返回值

| 返回值     | 含义      |
| ------- | ------- |
| `true`  | 请求打开成功。 |
| `false` | 打开失败。   |

---

## 5.4 `DisConnectRealVideo`

### 定义

```text
bool DisConnectRealVideo(int lChannelNo)
```

类型信息中返回 `bool`。

### 作用

关闭指定实时通道。

### 参数说明

| 参数           | 类型    | 说明            |
| ------------ | ----- | ------------- |
| `lChannelNo` | `int` | 通道 ID，0-base。 |

### 状态变化

正常关闭时，会触发：

```text
StateChanged(ci, ps=0, wid)
```

测试中，关闭通道 02 / 03 / 04 时都触发了 `ps=0` 事件。

### 重要异常情况

如果该通道已经因为窗口切换、回放占用或其他内部状态不再处于实时预览，`DisConnectRealVideo(ch)` 可能返回 `false`。测试日志里出现过 `DisConnectRealVideo(0)=false`、`DisConnectRealVideo(1)=false` 的情况。

因此当前程序保留 fallback：如果关闭失败，就将按钮状态重置为“打开 xx”，避免 UI 卡死。

---

## 5.5 `ConnectAllChannle`

### 定义

```text
bool ConnectAllChannle()
```

注意方法名拼写为 `Channle`，类型信息中返回 `bool`。

### 作用

打开全部通道，并由 ActiveX 内部负责分配到多个视频窗口。

### 原始网页调用

```js
if (ocx.ConnectAllChannle()) {
    gopenall = 1;
    o.innerText = ts;
}
```

原网页没有 JS 循环打开每个通道，也没有显式指定窗口号。

### 测试结果

测试中，调用 `ConnectAllChannle()` 后，ActiveX 依次触发了 01 到 08 的 `StateChanged(..., ps=1, ...)`，说明“打开全部”确实由控件内部完成通道分配。

### 返回值

| 返回值     | 含义        |
| ------- | --------- |
| `true`  | 打开全部请求成功。 |
| `false` | 打开失败。     |

---

## 5.6 `DisConnectAllChannel`

### 定义

```text
bool DisConnectAllChannel()
```

类型信息中返回 `bool`。

### 作用

关闭全部通道。

### 原始网页调用

```js
if (ocx.DisConnectAllChannel()) {
    gopenall = 0;
    o.innerText = tb;
}
```

### 测试结果

调用后，测试日志中 01 到 08 都触发了 `StateChanged(..., ps=0, ...)`。

---

## 5.7 `ShowDeviceConfig`

### 定义

```text
bool ShowDeviceConfig()
```

类型信息中返回 `bool`。

### 作用

打开系统设置窗口。

### 原始网页调用

顶部菜单：

```html
<a class='menu1' onclick="ocx.ShowDeviceConfig()">
```



### 当前封装

```js
function showDeviceConfig(){
    var r = ocx.ShowDeviceConfig();
    return r;
}
```

### 返回值

| 返回值     | 含义      |
| ------- | ------- |
| `true`  | 窗口打开成功。 |
| `false` | 打开失败。   |

---

## 5.8 `ShowPlayback`

### 定义

```text
bool ShowPlayback()
```

类型信息中返回 `bool`。

### 作用

打开录像查询 / 回放窗口。

### 原始网页调用

顶部菜单：

```html
<a class='menu2' onclick="ocx.ShowPlayback()">
```



### 回放状态管理

原网页并不在 `ShowPlayback()` 前主动关闭实时通道，而是依赖回调状态：

* `ReturnWindInfo(wid,cid,ps,sit)` 中，`ps==4 || ps==5` 时显示回放控制条。
* `StateChanged(ci,ps,wid)` 中，如果 `wid == gwid` 且 `ps==3 || ps==5`，也显示回放控制条。
* 通道列表样式只在 `ci != -1 && ci != 32` 时修改；`ci==32` 被当作特殊播放状态排除。

### 当前程序策略

当前程序参考原网页：

1. 通道按钮状态只由 `StateChanged` 更新。
2. `ReturnWindInfo` 只记录当前窗口和窗口状态，不主动修改通道按钮。
3. `ps==3` 在当前二态按钮里按“非实时预览状态”处理，按钮恢复为“打开 xx”。
4. `closeChannel()` 如果返回 `false`，做 UI fallback，避免按钮卡死。

---

## 5.9 `ShowAlarm`

### 定义

```text
bool ShowAlarm()
```

类型信息中返回 `bool`。

### 作用

打开警报设置窗口。

### 原始网页调用

顶部菜单：

```html
<a class='menu3' onclick="ocx.ShowAlarm()">
```



---

## 5.10 `AboutBox`

### 定义

```text
pointer AboutBox()
```

类型信息中返回 `pointer`。

### 作用

打开 ActiveX 关于窗口。

### 原始网页调用

原网页顶部“关于”按钮调用 `showAbout()`，此前分析确认该函数最终调用 `ocx.AboutBox()`。类型信息中也存在 `AboutBox()`。

当前封装：

```js
function showAbout(){
    ocx.AboutBox();
    return true;
}
```

---

## 5.11 `ControlPtz`

### 定义

```text
bool ControlPtz(
    int lCommand,
    int lParm1,
    int lParm2,
    int lParm3,
    int iStop
)
```

类型信息中返回 `bool`。

### 参数说明

| 参数         | 说明                            |
| ---------- | ----------------------------- |
| `lCommand` | 云台命令。方向、巡航、辅助功能都通过不同命令号区分。    |
| `lParm1`   | 参数 1。不同命令含义不同。                |
| `lParm2`   | 参数 2。方向控制中通常作为速度值。            |
| `lParm3`   | 参数 3。不同命令含义不同。                |
| `iStop`    | 是否停止。`0` 通常表示开始动作，`1` 表示停止动作。 |

### 常用方向命令

原网页键盘和按钮中使用：

| 动作 | 调用                                                          |
| -- | ----------------------------------------------------------- |
| 上  | `ControlPtz(0,0,step,0,0)` 开始，`ControlPtz(0,0,step,0,1)` 停止 |
| 下  | `ControlPtz(1,0,step,0,0)` 开始，`ControlPtz(1,0,step,0,1)` 停止 |
| 左  | `ControlPtz(2,0,step,0,0)` 开始，`ControlPtz(2,0,step,0,1)` 停止 |
| 右  | `ControlPtz(3,0,step,0,0)` 开始，`ControlPtz(3,0,step,0,1)` 停止 |

原网页中 `step` 来自输入框 `ps`，默认值为 `5`。

### 其他命令示例

原网页还使用了很多高级云台命令，例如：

| 功能                        | 命令                                                    |
| ------------------------- | ----------------------------------------------------- |
| 云台开关 / PTZ control toggle | `ControlPtz(51,0,0,0,0/1)`                            |
| AUX ON / OFF              | `ControlPtz(52,...)` / `ControlPtz(53,...)`           |
| Auto-Tour                 | `ControlPtz(13,1,0,76,0)` / `ControlPtz(13,1,0,96,0)` |
| Auto-Pan                  | `ControlPtz(39,...)` / `ControlPtz(40,...)`           |
| Auto-Scan                 | `ControlPtz(43,...)` / `ControlPtz(44,...)`           |
| Pattern                   | `ControlPtz(47,...)` / `ControlPtz(48,...)`           |
| Flip                      | `ControlPtz(50,0,0,0,0)`                              |

这些命令来自原始 HTML 的云台区域。

---

## 5.12 `GetDevConfig`

### 定义

```text
string GetDevConfig(int type)
```

类型信息中返回 `string`。

### 原始用途

原网页使用：

```js
sret = ocx.GetDevConfig(1);
strhtm = "<a onclick='onmu(1)'>MainStream</a>";
if (sret.substring(1,2) == "1") {
    strhtm += "<a onclick='onmu(2)'>SecondStream</a>";
}
```

这说明 `GetDevConfig(1)` 的返回字符串至少用于判断是否支持子码流。

### 参数说明

| 参数     | 说明                      |
| ------ | ----------------------- |
| `type` | 配置类别。已知 `1` 用于设备码流能力查询。 |

### 返回值结构

未完整公开。根据原网页可知：

| 位置               | 含义                 |
| ---------------- | ------------------ |
| `substring(1,2)` | 如果为 `"1"`，显示子码流选项。 |

---

## 5.13 `GetChannelName`

### 定义

```text
string GetChannelName()
```

类型信息中返回 `string`。

### 原始用途

原网页用它生成通道列表：

```js
sc = ocx.GetChannelName();
sc = sc.substr(0, sc.length - 1);
t = sc.split(String.fromCharCode(9));
ts = t[i].split(String.fromCharCode(16));
```



### 返回值结构

根据原始 JS 解析逻辑，返回值结构推断如下：

```text
通道ID + char(16) + 通道名 + char(9) + 通道ID + char(16) + 通道名 + char(9) + ...
```

其中：

| 分隔符  | 字符                        | 作用             |
| ---- | ------------------------- | -------------- |
| 一级分隔 | `String.fromCharCode(9)`  | 分隔多个通道。        |
| 二级分隔 | `String.fromCharCode(16)` | 分隔通道 ID 和通道名称。 |

### 示例结构

```text
0<0x10>01<0x09>1<0x10>02<0x09>...
```

实际通道名称可能不是简单的 `01`，而是设备端设置的名称。

---

## 5.14 `GetColor` / `SetColor`

### 定义

```text
string GetColor()

bool SetColor(
    int lRegionNum,
    int lBrightness,
    int lContrast,
    int lSaturation,
    int lHue
)
```

类型信息中列出 `GetColor()` 返回 `string`，`SetColor(...)` 返回 `bool`。

### 原始用途

原网页 `getcolors()` 调用 `GetColor()`，并用逗号拆分：

```js
colors = ocx.GetColor();
t = colors.split(',');
```

然后将四个值绑定到亮度、对比度、饱和度、色调滑块。`setcolors()` 调用：

```js
ocx.SetColor(0, gca, gcb, gcc, gcd);
```



### 返回值结构

```text
brightness,contrast,saturation,hue
```

推断为逗号分隔的 4 个整数。

---

## 5.15 `PlayVideo`

### 定义

```text
bool PlayVideo(word operationType)
```

类型信息中返回 `bool`。

### 原始用途

原网页回放控制函数：

```js
function videoControl(_value){
    ocx.PlayVideo(_value);

    if(_value == 3) {
        flushData();
    } else {
        flushSpeed();
    }
}
```



### 参数说明

`operationType` 枚举未完整公开。根据原网页注释，`3` 表示停止。

|   值 | 推断含义                             |
| --: | -------------------------------- |
| `3` | 停止。                              |
|  其他 | 播放、暂停、快进、慢放等，需结合原 UI 按钮或进一步测试确认。 |

---

## 5.16 `SetPlayPos`

### 定义

```text
bool SetPlayPos(int posValue)
```

类型信息中返回 `bool`。

### 原始用途

原网页在回放进度条 slider 完成拖动后调用：

```js
ocx.SetPlayPos(step);
```

并且 `ReturnPlayState(pos)` 事件会回调当前位置，再更新 slider。

### 参数说明

| 参数         | 说明                                                  |
| ---------- | --------------------------------------------------- |
| `posValue` | 回放进度位置。原网页 slider 设置 `steps:1000`，所以推测范围是 `0~1000`。 |

---

## 5.17 `CloseLocalPlay`

### 定义

```text
bool CloseLocalPlay()
```

类型信息中返回 `bool`。

### 作用

关闭本地播放 / 回放。

### 原始网页用途

原网页退出登录流程 `loeft()` 中调用 `ocx.CloseLocalPlay()`。

### 当前使用建议

当前程序不在每次打开通道前强制调用它，以免破坏 ActiveX 原始回放流程。建议只在：

* 退出设备；
* 关闭程序；
* 用户明确需要退出回放；

时调用。

---

## 5.18 `SetDeviceMode`

### 定义

```text
bool SetDeviceMode(int type, int value)
```

类型信息中返回 `bool`。

### 测试结论

我们做过自动测试：

* `type=0` 时多个 `value` 返回 `true`，但肉眼未看到布局变化。
* `type=1~10` 多数返回 `false`。
* `GetCurPlayChan()` 在测试中多次返回 `<null>`。

因此目前不能确认它能选择窗口、设置分屏或恢复窗口布局。

### 当前建议

不建议在主程序中依赖 `SetDeviceMode` 实现窗口布局或窗口选择。默认 4 窗格应通过 `<param name="lVideoWindNum" value="4">` 在 ActiveX 创建时传入。

---

# 6. 事件回调说明

事件没有出现在类型信息导出中，但原始 HTML 使用了 IE ActiveX 事件脚本语法：

```html
<script language="javascript" for="ocx" event="StateChanged(ci,ps,wid)">
</script>
```

当前 aardio 极简 HTML 也沿用此方式，再通过 `window.external` 回传。

---

## 6.1 `StateChanged(ci, ps, wid)`

### 作用

通道播放状态变化事件。原网页中，**通道列表状态只由这个事件更新**。

### 参数说明

| 参数    | 说明                                               |
| ----- | ------------------------------------------------ |
| `ci`  | Channel ID，通道 ID。0-base。特殊值 `-1`、`32` 不作为普通通道处理。 |
| `ps`  | Play State，播放状态。                                 |
| `wid` | Window ID，窗口 ID。测试中常为 `<null>`，原网页会与 `gwid` 比较。  |

### 原始网页状态处理

原网页逻辑：

```js
if (ci != -1 && ci != 32) {
    if (ps == 0) addClass('cl1');
    if (ps == 1) addClass('cl2');
    if (ps == 3) addClass('cl3');
}
```

并且：

```js
if (wid == gwid) {
    if (ps == 3 || ps == 5) 显示回放控制条;
    else 隐藏回放控制条;
}
```



### 当前程序映射

因为当前右侧按钮只有“打开 / 关闭”二态，所以采用：

|              `ps` | 原网页样式       | 当前程序处理                          |
| ----------------: | ----------- | ------------------------------- |
|               `0` | `cl1`       | 通道关闭，按钮显示“打开 xx”。               |
|               `1` | `cl2`       | 通道实时播放中，按钮显示“关闭 xx”。            |
|               `2` | 原网页用于码率刷新   | 当前也视为播放中。                       |
|               `3` | `cl3`       | 当前视为非普通实时预览状态，按钮恢复“打开 xx”，避免卡死。 |
|               `5` | 回放 / 播放控制状态 | 不作为普通通道按钮直接处理。                  |
| `ci=-1` 或 `ci=32` | 特殊状态        | 不更新通道按钮。                        |

### 测试结果

测试中已确认：

* 打开通道会触发 `StateChanged(ci, ps=1)`。
* 在同一窗口打开另一个通道时，旧通道会触发 `ps=0`。
* 打开全部通道会依次触发 01~08 的 `ps=1`。
* 关闭全部通道会依次触发 01~08 的 `ps=0`。

---

## 6.2 `ReturnWindInfo(wid, cid, ps, sit)`

### 作用

当前视频窗口信息回调。原网页用它记录当前窗口 ID、云台状态、控制回放条显示、刷新码率或回放速度。

### 参数说明

| 参数    | 说明                              |
| ----- | ------------------------------- |
| `wid` | 当前窗口 ID。点击视频窗口时会返回。             |
| `cid` | 当前窗口绑定通道 ID，0-base；空窗口可能是 `-1`。 |
| `ps`  | 当前窗口播放状态。                       |
| `sit` | 云台状态。原网页保存为 `gptz`。             |

### 原网页状态处理

原网页逻辑：

* `gptz = sit`
* `gwid = wid`
* `ps==4 || ps==5` 时显示回放控制条
* `ps==1 || ps==2` 时刷新实时码率
* `ps==0` 时刷新空闲码率并隐藏回放控制条
* `ps==5` 时刷新回放速度
* 最后调用 `setptzs()` 更新云台状态显示。

### 当前程序策略

当前程序参考原网页：

* 记录 `currentWid = wid`
* 维护 `winMap["w" + wid] = cid`
* 维护 `winState["w" + wid] = ps`
* **不在 `ReturnWindInfo` 里修改通道按钮状态**
* 通道按钮只由 `StateChanged` 更新

这样可以避免回放状态下错误地重置通道按钮。

---

## 6.3 `ReturnPlayState(pos)`

### 作用

回放进度回调。原网页中用于更新回放进度条：

```js
sldtopos(gsld, pos);
```



### 参数说明

| 参数    | 说明                                           |
| ----- | -------------------------------------------- |
| `pos` | 当前回放进度位置。推测范围和 `SetPlayPos` 一致，可能为 `0~1000`。 |

### 当前程序状态

当前简化版尚未实现回放进度条，因此暂未接入该事件。

---

## 6.4 `DeviceDisconnected(ip, pt)`

### 作用

设备断开事件。

### 原始网页处理

原网页收到后调用：

```js
loeft();
```

即回到登录状态，关闭菜单、复位打开全部状态、关闭本地播放。

### 当前程序处理

当前程序收到后：

* `isLoggedIn = 0`
* 清空 8 个通道按钮状态
* 清空当前窗口映射
* 状态栏显示设备断开

---

## 6.5 `DeviceChanged(strDevIp, lPort, lType)`

### 作用

设备地址或设备状态变化事件。

### 原始网页处理

原网页中，如果 `lType == 3`，会登出并跳转到新的设备 IP。

### 当前程序状态

当前简化版只记录日志并显示状态，不自动跳转。

---

# 7. 状态模型

## 7.1 原始网页通道状态模型

原始网页使用 CSS 三态：

| 类名    | 触发条件                          | 含义                              |
| ----- | ----------------------------- | ------------------------------- |
| `cl1` | `StateChanged(ci, ps=0, ...)` | 关闭 / 未播放                        |
| `cl2` | `StateChanged(ci, ps=1, ...)` | 实时播放中                           |
| `cl3` | `StateChanged(ci, ps=3, ...)` | 非普通实时播放状态，可能与回放 / 异常 / 其他播放状态有关 |

原网页只在 `ci != -1 && ci != 32` 时更新通道列表；这说明 `ci=-1` 和 `ci=32` 是特殊事件，不应当作为普通通道处理。

---

## 7.2 当前程序状态模型

当前程序只有二态按钮：

| 内部变量                     | 含义                     |
| ------------------------ | ---------------------- |
| `chOpened[i] = 0`        | 通道 `i` 关闭，按钮显示“打开 xx”。 |
| `chOpened[i] = 1`        | 通道 `i` 打开，按钮显示“关闭 xx”。 |
| `winMap["w"+wid] = cid`  | 窗口 `wid` 当前通道为 `cid`。  |
| `winState["w"+wid] = ps` | 窗口 `wid` 当前播放状态。       |

由于按钮只有二态，所以当前程序将：

* `ps=1/2` 映射为打开；
* `ps=0` 映射为关闭；
* `ps=3` 映射为“非普通实时状态”，按钮恢复为打开，避免卡死；
* `ci=-1/32` 不修改按钮。

---

# 8. 当前 aardio 集成方案

## 8.1 为什么不用纯 `createEmbed`

纯 `createEmbed` 可以调用 ActiveX 方法，也可以通过 `com.Connect` 接收事件；测试中 `LoginDeviceEx`、`ConnectRealVideo`、`StateChanged`、`ReturnWindInfo` 都可用。

但纯 `createEmbed` 无法可靠在 ActiveX 创建瞬间传入 `<param name="lVideoWindNum" value="4">`，导致默认 4 窗格初始化不稳定。因此最终采用：

```text
aardio win.form
    └── web.form
          └── 极简 HTML
                └── ActiveX <object><param ...>
```

这种结构。

---

## 8.2 为什么用 `wb.doScript`

测试中 `wb.document.script.xxx(...)` 在当前环境中无法可靠调用页面函数，返回 `<null>`；而早期测试版和最终版本使用 `wb.doScript("loginFromExternal();")` 正常工作。因此当前封装统一使用 `doScript`。最终代码中 `callJs` 就是把函数名转换成 JS 字符串，再调用 `wb.doScript(script)`。

---

## 8.3 JS 与 aardio 的桥接方式

JS 调 aardio：

```js
window.external.LoginResult(r);
window.external.StateChanged(ci, ps, wid);
window.external.ReturnWindInfo(wid, cid, ps, sit);
```

aardio 调 JS：

```aardio
callJs("loginFromExternal");
callJs("openAll");
callJs("openChannel", chId);
```

ActiveX 事件到 aardio 的桥接：

```html
<script language="javascript" for="ocx" event="StateChanged(ci,ps,wid)">
    try {
        window.external.StateChanged(ci,ps,wid);
    } catch(e) {}
</script>
```

当前最终代码也采用了这种方式。

---

# 9. 推荐工作流程

## 9.1 程序启动

1. 读取 `monitor.ini`：

   * `[device]`
   * `ip`
   * `username`
   * `password`
2. 创建主窗口并居中。
3. 创建 `web.form`。
4. 写入极简 HTML。
5. ActiveX 根据 `<param>` 初始化 4 窗格。
6. 延迟 2 秒后执行 `ping()` 测试 JS 可调用。
7. 如果配置完整，则自动登录。
8. 登录成功后自动调用 `ConnectAllChannle()`。

## 9.2 登录成功后

1. `LoginDeviceEx(...)` 返回 `true`。
2. JS 调用 `window.external.LoginResult(true)`。
3. aardio 设置 `isLoggedIn=1`。
4. 如果 `pendingAutoOpenAll=1`，延迟调用 `openAllChannels()`。
5. ActiveX 触发多个 `StateChanged(ci, ps=1, wid)`。
6. aardio 根据 `StateChanged` 更新 8 个通道按钮。

## 9.3 打开单通道

1. 用户点击“打开 03”。
2. aardio 调用：

```aardio
callJs("openChannel", 2);
```

3. JS 调用：

```js
ocx.ConnectRealVideo(2, 1);
```

4. ActiveX 触发 `StateChanged(2, 1, wid)`。
5. aardio 将按钮改为“关闭 03”。

## 9.4 同窗口切换通道

测试确认同窗口打开新通道时，ActiveX 内部会自动关闭旧通道：

```text
StateChanged(旧通道, 0, null)
StateChanged(新通道, 1, null)
```

因此当前程序不需要自己查找旧通道，只需要根据 `StateChanged` 更新按钮即可。

## 9.5 打开录像查询

1. 用户点击“录像”。
2. aardio 调用：

```aardio
callJs("showPlayback");
```

3. JS 调用：

```js
ocx.ShowPlayback();
```

4. 后续回放状态由 ActiveX 内部处理。
5. `ReturnWindInfo(ps=4/5)` 只用于窗口状态记录，不直接改通道按钮。
6. `StateChanged(ps=3)` 作为非普通实时状态处理，按钮恢复为“打开 xx”。

## 9.6 退出

1. 用户点击“断开”或关闭程序。
2. 调用：

```js
ocx.DisConnectAllChannel();
ocx.LogoutDevice();
ocx.CloseLocalPlay();
```

3. aardio 清空按钮状态、窗口映射、登录状态。

---

# 10. 已知限制与注意事项

## 10.1 无公开“选择窗口”接口

类型信息中没有发现类似：

```text
SelectWindow(wid)
SetCurrentWindow(wid)
SetVideoWindow(wid, cid)
```

的接口。窗口选择由用户点击 ActiveX 内部窗口后，控件内部记录；`ReturnWindInfo(wid,cid,ps,sit)` 只回传当前窗口信息。

因此当前程序可以：

* 识别当前点击窗口；
* 维护窗口与通道映射；
* 监听通道开关状态；

但不能可靠通过公开接口自动指定“窗口 2 打开通道 5”。

## 10.2 `StateChanged` 中 `wid` 经常为空

测试日志中，`StateChanged` 的 `wid` 多次为 `<null>`。因此通道状态更新不能依赖 `wid`，应只依赖 `ci` 和 `ps`。

## 10.3 `DisConnectRealVideo` 可能返回 false

当通道已经被内部切换、回放占用或不再处于实时播放时，`DisConnectRealVideo(ch)` 可能返回 `false`。当前程序需要 fallback 重置按钮，避免 UI 卡死。

## 10.4 `SetDeviceMode` 目前不建议使用

自动测试中，`SetDeviceMode` 没有表现出可用的窗口布局或窗口选择能力，不建议依赖它。

## 10.5 密码存储

当前 `monitor.ini` 明文保存密码，适合家庭自用。如果用于多人环境，应考虑加密或至少混淆。

---

# 11. 推荐最小接口清单

如果只做当前这个“简洁监控客户端”，实际必须用到的接口是：

| 类别   | 方法 / 事件                                                                 |
| ---- | ----------------------------------------------------------------------- |
| 初始化  | `<object><param lVideoWindNum=4 ...>`                                   |
| 登录   | `LoginDeviceEx`                                                         |
| 登出   | `LogoutDevice`, `CloseLocalPlay`                                        |
| 预览   | `ConnectRealVideo`, `DisConnectRealVideo`                               |
| 全部通道 | `ConnectAllChannle`, `DisConnectAllChannel`                             |
| 云台   | `ControlPtz`                                                            |
| 菜单   | `ShowDeviceConfig`, `ShowPlayback`, `ShowAlarm`, `AboutBox`             |
| 状态事件 | `StateChanged`, `ReturnWindInfo`, `DeviceDisconnected`, `DeviceChanged` |

---

# 12. 后续可扩展功能

## 12.1 显示真实通道名称

可调用：

```js
ocx.GetChannelName()
```

然后按原网页方式解析 `char(9)` 和 `char(16)` 分隔符，替换按钮文本为真实通道名。

## 12.2 主码流 / 子码流切换

可调用：

```js
ocx.GetDevConfig(1)
```

判断是否支持子码流，再让 `openChannel(ch)` 使用 `ConnectRealVideo(ch, 1)` 或 `ConnectRealVideo(ch, 2)`。

## 12.3 回放控制条

可接入：

```js
ocx.PlayVideo(operationType)
ocx.SetPlayPos(posValue)
```

并监听：

```js
ReturnPlayState(pos)
```

实现暂停、停止、快进、进度条拖动等功能。

## 12.4 图像参数调整

可接入：

```js
ocx.GetColor()
ocx.SetColor(0, brightness, contrast, saturation, hue)
```

实现亮度、对比度、饱和度、色调调节。
