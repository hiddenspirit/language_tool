#!/usr/bin/env python3
"""Download latest LanguageTool distribution
"""

import glob
import os
import re
import shutil
import sys

from contextlib import closing
from tempfile import TemporaryFile
from zipfile import ZipFile

from urllib.request import urlopen, Request
from urllib.parse import urljoin
from packaging.version import Version, InvalidVersion


def parse_version(version):
    """Parse a version string, returning None if it isn't PEP 440 compliant.
    """
    try:
        return Version(version)
    except InvalidVersion:
        return None


def urlopen_with_ua(url):
    req = Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    return urlopen(req)

BASE_URLS = ["https://languagetool.org/download/"]
PACKAGE_PATH = "language_tool"


def get_common_prefix(z):
    """Get common directory in a zip file if any.
    """
    l = z.namelist()
    if l and all(n.startswith(l[0]) for n in l[1:]):
        return l[0]
    return None


def download_lt(update=False):
    assert os.path.isdir(PACKAGE_PATH)
    old_path_list = [
        path for path in
        glob.glob(os.path.join(PACKAGE_PATH, "LanguageTool*"))
        if os.path.isdir(path)
    ]

    if old_path_list and not update:
        return

    contents = ""

    for n, base_url in enumerate(BASE_URLS):
        try:
            with closing(urlopen_with_ua(base_url)) as u:
                while True:
                    data = u.read()
                    if not data:
                        break
                    contents += data.decode()
            break
        except IOError as e:
            if n == len(BASE_URLS) - 1:
                raise

    href_format = r'<a href="(LanguageTool-(\d+.*?)\.{})">'

    def find_matches(ext):
        result = []
        for m in re.finditer(href_format.format(ext), contents, re.I):
            version = parse_version(m.group(2))
            if version is not None:
                result.append((m.group(1), version))
        return result

    matches = find_matches("zip") or find_matches("oxt")

    if not matches:
        raise RuntimeError(
            "no LanguageTool download found at {!r}".format(base_url))

    matches.sort(key=lambda item: item[1])
    filename, version = matches[-1]
    url = urljoin(base_url, filename)
    dirname = os.path.splitext(filename)[0]
    extract_path = os.path.join(PACKAGE_PATH, dirname)

    if extract_path in old_path_list:
        print("No update needed: {!r}".format(dirname))
        return

    for old_path in old_path_list:
        match = re.search(r"LanguageTool-(\d+.*?)$", old_path)
        if match:
            current_version = parse_version(match.group(1))
            if current_version is None:
                continue
            if current_version > version:
                print(
                    "Local version: {!r}, Remote version: {!r}"
                    .format(str(current_version), str(version))
                )
                return

    with closing(TemporaryFile()) as t:
        with closing(urlopen_with_ua(url)) as u:
            content_len = int(u.headers["Content-Length"])
            sys.stdout.write(
                "Downloading {!r} ({:.1f} MiB)...\n"
                .format(filename, content_len / 1048576.)
            )
            sys.stdout.flush()
            chunk_len = content_len // 100
            data_len = 0
            while True:
                data = u.read(chunk_len)
                if not data:
                    break
                data_len += len(data)
                t.write(data)
                sys.stdout.write(
                    "\r{:.0%}".format(float(data_len) / content_len))
                sys.stdout.flush()
            sys.stdout.write("\n")
        t.seek(0)
        for old_path in old_path_list:
            if os.path.isdir(old_path):
                shutil.rmtree(old_path)
        with closing(ZipFile(t)) as z:
            prefix = get_common_prefix(z)
            if prefix:
                z.extractall(PACKAGE_PATH)
                os.rename(os.path.join(PACKAGE_PATH, prefix),
                          os.path.join(PACKAGE_PATH, dirname))
            else:
                z.extractall(extract_path)


if __name__ == "__main__":
    sys.exit(download_lt(update=True))
