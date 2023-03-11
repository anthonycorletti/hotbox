import os

from pyrocloud.main import foo


def test_timezone() -> None:
    assert foo() == "foo"
    assert os.environ["TZ"] == "UTC"
