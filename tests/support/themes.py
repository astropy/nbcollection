"""Support code for testing themes."""

from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from typing import Any


def write_conversion(*, base_dir: str, content: str, resources: dict[str, Any]) -> None:
    """Write an nbconvert conversion out to the filesystem, in the _build/ directory."""
    build_dir = Path(__file__).parent.joinpath("../../_build")
    build_dir.mkdir(exist_ok=True)

    instance_dir = build_dir.joinpath(base_dir)
    if instance_dir.is_dir():
        rmtree(instance_dir)
    instance_dir.mkdir(parents=True)

    content_path = instance_dir.joinpath(
        f"{resources['metadata']['name']}{resources['output_extension']}"
    )
    content_path.write_text(content)

    for name, file_content in resources["outputs"].items():
        p = instance_dir.joinpath(name)
        p.write_bytes(file_content)
