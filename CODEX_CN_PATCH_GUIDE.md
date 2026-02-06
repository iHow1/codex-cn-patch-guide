# Codex 桌面端中文硬替换补丁指南（可复用）

> 适用目标：给 `Codex.app` 做本地中文化（非官方多语言开关），并保证应用可启动。

## 1. 结论先说

这条路径是可行的：

1. 只改 **用户目录副本**（`~/Applications/Codex.app`），不要直接改系统安装版。
2. 对 `app.asar` 做 **等字节长度** 文案替换（中文不足用空格补齐）。
3. 同步更新 `asar` 内部完整性（文件 hash + blocks）。
4. 同步更新 `Info.plist` 里的 `ElectronAsarIntegrity` 哈希（哈希对象是 `asar header`）。
5. 重新 `codesign --deep`。
6. 清缓存并从指定路径启动。

否则会出现：启动崩溃、`ASAR Integrity Violation`、界面不生效、总是看到旧英文。

---

## 2. 必要前提

- macOS
- 已安装 Codex
- 有权限写 `~/Applications`
- 终端可用 `python3`、`codesign`

---

## 2.1 一键脚本（推荐）

仓库已提供可直接执行的补丁脚本：

- `scripts/apply_codex_cn_patch.sh`
- `scripts/apply_codex_cn_patch.py`
- `patches/codex_5_3_cn_patch.json`

执行方式：

```bash
./scripts/apply_codex_cn_patch.sh ~/Applications/Codex.app
```

只检测不写入：

```bash
python3 ./scripts/apply_codex_cn_patch.py --app ~/Applications/Codex.app --dry-run
```

---

## 3. 工作目录约定

- 补丁目标（推荐）：`/Users/<你用户名>/Applications/Codex.app`
- 官方安装（只读参考）：`/Applications/Codex.app`

先复制一份官方应用到用户目录：

```bash
mkdir -p ~/Applications
rsync -a /Applications/Codex.app/ ~/Applications/Codex.app/
```

---

## 4. 为什么以前“改了但没生效”

常见原因：

1. 实际运行的是另一个 `Codex.app`（系统版和用户版混用）。
2. `app.asar` 改了，但没更新 Electron 完整性哈希。
3. 改了字符串长度，导致 asar 结构偏移或校验失败。
4. 缓存没清（Code Cache / Cache / GPUCache）。
5. 钥匙串弹窗未处理，页面操作被拦截。

---

## 5. 安全替换原则（最重要）

### 5.1 只做“等长度替换”

- 原文：`"Open"`（4 字节）
- 替换：`"开 "`（中文 3 字节 + 空格 1 字节）

规则：

- 新字符串字节数 **<=** 原字符串字节数
- 不足部分用空格补齐
- 不要改变 JS 文件总长度

### 5.2 不要整包重打 `asar`

除非你非常确定工具输出兼容。推荐只做“原地字节替换 + header 校验更新”。

---

## 6. 一次性补丁脚本模板

下面脚本是通用模板：

- 读取 `app.asar` header
- 定位目标 js 文件
- 做等长替换
- 更新该文件 `integrity.hash` 与 `integrity.blocks`
- 回写 header
- 更新 `Info.plist` 中 `ElectronAsarIntegrity`
- 重签名

> 注意：`replacements` 里仅填“你确认存在”的文本对。

