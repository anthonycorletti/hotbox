from hotbox.utils import _set_templates_home


async def test_set_templates_home_import_error() -> None:
    assert _set_templates_home().endswith("hotbox/templates")
