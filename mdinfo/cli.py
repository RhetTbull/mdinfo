""" Use template to automatically move files into directories """

from __future__ import annotations

import io
import re
import sys
from typing import List, Optional

import click
from cloup import (
    Command,
    Context,
    HelpFormatter,
    HelpTheme,
    Style,
    argument,
    command,
    constraint,
    option,
    option_group,
    version_option,
)
from cloup.constraints import If, RequireExactly, accept_none, mutually_exclusive
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.markdown import Markdown

from mdinfo.mtlparser import UnknownFieldError

from ._version import __version__
from .constants import APP_NAME
from .filetemplate import get_template_help
from .mdinfo import (
    print_templates_for_files,
    print_templates_to_csv_for_files,
    print_templates_to_json_for_files,
)
from .utils import bold

# Set up rich console
_global_console = Console()
_global_console_stderr = Console(stderr=True)

# if True, shows verbose output, turned off via --quiet flag
_global_verbose = True


def verbose(message_str, **kwargs):
    if not _global_verbose:
        return
    _global_console.print(message_str, **kwargs)


def print_help_msg(command):
    with Context(command) as ctx:
        click.echo(command.get_help(ctx))


def print_error(message):
    """Print error message to stderr with rich"""
    _global_console_stderr.print(message, style="bold red")


def print_warning(message):
    """Print warning message to stdout with rich"""
    _global_console.print(message, style="bold yellow")


def echo(message):
    """print to stdout using rich"""
    _global_console.print(message)


class MDInfoCommand(Command):
    """Custom cloup.command that overrides get_help() to show additional help info for mdinfo"""

    def get_help(self, ctx):
        help_text = super().get_help(ctx)
        formatter = HelpFormatter()

        formatter.write("\n\n")
        formatter.write(rich_text(bold("Template System"), width=formatter.width))
        formatter.write("\n\n")
        for help_item in get_template_help():
            # items from get_template_help are either markdown strings or lists of lists
            if type(help_item) is str:
                formatter.write(format_markdown_str(help_item, width=formatter.width))
                formatter.write("\n")
            elif isinstance(help_item, (tuple, list)):
                help_list = [tuple(rich_text(bold(col)) for col in help_item[0])]
                help_list.extend(tuple(h) for h in help_item[1:])
                formatter.write_dl(help_list)
                formatter.write("\n")
        formatter.write_text("")
        help_text += formatter.getvalue()
        return help_text

    def get_help_option(self, ctx: Context) -> Optional["click.Option"]:
        """Returns the help option object."""
        # copied from Click source code and modified to use pager
        help_options = self.get_help_option_names(ctx)

        if not help_options or not self.add_help_option:
            return None

        def show_help(ctx: Context, param: "click.Parameter", value: str) -> None:
            if value and not ctx.resilient_parsing:
                click.echo_via_pager(ctx.get_help(), color=ctx.color)
                ctx.exit()

        return click.Option(
            help_options,
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=show_help,
            help="Show this message and exit.",
        )


formatter_settings = HelpFormatter.settings(
    theme=HelpTheme(
        invoked_command=Style(fg="bright_yellow"),
        heading=Style(fg="bright_white", bold=True),
        constraint=Style(fg="magenta"),
        col1=Style(fg="bright_yellow"),
    )
)


