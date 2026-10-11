"""Minijuegos del laboratorio: lo que antes era elegir de un menú ahora se
hace con las manos.

  deslizador   detener un cursor en el valor correcto (volúmenes, carga…)
  ordenar      poner los pasos de un procedimiento en orden
  placa        acomodar las muestras en una placa de cultivo
  terminal     elegir un comando o una fórmula

Cada uno dibuja su propio recuadro sobre el laboratorio y devuelve qué tan
bien salió; las estaciones (estaciones.py) convierten eso en consecuencias
para la simulación y el Revisor 2.
"""

import curses
import random
import time

import dibujo as d
from idioma import tr


def _caja(win, h, w, titulo):
    alto, ancho = win.getmaxyx()
    h, w = min(h, alto - 2), min(w, ancho - 2)
    y0, x0 = (alto - h) // 2, (ancho - w) // 2
    d.limpiar_area(win, y0, x0, h, w)
    d.caja(win, y0, x0, h, w, titulo)
    return y0, x0, h, w


# ================================================================ deslizador
ARMADO = 0.4        # segundos en que el cursor no se puede detener al empezar


def detener(k, inicio):
    """Solo ESPACIO detiene un cursor, y no en cuanto aparece: dejar Enter o
    ESPACIO presionados ya no pasa el minijuego."""
    return k == ord(" ") and time.monotonic() - inicio >= ARMADO


def deslizador(lab, titulo, texto, minimo, maximo, unidad, zona, paso=None, formato="{:.2f}"):
    """Un cursor recorre la escala de `minimo` a `maximo` desde un punto al
    azar; ESPACIO lo detiene. Devuelve (valor, dentro_de_la_zona)."""
    win = lab.win
    lab.dibujar()
    ancho_b = 50
    paso = paso or (maximo - minimo) / 70
    pos, dir_ = random.uniform(minimo, maximo), random.choice((1, -1))
    inicio = time.monotonic()
    lineas = d.envolver(texto, ancho_b + 4)
    win.nodelay(True)
    curses.flushinp()
    try:
        while True:
            t = time.monotonic()
            y0, x0, h, w = _caja(win, len(lineas) + 9, ancho_b + 8, titulo)
            for i, l in enumerate(lineas):
                d.put(win, y0 + 1 + i, x0 + 2, l, d.c("texto"))
            yb = y0 + 2 + len(lineas)
            for i in range(ancho_b):
                v = minimo + (maximo - minimo) * i / (ancho_b - 1)
                dentro = zona[0] <= v <= zona[1]
                d.put(win, yb, x0 + 4 + i, "█" if dentro else "─", d.c("bien" if dentro else "tenue"))
            px = round((pos - minimo) / (maximo - minimo) * (ancho_b - 1))
            d.put(win, yb + 1, x0 + 4 + px, "▲", d.c("titulo", curses.A_BOLD))
            d.put(win, yb + 2, x0 + 4, f"{formato.format(minimo)} {unidad}", d.c("tenue"))
            fin = f"{formato.format(maximo)} {unidad}"
            d.put(win, yb + 2, x0 + 4 + ancho_b - len(fin), fin, d.c("tenue"))
            d.put(win, yb + 3, x0 + 4, f"{formato.format(pos)} {unidad}", d.c("titulo", curses.A_BOLD))
            d.put(win, y0 + h - 2, x0 + 2, "ESPACIO para detener", d.c("tenue"))
            win.refresh()
            d.pausa(40, t)
            k = win.getch()
            if detener(k, inicio):
                break
            pos += paso * dir_
            if pos >= maximo or pos <= minimo:
                dir_ = -dir_
                pos = min(maximo, max(minimo, pos))
    finally:
        win.nodelay(False)
        curses.flushinp()
    return pos, zona[0] <= pos <= zona[1]


# ================================================================== ordenar
def ordenar(lab, titulo, intro, pasos):
    """El jugador elige, uno por uno, el siguiente paso. Si se equivoca, el
    paso no se coloca y vuelve a elegir; solo al segundo error en el mismo
    paso se le dice cuál era. Devuelve el número de errores."""
    win = lab.win
    restantes = list(pasos)
    random.shuffle(restantes)
    hechos, errores, fallos_paso = [], 0, 0
    while restantes:
        lab.dibujar()
        texto = tr(intro) + "\n\n" + "\n".join(f"<bien>{i + 1}. {tr(p)}</>" for i, p in enumerate(hechos))
        d.popup(win, texto, titulo, ancho=76, esperar=False)
        op = d.menu(win, f"Paso {len(hechos) + 1} de {len(pasos)}: ¿qué sigue?", restantes,
                    y=win.getmaxyx()[0] - len(restantes) - 4)
        if op is None:
            continue
        correcto = pasos[len(hechos)]
        if restantes[op] != correcto:
            errores += 1
            fallos_paso += 1
            lab.dibujar()
            if fallos_paso < 2:
                d.popup(win, "<mal!>No, ese no va aquí.</> Piensa qué necesita la muestra "
                             "antes y vuelve a elegir.", titulo, ancho=70)
                continue
            d.popup(win, f"<mal!>Tampoco.</> Ahí iba: <titulo>{correcto}</>", titulo, ancho=70)
        fallos_paso = 0
        hechos.append(correcto)
        restantes.remove(correcto)
    lab.dibujar()
    d.popup(win, ("<bien!>Procedimiento correcto.</>" if not errores else
                  tr(f"<titulo!>Terminado con {errores} error(es).</> Así va el orden:\n\n")
                  + "\n".join(f"{i + 1}. {tr(p)}" for i, p in enumerate(pasos))), titulo, ancho=76)
    return errores


