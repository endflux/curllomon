"""Core per-call curl_easy_setopt / perform / read-result logic.

Split out of the top-level `request()` (see __init__.py) so both it and
`Session.request()` (session.py) can share the same option-setting/perform/
read-result code. The caller owns the handle's lifecycle: `request()` runs
curl_easy_init/curl_easy_cleanup around a single call; `Session` reuses one
handle across calls and runs curl_easy_reset between them instead.
"""

import ctypes
import json as _json
from typing import Any, Optional, Union

from . import _binding
from .const import CurlInfo, CurlOpt
from .headers import Headers, HeaderTypes
from .impersonate import BrowserTypeLiteral, resolve_latest_browser_type
from .response import Response

lib = _binding.lib


def perform(
    curl: "ctypes.c_void_p",
    url: str,
    method: str = "GET",
    headers: Optional[HeaderTypes] = None,
    json: Optional[Any] = None,
    data: Optional[Union[bytes, str]] = None,
    impersonate: Optional["BrowserTypeLiteral"] = None,
) -> Response:
    """Set options on `curl`, perform the request, and return the Response."""
    header_slist = ctypes.c_void_p(None)
    try:
        lib.curl_easy_setopt(curl, CurlOpt.URL, url.encode())

        req_headers = Headers(headers)

        body: Optional[bytes] = None
        if json is not None:
            body = _json.dumps(json).encode()
            if req_headers.get("Content-Type") is None:
                req_headers["Content-Type"] = "application/json"
        elif data is not None:
            body = data if isinstance(data, bytes) else data.encode()

        if body is not None:
            lib.curl_easy_setopt(curl, CurlOpt.POSTFIELDS, body)
            if method == "GET":
                method = "POST"

        if method != "GET":
            lib.curl_easy_setopt(curl, CurlOpt.CUSTOMREQUEST, method.encode())

        for name, value in req_headers.multi_items():
            line = f"{name}: {value}" if value is not None else f"{name}:"
            header_slist = ctypes.c_void_p(
                lib.curl_slist_append(header_slist, line.encode())
            )
        if header_slist.value:
            lib.curl_easy_setopt(curl, CurlOpt.HTTPHEADER, header_slist)

        body_buf = bytearray()
        write_cb = _binding.make_buffer_callback(body_buf)
        lib.curl_easy_setopt(curl, CurlOpt.WRITEFUNCTION, write_cb)

        header_buf = bytearray()
        header_cb = _binding.make_buffer_callback(header_buf)
        lib.curl_easy_setopt(curl, CurlOpt.HEADERFUNCTION, header_cb)

        if impersonate:
            target = resolve_latest_browser_type(impersonate)
            ret = lib.curl_easy_impersonate(curl, target.encode(), 1)
            if ret != 0:
                raise RuntimeError(f"curl_easy_impersonate failed: CURLcode {ret}")

        ret = lib.curl_easy_perform(curl)
        if ret != 0:
            raise RuntimeError(f"curl_easy_perform failed: CURLcode {ret}")

        status_code = ctypes.c_long()
        lib.curl_easy_getinfo(curl, CurlInfo.RESPONSE_CODE, ctypes.byref(status_code))

        response_headers = Headers(
            [
                line
                for line in header_buf.decode("ascii", "replace").split("\r\n")
                if ":" in line
            ]
        )

        return Response(status_code.value, response_headers, bytes(body_buf))
    finally:
        if header_slist.value:
            lib.curl_slist_free_all(header_slist)
