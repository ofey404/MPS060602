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
    """Mode to select input AD channel.

    In ``in1_and_2`` mode:

    * ``MPS060602.buffer[0::2]`` are data from ``In1``.
    * ``MPS060602.buffer[1::2]`` are data from ``In2``.

    In ``difference`` mode, :func:`MPS060602.data_in` put
    voltage difference of ``In1`` and ``In2`` into buffer.
    """

    forbid = 0
    in1 = 1
    in2 = 2
    in1_and_2 = 3
    difference = 4


class PGAAmpRate(Enum):
    """Information to control on board Programmable Gain Amplifier (PGA).

    ``range_10V = (0, 10)`` (index, volt):

    * ``index`` would be passed to DLL function``MPS_Configure``, which is
    handled in :func:`MPS060602.configure_and_update_state`.

    * ``volt`` is the corresponding volt range of the ``index``, used to
    convert raw data to voltage in :func:`MPS060602.to_volt`.
    """

    range_10V = (0, 10)
    range_5V = (1, 5)
    range_2V = (2, 2)
    range_1v = (3, 1)

    def __init__(self, index, volt) -> None:
        self.index = index
        self.volt = volt


class MPS060602Para:
    """Configuration parameters of MPS060602 acquisition card.

    Args:
        ADChannel (ADChannelMode, optional): Input AD channel mode.Defaults to ADChannelMode.in1_and_2.
        ADSampleRate (int, optional): Sample rate, should be in [1000, 450000], rounded to closest 1000. Defaults to 1000.
        Gain (PGAAmpRate, optional): On board gain amplifier mode. Defaults to PGAAmpRate.range_10V.

    Raises:
        ADSampleRateOutOfRange: Given invalid AD sample rate.
        ADSampleRateRoundToNearest1000: Given sample rate doesn't round to 1000.
    """

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
    """Python wrapper for MPS060602 acquisition card.

    Args:
        para (MPS060602Para): Configuration parameters for MPS060602 card.
        device_number (int, optional): Device number of card, int in [0, 9]. Defaults to 0.
        buffer_size (int, optional): Data buffer size for :func:`MPS060602.data_in`. Defaults to 1024.

    Raises:
        InvalidDeviceNumber: Given invliad ``device_number``.
    """

    @dataclass
    class __Device:
        handle: HANDLE
        number: int

    @dataclass
    class __InternalState:
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
        self.state = self.__InternalState()
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

    def __open_device(self, device_number: int) -> __Device:
        all_bit_1 = sum([1 << i for i in range(sizeof(HANDLE) * 8)])
        failed = lambda handle: handle == all_bit_1

        handle = self.dll.MPS_OpenDevice(device_number)
        if failed(handle):
            raise OpenDeviceFailed(device_number)
        return self.__Device(handle, device_number)

    def configure_and_update_state(self, para: MPS060602Para):
        """Configure MPS060602 card and update the internal object state.

        Args:
            para (MPS060602Para): Parameters.

        Raises:
            ConfigureDeviceFailed: Failed to run configuration function.
        """
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
        """Start card.

        Raises:
            DeviceStartFailed: Failed to start card.
        """
        failed = lambda res: res == 0
        if failed(self.__start_raw(self.device.handle)):
            raise DeviceStartFailed(self.device.number)
        self.state.started = True

    def __start_raw(self, handle: HANDLE) -> c_int:
        return self.dll.MPS_Start(handle)

    def data_in(self, sample_number: int = None) -> Iterable[c_ushort]:
        """Read ``sample_number`` of data, to ``MPS060602.buffer`` of this object.

        Args:
            sample_number (int, optional): Sample number, when None is given, use buffer size. Defaults to None.

        Raises:
            DataInFailed: Failed to run DataIn function in DLL.

        Returns:
            Iterable[c_ushort]: A slice of internal data buffer, length is ``sample_umber``.
        """
        if not sample_number:
            sample_number = len(self.buffer)
        failed = lambda res: res == 0
        if failed(self.__data_in_raw(self.buffer, sample_number, self.device.handle)):
            raise DataInFailed(self.device.number)
        return self.buffer[0:sample_number]

    def to_volt(self, data: c_ushort) -> float:
        """Convert internal ushort data to volt: (1 - (data / 65536) * 2) * volt_range

        Args:
            data (c_ushort): Internal ushort data.

        Returns:
            float: Voltage value.
        """
        volt_range = self.state.parameter.Gain.volt
        return (1 - (data / 65536) * 2) * volt_range

    def read_to_volt(self, sample_number: int = None) -> Iterable[float]:
        """Read ``sample_number`` of data, convert to voltage, and return 
        a immutable iterable.

        Args:
            sample_number (int, optional): Sample number, when None is given,
            use buffer size. Defaults to None.

        Returns:
            Iterable[float]: Immutable copy of data, converted to volt.
        """
        buffer = self.data_in(sample_number)
        return tuple(self.to_volt(i) for i in buffer)

    def __data_in_raw(self, DataBuffer, SampleNumber, DeviceHandle) -> c_int:
        # TODO: async this.
        if not self.state.started:
            raise DeviceNotStarted(self.device.number)
        return self.dll.MPS_DataIn(DataBuffer, SampleNumber, DeviceHandle)

    def suspend(self):
        """Suspend the board. During suspending, :func:`MPS060602.data_in`
        cannot be called.
        
        Use :func:`MPS060602.start` to start it again.

        Raises:
            DeviceStopFailed: Failed to suspend the device.
        """
        failed = lambda res: res == 0
        if failed(self.__stop_raw(self.device.handle)):
            raise DeviceStopFailed(self.device.number)
        self.state.started = False

    def __stop_raw(self, handle: HANDLE) -> c_int:
        return self.dll.MPS_Stop(handle)

    def close(self):
        """Close the board.

        Raises:
            DeviceCloseFailed: Failed to close the device
        """
        failed = lambda res: res == 0
        if failed(self.__close_raw(self.device.handle)):
            raise DeviceCloseFailed(self.device.number)
        self.state.started = False

    def __close_raw(self, handle: HANDLE) -> c_int:
        return self.dll.MPS_CloseDevice(handle)
