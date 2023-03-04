"""Print file metadata info"""

from __future__ import annotations

import csv
import datetime
import json
import pathlib
import sys
from typing import Any

from .constants import NONE_STR_SENTINEL
from .filetemplate import FileTemplate
from .renderoptions import RenderOptions

__all__ = [
    "print_templates_for_files",
    "print_templates_to_csv_for_files",
    "print_templates_to_json_for_files",
]


def print_templates_for_files(
    filepaths: tuple[str],
    templates: tuple[str],
    no_filename: bool,
    path: bool,
    null_separator: bool,
) -> None:
    """Print template string for each filepath"""
    for filepath in filepaths:
        print_templates(filepath, templates, no_filename, path, null_separator)


def print_templates(
    filepath: str,
    templates: tuple[str],
    no_filename: bool,
    path: bool,
    null_separator: bool,
) -> None:
    """Print template string for filepath"""
    options = RenderOptions(none_str=NONE_STR_SENTINEL)
    rendered_templates = []
    for template in templates:
        rendered_templates.extend(
            FileTemplate(filepath).render(template, options=options)
        )
    header = (
        ""
        if no_filename
        else (f"{filepath}: " if path else f"{pathlib.Path(filepath).name}: ")
    )
    separator = "\0" if null_separator else " "
    print(f"{header}{separator.join(rendered_templates)}")


def print_templates_to_csv_for_files(
    filepaths: tuple[str],
    field_templates: tuple[tuple[str, str]],
    no_filename: bool,
    path: bool,
    no_header: bool,
    delimiter: str,
) -> None:
    """Print template string for each filepath as CSV"""

    delimiter = delimiter or ","  # default to comma if delimiter is None

    # passing tab as delimiter on command line is tricky
    # so do what the user is probably trying to do
    if delimiter == "\\t":  # this is what happens if user passes "\t" as the argument
        delimiter = "\t"
    if delimiter.lower() == "tab":
        delimiter = "\t"

    fields = [field for field, _ in field_templates]
    if not no_filename:
        fields.insert(0, "filename")
    csv_writer = csv.writer(sys.stdout, delimiter=delimiter)
    if not no_header:
        csv_writer.writerow(fields)

    templates = [template for _, template in field_templates]
    if not no_filename:
        templates.insert(0, "{filepath}" if path else "{filepath.name}")
    for filepath in filepaths:
        print_templates_to_csv(filepath, templates, csv_writer)


def print_templates_to_csv(
    filepath: str, templates: tuple[str], csv_writer: csv.writer
) -> None:
    """Print template string for filepath as CSV"""
    options = RenderOptions(none_str=NONE_STR_SENTINEL)
    columns = [
        " ".join(FileTemplate(filepath).render(template, options=options))
        for template in templates
    ]
    csv_writer.writerow(columns)


def print_templates_to_json_for_files(
    filepaths: tuple[str],
    field_templates: tuple[tuple[str, str]],
    no_filename: bool,
    path: bool,
    array: bool,
) -> None:
    """Print template string for each filepath as JSON"""
    data_list = []
    for filepath in filepaths:
        data = get_dict_for_templates(filepath, field_templates)
        if not no_filename:
            data["filename"] = filepath if path else pathlib.Path(filepath).name
        data_list.append(data)
    if array:
        print(convert_to_json(data_list))
    else:
        for data in data_list:
            print(convert_to_json(data))


def get_dict_for_templates(
    filepath: str, field_templates: tuple[tuple[str, str]]
) -> dict[str, str]:
    """Get JSON for filepath"""
    options = RenderOptions(none_str=NONE_STR_SENTINEL)
    data = {}
    for field, tempalte in field_templates:
        rendered = FileTemplate(filepath).render(tempalte, options=options)
        data[field] = rendered[0] if len(rendered) == 1 else rendered
    return data


def convert_to_json(data: Any, indent: int = 4) -> str:
    """Convert data to JSON, converting datetime objects to ISO format"""
    default = lambda o: o.isoformat() if isinstance(o, datetime.datetime) else o
    return json.dumps(data, indent=indent, sort_keys=True, default=default)
