# Codex 桌面端中文补丁指南（非官方）

这是一个面向中文用户的 Codex 桌面端汉化补丁仓库。  
目标是提供一条**可复现**、**可排错**、**可回滚**的工程化路径。

## 这个仓库是做什么的

- 把 Codex 桌面端核心界面文案替换成中文
- 保证替换后应用仍可启动（通过完整性修复）
- 提供完整操作文档和常见问题排查

## 核心能力

- 等长字符串替换（避免 asar 偏移问题）
- 更新 `app.asar` 内部完整性字段
- 更新 `Info.plist` 的 `ElectronAsarIntegrity`
- 重签名与缓存清理流程

## 文档入口

- 主流程文档：[`CODEX_CN_PATCH_GUIDE.md`](./CODEX_CN_PATCH_GUIDE.md)
- 中文说明页：[`README.zh-CN.md`](./README.zh-CN.md)
- 发布文案与模板：[`publish-kit`](./publish-kit)
- 一键补丁脚本：[`scripts/apply_codex_cn_patch.sh`](./scripts/apply_codex_cn_patch.sh)
- 补丁映射表：[`patches/codex_5_3_cn_patch.json`](./patches/codex_5_3_cn_patch.json)

## 适用范围

- 目标版本：`Codex 5.3.x`（实测）
- 系统环境：macOS

## 重要声明

- 本项目为**非官方补丁**，仅用于技术研究和学习交流。
- 请勿分发官方应用二进制文件。
- 官方更新可能覆盖补丁，需要重新适配。
- 相关商标与产品名称归其所有者所有。

## 给第一次用 GitHub 的用户

先看这个文件：

- [`publish-kit/GITHUB_BEGINNER_STEPS.md`](./publish-kit/GITHUB_BEGINNER_STEPS.md)

## 快速使用（脚本版）

先准备一个可写的 Codex 副本（推荐）：

```bash
mkdir -p ~/Applications
rsync -a /Applications/Codex.app/ ~/Applications/Codex.app/
```

直接执行补丁：

```bash
./scripts/apply_codex_cn_patch.sh ~/Applications/Codex.app
```

只做匹配检测（不写入）：

```bash
python3 ./scripts/apply_codex_cn_patch.py --app ~/Applications/Codex.app --dry-run
```
