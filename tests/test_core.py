import pytest

from mps060602 import MPS060602, ADSampleRate
from mps060602.core import ADSampleRateOutOfRange, ADSampleRateRoundToNearest1000

__author__ = "Ofey Chan"
__copyright__ = "Ofey Chan"
__license__ = "MIT"


def test_MPS():
    """API Tests"""
    m = MPS060602()
    assert m.hello() == "hello"


def test_ADSampleRate():
    assert ADSampleRate(1000) == 1000, "ADSampleRate should interoperate with int"
    with pytest.raises(ADSampleRateOutOfRange):
        ADSampleRate(-1)
    with pytest.raises(ADSampleRateOutOfRange):
        ADSampleRate(450001)
    with pytest.raises(ADSampleRateRoundToNearest1000):
        ADSampleRate(449999)
    assert ADSampleRate(449999, allow_not_allign_to_1000=True) == 449999
