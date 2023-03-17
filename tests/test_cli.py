"""Test mdinfo CLI"""

import pathlib
import re
from os import stat, utime
from shutil import copyfile
import json

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
def source(tmpdir_factory):
    cwd = pathlib.Path.cwd()
    tmpdir = pathlib.Path(tmpdir_factory.mktemp("data"))
    copy_file(cwd / TEST_IMAGE_1, tmpdir / pathlib.Path(TEST_IMAGE_1).name)
    copy_file(cwd / TEST_IMAGE_2, tmpdir / pathlib.Path(TEST_IMAGE_2).name)
    copy_file(cwd / TEST_MP3_1, tmpdir / pathlib.Path(TEST_MP3_1).name)

    return tmpdir


@pytest.fixture(scope="function")
def target(tmpdir_factory):
    return pathlib.Path(tmpdir_factory.mktemp("target"))


def test_cli_print(source, target):
    """Test CLI with -p/--print"""
    from mdinfo.cli import cli

    source_files = list(source.glob("*"))

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


def test_cli_csv(source, target):
    """Test CLI with --csv"""
    from mdinfo.cli import cli

    source_files = list(source.glob("*"))

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


def test_cli_json(source, target):
    """Test CLI with --json"""
    from mdinfo.cli import cli

    source_files = list(source.glob("*"))

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
