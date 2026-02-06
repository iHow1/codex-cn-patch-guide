# GitHub 首发帖（可直接发到 README/Discussion）

Title:
`Unofficial Chinese Patch Workflow for Codex Desktop (5.3.x)`

Body:

This repository documents a reproducible workflow to localize Codex desktop UI into Chinese while keeping Electron integrity checks valid.

What is included:

- Byte-length-safe UI string replacement strategy
- `app.asar` internal integrity update
- `Info.plist` `ElectronAsarIntegrity` update
- Re-signing and cache-clearing workflow
- Troubleshooting for multi-app copies, keychain prompts, and stale cache

Important:

- Unofficial patch, for research/learning only
- No redistribution of official binaries
- App updates may overwrite patch

If this helps, feel free to open issues/PRs with version-specific offsets and verified mappings.
