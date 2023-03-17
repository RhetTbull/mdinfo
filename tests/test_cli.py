"""Test mdinfo CLI"""

import json
import pathlib
import re
from os import stat, utime
from shutil import copyfile

import pytest
from click.testing import CliRunner

TEST_IMAGE_1 = "tests/test_files/pears.jpg"
TEST_IMAGE_2 = "tests/test_files/flowers.jpeg"
TEST_MP3_1 = "tests/test_files/warm_lights.mp3"


def copy_file(source, target):
    """Copy a file while preserving the original timestamp"""
    copyfile(source, target)
    stats = stat(str(source))
    utime(str(target), (stats.st_atime, stats.st_mtime))


@pytest.fixture(scope="function")
def source(tmpdir_factory) -> pathlib.Path:
    cwd = pathlib.Path.cwd()
    tmpdir = pathlib.Path(tmpdir_factory.mktemp("data"))
    copy_file(cwd / TEST_IMAGE_1, tmpdir / pathlib.Path(TEST_IMAGE_1).name)
    copy_file(cwd / TEST_IMAGE_2, tmpdir / pathlib.Path(TEST_IMAGE_2).name)
    copy_file(cwd / TEST_MP3_1, tmpdir / pathlib.Path(TEST_MP3_1).name)

    return tmpdir


@pytest.fixture(scope="function")
def target(tmpdir_factory) -> pathlib.Path:
    return pathlib.Path(tmpdir_factory.mktemp("target"))


def test_cli_print(source: pathlib.Path, target: pathlib.Path):
    """Test CLI with -p/--print"""
    from mdinfo.cli import cli

    source_files = sorted(list(source.glob("*")))

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--print",
            "{filepath.name}",
            *[str(p) for p in source_files],
        ],
    )
    assert result.exit_code == 0
    assert (
        result.output == "\n".join([f"{p.name}: {p.name}" for p in source_files]) + "\n"
    )


def test_cli_print_no_filename(source: pathlib.Path, target: pathlib.Path):
    """Test CLI with -p/--print with --no-filename"""
    from mdinfo.cli import cli

    source_files = sorted(list(source.glob("*")))

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--print",
            "{filepath.name}",
            "--no-filename",
            *[str(p) for p in source_files],
        ],
    )
    assert result.exit_code == 0
    assert result.output == "\n".join([p.name for p in source_files]) + "\n"


def test_cli_print_null_separator(source: pathlib.Path, target: pathlib.Path):
    """Test CLI with -p/--print and --null-separator"""
    from mdinfo.cli import cli

    source_files = sorted(list(source.glob("*")))

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--print",
            "{filepath.name}",
            "--print",
            "{size}",
            "--no-filename",
            "--null-separator",
            *[str(p) for p in source_files],
        ],
    )
    assert result.exit_code == 0
    assert (
        result.output
        == "\n".join(f"{p.name}\0{p.stat().st_size}" for p in source_files) + "\n"
    )


def test_cli_csv(source: pathlib.Path, target: pathlib.Path):
    """Test CLI with --csv"""
    from mdinfo.cli import cli

    source_files = sorted(list(source.glob("*")))

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--print",
            "file:{filepath.name}",
            "-p",
            "{size}",
            "--no-filename",
            "--csv",
            *[str(p) for p in source_files],
        ],
    )
    assert result.exit_code == 0
    assert sorted(
        s for s in [string.strip() for string in result.output.split("\n")] if s
    ) == [
        "file,size",
        "flowers.jpeg,3449684",
        "pears.jpg,2771656",
        "warm_lights.mp3,7982019",
    ]


def test_cli_csv_no_header(source: pathlib.Path, target: pathlib.Path):
    """Test CLI with --csv and --no-header"""
    from mdinfo.cli import cli

    source_files = sorted(list(source.glob("*")))

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--print",
            "file:{filepath.name}",
            "-p",
            "{size}",
            "--no-filename",
            "--csv",
            "--no-header",
            *[str(p) for p in source_files],
        ],
    )
    assert result.exit_code == 0
    assert sorted(
        s for s in [string.strip() for string in result.output.split("\n")] if s
    ) == [
        "flowers.jpeg,3449684",
        "pears.jpg,2771656",
        "warm_lights.mp3,7982019",
    ]


def test_cli_json(source: pathlib.Path, target: pathlib.Path):
    """Test CLI with --json"""
    from mdinfo.cli import cli

    source_file = sorted(list(source.glob("*")))[0]
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "--print",
            "file:{filepath.name}",
            "-p",
            "{size}",
            "--no-filename",
            "--json",
            str(source_file),
        ],
    )
    assert result.exit_code == 0
    got = json.loads(result.output)
    expected = {"file": "flowers.jpeg", "size": "3449684"}
    assert got == expected


def test_cli_json_array(source: pathlib.Path, target: pathlib.Path):
    """Test CLI with --json with --array"""
    from mdinfo.cli import cli

    source_files = sorted(list(source.glob("*")))

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--print",
            "file:{filepath.name}",
            "-p",
            "{size}",
            "--no-filename",
            "--json",
            "--array",
            *[str(p) for p in source_files],
        ],
    )
    assert result.exit_code == 0
    got = sorted(json.loads(result.output), key=lambda x: x["file"])
    expected = [
        {"file": "flowers.jpeg", "size": "3449684"},
        {"file": "pears.jpg", "size": "2771656"},
        {"file": "warm_lights.mp3", "size": "7982019"},
    ]
    assert got == expected
