import pytest

from mps060602 import MPS01602

__author__ = "Ofey Chan"
__copyright__ = "Ofey Chan"
__license__ = "MIT"


def test_MPS():
    """API Tests"""
    m = MPS01602()
    assert m.hello() == "hello"
