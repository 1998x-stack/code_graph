# utils/id_gen.py
# ── 确定性节点 ID 生成器 ──────────────────────────────────────────────
# 规则：全局唯一 + 可读 + 可逆推来源
# dir::<abs>  /  file::<abs>  /  class::<abs>::<Class>
# func::<abs>::<Class>::<fn>  (方法)
# func::<abs>::<fn>           (顶级函数)
import os


def _abs(path: str) -> str:
    return os.path.abspath(path)


def dir_id(dir_path: str) -> str:
    return f"dir::{_abs(dir_path)}"


def file_id(file_path: str) -> str:
    return f"file::{_abs(file_path)}"


def class_id(file_path: str, class_name: str) -> str:
    return f"class::{_abs(file_path)}::{class_name}"


def func_id(
    file_path: str,
    func_name: str,
    class_name: str | None = None,
) -> str:
    base = _abs(file_path)
    if class_name:
        return f"func::{base}::{class_name}::{func_name}"
    return f"func::{base}::{func_name}"


def relation_id(source_id: str, rel_type: str, target_id: str) -> str:
    """关系 ID = <source>::<type>::<target>（保证唯一）"""
    return f"{source_id}::{rel_type}::{target_id}"