#!/usr/bin/env python3
"""Download the project dataset from the shared OneDrive/SharePoint link."""

from __future__ import annotations

import argparse
from http.cookiejar import CookieJar
from pathlib import Path
import shutil
import sys
import zipfile
from tempfile import NamedTemporaryFile
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import HTTPCookieProcessor, Request, build_opener


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "raw" / "traffic_accidents_mx.xlsx"
SHARE_URL = (
    "https://unisonmx-my.sharepoint.com/:x:/g/personal/a214202502_unison_mx/cQqFdDoiEjE6RarWH9MFphQOEgUB22tLPFaszvvUasMG-KsY1w?nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMH0"
)
CHUNK_SIZE = 1024 * 1024


def download_url(share_url: str) -> str:
    """Request the file itself instead of the SharePoint preview page."""
    parts = urlsplit(share_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["download"] = "1"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def is_xlsx(path: Path) -> bool:
    """An .xlsx file is a ZIP archive containing the Excel workbook manifest."""
    if not zipfile.is_zipfile(path):
        return False

    with zipfile.ZipFile(path) as workbook:
        return "[Content_Types].xml" in workbook.namelist()


def download(output_path: Path, source_url: str = SHARE_URL) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    request = Request(download_url(source_url), headers={"User-Agent": "Mozilla/5.0"})
    # SharePoint gives public links an anonymous FedAuth cookie on the first redirect.
    # Keep it for the next redirect, which serves the actual workbook.
    opener = build_opener(HTTPCookieProcessor(CookieJar()))

    with opener.open(request, timeout=60) as response:
        content_type = response.headers.get_content_type()
        if content_type == "text/html":
            raise RuntimeError(
                "SharePoint returned an HTML page instead of the workbook. "
                "Confirm that the sharing link allows downloads without signing in."
            )

        with NamedTemporaryFile(
            mode="wb", delete=False, dir=output_path.parent, prefix=f".{output_path.name}."
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            try:
                shutil.copyfileobj(response, temporary_file, length=CHUNK_SIZE)
            except Exception:
                temporary_path.unlink(missing_ok=True)
                raise

    try:
        if not is_xlsx(temporary_path):
            raise RuntimeError(
                "The downloaded file is not a valid .xlsx workbook. "
                "Check that the shared link points to the dataset and permits downloads."
            )
        temporary_path.replace(output_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Destination file (default: {DEFAULT_OUTPUT.relative_to(PROJECT_ROOT)})",
    )
    args = parser.parse_args()

    try:
        download(args.output)
    except (HTTPError, URLError, RuntimeError) as error:
        print(f"Download failed: {error}", file=sys.stderr)
        return 1

    print(f"Dataset saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
