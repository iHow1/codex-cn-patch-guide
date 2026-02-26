#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Codex desktop Chinese patch applier (unofficial).

What it does:
1) Applies byte-length-safe string replacements in app.asar JS files.
2) Updates asar per-file integrity metadata.
3) Updates Info.plist ElectronAsarIntegrity hash.
4) Optionally re-signs the app and clears cache.
"""

from __future__ import annotations

import argparse
import json
import hashlib
import plistlib
import shutil
import struct
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Replacement:
    label: str
    old: bytes
    new: bytes


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def parse_args() -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Apply Codex Chinese patch to Codex.app")
    parser.add_argument(
        "--app",
        default=str(Path.home() / "Applications" / "Codex.app"),
        help="Target Codex.app path (default: ~/Applications/Codex.app)",
    )
    parser.add_argument(
        "--map",
        default=str(default_root / "patches" / "codex_5_3_cn_patch.json"),
        help="Patch mapping json path",
    )
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, no write")
    parser.add_argument("--no-backup", action="store_true", help="Skip asar/plist backup")
    parser.add_argument("--no-codesign", action="store_true", help="Skip codesign after patch")
    parser.add_argument("--no-clear-cache", action="store_true", help="Skip cache cleanup")
    parser.add_argument("--strict-length", action="store_true", help="Fail if any translation is too long")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def load_map(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"patch map not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def pad_text_bytes(new_text: str, old_text: str) -> Tuple[bytes, bool]:
    old_b = old_text.encode("utf-8")
    new_b = new_text.encode("utf-8")
    if len(new_b) > len(old_b):
        return b"", False
    return new_b + b" " * (len(old_b) - len(new_b)), True


def build_replacements(cfg: dict, strict_length: bool) -> Tuple[List[Replacement], List[str]]:
    replacements: List[Replacement] = []
    skipped: List[str] = []

    for item in cfg.get("intl_replacements", []):
        rid = item["id"]
        old_msg = item["from"]
        new_msg = item["to"]
        old_token = f'id:"{rid}",defaultMessage:"{old_msg}"'

        padded, ok = pad_text_bytes(new_msg, old_msg)
        if not ok:
            msg = f"intl too long: {rid} | from={old_msg!r} to={new_msg!r}"
            if strict_length:
                raise ValueError(msg)
            skipped.append(msg)
            continue

        # reconstruct message string from padded bytes
        new_msg_padded = padded.decode("utf-8")
        new_token = f'id:"{rid}",defaultMessage:"{new_msg_padded}"'
        replacements.append(
            Replacement(
                label=f"intl:{rid}",
                old=old_token.encode("utf-8"),
                new=new_token.encode("utf-8"),
            )
        )

    for item in cfg.get("literal_replacements", []):
        old_text = item["from"]
        new_text = item["to"]
        padded, ok = pad_text_bytes(new_text, old_text)
        if not ok:
            msg = f"literal too long: from={old_text!r} to={new_text!r}"
            if strict_length:
                raise ValueError(msg)
            skipped.append(msg)
            continue
        replacements.append(
            Replacement(
                label=f"literal:{old_text[:40]}",
                old=old_text.encode("utf-8"),
                new=padded,
            )
        )

    return replacements, skipped


def walk_files(tree: dict, prefix: str = ""):
    for name, value in tree.get("files", {}).items():
        path = (f"{prefix}/{name}").lstrip("/")
        if "files" in value:
            yield from walk_files(value, path)
        else:
            if "offset" in value and "size" in value:
                yield path, value


def load_asar_header(asar_path: Path) -> Tuple[dict, int, int]:
    """
    Parse Electron ASAR header.

    Header layout (little-endian u32):
      - [0:4]   pickle payload size marker (typically 4)
      - [4:8]   header blob size used for payload offset
      - [8:12]  header object size (legacy/internal)
      - [12:16] JSON header string length

    File payload offsets in the header are relative to:
      data_start = 8 + header_blob_size

    NOTE:
      Older patch scripts used `16 + header_json_len`. That is wrong for newer
      Codex builds and causes a 1-2 byte skew, which breaks ASAR integrity.
    """
    with asar_path.open("rb") as f:
        head = f.read(16)
        if len(head) != 16:
            raise RuntimeError("invalid asar header")
        _pickle_size, header_blob_size, _header_obj_size, header_len = struct.unpack("<IIII", head)
        header_bytes = f.read(header_len)

    header_obj = json.loads(header_bytes.decode("utf-8"))
    base_offset = 8 + header_blob_size
    return header_obj, header_len, base_offset


def backup_files(asar_path: Path, plist_path: Path):
    stamp = now_stamp()
    asar_backup = asar_path.with_suffix(asar_path.suffix + f".bak.{stamp}")
    plist_backup = plist_path.with_suffix(plist_path.suffix + f".bak.{stamp}")
    shutil.copy2(asar_path, asar_backup)
    shutil.copy2(plist_path, plist_backup)
    print(f"[backup] {asar_backup}")
    print(f"[backup] {plist_backup}")


def apply_patch(
    app_path: Path,
    cfg: dict,
    replacements: List[Replacement],
    dry_run: bool,
    verbose: bool,
) -> Tuple[int, int, List[str]]:
    asar = app_path / "Contents" / "Resources" / "app.asar"
    plist = app_path / "Contents" / "Info.plist"
    if not asar.exists():
        raise FileNotFoundError(f"missing asar: {asar}")
    if not plist.exists():
        raise FileNotFoundError(f"missing plist: {plist}")

    header, header_len, base = load_asar_header(asar)

    js_paths = []
    for path, node in walk_files(header):
        if path.endswith(".js"):
            js_paths.append((path, node))

    replace_hits: Dict[str, int] = {r.label: 0 for r in replacements}
    changed_paths: List[str] = []

    if dry_run:
        with asar.open("rb") as f:
            for path, node in js_paths:
                offset = base + int(node["offset"])
                size = int(node["size"])
                f.seek(offset)
                data = f.read(size)
                for rp in replacements:
                    c = data.count(rp.old)
                    if c:
                        replace_hits[rp.label] += c
                        if verbose:
                            print(f"[hit] {path} | {rp.label} x{c}")
        total = sum(replace_hits.values())
        touched = len([k for k, v in replace_hits.items() if v > 0])
        print(f"[dry-run] total hits: {total}, matched rules: {touched}/{len(replacements)}")
        min_expected = int(cfg.get("min_total_replacements", 0))
        if min_expected and total < min_expected:
            raise RuntimeError(f"dry-run hits too low: {total} < min_total_replacements({min_expected})")
        return total, 0, []

    with asar.open("r+b") as f:
        # read existing header once
        f.read(16)
        _old_header_bytes = f.read(header_len)

        for path, node in js_paths:
            offset = base + int(node["offset"])
            size = int(node["size"])
            f.seek(offset)
            data = f.read(size)
            new_data = data

            local_changed = False
            for rp in replacements:
                c = new_data.count(rp.old)
                if c:
                    replace_hits[rp.label] += c
                    new_data = new_data.replace(rp.old, rp.new)
                    local_changed = True

            if not local_changed:
                continue

            if len(new_data) != len(data):
                raise RuntimeError(f"file size changed unexpectedly: {path}")

            f.seek(offset)
            f.write(new_data)
            changed_paths.append(path)

            # update file integrity block hashes
            bs = 4 * 1024 * 1024
            node["integrity"] = {
                "algorithm": "SHA256",
                "hash": hashlib.sha256(new_data).hexdigest(),
                "blockSize": bs,
                "blocks": [
                    hashlib.sha256(new_data[i : i + bs]).hexdigest()
                    for i in range(0, len(new_data), bs)
                ],
            }

        total = sum(replace_hits.values())
        if verbose:
            for k, v in sorted(replace_hits.items(), key=lambda kv: kv[1], reverse=True):
                if v:
                    print(f"[replace] {k}: {v}")

        # rewrite asar header in-place (must keep same length)
        new_header_bytes = json.dumps(header, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        if len(new_header_bytes) != header_len:
            raise RuntimeError(
                f"asar header length changed {header_len} -> {len(new_header_bytes)}; abort"
            )
        f.seek(16)
        f.write(new_header_bytes)

    # update plist ElectronAsarIntegrity hash (sha256(header_bytes))
    with asar.open("rb") as f:
        f.read(12)
        hlen = struct.unpack("<I", f.read(4))[0]
        header_bytes = f.read(hlen)
    header_sha = hashlib.sha256(header_bytes).hexdigest()

    with plist.open("rb") as pf:
        pl = plistlib.load(pf)

    integrity = pl.get("ElectronAsarIntegrity")
    if not isinstance(integrity, dict) or "Resources/app.asar" not in integrity:
        raise RuntimeError("ElectronAsarIntegrity key missing in Info.plist")

    pl["ElectronAsarIntegrity"]["Resources/app.asar"]["hash"] = header_sha
    with plist.open("wb") as pf:
        plistlib.dump(pl, pf)

    return total, len(changed_paths), changed_paths


def run_codesign(app_path: Path):
    cmd = ["codesign", "--force", "--deep", "--sign", "-", str(app_path)]
    subprocess.run(cmd, check=True)


def clear_cache():
    base = Path.home() / "Library" / "Application Support" / "Codex"
    for rel in ["Code Cache", "Cache", "GPUCache", "DawnGraphiteCache", "DawnWebGPUCache"]:
        p = base / rel
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)


def main() -> int:
    args = parse_args()
    app_path = Path(args.app).expanduser().resolve()
    map_path = Path(args.map).expanduser().resolve()

    cfg = load_map(map_path)
    strict_length = args.strict_length or bool(cfg.get("strict_length", False))

    print(f"[app] {app_path}")
    print(f"[map] {map_path}")
    print(f"[dry-run] {args.dry_run}")

    replacements, skipped = build_replacements(cfg, strict_length=strict_length)
    if skipped:
        print(f"[warn] skipped {len(skipped)} replacements due to length overflow")
        if args.verbose:
            for line in skipped:
                print(f"  - {line}")

    if not replacements:
        eprint("[error] no valid replacements to apply")
        return 2

    asar = app_path / "Contents" / "Resources" / "app.asar"
    plist = app_path / "Contents" / "Info.plist"

    if not args.dry_run and not args.no_backup:
        backup_files(asar, plist)

    total_hits, changed_file_count, changed_paths = apply_patch(
        app_path=app_path,
        cfg=cfg,
        replacements=replacements,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    print(f"[result] total replacements: {total_hits}")
    if args.dry_run:
        print("[result] dry-run complete")
        return 0

    print(f"[result] changed files: {changed_file_count}")
    if args.verbose and changed_paths:
        for p in changed_paths:
            print(f"  - {p}")

    min_expected = int(cfg.get("min_total_replacements", 0))
    if min_expected and total_hits < min_expected:
        eprint(
            f"[error] replacements too low ({total_hits} < {min_expected}); maybe unsupported app version"
        )
        return 3

    if not args.no_codesign:
        print("[codesign] signing app...")
        run_codesign(app_path)
        print("[codesign] done")

    if not args.no_clear_cache:
        clear_cache()
        print("[cache] cleared")

    print("[done] patch applied successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
