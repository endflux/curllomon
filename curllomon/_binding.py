import ctypes
import json
import platform
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIBS_JSON = ROOT / "libs.json"
IMPERSONATE_LIBDIR = ROOT / "impersonate_libdir"

CURL_GLOBAL_ALL = 3


def _detect_arch() -> dict:
    """Match this machine against libs.json's per-platform table.

    Same matching rule as scripts/build.py's detect_arch(): system + machine
    + pointer size, plus libc flavor (glibc/musl) when the entry specifies
    one.
    """
    with open(LIBS_JSON) as f:
        archs = json.load(f)

    uname = platform.uname()
    glibc_flavor = "gnueabihf" if uname.machine in ("armv7l", "armv6l") else "gnu"
    libc_name, _ = platform.libc_ver()
    libc = glibc_flavor if libc_name == "glibc" else "musl"
    pointer_size = struct.calcsize("P") * 8

    for arch in archs:
        if (
            arch["system"] == uname.system
            and arch["machine"] == uname.machine
            and arch["pointer_size"] == pointer_size
            and ("libc" not in arch or arch.get("libc") == libc)
        ):
            return arch

    raise RuntimeError(f"Unsupported arch in {LIBS_JSON}: {uname}")


def _resolve_libdir(arch: dict) -> Path:
    """Directory to look for this arch's binary in.

    libs.json entries may carry a "libdir" (e.g. "~/.local/bin/") naming
    where that platform's binary should be installed; relative paths are
    resolved against the package root, `~` is expanded against the home
    directory. Entries with no "libdir" fall back to the bundled
    impersonate_libdir/.
    """
    libdir = arch.get("libdir")
    if libdir is None:
        return IMPERSONATE_LIBDIR
    path = Path(libdir).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path


def _find_dylib() -> str:
    arch = _detect_arch()
    name = arch["obj_name"]
    libdir = _resolve_libdir(arch)
    path = libdir / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. libs.json matched this machine to "
            f"{arch['system']}/{arch['machine']} ({name}), but {libdir} "
            "doesn't have it. Build/download the matching libcurl-impersonate "
            f"binary and drop it in {libdir} to support this platform."
        )
    return str(path)


lib = ctypes.CDLL(_find_dylib())

lib.curl_global_init.argtypes = [ctypes.c_long]
lib.curl_global_init.restype = ctypes.c_int

lib.curl_easy_init.argtypes = []
lib.curl_easy_init.restype = ctypes.c_void_p

lib.curl_easy_setopt.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.curl_easy_setopt.restype = ctypes.c_int

lib.curl_easy_getinfo.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.curl_easy_getinfo.restype = ctypes.c_int

lib.curl_easy_perform.argtypes = [ctypes.c_void_p]
lib.curl_easy_perform.restype = ctypes.c_int

lib.curl_easy_cleanup.argtypes = [ctypes.c_void_p]
lib.curl_easy_cleanup.restype = None

lib.curl_easy_impersonate.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
lib.curl_easy_impersonate.restype = ctypes.c_int

# void curl_easy_reset(void *curl);
lib.curl_easy_reset.argtypes = [ctypes.c_void_p]
lib.curl_easy_reset.restype = None

lib.curl_slist_append.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lib.curl_slist_append.restype = ctypes.c_void_p

lib.curl_slist_free_all.argtypes = [ctypes.c_void_p]
lib.curl_slist_free_all.restype = None

lib.curl_global_init(CURL_GLOBAL_ALL)

WRITEFUNC = ctypes.CFUNCTYPE(
    ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_void_p
)


def make_buffer_callback(buf: bytearray) -> "ctypes._FuncPointer":
    """Build a WRITEFUNC that appends incoming bytes to `buf`."""

    def _write(ptr, size, nmemb, userdata):
        n = size * nmemb
        buf.extend(ctypes.string_at(ptr, n))
        return n

    return WRITEFUNC(_write)
