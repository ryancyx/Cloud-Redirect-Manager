from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path

from .junction_ops import is_junction_or_reparse_point

logger = logging.getLogger(__name__)
WINDOWS_RMDIR_TIMEOUT_SECONDS = 30


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def dir_has_entries(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_file():
        return True
    try:
        next(path.iterdir())
        return True
    except StopIteration:
        return False


def unique_backup_path(path: Path) -> Path:
    candidate = path.with_name(f"{path.name}_backup")
    index = 0
    while candidate.exists():
        index += 1
        candidate = path.with_name(f"{path.name}_backup_{index}")
    return candidate


def backup_path(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"路径不存在，无法备份：{path}")
    candidate = unique_backup_path(path)
    path.rename(candidate)
    return candidate


def move_directory(source: Path, target: Path) -> None:
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"源目录不存在：{source}")
    if target.exists():
        raise FileExistsError(f"目标目录已存在：{target}")
    ensure_dir(target.parent)
    shutil.move(str(source), str(target))


def copy_directory_contents(source: Path, target: Path) -> None:
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"源目录不存在：{source}")
    ensure_dir(target)
    for child in source.iterdir():
        destination = target / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(child, destination)


def remove_tree(path: Path) -> None:
    target = Path(path)

    if not target.exists() and not is_junction_or_reparse_point(target):
        return
    if is_junction_or_reparse_point(target):
        raise RuntimeError("目标是链接入口，不允许作为云端目录递归删除")

    try:
        shutil.rmtree(target)
    except Exception as exc:
        logger.warning(
            "shutil.rmtree failed for %s: %s; attempting Windows rmdir fallback",
            target,
            exc,
        )
        if os.name != "nt":
            logger.exception("Directory deletion failed without Windows fallback: %s", target)
            raise RuntimeError(f"删除目录失败：{target}；原因：{exc}") from exc

        try:
            result = subprocess.run(
                ["cmd", "/c", "rmdir", "/S", "/Q", str(target)],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
                timeout=WINDOWS_RMDIR_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as timeout_exc:
            details = (
                f"删除目录超时：{target}；超时：{WINDOWS_RMDIR_TIMEOUT_SECONDS} 秒；"
                "建议关闭占用该目录的程序或等待 OneDrive 同步完成后重试"
            )
            if target.exists():
                details = f"{details}；原因：{timeout_exc}"
            logger.error("Windows rmdir fallback timed out for %s after %s seconds", target, WINDOWS_RMDIR_TIMEOUT_SECONDS)
            raise RuntimeError(details) from timeout_exc

        if target.exists():
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            details = stderr or stdout or str(exc)
            logger.error("Windows rmdir fallback failed for %s: %s", target, details)
            raise RuntimeError(f"删除目录失败：{target}；原因：{details}") from exc