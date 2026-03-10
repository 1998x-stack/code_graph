# utils/file_utils.py
# ── 文件遍历、读取、MD5 工具 ──────────────────────────────────────────
import os
import hashlib

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def walk_project(
    project_root: str,
    suffixes: list[str] | None = None,
) -> list[str]:
    """
    递归遍历项目，返回所有匹配后缀的文件绝对路径列表。

    :param project_root: 项目根目录
    :param suffixes:     目标后缀列表，如 [".py"]；None 则返回所有文件
    :return:             绝对路径列表
    """
    root = os.path.abspath(project_root)
    if not os.path.isdir(root):
        logger.error(f"项目路径不存在或不是目录: {root}")
        return []

    exclude = set(settings.EXCLUDE_DIRS)
    results: list[str] = []

    for dirpath, dirnames, filenames in os.walk(root):
        # 原地过滤，防止 os.walk 进入排除目录
        dirnames[:] = [
            d for d in dirnames
            if d not in exclude and not d.startswith(".")
        ]
        for fname in filenames:
            if suffixes is None or os.path.splitext(fname)[1] in suffixes:
                results.append(os.path.join(dirpath, fname))

    logger.info(f"遍历完成: {root}，共 {len(results)} 个目标文件")
    return results


def read_file(path: str) -> str:
    """读取文件内容，依次尝试 utf-8 / gbk，失败返回空串"""
    for encoding in ("utf-8", "gbk"):
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except OSError as e:
            logger.error(f"文件读取失败: {path} — {e}")
            return ""
    logger.warning(f"编码识别失败，跳过: {path}")
    return ""


def file_md5(path: str) -> str:
    """计算文件 MD5，用于增量更新时的变更检测"""
    if not os.path.isfile(path):
        return ""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()