@command(cls=MDInfoCommand, formatter_settings=formatter_settings)
@option_group(
    "Required",
    option(
        "--print",
        "-p",
        "print_option",
        metavar="METADATA_TEMPLATE",
        multiple=True,
        required=True,
        help="Template to use for printing metadata to stdout. "
        "May be repeated to print multiple templates. ",
    ),
)
@option_group(
    "Output Type",
    option(
        "--json",
        "-j",
        "json_option",
        is_flag=True,
        help="Print metadata as JSON. The JSON field name will be the same as the template name. "
        "You may specify a different field name by using the syntax: 'field_name:{template}' or 'field_name={template}'. ",
    ),
    option(
        "--csv",
        "-c",
        "csv_option",
        is_flag=True,
        help="Print metadata as CSV. The CSV field name will be the same as the template name. "
        "You may specify a different field name by using the syntax: 'field_name:{template}' or 'field_name={template}'. ",
    ),
    constraint=mutually_exclusive,
)
@option_group(
    "Formatting Options",
    option(
        "--no-filename",
        "-f",
        is_flag=True,
        help="Do not print filename headers. "
        "Without -h/--no-header, prints headers for each file which varies based on output type: "
        "With -p/--print, prints filename header before each line (similar to output of grep). "
        "With -c/--csv, prints filename as first column. "
        "With -j/--json, includes 'filename' in JSON dictionary which is set to the name of the file. "
        "The use of -h/--no-header overrides the default behavior such that: "
        "With -p/--print, does not print filename header. "
        "With -c/--csv, does not print filename in first column. "
        "With -j/--json, does not include 'filename' in JSON dictionary. "
        "See also -P/--path to print full file path instead of filename.",
    ),
    option(
        "--no-header", "-h", is_flag=True, help="Do not print headers with CSV output."
    ),
    option(
        "-0",
        "--null-separator",
        "null_separator",
        help="Use null character as field separator with -p/--print.",
        is_flag=True,
    ),
    option(
        "--undefined",
        "-u",
        help="String to use for undefined values. "
        "Default is empty string for standard output and --csv and `null` for --json.",
    ),
    option(
        "--delimiter",
        "-d",
        help="Field delimiter for CSV output. Default is comma (,). "
        "To use tab as delimiter, use `-d '\\t'` or `-d tab`.",
    ),
    option(
        "--array",
        "-a",
        is_flag=True,
        help="When used with --json, outputs a JSON array of objects instead single objects.",
    ),
    option(
        "--path",
        "-P",
        is_flag=True,
        help="Print full file path instead of filename. See also -f/--no-filename.",
    ),
)
@constraint(If("null_separator", then=accept_none), ["csv_option", "json_option"])
@constraint(If("delimiter", then=RequireExactly(1)), ["csv_option"])
@constraint(If("no_header", then=RequireExactly(1)), ["csv_option"])
@constraint(If("array", then=RequireExactly(1)), ["json_option"])
@constraint(If("path", then=accept_none), ["no_filename"])
@version_option(version=__version__)
@argument(
    "files", nargs=-1, required=True, type=click.Path(exists=True, resolve_path=True)
)
def cli(
    print_option: list[str],
    json_option: list[list[str]],
    csv_option: list[list[str]],
    no_filename: bool,
    no_header: bool,
    null_separator: bool,
    undefined: str | None,
    delimiter: str,
    array: bool,
    path: bool,
    files: list[str],
):
    """Print metadata info for files"""
    try:
        if csv_option:
            print_templates_to_csv_for_files(
                files, print_option, no_filename, path, no_header, delimiter, undefined
            )
        elif json_option:
            print_templates_to_json_for_files(
                files, print_option, no_filename, path, array, undefined
            )
        else:
            print_templates_for_files(
                files, print_option, no_filename, path, null_separator, undefined
            )
    except UnknownFieldError as e:
        print_error(e)
        sys.exit(1)


def rich_text(text, width=78):
    """Return rich formatted text"""
    sio = io.StringIO()
    console = Console(file=sio, force_terminal=True, width=width)
    console.print(text)
    rich_text = sio.getvalue()
    rich_text = rich_text.rstrip()
    sio.close()
    return rich_text


def strip_md_header_and_links(md):
    """strip markdown headers and links from markdown text md

    Args:
        md: str, markdown text

    Returns:
        str with markdown headers and links removed

    Note: This uses a very basic regex that likely fails on all sorts of edge cases
    but works for the links in the docs
    """
    links = r"(?:[*#])|\[(.*?)\]\(.+?\)"

    def subfn(match):
        return match.group(1)

    return re.sub(links, subfn, md)


def strip_md_links(md):
    """strip markdown links from markdown text md

    Args:
        md: str, markdown text

    Returns:
        str with markdown links removed

    Note: This uses a very basic regex that likely fails on all sorts of edge cases
    but works for the links in the osxphotos docs
    """
    links = r"\[(.*?)\]\(.+?\)"

    def subfn(match):
        return match.group(1)

    return re.sub(links, subfn, md)


def strip_html_comments(text):
    """Strip html comments from text (which doesn't need to be valid HTML)"""
    return re.sub(r"<!--(.|\s|\n)*?-->", "", text)


def format_markdown_str(string, width=78):
    """Return formatted markdown str for terminal"""
    sio = io.StringIO()
    console = Console(file=sio, force_terminal=True, width=width)
    console.print(Markdown(string))
    help_str = sio.getvalue()
    sio.close()
    return help_str
