# 补丁脚本说明

## 文件

- `apply_codex_cn_patch.sh`：一键执行入口
- `apply_codex_cn_patch.py`：主脚本（可加参数）

## 最快用法

```bash
./scripts/apply_codex_cn_patch.sh ~/Applications/Codex.app
```

## 常用参数

```bash
# 只检测匹配，不写入
python3 ./scripts/apply_codex_cn_patch.py --app ~/Applications/Codex.app --dry-run

# 跳过重签名（调试用）
python3 ./scripts/apply_codex_cn_patch.py --app ~/Applications/Codex.app --no-codesign

# 跳过清缓存
python3 ./scripts/apply_codex_cn_patch.py --app ~/Applications/Codex.app --no-clear-cache
```

## 注意

- 建议只对 `~/Applications/Codex.app` 副本执行。
- 首次运行可能弹钥匙串授权，建议选择“始终允许”。
- 官方更新后可能需要重新打补丁。
