""" plugin example for mdinfo template system """

from typing import Iterable, List, Optional

import mdinfo

"""
mdinfo uses the [pluggy](https://pluggy.readthedocs.io/en/latest/) plugin system to allow you to extend the template system.

To create a template plugin, you need create a python package with a module that contains a hook implementation for the 
`get_template_help` and `get_template_value` hooks.

`get_template_help` returns the help text used by the `mdinfo --help` command.

`get_template_value` returns the value for the template field.
"""
# specify which template fields your plugin will provide
FIELDS = {"{foo}": "Returns BAR", "{bar}": "Returns FOO"}


@mdinfo.hookimpl
def get_template_help() -> Iterable:
    """Specify help text for your plugin; will get displayed with mdinfo --help
    Returns:
        Iterable (e.g. list) of help text as str or list of lists
        str items may be formatted with markdown
        list of lists items can be used for definition lists (e.g. [[key1, value1], [key2, value2]])
    """
    text = """
    This a useless example plugin that returns the text "FOO" or "BAR".

    mdinfo will correctly format this text for you so don't worry about the spaces preceding each line
    in the docstring block quote. 

    You can use markdown in the docstring to format the text. **This is bold** and *this is italic*.

    - You can also use lists
    - This is another list item

    """
    fields = [["Field", "Description"], *[[k, v] for k, v in FIELDS.items()]]
    return ["**FooBar Fields**", fields, text]


@mdinfo.hookimpl
def get_template_value(
    filepath: str,
    field: str,
    subfield: Optional[str],
    field_arg: Optional[str],
    default: List[str],
) -> Optional[List[Optional[str]]]:
    """Example implementation of get_template_value hook

    Args:
        filepath: path to the file being processed
        field: template field to find value for
        subfield: the subfield provided, if any (e.g. {field:subfield})
        field_arg: the field argument provided, if any (e.g. {field(arg)})
        default: the default value provided to the template, if any (e.g. {field,default})

    Returns:
        The matching template value (which may be None) as a list or None if template field is not handled.

    Raises:
        ValueError: if the template is not correctly formatted (e.g. plugin expected a subfield but none provided)
    """
    # if your plugin does not handle a certain field, return None
    if "{" + field + "}" not in FIELDS:
        return None

    if field == "foo":
        return ["BAR"]
    elif field == "bar":
        return ["FOO"]
    else:
        return None