# ==================================================================== placa
def placa(lab, caso, dis):
    """Acomodar las muestras en una placa. Los pozos del borde se evaporan
    más (efecto de borde): si un grupo cae casi todo en el borde, eso se
    confunde con el tratamiento. Devuelve el desbalance de borde (0-1)."""
    win = lab.win
    muestras = [(g, r) for g in range(len(caso["grupos"])) for r in range(dis["replicas"])]
    n = len(muestras)
    filas, cols = (4, 6) if n <= 24 else (6, 8) if n <= 48 else (8, 12)
    pozos = {}                              # (f, c) -> (g, r)
    pendientes = list(muestras)             # en el orden de la lista: grupo por grupo
    cur = [0, 0]
    letras = "ABCDEFGH"

    def borde(f, c):
        return f in (0, filas - 1) or c in (0, cols - 1)

    def desbalance():
        frac = []
        for g in range(len(caso["grupos"])):
            del_g = [p for p, m in pozos.items() if m[0] == g]
            frac.append(sum(borde(*p) for p in del_g) / max(1, len(del_g)))
        return max(frac) - min(frac) if frac else 0.0

    while True:
        lab.dibujar()
        alto, ancho = win.getmaxyx()
        w = min(max(cols * 5 + 12, 70), ancho - 2)
        intro = d.envolver("Siembra cada muestra en un pozo. Los pozos del borde (▒) se "
                           "evaporan más.", w - 4)
        ayuda = d.envolver("Flechas mover · Enter sembrar aquí · X quitar · "
                           "A acomodo al azar · T terminar", w - 4)
        if pendientes:
            g, r = pendientes[0]
            estado = [(tr("Siguiente tubo: "), "tenue"),
                      (f"{caso['abrev'][g]}{r + 1} {tr(caso['grupos'][g])}",
                       d.COLORES_GRUPO[g % 6], curses.A_BOLD),
                      (tr(f"   (faltan {len(pendientes)})"), "tenue")]
        else:
            db = desbalance()
            color = "bien" if db <= 0.25 else "titulo" if db <= 0.5 else "mal"
            estado = [(tr(f"Placa completa. Diferencia de pozos en el borde entre "
                          f"grupos: {db:.0%}"), color, curses.A_BOLD)]
        estado = d.envolver_partes(estado, w - 4)
        fijo = len(intro) + len(estado) + len(ayuda) + 8
        paso = 2 if fijo + (filas - 1) * 2 <= alto - 2 else 1   # filas separadas si cabe
        y0, x0, h, w = _caja(win, fijo + (filas - 1) * paso, w, "Placa de cultivo")
        for i, l in enumerate(intro):
            d.put(win, y0 + 1 + i, x0 + 2, l, d.c("texto"), x0 + w - 2)
        yp = y0 + 2 + len(intro)                 # números de columna
        for c in range(cols):
            d.put(win, yp, x0 + 7 + c * 5, f"{c + 1:>2}", d.c("tenue"))
        for f in range(filas):
            d.put(win, yp + 1 + f * paso, x0 + 3, letras[f], d.c("tenue"))
            for c in range(cols):
                x = x0 + 6 + c * 5
                sel = cur == [f, c]
                if (f, c) in pozos:
                    g, r = pozos[(f, c)]
                    txt = f"{caso['abrev'][g]}{r + 1}"[:3].center(4)
                    attr = d.c(d.COLORES_GRUPO[g % 6], curses.A_BOLD | (curses.A_REVERSE if sel else 0))
                else:
                    txt = " ▒▒ " if borde(f, c) else " ·· "
                    attr = d.c("oscuro" if not sel else "titulo", curses.A_REVERSE if sel else 0)
                d.put(win, yp + 1 + f * paso, x, txt, attr)
        yy = yp + (filas - 1) * paso + 3
        for i, partes in enumerate(estado):
            d.trozos(win, yy + i, x0 + 2, partes, x0 + w - 2)
        for i, l in enumerate(ayuda):
            d.put(win, yy + len(estado) + 1 + i, x0 + 2, l, d.c("tenue"), x0 + w - 2)
        win.refresh()
        k = d.tecla(win)
        if d.es(k, curses.KEY_UP, "w"):
            cur[0] = (cur[0] - 1) % filas
        elif d.es(k, curses.KEY_DOWN, "s"):
            cur[0] = (cur[0] + 1) % filas
        elif d.es(k, curses.KEY_LEFT):
            cur[1] = (cur[1] - 1) % cols
        elif d.es(k, curses.KEY_RIGHT, "d"):
            cur[1] = (cur[1] + 1) % cols
        elif (k in d.ENTER or k == " ") and pendientes and tuple(cur) not in pozos:
            pozos[tuple(cur)] = pendientes.pop(0)
            # avanza al siguiente pozo libre, como haría la mano
            for _ in range(filas * cols):
                cur[1] += 1
                if cur[1] >= cols:
                    cur[1] = 0
                    cur[0] = (cur[0] + 1) % filas
                if tuple(cur) not in pozos:
                    break
        elif d.es(k, "x") and tuple(cur) in pozos:
            pendientes.insert(0, pozos.pop(tuple(cur)))
        elif d.es(k, "a"):
            libres = [(f, c) for f in range(filas) for c in range(cols)]
            random.shuffle(libres)
            pozos = dict(zip(libres, muestras))
            pendientes = []
        elif d.es(k, "t") or k == d.ESC:
            if pendientes:
                lab.dibujar()
                d.popup(win, f"Faltan {len(pendientes)} tubos por sembrar.", "Placa de cultivo")
                continue
            return desbalance()


