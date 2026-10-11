"""Idioma del juego: español (el del código) o inglés.

Los textos se escriben en español en el código. En inglés, la capa de dibujo
(dibujo.py) pasa cada texto por tr() antes de mostrarlo:

  1. Si el texto completo está en EN (en_*.py), se usa su traducción.
  2. Si no, se prueba contra las plantillas: claves con huecos {0}, {1}…
     (salen de los f-strings del código). Lo que llena cada hueco también se
     traduce, así un texto armado con datos queda traducido completo.
  3. Si nada coincide, se deja el español.

El idioma se elige en Opciones o al abrir con `reviewer2 --en` / `--es`; se
recuerda en ~/.reviewer2_idioma. La primera vez se usa el del sistema: español
si está en español, inglés en cualquier otro caso.
"""

import locale
import os
import re
import subprocess
import sys

ARCHIVO = os.path.expanduser("~/.reviewer2_idioma")
IDIOMAS = ("es", "en")


def migrar(viejo, nuevo):
    """El juego se llamaba Revisor 2: sus archivos (~/.revisor2…) pasan al
    nombre nuevo la primera vez."""
    viejo, nuevo = os.path.expanduser(viejo), os.path.expanduser(nuevo)
    if os.path.exists(viejo) and not os.path.exists(nuevo):
        try:
            os.replace(viejo, nuevo)
        except OSError:
            return viejo
    return nuevo


migrar("~/.revisor2_idioma", ARCHIVO)


def _del_sistema():
    nombres = [os.environ.get(v, "") for v in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE")]
    try:
        nombres.append(locale.getlocale()[0] or "")
    except ValueError:
        pass
    if sys.platform == "win32":
        try:
            import ctypes
            if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x0A:
                return "es"
        except Exception:  # noqa: BLE001
            pass
    elif sys.platform == "darwin":
        try:
            nombres.append(subprocess.run(["defaults", "read", "-g", "AppleLocale"],
                                          capture_output=True, text=True, timeout=2).stdout)
        except Exception:  # noqa: BLE001
            pass
    for n in nombres:
        n = n.strip().lower()
        if n and n not in ("c", "posix", "c.utf-8"):
            return "es" if n.startswith(("es", "spanish")) else "en"
    return "en"


def _detectar():
    for arg in sys.argv[1:]:
        if arg in ("--es", "--en"):
            return arg[2:]
    try:
        with open(ARCHIVO, encoding="utf-8") as f:
            idioma = f.read().strip()
    except OSError:
        return _del_sistema()
    return idioma if idioma in IDIOMAS else _del_sistema()


ACTUAL = _detectar()
EN = {}
_PLANTILLAS = []          # (regex, plantilla inglesa, n huecos)
_CACHE = {}
_LETRAS = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]{2}")
_LETRAS_1 = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]")
_HUECO = re.compile(r"(?<!\{)\{(\w+)\}(?!\})")


def _nombre(hueco):
    return f"h_{hueco}"


def _cargar():
    EN.clear()
    _PLANTILLAS.clear()
    _CACHE.clear()
    if ACTUAL != "en":
        return
    import en
    EN.update(en.EN)
    for es, ing in EN.items():
        if not _HUECO.search(es):
            continue
        partes = _HUECO.split(es)
        patron, nombres = "", []
        for i, p in enumerate(partes):
            if i % 2:
                if p in nombres:            # el mismo hueco dos veces
                    patron += f"(?P={_nombre(p)})"
                    continue
                nombres.append(p)
                patron += f"(?P<{_nombre(p)}>.*?)"
            else:
                patron += re.escape(p.replace("{{", "{").replace("}}", "}"))
        try:
            _PLANTILLAS.append((re.compile(patron + r"\Z", re.S), ing, nombres,
                                partes[0].replace("{{", "{").replace("}}", "}")[:6],
                                (len(_LETRAS_1.findall(_HUECO.sub("", es))), len(partes[0]),
                                 len(_HUECO.sub("", es)))))
        except re.error:
            pass
    # las plantillas con más texto fijo primero (más específicas)
    # (letras fijas, largo del inicio fijo, texto fijo total)
    _PLANTILLAS.sort(key=lambda x: tuple(-v for v in x[4]))


def cambiar(idioma):
    global ACTUAL
    ACTUAL = idioma
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write(idioma + "\n")
    _cargar()


def tr(texto):
    """Traduce un texto para mostrarlo (no cambia datos ni claves)."""
    if ACTUAL == "es" or not isinstance(texto, str) or not _LETRAS.search(texto):
        return texto
    if texto in _CACHE:
        return _CACHE[texto]
    r = _traducir(texto, 0)
    _CACHE[texto] = r
    return r


def _traducir(texto, nivel):
    if texto in EN:
        return EN[texto]
    sin_espacios = texto.strip()
    if sin_espacios != texto and sin_espacios in EN:
        ini = texto[: len(texto) - len(texto.lstrip())]
        fin = texto[len(texto.rstrip()):]
        return ini + EN[sin_espacios] + fin
    if nivel > 8 or len(texto) > 4000:
        return texto
    for patron, ing, nombres, prefijo, _fijo in _PLANTILLAS:
        if prefijo and not texto.startswith(prefijo):
            continue
        m = patron.match(texto)
        if m:
            valores = {}
            for h in nombres:
                v = m.group(_nombre(h))
                valores[h] = _traducir(v, nivel + 1) if v and _LETRAS.search(v) else v
            return _HUECO.sub(lambda mm: valores.get(mm.group(1), mm.group(0)), ing)
    return texto


_cargar()
