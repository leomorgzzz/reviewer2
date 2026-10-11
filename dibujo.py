"""Colores, cajas, barras, menús y ventanas emergentes con curses."""

import curses
import os
import random
import textwrap
import time

from idioma import tr

# Paleta: grises neutros + acentos desaturados (índices xterm-256).
# (color 256, respaldo de 8 colores)
_PALETA = {
    "texto": (254, curses.COLOR_WHITE),
    "tenue": (245, curses.COLOR_WHITE),
    "oscuro": (240, curses.COLOR_WHITE),
    "titulo": (187, curses.COLOR_YELLOW),
    "agua": (109, curses.COLOR_CYAN),
    "bien": (108, curses.COLOR_GREEN),
    "mal": (138, curses.COLOR_RED),
    # grupos experimentales (en el orden de cada caso)
    "g0": (109, curses.COLOR_CYAN),
    "g1": (174, curses.COLOR_RED),
    "g2": (144, curses.COLOR_YELLOW),
    "g3": (139, curses.COLOR_MAGENTA),
    "g4": (108, curses.COLOR_GREEN),
    "g5": (181, curses.COLOR_WHITE),
    # bases
    "A": (108, curses.COLOR_GREEN),
    "C": (110, curses.COLOR_CYAN),
    "G": (187, curses.COLOR_YELLOW),
    "T": (138, curses.COLOR_RED),
    "base": (243, curses.COLOR_WHITE),
}
COLORES_GRUPO = ["g0", "g1", "g2", "g3", "g4", "g5"]
_PARES = {}
_FONDOS = {}          # (nombre, fondo) -> número de par
_SIGUIENTE = [0]


def init_colores():
    curses.start_color()
    try:
        curses.use_default_colors()
        fondo = -1
    except curses.error:
        fondo = curses.COLOR_BLACK
    for i, (nombre, (c256, c8)) in enumerate(_PALETA.items(), start=1):
        curses.init_pair(i, _color(c256, c8), fondo)
        _PARES[nombre] = i
    _SIGUIENTE[0] = len(_PALETA) + 1
    _paleta_consola()


