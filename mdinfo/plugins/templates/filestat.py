"""File stat template plugin for mdinfo"""

import grp
import os
import pwd
from typing import Iterable, List, Optional

import mdinfo

FIELDS = {
    "{size}": "Size of file in bytes",
    "{uid}": "User identifier of the file owner",
    "{gid}": "Group identifier of the file owner",
    "{user}": "User name of the file owner",
    "{group}": "Group name of the file owner",
}


@mdinfo.hookimpl
def get_template_help() -> Iterable:
    fields = [["Field", "Description"], *[[k, v] for k, v in FIELDS.items()]]
    return ["**File Information Fields**", fields]


@mdinfo.hookimpl
def get_template_value(
    filepath: str,
    field: str,
    subfield: Optional[str],
    field_arg: Optional[str],
    default: List[str],
) -> Optional[List[Optional[str]]]:
    """lookup value for os.stat values for filepath

    Args:
        field: template field to find value for.

    Returns:
        The matching template value (which may be None).
    """
    if "{" + field + "}" not in FIELDS:
        return None

    # TODO: add size.kB, size.MB, size.GB, size.TB, size.PB, size.EB, size.ZB, size.YB
    stat_info = os.stat(filepath)
    val = None
    if field == "size":
        val = stat_info.st_size
    elif field == "uid":
        val = stat_info.st_uid
    elif field == "gid":
        val = stat_info.st_gid
    elif field == "user":
        val = pwd.getpwuid(stat_info.st_uid).pw_name
    elif field == "group":
        val = grp.getgrgid(stat_info.st_gid).gr_name
    else:
        raise ValueError("Unknown field: {" + field + "}")

    return [str(val)]
