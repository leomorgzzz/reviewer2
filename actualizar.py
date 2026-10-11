"""Versión del juego y aviso de versiones nuevas.

Al abrir, un hilo pregunta a GitHub cuál es la última versión publicada
(releases/latest). Si es más nueva que la instalada, la pantalla de inicio
ofrece actualizar:

  - Windows (instalador): descarga el instalador nuevo y lo corre en modo
    silencioso; se instala encima, la partida guardada no se toca.
  - Repositorio clonado con git: `git pull`.
  - macOS u otra copia: abre la página de descarga.

Sin internet no pasa nada. `--sin-actualizar` / `--no-update` lo desactiva.
La versión la escribe el flujo de Ejecutables en version.py; en una copia de
git se toma de `git describe`.
"""

import functools
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import urllib.request

REPO = "leomorgzzz/reviewer2"
INSTALADOR = "Reviewer2-Windows-Setup.exe"
PAGINA = f"https://github.com/{REPO}/releases/latest"
CARPETA = os.path.dirname(os.path.abspath(__file__))
NUEVA = None              # "v1.8" cuando hay una versión más nueva
_HILO = None


@functools.cache
def version():
    try:
        from version import VERSION
    except ImportError:
        VERSION = "dev"
    if VERSION != "dev":
        return VERSION
    try:
        r = subprocess.run(["git", "-C", CARPETA, "describe", "--tags", "--abbrev=0"],
                           capture_output=True, text=True, timeout=3)
        return r.stdout.strip().lstrip("v") or "dev"
    except (OSError, subprocess.SubprocessError):
        return "dev"


def _numeros(v):
    return tuple(int(n) for n in re.findall(r"\d+", v)[:4])


def _con_git():
    return not getattr(sys, "frozen", False) and os.path.isdir(os.path.join(CARPETA, ".git"))


def _revisar():
    global NUEVA
    actual = version()
    if actual == "dev":
        return
    try:
        pedido = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/latest",
                                        headers={"User-Agent": "reviewer2"})
        with urllib.request.urlopen(pedido, timeout=4) as r:
            ultima = json.load(r)["tag_name"]
    except Exception:  # noqa: BLE001  sin red, sin aviso
        return
    if _numeros(ultima) > _numeros(actual):
        NUEVA = ultima


def revisar_en_fondo():
    global _HILO
    if any(a in sys.argv for a in ("--sin-actualizar", "--no-update")):
        return
    _HILO = threading.Thread(target=_revisar, daemon=True)
    _HILO.start()


def esperar(segundos=1.5):
    """Da tiempo a que llegue la respuesta antes de dibujar el menú."""
    if _HILO:
        _HILO.join(segundos)


def git_pull():
    """Actualiza una copia de git. Devuelve (bien, salida)."""
    try:
        r = subprocess.run(["git", "-C", CARPETA, "pull", "--ff-only"],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def preparar():
    """Lo que hace la opción «Actualizar», dentro de curses. Devuelve el
    instalador descargado (se corre al cerrar el juego), "git" si ya se
    actualizó con git, "pagina" si se abrió la página, o None si falló."""
    if sys.platform == "win32" and getattr(sys, "frozen", False):
        ruta = os.path.join(tempfile.mkdtemp(), INSTALADOR)
        try:
            urllib.request.urlretrieve(f"{PAGINA}/download/{INSTALADOR}", ruta)
        except Exception:  # noqa: BLE001
            return None
        return ruta
    if _con_git():
        return "git" if git_pull()[0] else None
    import webbrowser
    webbrowser.open(PAGINA)
    return "pagina"


def correr_instalador(ruta):
    """Se llama después de curses.wrapper: el instalador reemplaza los
    archivos del juego, así que el juego tiene que estar cerrado."""
    subprocess.Popen([ruta, "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS"],
                     creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