def _rgb(c256):
    """Índice xterm-256 → (r, g, b) de 0 a 255."""
    if c256 >= 232:
        v = 8 + 10 * (c256 - 232)
        return v, v, v
    n = c256 - 16
    niveles = (0, 95, 135, 175, 215, 255)
    return niveles[n // 36], niveles[n // 6 % 6], niveles[n % 6]


def _paleta_consola():
    """La consola de Windows solo tiene 16 colores y los trae muy saturados:
    se cambian por los de _PALETA (el primero de cada color de respaldo) y
    grises neutros. Las versiones brillantes, que salen con A_BOLD, quedan
    iguales para que la negrita no sature. PDCurses la restaura al salir."""
    if os.name != "nt" or curses.COLORS >= 256 or not curses.can_change_color():
        return
    tabla = {curses.COLOR_BLACK: (28, 28, 28), curses.COLOR_WHITE: _rgb(245)}
    for c256, c8 in _PALETA.values():
        if c8 not in tabla:
            tabla[c8] = _rgb(c256)
    for c8, rgb in tabla.items():
        r, g, b = (v * 1000 // 255 for v in rgb)
        try:
            curses.init_color(c8, r, g, b)
            if c8 not in (curses.COLOR_BLACK, curses.COLOR_WHITE) and curses.COLORS >= 16:
                curses.init_color(c8 + 8, r, g, b)
        except curses.error:
            return
    if curses.COLORS >= 16:
        for n, c256 in ((8, 240), (15, 254)):
            r, g, b = (v * 1000 // 255 for v in _rgb(c256))
            try:
                curses.init_color(n, r, g, b)
            except curses.error:
                return


def _color(c256, c8):
    """Color según lo que dé la terminal. Con 16 colores (la consola de
    Windows) los grises usan blanco brillante, gris claro y gris oscuro en
    vez de A_DIM, que ahí casi nunca se nota."""
    if curses.COLORS >= 256:
        return c256
    if curses.COLORS >= 16 and c8 == curses.COLOR_WHITE:
        return 15 if c256 >= 250 else 7 if c256 >= 244 else 8
    return c8


def c(nombre, extra=0, fondo=None):
    """Atributo de color. fondo: índice xterm-256 de gris para el fondo."""
    if nombre not in _PARES:
        return extra
    if fondo is not None and curses.COLORS >= 256:
        clave = (nombre, fondo)
        if clave not in _FONDOS:
            if _SIGUIENTE[0] >= curses.COLOR_PAIRS:
                return c(nombre, extra)
            curses.init_pair(_SIGUIENTE[0], _PALETA[nombre][0], fondo)
            _FONDOS[clave] = _SIGUIENTE[0]
            _SIGUIENTE[0] += 1
        return curses.color_pair(_FONDOS[clave]) | extra
    attr = curses.color_pair(_PARES[nombre])
    if nombre in ("tenue", "oscuro", "base") and curses.COLORS < 16:
        attr |= curses.A_DIM
    return attr | extra


def estrellas(n):
    """Calificación de 0 a 3: «* * · ». Sin estrellas Unicode, que la consola
    de Windows dibuja como «?»."""
    return "* " * n + "· " * (3 - n)


def put(win, y, x, texto, attr=0, fin=None):
    """addstr que recorta al tamaño de la ventana (o a la columna `fin`) y
    nunca revienta."""
    alto, ancho = win.getmaxyx()
    if y < 0 or y >= alto or x >= ancho or x < 0:
        return
    limite = ancho - (1 if y == alto - 1 else 0)
    if fin is not None:
        limite = min(limite, fin)
    texto = tr(str(texto))[: max(0, limite - x)]
    try:
        win.addstr(y, x, texto, attr)
    except curses.error:
        pass


def trozos(win, y, x, partes, fin=None):
    """Dibuja [(texto, color[, extra]), ...] seguidos. Devuelve la x final."""
    for p in partes:
        texto, color = tr(p[0]), p[1]
        extra = p[2] if len(p) > 2 else 0
        put(win, y, x, texto, c(color, extra), fin)
        x += len(texto)
    return x


def marcado(texto, base="texto"):
    """'hola <PPAR>PPARα</> y <mal!>no</>' → partes. '!' = negrita."""
    partes = []
    color, extra = base, 0
    texto = tr(texto)
    for i, trozo in enumerate(texto.split("<")):
        if i == 0:
            if trozo:
                partes.append((trozo, base))
            continue
        etiqueta, cierre, resto = trozo.partition(">")
        if not cierre:                       # un '<' literal
            partes.append(("<" + trozo, color))
            continue
        if etiqueta == "/":
            color, extra = base, 0
        else:
            extra = curses.A_BOLD if etiqueta.endswith("!") else 0
            color = etiqueta.rstrip("!")
        if resto:
            partes.append((resto, color, extra))
    return partes


def envolver_partes(partes, ancho, sangria=0):
    """Ajusta una línea de partes de colores al ancho. Devuelve lista de
    líneas (cada una una lista de partes). Las líneas siguientes llevan
    `sangria` espacios."""
    ancho = max(10, ancho)
    palabras = []                      # (texto, color, extra)
    for p in partes:
        texto, color = p[0], p[1]
        extra = p[2] if len(p) > 2 else 0
        actual = ""
        for ch in texto:
            actual += ch
            if ch == " ":
                palabras.append((actual, color, extra))
                actual = ""
        if actual:
            palabras.append((actual, color, extra))
    lineas, linea, largo = [], [], 0
    for texto, color, extra in palabras:
        while largo + len(texto.rstrip()) > ancho:
            if largo > (sangria if lineas else 0):
                lineas.append(linea)
                linea, largo = ([(" " * sangria, "texto")], sangria) if sangria else ([], 0)
                texto = texto.lstrip() if texto.strip() else texto
                continue
            cabe = ancho - largo                      # palabra más larga que la línea
            linea.append((texto[:cabe], color, extra))
            lineas.append(linea)
            linea, largo = ([(" " * sangria, "texto")], sangria) if sangria else ([], 0)
            texto = texto[cabe:]
        if texto:
            linea.append((texto, color, extra))
            largo += len(texto)
    lineas.append(linea)
    return lineas


def a_lineas(contenido, ancho, color="texto"):
    """Normaliza contenido (str, partes o lista de ambos) a líneas de partes
    ya ajustadas al ancho. Un str admite marcado <color>…</>."""
    salida = []
    for l in contenido:
        if isinstance(l, str):
            l = tr(l)
            if not l:
                salida.append([])
                continue
            sangria = len(l) - len(l.lstrip(" "))
            for parrafo in l.split("\n"):
                salida.extend(envolver_partes(marcado(parrafo, color), ancho,
                                              min(sangria + 2, 8) if sangria else 0))
        else:
            salida.extend(envolver_partes(l, ancho) if l else [[]])
    return salida


def caja(win, y, x, h, w, titulo=None, attr=None, color_titulo="titulo"):
    attr = c("tenue") if attr is None else attr
    titulo = tr(titulo) if titulo else titulo
    put(win, y, x, "┌" + "─" * (w - 2) + "┐", attr)
    for i in range(1, h - 1):
        put(win, y + i, x, "│", attr)
        put(win, y + i, x + w - 1, "│", attr)
    put(win, y + h - 1, x, "└" + "─" * (w - 2) + "┘", attr)
    if titulo:
        put(win, y, x + 2, f" {titulo} "[: max(0, w - 4)], c(color_titulo, curses.A_BOLD))


def limpiar_area(win, y, x, h, w):
    for i in range(h):
        put(win, y + i, x, " " * w)


def barra(win, y, x, ancho, valor, maximo, attr, banda=None):
    """Barra de nivel. banda=(min, max) marca el rango objetivo con ¦."""
    llenos = 0 if maximo <= 0 else round(ancho * max(0, min(valor, maximo)) / maximo)
    put(win, y, x, "█" * llenos, attr)
    put(win, y, x + llenos, "░" * (ancho - llenos), c("oscuro"))
    if banda:
        for v in banda:
            if v is None:
                continue
            bx = x + min(ancho - 1, round(ancho * v / maximo))
            put(win, y, bx, "¦", c("titulo", curses.A_BOLD))


def envolver(texto, ancho):
    salida = []
    for parrafo in tr(str(texto)).split("\n"):
        salida.extend(textwrap.wrap(parrafo, max(10, ancho)) or [""])
    return salida


MOVIMIENTO = (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT,
              "w", "a", "s", "d", "W", "A", "S", "D")


def tecla(win, texto=False):
    """Lee una tecla; devuelve int de curses o str de un carácter. Al dejar
    presionada una flecha, las repeticiones que se juntaron mientras se
    dibujaba se descartan: si no, en Windows (donde dibujar tarda más) el
    personaje sigue avanzando después de soltarla. texto=True no descarta
    nada (para escribir)."""
    while True:
        try:
            k = win.get_wch()
        except curses.error:
            continue
        if k == curses.KEY_RESIZE and os.name == "nt":
            curses.resize_term(0, 0)        # PDCurses no actualiza el tamaño solo
        if not texto and k in MOVIMIENTO:
            _descartar_repetidas(win, k)
        return k


def _descartar_repetidas(win, k):
    win.nodelay(True)
    try:
        while True:
            try:
                sig = win.get_wch()
            except curses.error:
                return
            if sig != k:
                # la primera tecla distinta se devuelve a la cola
                if isinstance(sig, int):
                    curses.ungetch(sig)
                else:
                    curses.unget_wch(sig)
                return
    finally:
        win.nodelay(False)


def pausa(ms, desde):
    """Espera a que pasen ms desde `desde` (time.monotonic()). Lo que tardó
    dibujar el cuadro ya cuenta: en la consola de Windows dibujar es lento y
    con una pausa fija las animaciones duraban mucho más."""
    resto = ms - int((time.monotonic() - desde) * 1000)
    if resto > 0:
        curses.napms(resto)


def es(k, *opciones):
    """Compara una tecla con caracteres (sin importar mayúsculas) o códigos."""
    for o in opciones:
        if isinstance(o, str) and isinstance(k, str) and k.lower() == o.lower():
            return True
        if isinstance(o, int) and k == o:
            return True
    return False


ESC = "\x1b"
ENTER = ("\n", "\r", curses.KEY_ENTER)


def popup(win, texto, titulo=None, ancho=64, attr=None, esperar=True):
    """Ventana centrada con texto (admite marcado <color>…</>); espera una
    tecla. Si no cabe en la pantalla, se desplaza con ↑↓."""
    alto_p, ancho_p = win.getmaxyx()
    ancho = min(ancho, ancho_p - 2)
    color = "texto"
    if attr is not None:
        # attr viene de c(nombre): se busca el nombre para el marcado
        for nombre, par in _PARES.items():
            if attr == curses.color_pair(par):
                color = nombre
                break
    lineas = a_lineas(tr(str(texto)).split("\n"), ancho - 4, color)
    h = min(len(lineas) + 4, alto_p - 1)
    visibles = h - 4
    y0 = max(0, (alto_p - h) // 2)
    x0 = max(0, (ancho_p - ancho) // 2)
    pos = 0
    while True:
        limpiar_area(win, y0, x0, h, ancho)
        caja(win, y0, x0, h, ancho, titulo)
        for i, partes in enumerate(lineas[pos:pos + visibles]):
            trozos(win, y0 + 1 + i, x0 + 2, partes, fin=x0 + ancho - 2)
        mas = len(lineas) > visibles
        if mas:
            put(win, y0 + h - 2, x0 + 2, f"↑↓ más texto ({pos + visibles}/{len(lineas)})",
                c("agua"))
        if not esperar:
            win.refresh()
            return None
        put(win, y0 + h - 2, x0 + ancho - 18, "[Enter] seguir", c("tenue"))
        win.refresh()
        k = tecla(win)
        if k == curses.KEY_RESIZE:
            continue
        if mas and es(k, curses.KEY_UP, "w", "k"):
            pos = max(0, pos - 1)
        elif mas and es(k, curses.KEY_DOWN, "s", "j"):
            pos = min(len(lineas) - visibles, pos + 1)
        elif mas and pos + visibles < len(lineas) and k in ENTER + (" ",):
            pos = min(len(lineas) - visibles, pos + visibles)
        else:
            return k


def dialogo(win, paginas, titulo=None, ancho=64, fondo=None):
    """Varias ventanas seguidas. fondo: función que redibuja lo de atrás."""
    for p in paginas:
        if fondo:
            fondo()
        else:
            win.erase()
        popup(win, p, titulo, ancho=ancho)


def menu(win, titulo, opciones, y=None, x=None, ancho=None, ayuda=None,
         inicial=0, colores=None, barajar=False):
    """Menú vertical. opciones: lista de str. Devuelve índice o None (Esc).
    colores: lista opcional con el color de cada opción. Las opciones largas
    se parten en varias líneas en vez de recortarse; `ancho` es el mínimo.
    barajar: las opciones salen en otro orden (salvo «Volver», al final) para
    que la correcta no sea siempre la primera; devuelve el índice original."""
    if barajar:
        fijas = [i for i, o in enumerate(opciones) if o == "Volver"]
        orden = [i for i in range(len(opciones)) if i not in fijas]
        random.shuffle(orden)
        orden += fijas
        op = menu(win, titulo, [opciones[i] for i in orden], y, x, ancho, ayuda, inicial,
                  [colores[i] for i in orden] if colores else None)
        return None if op is None else orden[op]
    titulo = tr(titulo) if titulo else titulo
    opciones = [tr(o) for o in opciones]
    ayuda = tr(ayuda) if ayuda else ayuda
    alto_p, ancho_p = win.getmaxyx()
    natural = max([len(o) for o in opciones] + [len(titulo or "") + 4,
                                                len(ayuda or "")]) + 8
    ancho = min(max(ancho or 0, natural), ancho_p - 2, 110)
    partes = [envolver(o, ancho - 8) for o in opciones]       # líneas de cada opción
    alto_ops = sum(len(p) for p in partes)
    h = min(alto_ops + 2 + (2 if ayuda else 0), alto_p - 1)
    y = max(0, (alto_p - h) // 2 if y is None else min(y, alto_p - h))
    if x is None or x + ancho > ancho_p:
        x = (ancho_p - ancho) // 2
    sel = inicial
    visibles = h - 2 - (2 if ayuda else 0)
    while True:
        limpiar_area(win, y, x, h, ancho)
        caja(win, y, x, h, ancho, titulo)
        # primera opción visible: la seleccionada tiene que caber completa
        inicio = 0
        while sum(len(p) for p in partes[inicio:sel + 1]) > visibles and inicio < sel:
            inicio += 1
        fila = 0
        for idx in range(inicio, len(opciones)):
            if fila + len(partes[idx]) > visibles:
                break
            color = colores[idx] if colores else "texto"
            attr = c("titulo", curses.A_BOLD) if idx == sel else c(color)
            for j, linea in enumerate(partes[idx]):
                marca = ("► " if idx == sel else "  ") if j == 0 else "    "
                put(win, y + 1 + fila, x + 2, (marca + linea)[: ancho - 4], attr)
                fila += 1
        if ayuda:
            put(win, y + h - 2, x + 2, ayuda[: ancho - 4], c("tenue"))
        win.refresh()
        k = tecla(win)
        if es(k, curses.KEY_UP, "k", "w"):
            sel = (sel - 1) % len(opciones)
        elif es(k, curses.KEY_DOWN, "j", "s"):
            sel = (sel + 1) % len(opciones)
        elif k in ENTER or k == " ":
            return sel
        elif k == ESC or es(k, "q"):
            return None
        elif isinstance(k, str) and k.isdigit() and 1 <= int(k) <= min(9, len(opciones)):
            return int(k) - 1


def visor(win, titulo, contenido, ayuda=None, salir=None, color=None, ancho_max=100):
    """Visor con desplazamiento a casi pantalla completa.
    contenido: lista de str (con marcado) o listas de partes.
    salir: teclas extra que cierran el visor; devuelve la tecla pulsada."""
    pos = 0
    while True:
        alto, ancho = win.getmaxyx()
        w = min(ancho - 2, ancho_max)
        x0 = (ancho - w) // 2
        h = alto - 2
        visibles = h - 3
        planas = a_lineas(contenido, w - 4, color or "texto")
        pos = max(0, min(pos, len(planas) - visibles))
        win.erase()
        caja(win, 1, x0, h, w, titulo)
        for i, partes in enumerate(planas[pos:pos + visibles]):
            trozos(win, 2 + i, x0 + 2, partes, fin=x0 + w - 2)
        mas = len(planas) > visibles
        pie = ayuda or "Esc/Q/Enter volver"
        if mas:
            pie = tr("↑↓ desplazar · ") + tr(pie)
        put(win, h, x0 + 2, f" {pie} "[: w - 16], c("tenue"))
        if mas:
            marca = f" {min(100, round(100 * (pos + visibles) / len(planas)))}% "
            put(win, h, x0 + w - len(marca) - 2, marca, c("tenue"))
        win.refresh()
        k = tecla(win)
        if salir and (k in salir or (isinstance(k, str) and k.lower() in salir)):
            return k
        if es(k, curses.KEY_UP, "w", "k"):
            pos -= 1
        elif es(k, curses.KEY_DOWN, "s", "j"):
            pos += 1
        elif k == curses.KEY_PPAGE:
            pos -= visibles
        elif k == curses.KEY_NPAGE or k == " ":
            pos += visibles
        elif k == ESC or es(k, "q") or k in ENTER:
            return k


def entrada(win, pregunta, inicial="", largo=40):
    """Pide una línea de texto. Devuelve el texto o None (Esc)."""
    texto = inicial
    curses.curs_set(1)
    try:
        while True:
            alto, ancho = win.getmaxyx()
            w = min(max(largo, len(pregunta)) + 6, ancho - 2)
            y0, x0 = (alto - 5) // 2, (ancho - w) // 2
            limpiar_area(win, y0, x0, 5, w)
            caja(win, y0, x0, 5, w, pregunta)
            visible = texto[-(w - 5):]
            put(win, y0 + 2, x0 + 2, visible, c("texto", curses.A_BOLD))
            put(win, y0 + 4, x0 + 2, " Enter aceptar · Esc cancelar ", c("tenue"))
            win.move(y0 + 2, x0 + 2 + len(visible))
            win.refresh()
            k = tecla(win, texto=True)
            if k in ENTER:
                return texto.strip()
            if k == ESC:
                return None
            if k in (curses.KEY_BACKSPACE, "\x7f", "\b", 127, 8):
                texto = texto[:-1]
            elif isinstance(k, str) and k.isprintable() and len(texto) < largo:
                texto += k
    finally:
        curses.curs_set(0)


def texto_largo(win, titulo, lineas, color=None):
    visor(win, titulo, lineas, color=color)


def navegador(win, titulo, entradas, contenido, ayuda_lista=None, colores=None, salir=None):
    """Lista a la izquierda y contenido a la derecha (Manual, Catálogo).
    entradas: lista de str. contenido(i) -> lista para a_lineas.
    ↑↓ elegir · PgUp/PgDn o espacio desplazar · Esc/Q volver.
    salir: teclas extra que cierran y se devuelven."""
    sel, pos = 0, 0
    # se traducen antes de recortarlas: un título recortado ya no coincide
    entradas = [tr(e) for e in entradas]
    while True:
        alto, ancho = win.getmaxyx()
        w = min(ancho - 2, 130)
        x0 = (ancho - w) // 2
        h = alto - 2
        lw = min(30, max(len(e) for e in entradas) + 5, w // 3)
        cw = w - lw - 1
        win.erase()
        caja(win, 1, x0, h, w, titulo)
        if lw > len(titulo) + 5:
            put(win, 1, x0 + lw, "┬", c("tenue"))
        put(win, h, x0 + lw, "┴", c("tenue"))
        for yy in range(2, h):
            put(win, yy, x0 + lw, "│", c("tenue"))
        visibles_l = h - 2
        ini = max(0, min(sel - visibles_l // 2, len(entradas) - visibles_l))
        for i, e in enumerate(entradas[ini:ini + visibles_l]):
            idx = ini + i
            marca = "► " if idx == sel else "  "
            color = colores[idx] if colores else "texto"
            attr = c("titulo", curses.A_BOLD | curses.A_REVERSE) if idx == sel else c(color)
            put(win, 2 + i, x0 + 1, (marca + e)[: lw - 2].ljust(lw - 2), attr)
        planas = a_lineas(contenido(sel), cw - 4)
        visibles = h - 3
        pos = max(0, min(pos, len(planas) - visibles))
        for i, partes in enumerate(planas[pos:pos + visibles]):
            trozos(win, 2 + i, x0 + lw + 2, partes, fin=x0 + w - 2)
        mas = len(planas) > visibles
        pie = tr("↑↓ elegir · ") + (tr("PgDn/espacio bajar · PgUp subir · ") if mas else "") + tr("Esc/Q volver")
        put(win, h, x0 + 2, f" {tr(ayuda_lista) if ayuda_lista else pie} "[: w - 14], c("tenue"))
        if mas:
            marca = f" {min(100, round(100 * (pos + visibles) / len(planas)))}% "
            put(win, h, x0 + w - len(marca) - 2, marca, c("agua"))
        win.refresh()
        k = tecla(win)
        if salir and isinstance(k, str) and k.lower() in salir:
            return k
        if es(k, curses.KEY_UP, "w", "k"):
            sel, pos = (sel - 1) % len(entradas), 0
        elif es(k, curses.KEY_DOWN, "s", "j"):
            sel, pos = (sel + 1) % len(entradas), 0
        elif k in (curses.KEY_NPAGE, " ") or es(k, curses.KEY_RIGHT, "d"):
            pos += visibles - 1 if k in (curses.KEY_NPAGE, " ") else 1
        elif k == curses.KEY_PPAGE or es(k, curses.KEY_LEFT, "a"):
            pos -= visibles - 1 if k == curses.KEY_PPAGE else 1
        elif k in ENTER and pos + visibles < len(planas):
            pos += visibles - 1
        elif k == ESC or es(k, "q") or k in ENTER:
            win.erase()
            return
