from dataquery_processor import pathutils
from pathvalidate import ValidationError
import pytest


def test_sanitise_filename():
    assert pathutils.sanitise_filename("order 66/evil/../path") == 'order 66evil..path'
    assert pathutils.sanitise_filename("/root/") == 'root'


def test_sanitise_filename_numbers_only():
    assert pathutils.sanitise_filename("11988") == '11988'


def test_sanitise_invalid_filename():
    with pytest.raises(ValidationError):
        pathutils.sanitise_filename("/")