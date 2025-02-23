from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from pyfuture.utils import transfer_file

if TYPE_CHECKING:
    from pdm.backend.hooks.base import Context


def get_target_str(hook_config: dict) -> str | None:
    target_str = os.environ.get("PYFUTURE_TARGET", None)
    if target_str is None:
        target_str = hook_config.get("target", None)
    return target_str


def get_target(target_str: str | None) -> tuple[int, int]:
    if target_str is None:
        return sys.version_info[:2]
    else:
        return (int(target_str[2:3]), int(target_str[3:]))


def get_hook_config(context: Context) -> dict:
    return context.config.data.get("tool", {}).get("pdm", {}).get("build", {}).get("hooks", {}).get("pyfuture", {})


def pdm_build_initialize(context: Context, target_str: str | None) -> None:
    context.config.build_config["is-purelib"] = True
    if target_str is not None:
        context.builder.config_settings["--python-tag"] = target_str


def pdm_build_update_files(context: Context, files: dict[str, Path], target: tuple[int, int]) -> None:
    build_dir = context.ensure_build_dir()
    package_dir = Path(context.config.build_config.package_dir)
    includes = context.config.build_config.includes
    for include in includes:
        src_path = package_dir / include
        tgt_path = build_dir / include
        for src_file in src_path.glob("**/*.py"):
            tgt_file = tgt_path / src_file.relative_to(src_path)
            files[f"{tgt_file.relative_to(build_dir)}"] = tgt_file
            transfer_file(src_file, tgt_file, target=target)
