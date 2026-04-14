from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
from pathlib import Path
from typing import Any

from lattice.utils import ensure_dir, slugify, write_json, write_jsonl


DEFAULT_USER_AGENT = "lattice-data-compiler/0.1 (mailto:h648zhan@uwaterloo.ca)"


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def http_get_json(url: str, headers: dict[str, str] | None = None) -> Any:
    request_headers = {"User-Agent": DEFAULT_USER_AGENT}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(url, headers=request_headers)
    with _open_with_retries(request) as response:
        return json.load(response)


def http_get_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    with _open_with_retries(request) as response:
        return response.read().decode("utf-8")


def safe_query(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def timestamp_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def source_root(base_output: str | Path, source_name: str) -> Path:
    return ensure_dir(Path(base_output) / source_name)


def write_source_jsonl(base_output: str | Path, source_name: str, rows: list[dict[str, Any]]) -> Path:
    root = source_root(base_output, source_name)
    path = root / f"{slugify(source_name)}.jsonl"
    write_jsonl(path, rows)
    return path


def write_source_manifest(base_output: str | Path, payload: dict[str, Any]) -> Path:
    root = ensure_dir(Path(base_output))
    path = root / "fetch_manifest.json"
    write_json(path, payload)
    return path


def _open_with_retries(request: urllib.request.Request, *, timeout: int = 45, retries: int = 3):
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            return urllib.request.urlopen(request, timeout=timeout, context=_ssl_context())
        except HTTPError as exc:
            if 400 <= exc.code < 500 and exc.code not in {408, 429}:
                raise
            last_error = exc
        except (TimeoutError, URLError) as exc:
            last_error = exc

        if attempt < retries - 1:
            time.sleep(1.2 * (attempt + 1))

    assert last_error is not None
    raise last_error
