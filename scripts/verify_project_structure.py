#!/usr/bin/env python3
"""
Verify repo layout (file counts + tree sample + presence of key paths).
Expects Next.js sources under frontend/src/.
Exit code 1 if any checked key file is missing.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = frozenset({
    "node_modules",
    "__pycache__",
    ".next",
    ".git",
    "venv",
    ".venv",
    "dist",
    "build",
    ".turbo",
})


def count_files(directory: Path) -> tuple[int, int, list[str]]:
    total_files = 0
    total_dirs = 0
    file_list: list[str] = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        root_path = Path(root)
        total_dirs += len(dirs)
        total_files += len(files)
        for file in files:
            rel_path = os.path.relpath(root_path / file, directory)
            file_list.append(rel_path)
    return total_files, total_dirs, file_list


def print_tree_sample(base_path: Path) -> None:
    print("📂 Directory Tree (top-level + samples):")
    print("─" * 60)
    for item in sorted(os.listdir(base_path)):
        item_path = base_path / item
        if item_path.is_dir() and not item.startswith("."):
            print(f"├── {item}/")
            try:
                subitems = sorted(os.listdir(item_path))
                shown = 0
                for subitem in subitems:
                    if shown >= 10:
                        break
                    subpath = item_path / subitem
                    if subitem.startswith(".") or subitem in SKIP_DIRS:
                        continue
                    if subpath.is_dir():
                        print(f"│   ├── {subitem}/")
                        try:
                            subsubitems = sorted(os.listdir(subpath))
                            n = 0
                            for s in subsubitems:
                                if n >= 5:
                                    break
                                if s.startswith(".") or s in SKIP_DIRS:
                                    continue
                                sp = subpath / s
                                if sp.is_file():
                                    print(f"│   │   ├── {s}")
                                    n += 1
                        except OSError:
                            pass
                    elif subpath.is_file():
                        print(f"│   ├── {subitem}")
                    shown += 1

                visible = [
                    x for x in subitems
                    if not x.startswith(".") and x not in SKIP_DIRS
                ]
                if len(visible) > 10:
                    print(f"│   └── ... ({len(visible) - 10} more items)")
            except OSError:
                pass
    print()


def main() -> int:
    base_path = Path(os.environ.get("SRTAPP_ROOT", REPO_ROOT)).resolve()

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           SRTAPP - PROJECT STRUCTURE SUMMARY                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print(f"📂 Root: {base_path}")

    total_files, total_dirs, _ = count_files(base_path)
    print()
    print(f"📁 Total Directories (walked): {total_dirs}")
    print(f"📄 Total Files (walked): {total_files}")
    print()

    print_tree_sample(base_path)
    print("─" * 60)

    # Next.js: all app/lib/store/components paths use frontend/src/ and repo file names.
    key_files = [
        "backend/config/settings/base.py",
        "backend/apps/accounts/models.py",
        "backend/apps/accounts/views.py",
        "backend/apps/core/models.py",
        "backend/apps/core/views.py",
        "backend/apps/students/models.py",
        "backend/apps/teachers/models.py",
        "backend/config/urls.py",
        "backend/manage.py",
        "frontend/src/middleware.ts",
        "frontend/src/lib/api/client.ts",
        "frontend/src/store/auth-store.ts",
        "frontend/src/app/login/page.tsx",
        "frontend/src/app/dashboard/layout.tsx",
        "frontend/src/components/layout/sidebar.tsx",
        "frontend/src/components/layout/topbar.tsx",
        "frontend/src/app/globals.css",
        "frontend/tailwind.config.js",
        "mobile/app/_layout.tsx",
        "mobile/app/(auth)/login.tsx",
        "mobile/app/(student)/dashboard.tsx",
        "mobile/store/auth-store.ts",
        "mobile/lib/api.ts",
        "mobile/constants/Colors.ts",
        "docker-compose.yml",
        "backend/Dockerfile",
        "frontend/Dockerfile",
        "nginx/nginx.conf",
        "README.md",
    ]

    print("\n🔑 Key files (Next.js under frontend/src/):")
    missing: list[str] = []
    for rel in key_files:
        full = base_path / rel
        if full.is_file():
            size = full.stat().st_size
            print(f"  ✅ {rel} ({size:,} bytes)")
        else:
            print(f"  ❌ {rel} (MISSING)")
            missing.append(rel)

    print()
    print("─" * 60)
    if missing:
        print(f"⚠️  Missing {len(missing)} path(s); fix layout or checklist.")
        print("─" * 60)
        return 1

    print("✅ All checked key files present.")
    print("✅ SRTAPP v2.0 - structure check passed!")
    print("─" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
