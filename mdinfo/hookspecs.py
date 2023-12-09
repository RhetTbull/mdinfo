""" pluggy hookimpl specification for mdinfo template system """

from typing import Iterable, List, Optional

from pluggy import HookspecMarker

hookspec = HookspecMarker("mdinfo")


@hookspec(firstresult=True)
def get_template_value(
    filepath: str,
    field: str,
    subfield: Optional[str],
    field_arg: Optional[str],
    default: List[str],
) -> Optional[List[Optional[str]]]:
    """Called by template.py to get template value for custom template

    Return: None if field is not handled by this plugin otherwise list of str values"""

    # return value of None means that field is not handled by this plugin
    # return value of [None] means that field is handled by this plugin but value resolved to None (no value)
    # return value of [value] means that field is handled by this plugin and value resolved to value


@hookspec
def get_template_help() -> Iterable:
    """Return iterable of one or more help elements. Each element may be a str, a dict, or a list of lists"""
