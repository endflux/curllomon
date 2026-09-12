import ctypes
from typing import Any, Optional, Union

from . import _binding
from ._request import perform
from .headers import Headers, HeaderTypes
from .impersonate import BrowserTypeLiteral
from .response import Response
from .session import Session

lib = _binding.lib

__all__ = ["request", "Response", "Headers", "BrowserTypeLiteral", "Session"]


def request(
    url: str,
    method: str = "GET",
    headers: Optional[HeaderTypes] = None,
    json: Optional[Any] = None,
    data: Optional[Union[bytes, str]] = None,
    impersonate: Optional["BrowserTypeLiteral"] = None,
) -> Response:
    """Perform one HTTP request and return a Response.

    One curl handle, created and torn down for this single call. For
    connection/handle reuse across multiple requests, use `Session`.
    """
    curl = ctypes.c_void_p(lib.curl_easy_init())
    if not curl.value:
        raise RuntimeError("curl_easy_init() failed")
    try:
        return perform(curl, url, method, headers, json, data, impersonate)
    finally:
        lib.curl_easy_cleanup(curl)
