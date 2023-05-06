import json
import os
import sys
from typing import Dict, Optional

from hotbox._types import Language


def handle_filetext(filetext: str) -> Dict:
    if os.path.isfile(filetext):
        with open(filetext, "r") as f:
            content = f.read().encode("utf-8")
    elif filetext == "-":
        content = sys.stdin.buffer.read()
    else:
        content = filetext.encode("utf-8")
    return json.loads(content)


def determine_lang(app_code_path: str) -> Optional[Language]:
    for _, _, filenames in os.walk(app_code_path):
        for filename in filenames:
            lang = os.path.splitext(filename)[-1].split(".")[-1]
            if lang in list(Language):
                return Language(lang)
    return None
