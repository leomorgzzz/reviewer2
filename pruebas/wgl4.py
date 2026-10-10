"""Caracteres que la consola clásica de Windows dibuja con Consolas (WGL4).
Los demás salen como «?».

    python3 pruebas/wgl4.py        lista los que sobran en los .py del juego
"""

import os
import pathlib
import sys


def _rango(a, b):
    return {chr(c) for c in range(a, b + 1)}


WGL4 = (_rango(0x20, 0x7E) | _rango(0xA0, 0x17F) | set("ƒǺǻǼǽǾǿˆˇˉ˘˙˚˛˜˝")
        | _rango(0x384, 0x38A) | {"Ό"} | _rango(0x38E, 0x3A1) | _rango(0x3A3, 0x3CE)
        | _rango(0x401, 0x40C) | _rango(0x40E, 0x44F) | _rango(0x451, 0x45C)
        | set("ўџҐґ")
        | set("ẀẁẂẃẄẅỲỳ‐‒–—―‗‘’‚‛“”„†‡•…‰′″‹›‼‾⁄ⁿ₣₤₧€℅ℓ№™Ω℮⅛⅜⅝⅞←↑→↓↔↕↨∂∆∏∑−∕∙√∞∟∩∫≈≠≡≤≥⌂⌐⌠⌡")
        | set("─│┌┐└┘├┤┬┴┼═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬▀▄█▌▐░▒▓■□▪▫▬▲►▼◄◊○●◘◙◦☺☻☼♀♂♠♣♥♦♪♫ﬁﬂ")
        | {"\n", "\t"})


def revisar(carpetas):
    """{carácter: ['archivo:línea', ...]} con lo que no está en WGL4."""
    malos = {}
    for carpeta in carpetas:
        for p in sorted(pathlib.Path(carpeta).rglob("*.py")):
            if "__pycache__" in p.parts or "pruebas" in p.parts:
                continue
            for n, linea in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                for ch in set(linea) - WGL4:
                    malos.setdefault(ch, []).append(f"{p.name}:{n}")
    return malos


if __name__ == "__main__":
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    malos = revisar([raiz])
    for ch, lugares in sorted(malos.items()):
        print(f"{ch} U+{ord(ch):04X}  {len(lugares)}  {' '.join(lugares[:6])}")
    sys.exit(1 if malos else 0)
