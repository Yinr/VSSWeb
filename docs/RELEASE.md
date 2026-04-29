# Release Guide

发布时必须严格按本文检查，不要跳过版本、tag、更新包校验。

## 发布原则

- Git tag 使用 `vX.Y.Z` 或 `vX.Y` 格式，例如 `v0.1.1`、`v0.2`。
- `default.aproj` 中的 `FileVersion` 与 `ProductVersion` 必须保持一致。
- `.update-files/` 是实际更新发布包目录，GitHub Release 附件也基于该目录内容。
- `dist/` 构建产物只用于本地运行验证，不参与更新发布。
- `.update-files/version.txt` 主要由升级包工具生成，默认以校验为主。
- 如需调整 `description`，只能写一条面向最终用户的简短更新说明；不要在其中写发布步骤、技术细节或内部备注。
- 版本一致性按语义比较，不要求字符串完全一致。例如 `0.1` 与 `0.1.0.0` 语义一致。
- 构建和更新包生成需要人工在 aardio 中执行，当前没有自动化构建流程。
- 发布提交默认只包含版本号变更、`CHANGELOG.md` 更新、必要的发布文档更新，以及 `.update-files/` 更新包内容。
- 如遇极特殊情况，确实需要纳入其他文件改动时，必须先明确说明原因、影响范围和纳入发布提交的必要性，再例外处理。
- 如果使用发布分支准备发布，该分支中最终要合并进主线的改动整体也必须满足上面的发布提交范围；不能把额外的功能提交、文档提交或其他无关改动通过 `squash merge` 混入发布提交。
- 发布 tag 必须打在 `main` 上对应的发布提交，而不是打在仅存在于临时发布分支的提交上。

## 发布前检查

1. 检查工作区：
   - 运行 `git status`。
   - 运行 `git diff` 查看未提交改动。
   - 不要提交 `config.ini`、`log.txt`、本机临时文件、设备私密信息。

2. 检查上一个 tag：
   - 获取最近 tag，例如 `git describe --tags --abbrev=0`。
   - 检查当前分支相对上一个 tag 是否有有效变更，例如 `git diff <last-tag>...HEAD`。
   - 如果没有有效代码、文档或发布内容变化，应提醒用户并拒绝继续发布。
   - 如果只有版本号或构建产物变化，也应提醒用户确认是否真的需要发布。

3. 确认目标版本：
   - 目标 tag 与 Windows 版本号必须能对应。
   - 示例：`v0.1` 对应 `0.1.0.0`，`v0.1.1` 对应 `0.1.1.0`。

## 更新版本号

1. 检查 `default.aproj` 当前版本：
   - 通常由开发者人工修改版本号。
   - 如果当前版本与上一发布版本一致，停止并提示开发者手动修改。
   - 如果开发者明确要求代为修改版本号，按其指定版本修改。
   - 如果开发者只要求自动递增版本，默认将 `Z + 1`，并将 `N` 重置为 `0`，即 `X.Y.Z.N` -> `X.Y.(Z+1).0`。

2. 修改 `default.aproj` 时只修改：
   - `FileVersion="X.Y.Z.N"`
   - `ProductVersion="X.Y.Z.N"`

3. 校验：
   - `FileVersion` 与 `ProductVersion` 必须语义一致，建议字符也保持一致。
   - 不要修改 `<project ver="10">`，这是 aardio 工程格式版本，不是应用版本。

4. 检查版本是否确实较上一个 tag 有发布意义：
   - 版本号必须大于上一发布版本。
   - 当前变更必须能支撑一次新发布。
   - 不满足时停止，并向用户说明原因。

5. 如果修改了版本号：
   - 必须要求开发者人工执行一次 aardio 构建。
   - 必须生成新的 `.update-files/` 更新包。
   - 未重新构建前，不能继续提交、打 tag 或创建 Release。

## 更新文档

1. 更新 `CHANGELOG.md`：
   - 新增目标版本小节。
   - 内容优先写用户能感知到的变化。
   - 开发实现细节放入 `Technical` 小节。
   - 常用分类：`Added`、`Changed`、`Fixed`、`Removed`、`Security`、`Technical`。
   - `Notes` 不是默认分类；只有确实需要补充面向最终用户的版本说明时才使用，不要写发布前检查、构建步骤或其他仅对发布人员有意义的内容。

2. 更新 `.update-files/version.txt` 中的 `description`：
   - 使用一句话高度浓缩地概括本次更新。
   - 面向最终用户，优先写可感知收益，不展开实现过程。
   - 保持简短，避免堆砌并列功能点，避免写发布说明、技术术语和内部备注。

3. 检查 `README.md`：
   - 只有运行方式、功能范围、构建方式或运行前提变化时才更新。
   - 保持简洁，不展开 ActiveX 接口细节。

## 构建与更新包校验

1. 构建项目由开发者人工执行：
   - 使用 aardio 工程 `default.aproj` 构建。
   - 本地 exe 输出到 `dist/`，仅用于运行验证。
   - 更新发布包输出到 `.update-files/`，该目录才是发布校验重点。
   - 更新版本号后必须人工执行一次构建，并生成新的更新包。
   - 未确认构建完成前，不能继续发布提交、创建 tag 或 GitHub Release。

