import json
import sys
import uuid
from datetime import date, datetime
from typing import Any, Dict

from typer import FileText

from hotbox.types import Language


def handle_filetext(filetext: FileText) -> Dict:
    if hasattr(filetext, "read"):
        content = filetext.read().encode("utf-8")
    if filetext == "-":
        content = sys.stdin.buffer.read()
    if isinstance(filetext, str):
        content = filetext.encode("utf-8")
    else:
        raise TypeError(f"Unsupported filetext type: {type(filetext)}")
    return json.loads(content)


def json_serializer(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def generate_app_id() -> str:
    return f"app-{uuid.uuid4().hex}"


def determine_lang(app_code_path: str) -> Language:
    # recursively go through files and if the extension of the file is is
    # in the Langugae enum, return that language
    pass
