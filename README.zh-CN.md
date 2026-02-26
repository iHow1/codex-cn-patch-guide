# Codex 桌面端中文补丁说明（非官方）

> 面向中文用户的 GitHub 入口说明。

这是一个针对 Codex 桌面端的**非官方**中文化补丁流程文档仓库，核心目标是：

1. 在本地将主要 UI 文案替换为中文。
2. 修复 Electron 完整性校验，保证应用可启动。
3. 提供可复现、可排错、可回滚的工程化路径。

## 适用范围

- 目标版本：`Codex 5.3.x`（实测路径）
- 运行环境：macOS
- 形式：本地补丁（不依赖官方语言开关）

## 你会得到什么

- 等长文案替换方法（避免 asar 偏移问题）
- `app.asar` 完整性字段更新方法
- `Info.plist` 里 `ElectronAsarIntegrity` 更新方法
- 重签名与缓存清理流程
- 常见问题排查（双应用路径、缓存、钥匙串弹窗）

## 文档入口

- 核心流程：[`CODEX_CN_PATCH_GUIDE.md`](./CODEX_CN_PATCH_GUIDE.md)
- 发布文案：[`publish-kit`](./publish-kit)
- 一键补丁脚本：[`scripts/apply_codex_cn_patch.sh`](./scripts/apply_codex_cn_patch.sh)
- 补丁映射表：[`patches/codex_5_3_cn_patch.json`](./patches/codex_5_3_cn_patch.json)

## 快速开始（建议）

1. 先复制系统版应用到用户目录副本（如 `~/Applications/Codex.app`）。
2. 按 [`CODEX_CN_PATCH_GUIDE.md`](./CODEX_CN_PATCH_GUIDE.md) 执行补丁流程。
3. 每次补丁后做：完整性更新 + 重签名 + 清缓存 + 指定路径启动验证。

## 重要声明

- 本项目仅用于技术研究/学习交流。
- 请勿分发官方应用二进制文件。
- 官方更新可能覆盖补丁，需要重新适配。
- 相关商标与产品名称归其所有者所有。

## 给中文用户的建议

如果你第一次用 GitHub，建议先看：

- [`publish-kit/GITHUB_BEGINNER_STEPS.md`](./publish-kit/GITHUB_BEGINNER_STEPS.md)

里面有从“创建仓库”到“推送代码”的最短路径。

## 脚本快速使用

建议先复制系统版到用户目录副本：

```bash
mkdir -p ~/Applications
rsync -a /Applications/Codex.app/ ~/Applications/Codex.app/
```

执行补丁：

```bash
./scripts/apply_codex_cn_patch.sh ~/Applications/Codex.app
```

仅检测匹配（不写入）：

```bash
python3 ./scripts/apply_codex_cn_patch.py --app ~/Applications/Codex.app --dry-run
```
