import re
from typing import Any, Optional

from .headers import Headers

CHARSET_RE = re.compile(r"charset=([\w-]+)")

JSON_NATIVE_ENCODINGS = {
    "utf-8",
    "utf8",
    "utf-8-sig",
    "utf-16",
    "utf16",
    "utf-16-be",
    "utf-16-le",
    "utf-16be",
    "utf-16le",
    "utf-32",
    "utf32",
    "utf-32-be",
    "utf-32-le",
    "utf-32be",
    "utf-32le",
}

from json import loads


class Response:
    """A minimal response wrapper: status code, headers, and content."""

    def __init__(
        self, status_code: int, headers: Headers, content: bytes
    ) -> None:
        self.status_code = status_code
        self.headers = headers
        self.content = content

    @property
    def charset_encoding(self) -> Optional[str]:
        """Return the encoding, as specified by the Content-Type header."""
        content_type = self.headers.get("Content-Type")
        if content_type:
            charset_match = CHARSET_RE.search(content_type)
            return charset_match.group(1) if charset_match else None
        return None

    @property
    def text(self) -> str:
        encoding = self.charset_encoding or "utf-8"
        return self.content.decode(encoding, errors="replace")

    def json(self, **kw) -> Any:
        """Return a parsed json object of the content."""
        charset_encoding = self.charset_encoding
        if charset_encoding is not None:
            encoding = charset_encoding.lower().replace("_", "-")
            if encoding not in JSON_NATIVE_ENCODINGS:
                return loads(self.text, **kw)
        return loads(self.content, **kw)
