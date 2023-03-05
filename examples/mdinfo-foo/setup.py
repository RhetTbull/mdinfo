from setuptools import setup

setup(
    version="0.0.1",
    name="mdinfo-foo",
    install_requires="mdinfo",
    entry_points={"mdinfo": ["foo = mdinfo_foo"]},
    py_modules=["mdinfo_foo"],
)
