"""Traducción al inglés: junta traduccion/es.json (hash → español) con
traduccion/en_*.py (hash → inglés). Ver traduccion/extraer.py."""

import glob
import json
import os

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "traduccion")
EN = {}
with open(os.path.join(_DIR, "es.json"), encoding="utf-8") as _f:
    _ES = json.load(_f)
for _arch in sorted(glob.glob(os.path.join(_DIR, "en_*.py"))):
    _mod = {}
    with open(_arch, encoding="utf-8") as _f:
        exec(_f.read(), _mod)
    for _k, _v in _mod["T"].items():
        if _k in _ES:
            EN[_ES[_k]] = _v
    EN.update(_mod.get("L", {}))
