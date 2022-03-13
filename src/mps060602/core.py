import platform
from ctypes import cdll
from pathlib import Path
from enum import Enum

from dataclasses import dataclass


def is_os_64bit() -> bool:
    return platform.machine().endswith("64")


def inpackage_dll_path() -> str:
    filename = "MPS-060602.dll"
    if is_os_64bit:
        filename = "MPS-060602x64.dll"
    return str(Path(__file__).parent / "static" / filename)


class MPS060602Error(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ADSampleRateOutOfRange(MPS060602Error):
    def __init__(self, sample_rate, *args: object) -> None:
        message = "AD sample rate out of range, given {}".format(sample_rate)
        super().__init__(message, *args)


class ADSampleRateRoundToNearest1000(MPS060602Error):
    def __init__(self, sample_rate, *args: object) -> None:
        message = "AD sample rate would rounded to nearest 1000, given {}".format(
            sample_rate
        )
        super().__init__(message, *args)


class ADChannelMode(Enum):
    forbid = 0
    in1 = 1
    in2 = 2
    in1_and_2 = 3
    difference = 4


class PGAAmpRate(Enum):
    range_10V = 0
    range_5V = 1
    range_2V = 2
    range_1v = 3


class ADSampleRate(int):
    def __new__(cls, rate, allow_not_allign_to_1000=False):
        int_rate = super().__new__(cls, rate)
        if int_rate < 1000 or int_rate > 450000:
            raise ADSampleRateOutOfRange(rate)
        if not allow_not_allign_to_1000 and int_rate % 1000 != 0:
            raise ADSampleRateRoundToNearest1000(rate)
        return int_rate


@dataclass
class MPS060602Para:
    ADChannel: ADChannelMode
    ADSampleRate: ADSampleRate
    Gain: PGAAmpRate


class MPS060602:
    def __init__(self, device_number: int = 0) -> None:
        dll_path = inpackage_dll_path()
        self.dll = cdll.LoadLibrary(dll_path)
        self.handle = self.__open_device(device_number=device_number)

    def __open_device(self, device_number: int):
        pass

    def configure(self):
        pass

    def hello(self) -> str:
        return "hello"
