# 小红书发布文案（可直接复制）

## 版本A（短）

标题：
`Codex 5.3 让我自己给自己打了中文补丁（可复现）`

正文：
`这次做了一个 Codex 桌面端非官方中文补丁，核心不是“翻译”，而是 Electron 完整性修复：`  
`等长文案替换 + asar 完整性更新 + Info.plist 的 ElectronAsarIntegrity 同步 + 重签名。`  
`现在首页、设置、MCP 页面都能中文显示。`  
`我把可复现流程整理成文档了，有需要我可以放 GitHub。`  
`（仅技术研究，不分发官方二进制）`

标签：
`#Codex #AI编程 #Electron #汉化补丁 #开发者日常 #工程实践`

---

## 版本B（中）

标题：
`首批实测：Codex 5.3 自举汉化补丁跑通了`

正文：
`记录一个有意思的实验：让 Codex“自己给自己”打中文补丁。`  
`最难的不是翻译，而是完整性校验：只改字符串会直接启动失败。`  
`我最后跑通的路径是：`  
`1) 只改用户目录副本`  
`2) 文案等长替换（不足补空格）`  
`3) 更新 app.asar 内部 integrity`  
`4) 更新 Info.plist 的 ElectronAsarIntegrity`  
`5) 重新 codesign + 清缓存重启`  
`效果：主页、设置、MCP 页都可用中文。`  
`有需要我把完整流程和排错清单发 GitHub。`  
`（非官方补丁，仅研究用途）`

标签：
`#Codex #GPT5 #AI工程 #逆向工程 #Electron开发 #产品本地化`

---

## 版本C（长）

标题：
`我给 Codex 5.3 做了非官方中文补丁：从崩溃到可复现`

正文：
`这几天做了个硬核小实验：把 Codex 桌面端界面中文化，并且保证应用还能正常启动。`  
`一开始我以为改文案就行，结果直接报 ASAR Integrity Violation。`  
`后面确认 Electron 会校验 asar header 完整性，所以必须一起修：`  
`- 字符串等长度替换（中文字节数问题是关键）`  
`- 回写目标文件 integrity.hash / blocks`  
`- 更新 Info.plist 里的 ElectronAsarIntegrity`  
`- 重签名（codesign --deep）`  
`- 清 Code Cache/Cache/GPUCache 后重启`  
`最终可见效果：首页 + 设置页 + MCP页都中文可用。`  
`我已经把完整流程整理成文档，后面会放 GitHub 供大家复现。`  
`声明：仅技术研究，不分发官方安装包，也不替代官方多语言方案。`

标签：
`#Codex #AI编程助手 #Electron #软件本地化 #开发实战 #工程复盘`
