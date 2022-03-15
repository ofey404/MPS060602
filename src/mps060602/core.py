import platform
from ctypes import POINTER, c_int, c_ushort, cdll, sizeof
from ctypes.wintypes import HANDLE
from typing import Iterable
from dataclasses import dataclass
from enum import IntEnum, Enum
from pathlib import Path

from .errors import (
    ADSampleRateOutOfRange,
    ADSampleRateRoundToNearest1000,
    ConfigureDeviceFailed,
    DataInFailed,
    DeviceCloseFailed,
    DeviceNotStarted,
    DeviceStartFailed,
    DeviceStopFailed,
    InvalidDeviceNumber,
    OpenDeviceFailed,
)


def _is_os_64bit() -> bool:
    return platform.machine().endswith("64")


def _inpackage_dll_path() -> str:
    filename = "MPS-060602.dll"
    if _is_os_64bit:
        filename = "MPS-060602x64.dll"
    return str(Path(__file__).parent / "static" / filename)


class ADChannelMode(IntEnum):
    forbid = 0
    in1 = 1
    in2 = 2
    in1_and_2 = 3
    difference = 4


class PGAAmpRate(Enum):
    range_10V = (0, 10)  # (index, volt)
    range_5V = (1, 5)
    range_2V = (2, 2)
    range_1v = (3, 1)

    def __init__(self, index, volt) -> None:
        self.index = index
        self.volt = volt


class MPS060602Para:
    def __init__(
        self,
        ADChannel: ADChannelMode = ADChannelMode.in1_and_2,
        ADSampleRate: int = 1000,
        Gain: PGAAmpRate = PGAAmpRate.range_10V,
    ) -> None:
        self.ADChannel: ADChannelMode = ADChannel
        self.Gain: PGAAmpRate = Gain

        if ADSampleRate < 1000 or ADSampleRate > 450000:
            raise ADSampleRateOutOfRange(ADSampleRate)
        if ADSampleRate % 1000 != 0:
            raise ADSampleRateRoundToNearest1000(ADSampleRate)
        self.ADSampleRate = ADSampleRate


class MPS060602:
    @dataclass
    class Device:
        handle: HANDLE
        number: int

    @dataclass
    class InternalState:
        parameter: MPS060602Para = None
        started: bool = False

    def __init__(
        self, para: MPS060602Para, device_number: int = 0, buffer_size: int = 1024
    ) -> None:
        invalid = lambda dn: dn < 0 or dn > 9
        if invalid(device_number):
            raise InvalidDeviceNumber(device_number)

        self.dll = cdll.LoadLibrary(_inpackage_dll_path())
        self.__init_dll_wrappers()

        self.device = self.__open_device(device_number)
        self.buffer = (c_ushort * buffer_size)()
        self.state = self.InternalState()
        self.configure_and_update_state(para)

    def __init_dll_wrappers(self):
        # TODO: Refactor with self.dll.__getitem__()
        self.dll.MPS_OpenDevice.argtypes = (c_int,)
        self.dll.MPS_OpenDevice.restype = HANDLE

        self.dll.MPS_Configure.argtypes = (c_int, c_int, c_int, HANDLE)
        self.dll.MPS_Configure.restype = c_int

        self.dll.MPS_Start.argtypes = (HANDLE,)
        self.dll.MPS_Start.restype = c_int

        self.dll.MPS_DataIn.argtypes = (POINTER(c_ushort), c_int, HANDLE)
        self.dll.MPS_DataIn.restype = c_int

        self.dll.MPS_Stop.argtypes = (HANDLE,)
        self.dll.MPS_Stop.restype = c_int

        self.dll.MPS_CloseDevice.argtypes = (HANDLE,)
        self.dll.MPS_CloseDevice.restype = c_int

    def __open_device(self, device_number: int) -> Device:
        all_bit_1 = sum([1 << i for i in range(sizeof(HANDLE) * 8)])
        failed = lambda handle: handle == all_bit_1

        handle = self.dll.MPS_OpenDevice(device_number)
        if failed(handle):
            raise OpenDeviceFailed(device_number)
        return self.Device(handle, device_number)

    def configure_and_update_state(self, para: MPS060602Para):
        failed = lambda res: res == 0
        if failed(
            self.__configure_raw(
                para.ADChannel,
                para.ADSampleRate,
                para.Gain.index,
                self.device.handle,
            )
        ):
            raise ConfigureDeviceFailed(self.device.number)
        self.state.parameter = para

    def __configure_raw(self, ADChannel, ADSampleRate, Gain, DeviceHandle) -> c_int:
        return self.dll.MPS_Configure(ADChannel, ADSampleRate, Gain, DeviceHandle)

    def start(self):
        failed = lambda res: res == 0
        if failed(self.__start_raw(self.device.handle)):
            raise DeviceStartFailed(self.device.number)
        self.state.started = True

    def __start_raw(self, handle: HANDLE) -> c_int:
        return self.dll.MPS_Start(handle)

    def data_in(self, sample_number: int = None) -> Iterable[c_ushort]:
        if not sample_number:
            sample_number = len(self.buffer)
        failed = lambda res: res == 0
        if failed(self.__data_in_raw(self.buffer, sample_number, self.device.handle)):
            raise DataInFailed(self.device.number)
        return self.buffer[0:sample_number]

    def to_volt(self, data: c_ushort) -> float:
        volt_range = self.state.parameter.Gain.volt
        return (1 - (data / 65536) * 2) * volt_range

    def read_to_volt(self, sample_number: int = None) -> Iterable[float]:
        buffer = self.data_in(sample_number)
        return (self.to_volt(i) for i in buffer)

    def __data_in_raw(self, DataBuffer, SampleNumber, DeviceHandle) -> c_int:
        # TODO: async this.
        if not self.state.started:
            raise DeviceNotStarted(self.device.number)
        return self.dll.MPS_DataIn(DataBuffer, SampleNumber, DeviceHandle)

    def stop(self):
        failed = lambda res: res == 0
        if failed(self.__stop_raw(self.device.handle)):
            raise DeviceStopFailed(self.device.number)
        self.state.started = False

    def __stop_raw(self, handle: HANDLE) -> c_int:
        return self.dll.MPS_Stop(handle)

    def close(self):
        failed = lambda res: res == 0
        if failed(self.__close_raw(self.device.handle)):
            raise DeviceCloseFailed(self.device.number)
        self.state.started = False

    def __close_raw(self, handle: HANDLE) -> c_int:
        return self.dll.MPS_CloseDevice(handle)
