"""Print file metadata info"""

from __future__ import annotations

import csv
import datetime
import json
import pathlib
import re
import sys
from typing import Any

from .constants import NONE_STR_SENTINEL
from .filetemplate import FileTemplate
from .mtlparser import MTLParser
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
    undefined: str | None,
) -> None:
    """Print template string for each filepath"""
    for filepath in filepaths:
        print_templates(
            filepath, templates, no_filename, path, null_separator, undefined
        )


def print_templates(
    filepath: str,
    templates: tuple[str],
    no_filename: bool,
    path: bool,
    null_separator: bool,
    undefined: str | None,
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
    rendered_templates = [
        str(t).replace(NONE_STR_SENTINEL, undefined or "") for t in rendered_templates
    ]
    separator = "\0" if null_separator else " "
    print(f"{header}{separator.join(rendered_templates)}")


def print_templates_to_csv_for_files(
    filepaths: tuple[str],
    templates: tuple[str],
    no_filename: bool,
    path: bool,
    no_header: bool,
    delimiter: str,
    undefined: str | None,
) -> None:
    """Print template string for each filepath as CSV"""

    delimiter = delimiter or ","  # default to comma if delimiter is None

    # passing tab as delimiter on command line is tricky
    # so do what the user is probably trying to do
    if delimiter == "\\t":  # this is what happens if user passes "\t" as the argument
        delimiter = "\t"
    if delimiter.lower() == "tab":
        delimiter = "\t"

    templates = list(templates)
    fields = [get_field_name(field) for field in templates]
    if not no_filename:
        fields.insert(0, "filename")
    csv_writer = csv.writer(sys.stdout, delimiter=delimiter)
    if not no_header:
        csv_writer.writerow(fields)

    templates = [strip_field_name(t) for t in templates]
    if not no_filename:
        templates.insert(0, "{filepath}" if path else "{filepath.name}")
    for filepath in filepaths:
        print_templates_to_csv(filepath, templates, csv_writer, undefined)


def print_templates_to_csv(
    filepath: str, templates: tuple[str], csv_writer: csv.writer, undefined: str | None
) -> None:
    """Print template string for filepath as CSV"""
    options = RenderOptions(none_str=NONE_STR_SENTINEL)
    columns = [
        " ".join(FileTemplate(filepath).render(template, options=options))
        for template in templates
    ]
    columns = [str(t).replace(NONE_STR_SENTINEL, undefined or "") for t in columns]
    csv_writer.writerow(columns)


def print_templates_to_json_for_files(
    filepaths: tuple[str],
    templates: tuple[str],
    no_filename: bool,
    path: bool,
    array: bool,
    undefined: str | None,
) -> None:
    """Print template string for each filepath as JSON"""
    data_list = []
    for filepath in filepaths:
        data = get_dict_for_templates(filepath, templates, undefined)
        if not no_filename:
            data["filename"] = filepath if path else pathlib.Path(filepath).name
        data_list.append(data)
    if array:
        print(convert_to_json(data_list))
    else:
        for data in data_list:
            print(convert_to_json(data))


def get_dict_for_templates(
    filepath: str, templates: tuple[str], undefined: str | None
) -> dict[str, str]:
    """Get dict for filepath for converting to JSON"""
    options = RenderOptions(none_str=NONE_STR_SENTINEL)
    data = {}
    for template in templates:
        field = get_field_name(template)
        template = strip_field_name(template)
        rendered = FileTemplate(filepath).render(template, options=options)
        rendered = [
            str(t).replace(NONE_STR_SENTINEL, undefined or "") for t in rendered
        ]
        rendered = [t or None for t in rendered]
        data[field] = rendered[0] if len(rendered) == 1 else rendered
    return data


def convert_to_json(data: Any, indent: int = 4) -> str:
    """Convert data to JSON, converting datetime objects to ISO format"""
    default = lambda o: o.isoformat() if isinstance(o, datetime.datetime) else o
    return json.dumps(data, indent=indent, sort_keys=True, default=default)


def get_field_name(template: str) -> str:
    """
    Get field name from template for use with CSV header and JSON keys

    Field name may be provided using format: "field: {template}" or "field={template}".

    If no field name is provided, the first template field encountered
    is used as the field name.

    If no field name is provided and no template fields are found,
    then the entire template string is used as the field name.

    Args:
        template: template string

    Returns:
        field name
    """
    if match := re.match(r"([^:{}]+):\s*", template):
        return match[1]

    if match := re.match(r"([^={}]+)=\s*", template):
        return match[1]

    parser = MTLParser(get_field_values=lambda *x: x)
    if template_statements := parser.parse_statement(template):
        if template_statements[0].field:
            field_name = template_statements[0].field
            if template_statements[0].subfield:
                field_name += f":{template_statements[0].subfield}"
            return field_name
        return template

    raise ValueError(f"Could not find field in template: {template}")


def strip_field_name(template: str) -> str:
    """
    Strip field name from template

    Args:
        template: template string

    Returns:
        template string with field name removed
    """
    if match := re.match(r"([^:{}]+):\s*", template):
        return template[match.end() :]
    if match := re.match(r"([^={}]+)=\s*", template):
        return template[match.end() :]
    return template
