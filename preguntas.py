"""Examen de Comité y Repaso libre, con repaso espaciado."""

import curses
import random

import banco
import datos
import dibujo as d
import progreso
from idioma import tr


def generar(clave):
    tema, texto, opciones, expl, fuentes = banco.PREGUNTAS[clave]
    ops = list(opciones)
    random.shuffle(ops)
    return dict(texto=texto, opciones=ops, respuesta=opciones[0], tema=tema,
                explicacion=f"{expl} [{datos.cita(*fuentes.split())}]" if fuentes else expl)


def elegir(juego, excluir=()):
    claves = [k for k in banco.PREGUNTAS if k not in excluir] or list(banco.PREGUNTAS)
    pesos = [progreso.peso(juego, f"banco:{k}") for k in claves]
    return random.choices(claves, pesos)[0]


def preguntar(win, juego, p, clave_registro=None, titulo="Pregunta"):
    """Muestra la pregunta centrada. Devuelve True si acierta."""
    alto, ancho = win.getmaxyx()
    w = min(80, ancho - 4)
    texto = d.envolver(p["texto"], w - 4)
    ops = [d.envolver(f"{i + 1}) {o}", w - 8) for i, o in enumerate(p["opciones"])]
    h = len(texto) + sum(len(o) for o in ops) + 6
    y, x = max(0, (alto - h) // 2), (ancho - w) // 2
    d.limpiar_area(win, y, x, h, w)
    d.caja(win, y, x, h, w, f"{titulo} · {p['tema']}")
    for i, l in enumerate(texto):
        d.put(win, y + 1 + i, x + 2, l, d.c("texto", curses.A_BOLD))
    yy = y + 2 + len(texto)
    for o in ops:
        for l in o:
            d.put(win, yy, x + 4, l, d.c("texto"))
            yy += 1
    d.put(win, y + h - 2, x + 2, "Pulsa el número de tu respuesta", d.c("tenue"))
    win.refresh()
    while True:
        k = d.tecla(win)
        if isinstance(k, str) and k.isdigit() and 1 <= int(k) <= len(p["opciones"]):
            eleccion = p["opciones"][int(k) - 1]
            break
    d.limpiar_area(win, y, x, h, w)
    bien = eleccion == p["respuesta"]
    if clave_registro:
        progreso.registrar(juego, clave_registro, bien)
    if bien:
        d.popup(win, tr("Correcto. ") + tr(p["explicacion"]), "Resultado", ancho=74,
                attr=d.c("bien"))
    else:
        d.popup(win, f"Incorrecto. Era: {p['respuesta']}.\n\n{p['explicacion']}",
                "Resultado", ancho=74, attr=d.c("mal"))
    return bien


def examen(win, juego, n=20, minimo=16):
    win.erase()
    d.popup(win, f"Examen de Comité: {n} preguntas de diseño, laboratorio, análisis y "
                 f"métodos. Con {minimo} aciertos obtienes el título de <titulo!>Revisora o "
                 "Revisor 1</> (el amable). Las preguntas que más has fallado salen más "
                 "seguido.", "Examen de Comité")
    aciertos, vistas = 0, []
    for i in range(n):
        k = elegir(juego, vistas)
        vistas.append(k)
        win.erase()
        d.put(win, 0, 1, f"Examen de Comité · pregunta {i + 1}/{n} · aciertos {aciertos}",
              d.c("titulo", curses.A_BOLD))
        if preguntar(win, juego, generar(k), f"banco:{k}", f"Pregunta {i + 1}/{n}"):
            aciertos += 1
    juego["examen"] = max(juego["examen"] or 0, aciertos)
    progreso.guardar(juego)
    win.erase()
    if aciertos >= minimo:
        d.popup(win, f"{aciertos}/{n}. {progreso.nombre(juego)}, aprobaste: obtienes el título "
                     "de Revisor 1. Tus dictámenes "
                     "serán justos, citados y constructivos.", "Examen de Comité",
                attr=d.c("bien"))
    else:
        d.popup(win, f"{aciertos}/{n}. Te faltaron {minimo - aciertos}. Repasa el Manual y "
                     "el Catálogo y vuelve a intentarlo.", "Examen de Comité", attr=d.c("mal"))


def repaso(win, juego):
    racha = 0
    while True:
        k = elegir(juego)
        win.erase()
        d.put(win, 0, 1, f"Repaso libre · racha {racha}", d.c("titulo", curses.A_BOLD))
        racha = racha + 1 if preguntar(win, juego, generar(k), f"banco:{k}", "Repaso") else 0
        progreso.guardar(juego)
        if d.menu(win, "¿Otra pregunta?", ["Sí", "Volver"]) != 0:
            return
