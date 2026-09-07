"""
Prepares the Darukaa.Earth project for sharing / submission.
1. Removes local build and interpreter caches (__pycache__, .pytest_cache, dist/, .pyc).
2. Verifies environment templates (.env.example).
3. Packages a pristine standalone zip archive (darukaa_earth_clean_share.zip)
   excluding large dependencies (node_modules, venv), git history, and secrets.
4. Leaves local dependencies intact so local servers and tests continue functioning.
"""
import os
import sys
import shutil
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    "venv",
    ".venv",
    "node_modules",
    ".git",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".idea",
    ".vscode",
    "htmlcov",
    ".coverage"
}

EXCLUDE_FILES = {
    ".DS_Store",
    "Thumbs.db",
    "darukaa_earth_clean_share.zip",
    "darukaa_earth_submission.zip",
    "audit_results.json"
}

def clean_caches(root: Path):
    print("--- 1. CLEANING CACHES AND TEMPORARY ARTIFACTS ---")
    deleted_dirs = 0
    deleted_files = 0

    # Clean __pycache__ and .pytest_cache
    for path in list(root.rglob("__pycache__")):
        if "venv" not in path.parts and "node_modules" not in path.parts:
            try:
                shutil.rmtree(path)
                deleted_dirs += 1
                print(f"  [REMOVED DIR] {path.relative_to(root)}")
            except Exception as e:
                print(f"  [WARN] Could not remove {path}: {e}")

    pytest_cache = root / ".pytest_cache"
    if pytest_cache.exists():
        try:
            shutil.rmtree(pytest_cache)
            deleted_dirs += 1
            print(f"  [REMOVED DIR] .pytest_cache")
        except Exception as e:
            print(f"  [WARN] Could not remove .pytest_cache: {e}")

    # Clean frontend/dist
    frontend_dist = root / "frontend" / "dist"
    if frontend_dist.exists():
        try:
            shutil.rmtree(frontend_dist)
            deleted_dirs += 1
            print(f"  [REMOVED DIR] frontend/dist")
        except Exception as e:
            print(f"  [WARN] Could not remove frontend/dist: {e}")

    # Clean *.pyc, *.pyo, .DS_Store, Thumbs.db
    for path in root.rglob("*"):
        if "venv" in path.parts or "node_modules" in path.parts:
            continue
        if path.is_file():
            if path.suffix in [".pyc", ".pyo"] or path.name in [".DS_Store", "Thumbs.db"]:
                try:
                    path.unlink()
                    deleted_files += 1
                    print(f"  [REMOVED FILE] {path.relative_to(root)}")
                except Exception as e:
                    print(f"  [WARN] Could not remove {path}: {e}")

    print(f"Cleanup complete: Removed {deleted_dirs} directories and {deleted_files} temporary files.\n")

def check_env_templates(root: Path):
    print("--- 2. VERIFYING ENVIRONMENT TEMPLATES ---")
    required_templates = [
        root / ".env.example",
        root / "backend" / ".env.example",
        root / "frontend" / ".env.example",
    ]
    all_ok = True
    for t in required_templates:
        if t.exists():
            print(f"  [OK] Found template: {t.relative_to(root)}")
        else:
            print(f"  [MISSING] {t.relative_to(root)}")
            all_ok = False
    print()
    return all_ok

def create_sharing_zip(root: Path, zip_filename: str = "darukaa_earth_submission.zip"):
    print(f"--- 3. CREATING CLEAN STANDALONE SHARE ZIP ({zip_filename}) ---")
    zip_path = root / zip_filename
    if zip_path.exists():
        zip_path.unlink()

    file_count = 0
    total_size = 0

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder_path, dirnames, filenames in os.walk(root):
            rel_folder = Path(folder_path).relative_to(root)
            
            # Skip excluded top-level and nested directories
            parts = set(rel_folder.parts)
            if parts.intersection(EXCLUDE_DIRS):
                continue
            
            # Prune dirnames in-place to prevent os.walk from recursing into excluded folders
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

            for filename in filenames:
                file_path = Path(folder_path) / filename
                rel_file = file_path.relative_to(root)

                # Skip .env files with credentials, logs, and excluded files
                if filename in EXCLUDE_FILES or filename.endswith(".pyc") or filename.endswith(".log"):
                    continue
                if filename == ".env" or filename.startswith(".env.") and not filename.endswith(".example"):
                    continue

                zf.write(file_path, arcname=str(rel_file))
                file_count += 1
                total_size += file_path.stat().st_size

    zip_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  [SUCCESS] Created clean archive: {zip_path.name}")
    print(f"  Files packaged: {file_count}")
    print(f"  Uncompressed size: {total_size / (1024 * 1024):.2f} MB")
    print(f"  Compressed ZIP size: {zip_mb:.2f} MB\n")
    return zip_path

def main():
    clean_caches(ROOT_DIR)
    check_env_templates(ROOT_DIR)
    zip_path = create_sharing_zip(ROOT_DIR)
    print("=================================================================")
    print("PROJECT IS CLEAN AND READY TO SHARE!")
    print(f"Clean archive created at: {zip_path.name}")
    print("You can now share the folder via Git or distribute the ZIP archive.")
    print("=================================================================")

if __name__ == "__main__":
    main()
