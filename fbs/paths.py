import os
import json
from os.path import join, normpath, dirname, exists

from fbs._state import SETTINGS
from functools import lru_cache
from fbs.error import FbsError
from fbs._settings import expand_placeholders


@lru_cache
def _get_paths() -> dict:
    """Get the user configurable paths mapping."""
    paths_file = project_path("paths.json")
    if os.path.isfile(paths_file):
        try:
            with open(paths_file) as f:
                _paths = json.load(f)
            if not isinstance(_paths, dict):
                raise TypeError("paths.json file must contain a dictionary if defined.")
        except Exception as e:
            raise FbsError(e) from e
        return _paths
    else:
        return {}


BuildSystemDefault = "build_system"
IconsDefault = "icons"


@lru_cache
def get_build_system_dir() -> str:
    """
    Get path to the build system directory in the project.
    Defaults to "build_system"
    """
    return _get_paths().get("build_path", BuildSystemDefault)


@lru_cache
def get_icon_dir() -> str:
    """
    Get the path to the icon directory in the project.
    Defaults to "icons"
    """
    return SETTINGS["icon_dir"]


@lru_cache
def get_script_path() -> str:
    """Get the path of the python main script."""
    return SETTINGS["main_module"]


@lru_cache
def get_python_path() -> str:
    """Get the path that python should run from."""
    return SETTINGS["python_path"]


@lru_cache
def get_configurable_settings() -> dict:
    return {
        "build_system_dir": get_build_system_dir(),
    }


def fix_path(base_dir, path_str):
    return normpath(join(base_dir, *path_str.split("/")))


def default_path(path_str: str) -> str:
    """
    Get the full path to a default file.
    Does not apply substitutions.
    >>> path = default_path("${build_system_dir}/build/settings/base.json")
    """
    defaults_dir = join(dirname(__file__), "_defaults")
    return fix_path(defaults_dir, path_str)


def get_project_root() -> str:
    """Get the root project path"""
    try:
        return SETTINGS["project_dir"]
    except KeyError:
        error_message = (
            "Cannot call project_path(...) until fbs.init(...) has been " "called."
        )
        raise FbsError(error_message) from None


def project_path(path_str):
    """
    Return the absolute path of the given file in the project directory. For
    instance: path('src/my_app'). The `path_str` argument should always use
    forward slashes `/`, even on Windows. You can use placeholders to refer to
    settings. For example: path('${freeze_dir}/foo').
    """
    project_dir = get_project_root()
    path_str = expand_placeholders(path_str, SETTINGS)
    return fix_path(project_dir, path_str)


def get_settings_paths(profiles):
    return list(
        filter(
            exists,
            (
                path_fn("${build_system_dir}/build/settings/%s.json" % profile)
                for path_fn in (default_path, project_path)
                for profile in profiles
            ),
        )
    )
