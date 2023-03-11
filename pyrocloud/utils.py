import json
import sys
from datetime import date, datetime
from typing import Any, Dict

from typer import FileText


def handle_spec(spec: FileText) -> Dict:
    if hasattr(spec, "read"):
        content = spec.read().encode("utf-8")
    if spec == "-":
        content = sys.stdin.buffer.read()
    if isinstance(spec, str):
        content = spec.encode("utf-8")
    else:
        raise TypeError(f"Unsupported spec type: {type(spec)}")
    return json.loads(content)


def json_serializer(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))
