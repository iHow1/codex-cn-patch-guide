# GitHub 中文说明模板（可直接发）

## 1) 仓库简介（放 README 顶部）

本仓库记录了 Codex 桌面端非官方中文补丁的可复现路径。  
重点是：在进行界面文案替换后，同步修复 Electron 完整性校验，保证应用可正常启动。

## 2) Release/Discussion 首发文案

标题：  
`[非官方] Codex 桌面端中文补丁流程（5.3.x）`

正文：  
`这是一套面向中文用户的可复现补丁流程，核心包含：`  
`- 等长字符串替换`  
`- app.asar 完整性字段更新`  
`- Info.plist 的 ElectronAsarIntegrity 更新`  
`- 重签名与缓存清理`  
`当前已验证首页、设置页、MCP页中文显示。`  
`说明：仅技术研究用途，不分发官方二进制。`

## 3) Issue 模板（用户反馈）

请附带以下信息，便于排查：

1. Codex 版本号（如 `5.3.x`）
2. 安装路径（`/Applications` 或 `~/Applications`）
3. 是否出现钥匙串弹窗
4. 是否清理缓存后重启
5. 报错截图与日志（如 `ASAR Integrity Violation`）

## 4) 合规提示（建议固定放在仓库）

- Unofficial patch for research/education only.
- Do not redistribute official binaries.
- Trademarks and product names belong to their owners.
