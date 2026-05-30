import os
import shutil
from datetime import datetime
from pathlib import Path


BACKUP_DIR_NAME = ".docx_backups"


def ensure_backup(file_path: str) -> str:
    abs_path = os.path.abspath(file_path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"文件不存在: {abs_path}")

    doc_dir = os.path.dirname(abs_path)
    backup_dir = os.path.join(doc_dir, BACKUP_DIR_NAME)
    os.makedirs(backup_dir, exist_ok=True)

    filename = os.path.basename(abs_path)
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{stem}_backup_{timestamp}{suffix}"
    backup_path = os.path.join(backup_dir, backup_filename)

    shutil.copy2(abs_path, backup_path)
    return backup_path


def check_file_writable(file_path: str) -> str | None:
    abs_path = os.path.abspath(file_path)
    if not os.path.isfile(abs_path):
        return f"文件不存在: {abs_path}"

    try:
        with open(abs_path, "a"):
            pass
    except PermissionError:
        return (
            f"文件被占用或无写入权限: {abs_path}\n"
            "请关闭 Word/WPS 中打开的该文件后重试。"
        )
    except OSError as e:
        return f"无法写入文件: {abs_path}，原因: {e}"

    return None


def list_backups(file_path: str) -> list[str]:
    abs_path = os.path.abspath(file_path)
    doc_dir = os.path.dirname(abs_path)
    backup_dir = os.path.join(doc_dir, BACKUP_DIR_NAME)

    if not os.path.isdir(backup_dir):
        return []

    stem = Path(abs_path).stem
    suffix = Path(abs_path).suffix
    backups = []
    for f in sorted(os.listdir(backup_dir), reverse=True):
        if f.startswith(stem) and f.endswith(suffix) and "backup" in f:
            backups.append(os.path.join(backup_dir, f))
    return backups


def restore_from_backup(file_path: str, backup_path: str) -> str:
    abs_path = os.path.abspath(file_path)
    if not os.path.isfile(backup_path):
        raise FileNotFoundError(f"备份文件不存在: {backup_path}")
    shutil.copy2(backup_path, abs_path)
    return abs_path
