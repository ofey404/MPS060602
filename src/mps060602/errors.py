class MPS060602Error(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ADSampleRateOutOfRange(MPS060602Error):
    def __init__(self, sample_rate, *args: object) -> None:
        message = "AD sample rate out of range, given {}.".format(sample_rate)
        super().__init__(message, *args)


class ADSampleRateRoundToNearest1000(MPS060602Error):
    def __init__(self, sample_rate, *args: object) -> None:
        message = "AD sample rate would rounded to nearest 1000, given {}.".format(
            sample_rate
        )
        super().__init__(message, *args)

class InvalidDeviceNumber(MPS060602Error):
    def __init__(self, device_number: int, *args: object) -> None:
        message = "Invalid device number {}, should be in [0, 9].".format(device_number)
        super().__init__(message, *args)
    

class OpenDeviceFailed(MPS060602Error):
    def __init__(self, device_number: int, *args: object) -> None:
        message = "Open device failed, given device number {}.".format(device_number)
        super().__init__(message, *args)

class ConfigureDeviceFailed(MPS060602Error):
    def __init__(self, device_number: int, *args: object) -> None:
        message = "Configure device failed, device number {}.".format(device_number)
        super().__init__(message, *args)
    