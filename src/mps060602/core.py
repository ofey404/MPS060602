import platform
from ctypes import cdll, c_int
from ctypes.wintypes import HANDLE
from pathlib import Path
from enum import IntEnum

from dataclasses import dataclass

from .errors import (
    ADSampleRateOutOfRange,
    ADSampleRateRoundToNearest1000,
    OpenDeviceFailed,
    ConfigureDeviceFailed,
    InvalidDeviceNumber,
)


def is_os_64bit() -> bool:
    return platform.machine().endswith("64")


def inpackage_dll_path() -> str:
    filename = "MPS-060602.dll"
    if is_os_64bit:
        filename = "MPS-060602x64.dll"
    return str(Path(__file__).parent / "static" / filename)


class ADChannelMode(IntEnum):
    forbid = 0
    in1 = 1
    in2 = 2
    in1_and_2 = 3
    difference = 4


class PGAAmpRate(IntEnum):
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
    ADChannel: ADChannelMode = ADChannelMode.in1_and_2
    ADSampleRate: ADSampleRate = ADSampleRate(1000)
    Gain: PGAAmpRate = PGAAmpRate.range_10V


class MPS060602:
    @dataclass
    class Device:
        handle: HANDLE
        number: int

    def __init__(self, device_number: int = 0) -> None:
        invalid = lambda dn: dn < 0 or dn > 9
        if invalid(device_number):
            raise InvalidDeviceNumber(device_number)
        self.dll = cdll.LoadLibrary(inpackage_dll_path())
        self.__init_dll_wrappers()
        self.device = self.__open_device(device_number)

    def __init_dll_wrappers(self):
        self.dll.MPS_OpenDevice.argtypes = (c_int,)
        self.dll.MPS_OpenDevice.restype = HANDLE

        self.dll.MPS_Configure.argtypes = (c_int, c_int, c_int, HANDLE)
        self.dll.MPS_Configure.restype = c_int

    def __open_device(self, device_number: int) -> Device:
        failed = lambda handle: handle == -1
        handle = self.dll.MPS_OpenDevice(device_number)
        if failed(handle):
            raise OpenDeviceFailed(device_number)
        return self.Device(handle, device_number)

    def configure(self, para: MPS060602Para):
        failed = lambda res: res == 0
        if failed(
            self.__configure_raw(
                para.ADChannel,
                para.ADSampleRate,
                para.Gain,
                self.device.handle,
            )
        ):
            raise ConfigureDeviceFailed(self.device.number)

    def __configure_raw(self, ADChannel, ADSampleRate, Gain, DeviceHandle):
        return self.dll.MPS_Configure(ADChannel, ADSampleRate, Gain, DeviceHandle)
