#!/usr/bin/env python3
# This script was automatically generated by packaging.
# Hand-tweaked to support environment markers.
import codecs
import re
try:
    from setuptools import setup
    SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    SETUPTOOLS = False
try:
    from configparser import RawConfigParser
except ImportError:
    from ConfigParser import RawConfigParser

# For environment markers
import platform #@UnusedImport
import os #@UnusedImport
import sys

python_version = "%s.%s" % sys.version_info[:2]
python_full_version = sys.version.split()[0]


def split_multiline(value):
    """Split a multiline string into a list, excluding blank lines."""

    return [element for element in
            (line.strip() for line in value.split('\n'))
            if element]


def eval_environ(value):
    """"Evaluate environment markers."""

    def eval_environ_str(value):
        parts = value.split(";")
        if len(parts) < 2:
            new_value = parts[0]
        else:
            expr = parts[1].lstrip()
            if not re.match("^((\\w+(\\.\\w+)?|'.*?'|\".*?\")\\s+"
                            "(in|==|!=|not in)\\s+"
                            "(\\w+(\\.\\w+)?|'.*?'|\".*?\")"
                            "(\s+(or|and)\s+)?)+$", expr):
                raise ValueError("bad environment marker: %r" % (expr,))
            expr = re.sub(r"(platform.\w+)", r"\1()", expr)
            new_value = parts[0] if eval(expr) else None
        return new_value

    if isinstance(value, list):
        new_value = []
        for element in value:
            element = eval_environ_str(element)
            if element is not None:
                new_value.append(element)
    elif isinstance(value, str):
        new_value = eval_environ_str(value)
    else:
        new_value = value

    return new_value


def cfg_to_args(path='setup.cfg'):
    """Compatibility helper to use setup.cfg in setup.py.

    This functions uses an existing setup.cfg to generate a dictionnary of
    keywords that can be used by distutils.core.setup(**kwargs).  It is used
    by generate_setup_py.

    *file* is the path to the setup.cfg file.  If it doesn't exist,
    PackagingFileError is raised.
    """

    # XXX ** == needs testing
    D1_D2_SETUP_ARGS = {"name": ("metadata",),
                        "version": ("metadata",),
                        "author": ("metadata",),
                        "author_email": ("metadata",),
                        "maintainer": ("metadata",),
                        "maintainer_email": ("metadata",),
                        "url": ("metadata", "home_page"),
                        "description": ("metadata", "summary"),
                        "long_description": ("metadata", "description"),
                        "download-url": ("metadata",),
                        "classifiers": ("metadata", "classifier"),
                        "platforms": ("metadata", "platform"),  # **
                        "license": ("metadata",),
                        "requires": ("metadata", "requires_dist"),
                        "provides": ("metadata", "provides_dist"),  # **
                        "obsoletes": ("metadata", "obsoletes_dist"),  # **
                        "package_dir": ("files", 'packages_root'),
                        "packages": ("files",),
                        "scripts": ("files",),
                        "py_modules": ("files", "modules"),  # **
                        }

    MULTI_FIELDS = set(["classifiers",
                        "platforms",
                        "requires",
                        "provides",
                        "obsoletes",
                        "packages",
                        "scripts",
                        "py_modules"])

    ENVIRON_FIELDS = set([("metadata", "requires_python"),
                          ("metadata", "requires_external"),
                          ("metadata", "requires_dist"),
                          ("metadata", "provides_dist"),
                          ("metadata", "obsoletes_dist"),
                          ("metadata", "classifier")])

    if SETUPTOOLS:
        D1_D2_SETUP_ARGS["install_requires"] = D1_D2_SETUP_ARGS["requires"]
        MULTI_FIELDS.add("install_requires")
        del D1_D2_SETUP_ARGS["requires"]
        MULTI_FIELDS.remove("requires")

    def has_get_option(config, section, option):
        if config.has_option(section, option):
            return config.get(section, option)
        elif config.has_option(section, option.replace('_', '-')):
            return config.get(section, option.replace('_', '-'))
        else:
            return False

    # The real code starts here
    config = RawConfigParser()
    f = codecs.open(path, encoding='utf-8')
    try:
        config.readfp(f)
    finally:
        f.close()

    kwargs = {}
    for arg in D1_D2_SETUP_ARGS:
        if len(D1_D2_SETUP_ARGS[arg]) == 2:
            # The distutils field name is different than packaging's
            section, option = D1_D2_SETUP_ARGS[arg]

        else:
            # The distutils field name is the same as packaging's
            section = D1_D2_SETUP_ARGS[arg][0]
            option = arg

        in_cfg_value = has_get_option(config, section, option)
        if not in_cfg_value:
            # There is no such option in the setup.cfg
            if arg == 'long_description':
                filenames = has_get_option(config, section, 'description-file')
                if filenames:
                    filenames = split_multiline(filenames)
                    in_cfg_value = []
                    for filename in filenames:
                        fp = codecs.open(filename, encoding='utf-8')
                        try:
                            in_cfg_value.append(fp.read())
                        finally:
                            fp.close()
                    in_cfg_value = '\n\n'.join(in_cfg_value)
            else:
                continue

        if arg == 'package_dir' and in_cfg_value:
            in_cfg_value = {'': in_cfg_value}

        if arg in MULTI_FIELDS:
            # support multiline options
            in_cfg_value = split_multiline(in_cfg_value)

        if (section, option) in ENVIRON_FIELDS:
            in_cfg_value = eval_environ(in_cfg_value)

        if in_cfg_value:
            kwargs[arg] = in_cfg_value

    return kwargs


setup(**cfg_to_args())