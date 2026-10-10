#!/usr/bin/env python3
"""Extrae los textos en español del código para traducirlos.

    python3 traduccion/extraer.py            regenera traduccion/es.json
    python3 traduccion/extraer.py --faltan   lista lo que no tiene traducción

Cada texto se identifica por un hash corto de su contenido. Los f-strings se
guardan como plantillas con huecos {0}, {1}… (lo que llena cada hueco se
traduce aparte). Las traducciones viven en traduccion/en_*.py como
{hash: "texto en inglés"}; si cambias un texto en español, su hash cambia y
--faltan lo muestra.
"""

import ast
import glob
import hashlib
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "traduccion", "es.json")


def clave(texto):
    return hashlib.sha1(texto.encode("utf-8")).hexdigest()[:10]


def _plantilla(nodo):
    partes, i = [], 0
    for v in nodo.values:
        if isinstance(v, ast.Constant):
            partes.append(str(v.value).replace("{", "{{").replace("}", "}}"))
        else:
            partes.append("{%d}" % i)
            i += 1
    return "".join(partes)


def extraer():
    textos = {}
    for f in sorted(glob.glob(os.path.join(RAIZ, "*.py"))):
        nombre = os.path.basename(f)
        if nombre.startswith("en") and nombre[2:3] in ("", ".", "_"):
            continue
        arbol = ast.parse(open(f, encoding="utf-8").read())
        padres = {h: n for n in ast.walk(arbol) for h in ast.iter_child_nodes(n)}
        for n in ast.walk(arbol):
            s = None
            if isinstance(n, ast.JoinedStr):
                s = _plantilla(n)
            elif isinstance(n, ast.Constant) and isinstance(n.value, str) \
                    and not isinstance(padres.get(n), ast.JoinedStr):
                if isinstance(padres.get(n), ast.Expr):
                    continue                                   # docstrings
                s = n.value
            if not s or not re.search(r"[a-záéíóúñ]{2}", s, re.I):
                continue
            if re.fullmatch(r"[a-z0-9_]+", s) or (re.fullmatch(r"[\w./~-]+", s) and "/" in s):
                continue                                       # claves y rutas
            if s.startswith("[") and s.endswith("]{2}"):
                continue
            textos.setdefault(clave(s), dict(es=s, archivo=nombre))
    return textos


def traducidos():
    hechos = {}
    sys.path.insert(0, os.path.join(RAIZ, "traduccion"))
    for f in sorted(glob.glob(os.path.join(RAIZ, "traduccion", "en_*.py"))):
        mod = {}
        exec(open(f, encoding="utf-8").read(), mod)
        hechos.update(mod["T"])
        hechos.update({clave(k): v for k, v in mod.get("L", {}).items()})
    return hechos


if __name__ == "__main__":
    textos = extraer()
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump({k: v["es"] for k, v in textos.items()}, f, ensure_ascii=False, indent=0)
    hechos = traducidos()
    faltan = {k: v for k, v in textos.items() if k not in hechos}
    print(f"{len(textos)} textos · {len(textos) - len(faltan)} traducidos · {len(faltan)} faltan")
    if "--faltan" in sys.argv:
        arch = sys.argv[sys.argv.index("--faltan") + 1] if len(sys.argv) > sys.argv.index("--faltan") + 1 else None
        for k, v in faltan.items():
            if arch and v["archivo"] != arch:
                continue
            print(f"{k}\t{v['archivo']}\t{v['es']!r}")
