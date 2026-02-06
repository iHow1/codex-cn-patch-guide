# Codex Desktop Chinese Patch Guide (Unofficial)

Unofficial Chinese localization patch workflow for Codex desktop app.

This repo documents a reproducible path to patch UI strings while keeping Electron integrity checks valid.

## Highlights

- Works on Codex desktop (tested on `5.3.x` family)
- Uses byte-length-safe string replacement
- Fixes `app.asar` file integrity fields and `ElectronAsarIntegrity`
- Re-signs app so it can launch
- Includes troubleshooting for cache / multiple app copies / keychain prompts

## File

- [`CODEX_CN_PATCH_GUIDE.md`](./CODEX_CN_PATCH_GUIDE.md)

## Important Disclaimer

- This is an **unofficial** patch for research/learning.
- Do **not** redistribute official app binaries.
- App updates may overwrite the patch.
- All trademarks and product names belong to their owners.

## Suggested Repo Structure

- `CODEX_CN_PATCH_GUIDE.md`
- `screenshots/`
- `scripts/` (optional patch scripts)
- `publish-kit/` (social + release copy)

## License Suggestion

Use MIT for docs/scripts only (not official binaries).
