from ctypes import *
from ctypes.wintypes import *

import pytest
from mps060602 import MPS060602
from mps060602.core import MPS060602Para
from mps060602.errors import (
    ADSampleRateOutOfRange,
    ADSampleRateRoundToNearest1000,
    ConfigureDeviceFailed,
    InvalidDeviceNumber,
    OpenDeviceFailed,
)
from pytest import raises

__author__ = "Ofey Chan"
__copyright__ = "Ofey Chan"
__license__ = "MIT"

# Now we just manually tune this, and plug our device on for testing.
# unplugged = True
unplugged = False


def test_MPS():
    """API Tests"""
    MPS060602(MPS060602Para())


def test_MPS060602Para():
    with raises(ADSampleRateOutOfRange):
        MPS060602Para(ADSampleRate=-1)
    with raises(ADSampleRateOutOfRange):
        MPS060602Para(ADSampleRate=450001)
    with raises(ADSampleRateRoundToNearest1000):
        MPS060602Para(ADSampleRate=449999)


def MPS060602_init_plugged():
    para = MPS060602Para()
    with raises(InvalidDeviceNumber):
        MPS060602(para, device_number=-1)
    with raises(InvalidDeviceNumber):
        MPS060602(para, device_number=-1)
    MPS060602(para, device_number=0)


def MPS060602_init_unplugged():
    with raises(OpenDeviceFailed):
        MPS060602(MPS060602Para(), device_number=0)


def MPS060602_configure():
    para = MPS060602Para()
    card = MPS060602(para, device_number=0)
    card.device.handle = -1  # Hack: Pollute the handle.
    with raises(ConfigureDeviceFailed):
        card.configure_and_update_state(MPS060602Para())

    card = MPS060602(para, device_number=0)
    card.configure_and_update_state(MPS060602Para())


def test_by_plug_status():
    if unplugged:
        MPS060602_init_unplugged()
        return
    MPS060602_init_plugged()
    MPS060602_configure()
