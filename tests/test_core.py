from pydantic import InvalidLengthForBrand
import pytest
from pytest import raises

from mps060602 import MPS060602, ADSampleRate
from mps060602.core import MPS060602Para
from mps060602.errors import (
    ADSampleRateOutOfRange,
    ADSampleRateRoundToNearest1000,
    InvalidDeviceNumber,
    OpenDeviceFailed,
    ConfigureDeviceFailed,
)

__author__ = "Ofey Chan"
__copyright__ = "Ofey Chan"
__license__ = "MIT"


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


def test_MPS060602():
    # __init__():
    with raises(InvalidDeviceNumber):
        MPS060602(-1)
    with raises(InvalidDeviceNumber):
        MPS060602(11)

    # configure():
    card = MPS060602(0)
    card.device.handle = -1  # Hack: Pollute the handle.
    with raises(ConfigureDeviceFailed):
        card.configure(MPS060602Para())

    card = MPS060602(0)
    card.configure(MPS060602Para())
            