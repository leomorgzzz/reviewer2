#!/usr/bin/env python3
"""Pruebas automáticas de Revisor 2 (no necesitan terminal ni curses).

    python3 pruebas/correr.py

Revisa lo que se rompió alguna vez y no se ve sin jugar:
  1. todos los módulos importan, en español y en inglés;
  2. traduccion/es.json está al día y todo texto tiene traducción;
  3. solo hay símbolos que la consola de Windows sabe dibujar (WGL4);
  4. toda cita apunta a una referencia que existe;
  5. el Revisor 2 y el protocolo funcionan en todos los casos;
  6. el código R exportado en inglés es el mismo que en español (si se
     traduce, deja de coincidir con el CSV de muestras y no corre).
Sale con código 1 si algo falla.
"""

import ast
import glob
import importlib
import json
import os
import random
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)

import wgl4  # noqa: E402

fallas = []


def revisar(nombre, condicion, detalle=""):
    print(("ok    " if condicion else "FALLA ") + nombre)
    if not condicion:
        fallas.append(nombre)
        if detalle:
            print("      " + str(detalle).replace("\n", "\n      "))


def modulos():
    return sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(RAIZ, "*.py"))
                  if not os.path.basename(f).startswith("revisor2"))


# ------------------------------------------------------------ 1. importar
for idioma_ in ("es", "en"):
    codigo = ("import sys; sys.argv = ['x', '--%s']\n"
              "import importlib\n"
              "for m in %r: importlib.import_module(m)\n") % (idioma_, modulos())
    r = subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, capture_output=True, text=True,
                       env=dict(os.environ, HOME=tempfile.mkdtemp()))
    revisar(f"los módulos importan ({idioma_})", r.returncode == 0, r.stderr[-1500:])

# ------------------------------------------------------- 2. traducciones
sys.argv = ["x", "--en"]
os.environ["HOME"] = tempfile.mkdtemp()
extraer = importlib.import_module("traduccion.extraer")
textos = extraer.extraer()
with open(os.path.join(RAIZ, "traduccion", "es.json"), encoding="utf-8") as f:
    guardado = json.load(f)
revisar("traduccion/es.json al día (corre: python3 traduccion/extraer.py)",
        guardado == {k: v["es"] for k, v in textos.items()})
hechos = extraer.traducidos()
faltan = [f"{v['archivo']}: {v['es'][:80]!r}" for k, v in textos.items() if k not in hechos]
revisar("todo texto tiene traducción al inglés", not faltan, "\n".join(faltan[:20]))

# ------------------------------------------------------------ 3. símbolos
malos = wgl4.revisar([RAIZ])
revisar("solo símbolos WGL4 (los que dibuja la consola de Windows)", not malos,
        "\n".join(f"{ch} U+{ord(ch):04X}  {' '.join(l[:3])}" for ch, l in sorted(malos.items())))

# -------------------------------------------------------------- 4. citas
import idioma  # noqa: E402
import casos  # noqa: E402
import datos  # noqa: E402
import expediente as X  # noqa: E402
import protocolo  # noqa: E402
import revisor  # noqa: E402
import simulacion as sim  # noqa: E402

idioma.cambiar = lambda i: None          # que las pruebas no cambien el idioma guardado
rotas = []
for f in glob.glob(os.path.join(RAIZ, "*.py")):
    for n in ast.walk(ast.parse(open(f, encoding="utf-8").read())):
        if isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) == "cita":
            for a in n.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    for r in a.value.split():
                        if r.partition(":")[0] not in datos._CORTOS:
                            rotas.append(f"{os.path.basename(f)}:{n.lineno}: {r}")
revisar("toda cita(...) del código existe en datos.FUENTES", not rotas, "\n".join(rotas))

# ------------------------------------------- 5. Revisor 2 y protocolo
errores, comentarios_rotos = [], []
carpeta = tempfile.mkdtemp()
protocolo.CARPETA = carpeta
for caso in casos.CASOS:
    for dif in revisor.DIFICULTADES:
        for formula in datos.FORMULAS:
            dis = dict(X.nuevo(caso)["dis"], formula=formula)
            try:
                res = sim.simular(dis, caso, random.Random(1))
                comentarios = revisor.revisar(dis, caso, res, dif)
                revisor.calificar(dis, caso, res, comentarios, dif)
                for c in comentarios:
                    for r in c["fuente"].split():
                        if r.partition(":")[0] not in datos._CORTOS:
                            comentarios_rotos.append(f"{caso['id']}: {r}")
            except Exception as e:  # noqa: BLE001
                errores.append(f"{caso['id']}/{dif}/{formula}: {e!r}")
revisar("el Revisor 2 revisa todos los casos sin errores", not errores, "\n".join(errores[:10]))
revisar("los comentarios del Revisor citan fuentes que existen", not comentarios_rotos,
        "\n".join(sorted(set(comentarios_rotos))[:10]))


# ------------------------------------- 6. código del protocolo exportado
def bloques_de_codigo(ruta):
    codigo, dentro = [], False
    for linea in open(ruta, encoding="utf-8").read().split("\n"):
        if linea.startswith("```"):
            dentro = not dentro
        elif dentro and not linea.lstrip().startswith("#"):
            codigo.append(linea)
    return codigo


distintos = []
for caso in casos.CASOS:
    dis = X.nuevo(caso)["dis"]
    rutas = {}
    for idioma_ in ("es", "en"):
        idioma.ACTUAL = idioma_
        idioma._cargar()
        rutas[idioma_] = protocolo.generar(dis, caso)
    if bloques_de_codigo(rutas["es"]) != bloques_de_codigo(rutas["en"]):
        distintos.append(caso["id"])
revisar("el código del protocolo en inglés es igual al de español", not distintos,
        ", ".join(distintos))

print()
print(f"{len(fallas)} prueba(s) fallaron." if fallas else "Todo bien.")
sys.exit(1 if fallas else 0)
