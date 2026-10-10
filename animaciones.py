"""Animaciones: secuenciación por síntesis, alineamiento con splicing y el
sello del Revisor 2.

Cada cuadro es una lista de (fila, columna, texto, color) relativa a un
recuadro centrado; la última fila es un subtítulo que explica qué pasa.
Cualquier tecla salta la animación.
"""

import curses
import random
import time

import dibujo as d

# ms por cuadro, ms de pausa final
VELOCIDADES = {"lenta": (160, 1600), "normal": (90, 900), "rápida": (35, 300)}
ORDEN_VEL = ["lenta", "normal", "rápida"]
AREA_H, AREA_W = 16, 68


def reproducir(win, cuadros, velocidad="normal", titulo=None):
    paso, pausa = VELOCIDADES.get(velocidad, VELOCIDADES["normal"])
    alto, ancho = win.getmaxyx()
    h, w = min(AREA_H, alto - 2), min(AREA_W, ancho - 2)
    y0, x0 = (alto - h) // 2, (ancho - w) // 2
    win.nodelay(True)
    curses.flushinp()
    try:
        for i, cuadro in enumerate(cuadros):
            t = time.monotonic()
            d.limpiar_area(win, y0, x0, h, w)
            d.caja(win, y0, x0, h, w, titulo)
            for fy, fx, texto, color in cuadro:
                if 0 <= fy < h - 2:
                    d.put(win, y0 + 1 + fy, x0 + 2 + fx, texto[: max(0, w - 4 - fx)],
                          d.c(color, curses.A_BOLD if color not in ("tenue", "oscuro") else 0))
            win.refresh()
            d.pausa(pausa if i == len(cuadros) - 1 else paso, t)
            if win.getch() != -1:
                break
    finally:
        win.nodelay(False)
        curses.flushinp()


def _sub(texto, color="tenue"):
    return (AREA_H - 3, max(0, (AREA_W - 4 - len(texto)) // 2), texto, color)


# ------------------------------------------------------------ secuenciación
def secuenciacion(win, n_muestras, velocidad="normal"):
    """Una flow cell con clusters que se iluminan con una base por ciclo."""
    rng = random.Random(n_muestras)
    filas, cols = 6, 14
    clusters = [(1 + f * 2 // 1, 4 + c * 4) for f in range(filas) for c in range(cols)
                if rng.random() < 0.7]
    secuencias = {p: [rng.choice("ACGT") for _ in range(12)] for p in clusters}
    cuadros = []
    marco = [(0, 2, "╔" + "═" * 58 + "╗", "tenue")] + \
            [(1 + i, 2, "║", "tenue") for i in range(12)] + \
            [(1 + i, 61, "║", "tenue") for i in range(12)] + \
            [(12, 2, "╚" + "═" * 58 + "╝", "tenue")]
    for ciclo in range(12):
        cuadro = list(marco)
        for (y, x) in clusters:
            b = secuencias[(y, x)][ciclo]
            cuadro.append((y, x, b, b))
        leidas = "".join(secuencias[clusters[0]][: ciclo + 1])
        cuadro.append((AREA_H - 4, 4, f"cluster 1: {leidas}", "texto"))
        cuadro.append(_sub(f"ciclo {ciclo + 1}: un nucleótido fluorescente por cluster, "
                           "foto, se quita el terminador"))
        cuadros.append(cuadro)
    final = list(marco) + [(y, x, "·", "oscuro") for y, x in clusters]
    final.append(_sub(f"{n_muestras} bibliotecas leídas · demultiplexando por índice…", "bien"))
    cuadros.append(final)
    reproducir(win, cuadros, velocidad, "Secuenciación por síntesis (Illumina)")


# ------------------------------------------------------------- alineamiento
def alineamiento(win, velocidad="normal"):
    """Una lectura que cruza una unión exón-exón se parte al alinear."""
    genoma_y = 8
    exon1, intron, exon2 = (6, 18), (18, 38), (38, 52)
    base = [
        (genoma_y, exon1[0], "▓" * (exon1[1] - exon1[0]), "agua"),
        (genoma_y, intron[0], "─" * (intron[1] - intron[0]), "oscuro"),
        (genoma_y, exon2[0], "▓" * (exon2[1] - exon2[0]), "agua"),
        (genoma_y + 1, exon1[0] + 2, "exón 1", "tenue"),
        (genoma_y + 1, intron[0] + 6, "intrón", "oscuro"),
        (genoma_y + 1, exon2[0] + 2, "exón 2", "tenue"),
        (genoma_y - 1, 0, "genoma", "tenue"),
    ]
    lectura = "ACGTTGCA" + "GGATCCAT"
    cuadros = []
    for i in range(8):
        cuadros.append(base + [(1 + i // 2, 12, lectura, "titulo"),
                               _sub("una lectura de ARNm maduro: no tiene intrones")])
    for paso in range(8):
        dx = round((intron[1] - intron[0]) * paso / 7)
        cuadros.append(base + [
            (genoma_y - 2, 10, lectura[:8], "titulo"),
            (genoma_y - 2, 10 + 8 + dx, lectura[8:], "titulo"),
            _sub("el alineador con splicing (STAR, HISAT2) la parte en dos")])
    union = base + [(genoma_y - 2, 10, lectura[:8], "bien"),
                    (genoma_y - 2, 18, "└" + "─" * 18 + "┘", "bien"),
                    (genoma_y - 2, 38, lectura[8:], "bien")]
    for _ in range(4):
        cuadros.append(union + [_sub("unión exón-exón detectada: así se ven isoformas y "
                                     "splicing", "bien")])
    reproducir(win, cuadros, velocidad, "Alineamiento con splicing")


# ------------------------------------------------------------------ sello
def sello(win, texto, color, velocidad="normal"):
    ancho = max(22, len(texto) + 6)
    arte = ["╔" + "═" * (ancho - 2) + "╗",
            "║" + texto.center(ancho - 2) + "║",
            "║" + "— Revisor 2 —".center(ancho - 2) + "║",
            "╚" + "═" * (ancho - 2) + "╝"]
    x = (AREA_W - 4 - ancho) // 2
    cuadros = []
    for y in range(-3, 5):
        cuadros.append([(y + i, x, l, color) for i, l in enumerate(arte)])
    final = [(4 + i, x, l, color) for i, l in enumerate(arte)]
    for _ in range(2):
        cuadros.append([(f[0] + 1, f[1], f[2], "tenue") for f in final])
        cuadros.append(final)
    reproducir(win, cuadros, velocidad, "Dictamen")