```python
# -*- coding: utf-8 -*-
import json, struct, hashlib, plistlib, subprocess
from pathlib import Path

APP = Path('/Users/<你用户名>/Applications/Codex.app')
ASAR = APP / 'Contents/Resources/app.asar'
PLIST = APP / 'Contents/Info.plist'
TARGET = 'webview/assets/index-xxxx.js'  # 先定位真实文件名

# old -> new（new 必须 <= old 字节长度）
replacements = [
    ('defaultMessage:"New thread"', 'defaultMessage:"新对话 "'),
    ('defaultMessage:"Open"', 'defaultMessage:"开 "'),
]

pairs = []
for old, new in replacements:
    ob = old.encode('utf-8')
    nb = new.encode('utf-8')
    if len(nb) > len(ob):
        raise ValueError(f'new too long: {old} -> {new}')
    nb = nb + b' ' * (len(ob) - len(nb))
    pairs.append((ob, nb, old))

with ASAR.open('r+b') as f:
    head = f.read(16)
    hlen = struct.unpack('<I', head[12:16])[0]
    hbytes = f.read(hlen)
    header = json.loads(hbytes.decode('utf-8'))
    base = 16 + hlen

    node = header
    for p in TARGET.split('/'):
        node = node['files'][p]

    off = base + int(node['offset'])
    size = int(node['size'])

    f.seek(off)
    data = f.read(size)
    old_data = data

    for ob, nb, label in pairs:
        count = data.count(ob)
        print(label, count)
        if count:
            data = data.replace(ob, nb)

    if data != old_data:
        f.seek(off)
        f.write(data)

    # 更新目标文件完整性
    block_size = 4 * 1024 * 1024
    node['integrity'] = {
        'algorithm': 'SHA256',
        'hash': hashlib.sha256(data).hexdigest(),
        'blockSize': block_size,
        'blocks': [
            hashlib.sha256(data[i:i+block_size]).hexdigest()
            for i in range(0, len(data), block_size)
        ],
    }

    new_hbytes = json.dumps(header, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    if len(new_hbytes) != hlen:
        raise RuntimeError(f'header size changed: {hlen} -> {len(new_hbytes)}')

    f.seek(16)
    f.write(new_hbytes)

# 更新 Info.plist 的 ElectronAsarIntegrity
with ASAR.open('rb') as f:
    f.read(12)
    hlen = struct.unpack('<I', f.read(4))[0]
    hbytes = f.read(hlen)
header_sha = hashlib.sha256(hbytes).hexdigest()

with PLIST.open('rb') as pf:
    pl = plistlib.load(pf)
pl['ElectronAsarIntegrity']['Resources/app.asar']['hash'] = header_sha
with PLIST.open('wb') as pf:
    plistlib.dump(pl, pf)

# 重签名
subprocess.run(['codesign', '--force', '--deep', '--sign', '-', str(APP)], check=True)
print('done')
```

---

## 7. 如何找“真实目标文件”

先在 asar 里搜文案关键词，确定是哪个 `webview/assets/*.js`：

```bash
rg -a -n "Let’s build|New thread|settings.nav.general-settings" ~/Applications/Codex.app/Contents/Resources/app.asar
```

再按 asar header 解析对应路径内容（可写个小脚本）确认该字符串确实在该文件中。

---

## 8. 清缓存与启动验证

每次补丁后都做：

```bash
pkill -f '/Users/<你用户名>/Applications/Codex.app/Contents/MacOS/Codex' || true
rm -rf "$HOME/Library/Application Support/Codex/Code Cache" \
       "$HOME/Library/Application Support/Codex/Cache" \
       "$HOME/Library/Application Support/Codex/GPUCache"
open -a /Users/<你用户名>/Applications/Codex.app
```

并确认运行进程路径：

```bash
ps -ax -o pid=,command= | rg 'Codex.app/Contents/MacOS/Codex'
```

必须看到你希望的路径（用户版或系统版）。

---

## 9. 钥匙串弹窗处理

首次读取 `Codex Safe Storage` 会弹钥匙串授权。

- 选 `始终允许`
- 如果不处理，该弹窗会挡住设置页和操作，造成“看起来没生效”

---

## 10. 推荐排错顺序

1. 看当前运行的是哪个 app 路径。
2. 查 `app.asar` 里目标字符串是否已是中文。
3. 若是中文但界面仍英文：清缓存后重启。
4. 若启动崩溃：检查 `ElectronAsarIntegrity` 与 `codesign`。
5. 若仍有英文：继续按页面截图做增量替换（分批次）。

---

## 11. 风险说明

- 每次官方更新可能覆盖补丁，需要重做。
- 非官方方式，存在兼容性风险。
- 建议保留一份未修改的 `Codex.app` 备份。
