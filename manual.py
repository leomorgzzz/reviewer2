"""Pantallas de consulta: Manual del laboratorio, Catálogo de métodos y
Glosario."""


import dibujo as d
import metodos

COLOR_SECCION = {"Fundamentos": "g3", "Diseño": "agua", "Laboratorio": "titulo", "Análisis": "bien"}


def mostrar(win, juego=None):
    ents = metodos.entradas()
    nombres = [t for _, t, _, _ in ents]
    colores = [COLOR_SECCION[s] for _, _, _, s in ents]

    def contenido(i):
        _, titulo, lineas, sec = ents[i]
        return [f"<{COLOR_SECCION[sec]}!>{sec.upper()}</>  <titulo!>{titulo}</>", ""] + lineas

    d.navegador(win, "Manual del laboratorio", nombres, contenido, colores=colores)


def catalogo(win):
    nombres = [f"{m[1]}" for m in metodos.METODOS]
    paleta = ["agua", "titulo", "bien", "g3", "g1", "g2"]
    colores = [paleta[metodos.CATEGORIAS.index(m[0]) % len(paleta)] for m in metodos.METODOS]
    d.navegador(win, "Catálogo de métodos de transcriptómica", nombres,
                lambda i: metodos.ficha_metodo(metodos.METODOS[i]), colores=colores)


def glosario(win):
    lineas = []
    for termino, defin in metodos.GLOSARIO:
        lineas.append(f"<titulo!>{termino}</>  {defin}")
    d.visor(win, "Glosario", lineas)
