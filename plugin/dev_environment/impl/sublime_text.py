from __future__ import annotations

import inspect
import os
import re
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, TypeVar

import sublime
from LSP.plugin.core.collections import DottedDict
from LSP.plugin.core.constants import ST_VERSION
from more_itertools import first_true

from ..interfaces import BaseDevEnvironmentHandler

T = TypeVar("T")


def get_latest_st_python_version() -> tuple[int, int]:
    if ST_VERSION >= 4201:
        return (3, 13)
    if ST_VERSION >= 4107:
        return (3, 8)
    return (3, 3)


def get_oldest_st_python_version() -> tuple[int, int]:
    return (3, 3)


LATEST_ST_PYTHON_VERSION = get_latest_st_python_version()
OLDEST_ST_PYTHON_VERSION = get_oldest_st_python_version()


class BaseVersionedSublimeTextDevEnvironmentHandler(BaseDevEnvironmentHandler, ABC):
    python_version: tuple[int, int] = (-1, -1)
    python_version_no_dot: str = ""

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if this handler is available in the current ST version."""

    def handle_(self, *, settings: DottedDict) -> None:
        self._inject_extra_paths(settings=settings, paths=self.find_package_dependency_dirs())

    def find_package_dependency_dirs(self) -> list[str]:
        dep_dirs = sys.path.copy()

        # replace paths for target Python version
        # @see https://github.com/sublimelsp/LSP-pyright/issues/28
        re_pattern = re.compile(r"(python)(3\.?[0-9]+)", flags=re.IGNORECASE)
        dep_dirs = [re_pattern.sub(Rf"\g<1>{self.python_version_no_dot}", dep_dir) for dep_dir in dep_dirs]

        # move the "Packages/" to the last
        # @see https://github.com/sublimelsp/LSP-pyright/pull/26#discussion_r520747708
        packages_path = sublime.packages_path()
        dep_dirs.remove(packages_path)
        dep_dirs.append(packages_path)

        # sublime stubs - add as first
        if self.python_version == (3, 3):
            dep_dirs.insert(0, str(self.server_dir / "resources/typings/sublime_text_py33"))

        return list(filter(os.path.isdir, dep_dirs))


class SublimeText33DevEnvironmentHandler(BaseVersionedSublimeTextDevEnvironmentHandler):
    """This handler will just assume the project uses Python 3.3."""

    python_version = (3, 3)
    python_version_no_dot = "33"

    @classmethod
    def is_available(cls) -> bool:
        return True


class SublimeText38DevEnvironmentHandler(BaseVersionedSublimeTextDevEnvironmentHandler):
    """This handler will just assume the project uses Python 3.8."""

    python_version = (3, 8)
    python_version_no_dot = "38"

    @classmethod
    def is_available(cls) -> bool:
        return 4200 >= ST_VERSION >= 4107


class SublimeText313DevEnvironmentHandler(BaseVersionedSublimeTextDevEnvironmentHandler):
    """This handler will just assume the project uses Python 3.13."""

    python_version = (3, 13)
    python_version_no_dot = "313"

    @classmethod
    def is_available(cls) -> bool:
        return ST_VERSION >= 4201


def list_all_subclasses(
    root: type[T],
    skip_abstract: bool = False,
    skip_self: bool = False,
) -> Generator[type[T], None, None]:
    """Gets all sub-classes of the root class."""
    if not skip_self and not (skip_abstract and inspect.isabstract(root)):
        yield root
    for leaf in root.__subclasses__():
        yield from list_all_subclasses(leaf, skip_self=False, skip_abstract=skip_abstract)


# should be sorted by python_version ascending
VERSIONED_SUBLIME_TEXT_DEV_ENVIRONMENT_HANDLERS = sorted(
    list_all_subclasses(BaseVersionedSublimeTextDevEnvironmentHandler, skip_abstract=True),  # type: ignore
    key=lambda cls: cls.python_version,
)


class SublimeTextDevEnvironmentHandler(BaseDevEnvironmentHandler):
    """This handler selects the most appropriate handler based on the detected project Python version."""

    def handle_(self, *, settings: DottedDict) -> None:
        handler_cls = (
            self.resolve_handler_cls(self.detect_project_python_version())
            or self.resolve_handler_cls(OLDEST_ST_PYTHON_VERSION)  # fallback to the oldest one
        )
        assert handler_cls

        handler = handler_cls(server_dir=self.server_dir, workspace_folders=self.workspace_folders)
        return handler.handle(settings=settings)

    def detect_project_python_version(self) -> tuple[int, int]:
        try:
            project_dir = Path(self.workspace_folders[0]).resolve()
        except Exception:
            return OLDEST_ST_PYTHON_VERSION

        # ST auto uses the latest Python for files in "Packages/User/"
        if (Path(sublime.packages_path()) / "User") in (project_dir, *project_dir.parents):
            return LATEST_ST_PYTHON_VERSION

        # detect from project's ".python-version" file
        if (py_verion_file := (project_dir / ".python-version")).is_file() and (
            m := re.match(b"^(\\d+)\\.(\\d+)$", py_verion_file.read_bytes(), re.MULTILINE)
        ):
            return (int(m[1]), int(m[2]))

        return OLDEST_ST_PYTHON_VERSION

    @staticmethod
    def resolve_handler_cls(
        wanted_version: tuple[int, int],
    ) -> type[BaseVersionedSublimeTextDevEnvironmentHandler] | None:
        return first_true(
            VERSIONED_SUBLIME_TEXT_DEV_ENVIRONMENT_HANDLERS,
            pred=lambda cls: cls.is_available() and cls.python_version >= wanted_version,
        )
