from typing import Literal

BrowserTypeLiteral = Literal[
    "edge99",
    "edge101",
    "chrome99",
    "chrome100",
    "chrome101",
    "chrome104",
    "chrome107",
    "chrome110",
    "chrome116",
    "chrome119",
    "chrome120",
    "chrome123",
    "chrome124",
    "chrome131",
    "chrome133a",
    "chrome136",
    "chrome142",
    "chrome145",
    "chrome146",
    "chrome150",
    "chrome99_android",
    "chrome131_android",
    "safari153",
    "safari155",
    "safari170",
    "safari172_ios",
    "safari180",
    "safari180_ios",
    "safari184",
    "safari184_ios",
    "safari260",
    "safari2601",
    "safari260_ios",
    "firefox133",
    "firefox135",
    "firefox144",
    "firefox147",
    "tor145",
    "chrome",
    "edge",
    "safari",
    "safari_ios",
    "safari_beta",
    "safari_ios_beta",
    "chrome_android",
    "firefox",
    "safari15_3",
    "safari15_5",
    "safari17_0",
    "safari17_2_ios",
    "safari18_0",
    "safari18_0_ios",
    "safari18_4",
    "safari18_4_ios",
]


DEFAULT_CHROME = "chrome150"
DEFAULT_EDGE = "edge101"
DEFAULT_SAFARI = "safari2601"
DEFAULT_SAFARI_IOS = "safari260_ios"
DEFAULT_SAFARI_BETA = "safari2601"
DEFAULT_SAFARI_IOS_BETA = "safari260_ios"
DEFAULT_CHROME_ANDROID = "chrome131_android"
DEFAULT_FIREFOX = "firefox147"
DEFAULT_TOR = "tor145"


REAL_TARGET_MAP = {
    "chrome": "chrome150",
    "edge": "edge101",
    "safari": "safari2601",
    "safari_ios": "safari260_ios",
    "safari_beta": "safari2601",
    "safari_ios_beta": "safari260_ios",
    "chrome_android": "chrome131_android",
    "firefox": "firefox147",
    "tor": "tor145",
}


def resolve_latest_browser_type(item):
    if item == "chrome":  # noqa: SIM116
        return DEFAULT_CHROME
    elif item == "edge":
        return DEFAULT_EDGE
    elif item == "safari":
        return DEFAULT_SAFARI
    elif item == "safari_ios":
        return DEFAULT_SAFARI_IOS
    elif item == "safari_beta":
        return DEFAULT_SAFARI_BETA
    elif item == "safari_ios_beta":
        return DEFAULT_SAFARI_IOS_BETA
    elif item == "chrome_android":
        return DEFAULT_CHROME_ANDROID
    elif item == "firefox":
        return DEFAULT_FIREFOX
    elif item == "tor":
        return DEFAULT_TOR
    else:
        return item
