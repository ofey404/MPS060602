from ctypes import *
from ctypes.wintypes import *

import pytest
from mps060602 import MPS060602, ADSampleRate
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
    m = MPS060602()


def test_ADSampleRate():
    assert ADSampleRate(1000) == 1000, "ADSampleRate should interoperate with int"

    with raises(ADSampleRateOutOfRange):
        ADSampleRate(-1)
    with raises(ADSampleRateOutOfRange):
        ADSampleRate(450001)

    with raises(ADSampleRateRoundToNearest1000):
        ADSampleRate(449999)

    assert ADSampleRate(449999, allow_not_allign_to_1000=True) == 449999


def MPS060602_init_plugged():
    with raises(InvalidDeviceNumber):
        MPS060602(-1)
    with raises(InvalidDeviceNumber):
        MPS060602(11)
    MPS060602(0)


def MPS060602_init_unplugged():
    with raises(OpenDeviceFailed):
        m = MPS060602(0)


def MPS060602_configure():
    card = MPS060602(0)
    card.device.handle = -1  # Hack: Pollute the handle.
    with raises(ConfigureDeviceFailed):
        card.configure(MPS060602Para())

    card = MPS060602(0)
    card.configure(MPS060602Para())


def test_on_plug_status():
    if unplugged:
        MPS060602_init_unplugged()
    else:
        MPS060602_init_plugged()
        MPS060602_configure()
