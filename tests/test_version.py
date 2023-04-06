from hotbox import __version__


async def test_version() -> None:
    assert __version__ is not None
