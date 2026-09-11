"""Session: reuses one curl handle across requests.

Ports curl_cffi's Session (curl_cffi/requests/session.py) — the piece
vistion.md's "perserv og sesstion magement" line asks to preserve — trimmed
to what that means at this project's scale: one curl handle reused across
calls instead of curl_easy_init/curl_easy_cleanup per call.

Kept, mirroring the original's structure directly:
  - close() / __enter__ / __exit__          (session.py ~588-596)
  - session-level default headers            (session.py's `headers` __init__ param)
  - request() dispatching to the verb methods, and the verb methods
    themselves (head/get/post/put/patch/delete) each a one-line wrapper
    calling request(url, method=...)          (session.py ~945-966)
  - reset the handle after each call so the next call starts clean — the
    original's `c.reset()` in a `finally` block around _request_once
    (session.py ~848), wrapping `curl_easy_reset` (curl.py's `reset()`,
    ~653)

Dropped (not asked for by vision.md's other preserves either): thread-local
curl handles, cookies, auth, proxies, retries, base_url/params, response
caching, streaming, websockets, and the extra HTTP verbs (options/trace/
query) — `request(url, method=...)` already accepts any verb string.
"""

from typing import Any, Optional, Union

import ctypes

from . import _binding
from ._request import perform
from .headers import Headers, HeaderTypes
from .impersonate import BrowserTypeLiteral
from .response import Response

lib = _binding.lib


class Session:
    """A request session: the curl handle (and default headers/impersonate) are reused."""

    def __init__(
        self,
        headers: Optional[HeaderTypes] = None,
        impersonate: Optional["BrowserTypeLiteral"] = None,
    ) -> None:
        self._curl = ctypes.c_void_p(lib.curl_easy_init())
        if not self._curl.value:
            raise RuntimeError("curl_easy_init() failed")
        self.headers = Headers(headers)
        self.impersonate = impersonate
        self._closed = False

    @property
    def curl(self) -> "ctypes.c_void_p":
        return self._curl

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the session."""
        if not self._closed:
            lib.curl_easy_cleanup(self._curl)
            self._closed = True

    def request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[HeaderTypes] = None,
        json: Optional[Any] = None,
        data: Optional[Union[bytes, str]] = None,
        impersonate: Optional["BrowserTypeLiteral"] = None,
    ) -> Response:
        if self._closed:
            raise RuntimeError("Session is closed")

        req_headers = self.headers.copy()
        if headers:
            req_headers.update(Headers(headers))

        try:
            return perform(
                self._curl,
                url,
                method,
                req_headers,
                json,
                data,
                impersonate if impersonate is not None else self.impersonate,
            )
        finally:
            lib.curl_easy_reset(self._curl)

    def head(self, url: str, **kwargs: Any) -> Response:
        return self.request(url, method="HEAD", **kwargs)

    def get(self, url: str, **kwargs: Any) -> Response:
        return self.request(url, method="GET", **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        return self.request(url, method="POST", **kwargs)

    def put(self, url: str, **kwargs: Any) -> Response:
        return self.request(url, method="PUT", **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Response:
        return self.request(url, method="PATCH", **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        return self.request(url, method="DELETE", **kwargs)