2. 校验 `.update-files/version.txt`：
   - 确认文件存在。
   - 读取其中的 `version` 字段。
   - 检查 `description` 是否仍然符合“面向最终用户的一句话更新说明”的要求。
   - 将该版本与 `default.aproj` 的 `FileVersion`、`ProductVersion` 做语义比较。
   - 例如 `.update-files/version.txt` 为 `0.1`，`default.aproj` 为 `0.1.0.0`，视为一致。
   - 如果语义不一致，停止发布并要求重新构建更新包。

3. 校验 `.update-files/` 内容：
   - 必须包含 `version.txt`。
   - 必须包含 `checksum.lzma`。
   - 必须包含 `files/`。
   - `version.txt` 中的 `main` 和 `updater` 应指向当前主程序，例如 `VSSWeb.exe`。

4. 校验构建后的程序版本：
   - 运行发布构建产物时，标题栏应显示当前产品版本。
   - 源码调试时可能显示 aardio 宿主版本，不作为发布判断依据。

## 提交与标签

1. 发布前最终检查：
   - 再次运行 `git status`。
   - 再次查看 `git diff`。
   - 确认 `CHANGELOG.md`、`default.aproj`、必要文档和 `.update-files/` 状态符合预期。
   - 发布提交应只包含版本号变更、`CHANGELOG.md` 更新、必要的发布文档更新，以及 `.update-files/` 更新包内容。
   - 如果还有功能代码、修复代码、README 大改或其他非发布内容，必须先拆分为独立提交，再进行发布提交。

2. 提交：
   - 提交信息建议使用 `release vX.Y.Z` 或 `prepare vX.Y.Z release`。
   - 不要提交敏感配置或本机日志。

3. 合并到主线：
   - 如果发布前另开了发布分支，先确认该分支中准备合并到主线的全部改动都满足发布提交范围。
   - 如果分支里还混有其他不属于发布提交范围的改动，必须先拆分或另行合并，不能直接用 `squash merge` 生成发布提交。
   - 当发布分支相对 `main` 只多出一条合规的发布提交时，优先使用 `fast-forward` 或等价方式让该发布提交原样进入 `main`。
   - 发布完成后再删除临时发布分支，保持主线历史清晰。

4. 创建 tag：
   - tag 名称必须与 `CHANGELOG.md` 当前版本一致。
   - 示例：`git tag v0.1.1`。
   - tag 必须创建在 `main` 上对应的发布提交。
   - 只有构建和 `.update-files` 校验通过后才能创建 tag。

## GitHub Release

1. GitHub Release 由 `.github/workflows/release.yml` 自动创建：
   - 推送 `v*` tag 后触发。
   - Release 标题使用 tag 名称，例如 `v0.1.1`。
   - Release 正文由 `scripts/release/extract_changelog.py` 从 `CHANGELOG.md` 对应版本小节提取。
   - 发布前由 `scripts/release/check_update_version.py` 校验 `.update-files/version.txt` 与 tag 版本语义一致。

2. Release 附件由 workflow 准备：
   - 从 `.update-files/files/VSSWeb.exe.lzma` 解压出 exe。
   - exe 附件命名为 `VSSWeb-vX.Y.Z.exe`。
   - 同时上传 `.update-files/version.txt`，保持原文件名 `version.txt`。
   - 不使用 `dist/` 作为 GitHub Release 附件来源。

3. 推送 tag 前必须确认：
   - `CHANGELOG.md` 中存在对应 `## [vX.Y.Z]` 小节。
   - `.update-files/version.txt` 与 tag 版本语义一致。
   - `.update-files/files/VSSWeb.exe.lzma` 是当前版本构建生成的更新包内容。

4. 发布后确认 tag、Release、`CHANGELOG.md`、`.update-files/version.txt`、`default.aproj` 版本语义一致。

## 必须停止的情况

- 当前版本相对上一个 tag 没有有效变更。
- 目标版本不大于上一发布版本。
- `FileVersion` 与 `ProductVersion` 不一致。
- `.update-files/version.txt` 的版本与 `FileVersion` / `ProductVersion` 语义不一致。
- `.update-files/` 缺少 `version.txt`、`checksum.lzma` 或 `files/`。
- `.update-files/files/VSSWeb.exe.lzma` 缺失，导致 GitHub Release 无法生成 exe 附件。
- `CHANGELOG.md` 缺少与 tag 对应的版本小节，导致 GitHub Release 无法生成正文。
- 版本号被修改后，开发者尚未人工重新构建并生成新的 `.update-files/` 更新包。
- 发布提交中混入功能代码、修复代码或其他非发布内容，且尚未拆分为独立提交。
- 发布提交中只包含版本号或构建产物变化，但相对上一 tag 没有可说明的实际变更。
- 工作区包含明显敏感配置、日志或本机临时文件且用户未明确要求提交。
