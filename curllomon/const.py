from enum import IntEnum


class CurlOpt(IntEnum):
    """Subset of ``CURLOPT_`` constants, see:
    https://curl.se/libcurl/c/curl_easy_setopt.html"""

    WRITEDATA = 10000 + 1
    URL = 10000 + 2
    POSTFIELDS = 10000 + 15
    HTTPHEADER = 10000 + 23
    HEADERDATA = 10000 + 29
    CUSTOMREQUEST = 10000 + 36
    FOLLOWLOCATION = 0 + 52
    WRITEFUNCTION = 20000 + 11
    HEADERFUNCTION = 20000 + 79


class CurlInfo(IntEnum):
    """Subset of ``CURLINFO_`` constants, see:
    https://curl.se/libcurl/c/curl_easy_getinfo.html"""

    RESPONSE_CODE = 0x200000 + 2