# ================================================================= terminal
def terminal(lab, titulo, contexto, prompt, opciones, validar, solucion, intentos=3):
    """Pantalla de terminal: muestra `contexto` (salida de programas) y una
    lista de comandos para elegir. opciones: [(lo que va después de `prompt`,
    qué hace)]. validar(texto) -> (valor o None, mensaje). Tras `intentos`
    fallos se marca la solución. Devuelve (valor, errores)."""
    win = lab.win
    historia = list(contexto)
    errores, sel, fallidas = 0, 0, set()
    while True:
        alto, ancho = win.getmaxyx()
        w = min(100, ancho - 2)
        lineas_op = []                       # (índice de opción, partes)
        for i, (cmd, que) in enumerate(opciones):
            if i == sel:
                color = "titulo"
            elif i in fallidas:
                color = "mal"
            elif errores >= intentos and cmd == solucion:
                color = "bien"
            else:
                color = "texto"
            marca = "► " if i == sel else "x " if i in fallidas else "  "
            lineas_op += [(i, l) for l in d.envolver_partes(
                [(marca + tr(prompt) + cmd, color, curses.A_BOLD)], w - 4, 4)]
            lineas_op += [(i, l) for l in d.envolver_partes(
                [("    " + tr(que), "tenue")], w - 4, 4)]
        planas = d.a_lineas(historia, w - 4)
        h = min(alto - 2, len(planas) + len(lineas_op) + 6)
        y0, x0 = (alto - h) // 2, (ancho - w) // 2
        d.limpiar_area(win, y0, x0, h, w)
        d.caja(win, y0, x0, h, w, titulo)
        # las opciones van abajo; si no cabe todo, se desplazan (sin bajar de 9
        # filas) y lo que sobre se recorta de la salida de arriba
        filas_ctx = min(len(planas), max(0, h - 5 - min(len(lineas_op), 9)))
        filas_op = h - 5 - filas_ctx
        primera = next(j for j, (i, _) in enumerate(lineas_op) if i == sel)
        ultima = max(j for j, (i, _) in enumerate(lineas_op) if i == sel)
        inicio = max(0, min(primera, ultima + 1 - filas_op))
        for k, partes in enumerate(planas[-filas_ctx:] if filas_ctx > 0 else []):
            d.trozos(win, y0 + 1 + k, x0 + 2, partes, x0 + w - 2)
        yo = y0 + h - 3 - filas_op
        for k, (_, partes) in enumerate(lineas_op[inicio:inicio + filas_op]):
            d.trozos(win, yo + k, x0 + 2, partes, x0 + w - 2)
        d.put(win, y0 + h - 2, x0 + 2, "↑↓ elegir · Enter ejecutar · Esc salir", d.c("tenue"))
        if filas_op < len(lineas_op):
            d.put(win, y0 + h - 2, x0 + w - 10, f"{sel + 1}/{len(opciones)}", d.c("agua"))
        win.refresh()
        k = d.tecla(win)
        if k == d.ESC:
            return None, errores
        if d.es(k, curses.KEY_UP, "w", "k"):
            sel = (sel - 1) % len(opciones)
        elif d.es(k, curses.KEY_DOWN, "s", "j"):
            sel = (sel + 1) % len(opciones)
        elif k in d.ENTER or k == " ":
            cmd = opciones[sel][0]
            historia.append(f"<bien>{tr(prompt)}{cmd}</>")
            valor, msg = validar(cmd)
            if valor is not None:
                historia.append(f"<agua>{msg}</>")
                lab.dibujar()
                d.popup(win, "\n".join(tr(h) for h in historia[-12:]), titulo, ancho=min(100, ancho - 2))
                return valor, errores
            errores += 1
            fallidas.add(sel)
            historia.append(f"<mal>{msg}</>")
            if errores >= intentos:
                historia.append(f"<titulo>Solución: {tr(prompt)}{solucion}</>")
