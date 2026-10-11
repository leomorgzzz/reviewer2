"""El laboratorio explorable: un plano con cuartos, estaciones y personas.

Te mueves con flechas/WASD; E o Enter usa la estación o habla con la persona
que tengas al lado. El panel muestra las etapas del experimento, el día y el
presupuesto. Cada etapa se hace en su estación y en orden.
"""

import curses
import os
import random

import datos
import dibujo as d
from idioma import tr
import estaciones as E
import expediente as X
import lab_datos as L
import manual
import progreso
import revisor
import simulacion as sim

ACCIONES = {
    "papel": E.papel, "librero": E.librero, "investigador": E.investigador,
    "replica": E.replica, "unidades": E.unidades, "calendario": E.calendario,
    "tecnico": E.tecnico, "nanodrop": lambda lab: E.qc(lab, 0),
    "gel": lambda lab: E.qc(lab, 1), "bioanalizador": lambda lab: E.qc(lab, 2),
    "secuenciador": E.secuenciador, "buzon": E.buzon, "campana": E.campana,
    "congelador": E.congelador, "kits": E.kits, "computadora": E.computadora,
    "cuaderno": E.cuaderno,
}
PERSONAS = {"investigador", "replica", "tecnico"}
# estaciones que no preguntan antes de rehacer una etapa terminada (las demás
# ya ofrecen «Volver» primero)
SIN_AVISO_PROPIO = {"unidades", "nanodrop", "gel", "bioanalizador", "computadora"}
DEPURAR = os.environ.get("REVISOR2_POS")      # solo para pruebas automáticas


def construir_plano(lugar, lugar_clave=None):
    """Rejilla de caracteres: '#' muro, '.' piso, 'm' mueble, ' ' fuera."""
    g = [[" "] * L.ANCHO for _ in range(L.ALTO)]
    for nombre, x0, y0, x1, y1 in L.CUARTOS:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                borde = y in (y0, y1) or x in (x0, x1)
                if borde and g[y][x] != ".":
                    g[y][x] = "#"
                elif not borde:
                    g[y][x] = "."
    for x, y in L.PUERTAS:
        g[y][x] = "."
    for x, y, _ch, _color in L.mobiliario(lugar_clave):
        if g[y][x] == ".":
            g[y][x] = "m"
    for nombre, (x, y, *_r) in L.ESTACIONES.items():
        g[y][x] = "E"
    return g


def _eje(p, c, vista, total):
    if vista >= total:
        return -(vista - total) // 2            # el plano cabe: centrado
    margen = vista // 5
    if c is None or not c + margen <= p < c + vista - margen:
        c = p - vista // 2
    return max(0, min(c, total - vista))


class Lab:
    def __init__(self, win, juego, caso, practica=False):
        self.win, self.juego, self.caso = win, juego, caso
        self.dif = juego["dificultad"]
        self.pistas = revisor.DIFICULTADES[self.dif]["pistas"] or practica
        self.tope_base = revisor.presupuesto(caso, self.dif)
        self.lugar = X.lugar(caso)
        guardado = juego.setdefault("expedientes", {}).get(caso["id"])
        self.exp = guardado or X.nuevo(caso)
        self.exp.setdefault("resultado_visto", False)
        self.exp.setdefault("ampliaciones", [])
        self.exp.setdefault("minijuegos", {})
        self.lugar_clave = X.info(caso)["lugar"]
        self.plano = construir_plano(self.lugar, self.lugar_clave)
        self.muebles = {(x, y): (ch, color) for x, y, ch, color in L.mobiliario(self.lugar_clave)}
        # sin puntos de piso en las puertas ni pegados a muebles y estaciones
        self.liso = set(L.PUERTAS) | {
            (x + dx, y) for y, fila in enumerate(self.plano) for x, c in enumerate(fila)
            if c in "mE" for dx in (-1, 1)}
        # una partida guardada con otro plano puede dejar al jugador dentro de un mueble
        px, py = self.exp["pos"]
        if self.plano[py][px] != ".":
            self.exp["pos"] = list(min(
                ((x, y) for y in range(L.ALTO) for x in range(L.ANCHO) if self.plano[y][x] == "."),
                key=lambda p: abs(p[0] - px) + abs(p[1] - py)))
        self.terminar = False
        self._camara = {}         # (ancho, alto) de la vista -> última esquina
        self.mensaje = "Habla con el investigador (☺ ) y con la Dra. Lazo (☻ ) en la oficina."

    @property
    def tope(self):
        return self.tope_base + sum(self.exp.get("ampliaciones", []))

    # ------------------------------------------------------------ utilidades
    def guardar(self):
        self.juego["expedientes"][self.caso["id"]] = self.exp
        progreso.guardar(self.juego)

    def hallar(self, clave):
        if clave not in self.exp["hallazgos"]:
            self.exp["hallazgos"].append(clave)

    def preguntas_papel(self):
        caso = self.caso
        malas = [p.format(org=caso["organismo"], grupo=caso["grupos"][-1], ref=caso["grupos"][0])
                 for p in L.PREGUNTAS_MALAS]
        return [caso["pregunta"]] + malas

    def analizar(self):
        """Simula con la misma semilla mientras no se repita el laboratorio:
        volver a correr el análisis no cambia los datos."""
        semilla = self.exp.get("semilla", 1) * 7 + self.exp.get("semilla_sec", 0)
        return sim.simular(datos.provisional(self.exp["dis"]), self.caso, random.Random(semilla))

    # --------------------------------------------------------------- dibujo
    def estacion_cerca(self):
        """La estación más cercana a dos pasos de lado o uno arriba/abajo: el
        rótulo sigue al símbolo y es fácil quedar a dos casillas."""
        px, py = self.exp["pos"]
        cerca = [(abs(x - px) + abs(y - py), nombre) for nombre, (x, y, *_r) in L.ESTACIONES.items()
                 if abs(x - px) <= 2 and abs(y - py) <= 1]
        return min(cerca)[1] if cerca else None

    def dibujar(self):
        win = self.win
        alto, ancho = win.getmaxyx()
        win.erase()
        # el panel va primero: el mapa se recorre con el personaje
        panel_w = 34 if ancho >= 80 + 34 and alto >= 26 else 0
        vista_w = ancho - panel_w - 1
        vista_h = alto - (3 if panel_w else 6)
        px, py = self.exp["pos"]
        ox, oy = self.camara(px, py, vista_w, vista_h)
        siguiente = L.ETAPAS[min(self.exp["etapa"], 7)][1]
        for sy in range(vista_h):
            y = oy + sy
            if not 0 <= y < L.ALTO:
                continue
            # las celdas seguidas del mismo color van en un solo put; los
            # íconos que pueden salir anchos (☺ ♣…) van solos
            corrida, color_c, x0 = [], None, 0
            for sx in range(max(0, -ox), min(vista_w, L.ANCHO - ox)):
                x = ox + sx
                c = self.plano[y][x]
                if c == "#":
                    ch, color = "█", "oscuro"
                elif c == "m":
                    ch, color = self.muebles[(x, y)]
                elif c == ".":
                    ch = "·" if (x * 3 + y * 5) % 11 == 0 and (x, y) not in self.liso else " "
                    color = "oscuro"
                else:
                    ch, color = " ", "oscuro"
                solo = not L.seguro(ch)
                if corrida and (color != color_c or solo):
                    d.put(win, sy, x0, "".join(corrida), d.c(color_c))
                    corrida = []
                if not corrida:
                    color_c, x0 = color, sx
                corrida.append(ch)
                if solo:
                    d.put(win, sy, x0, ch, d.c(color))
                    corrida = []
            if corrida:
                d.put(win, sy, x0, "".join(corrida), d.c(color_c))
        # nombres de cuartos
        for nombre, x0, y0, x1, y1 in L.CUARTOS:
            if nombre == "PASILLO" or not 0 <= y0 - oy < vista_h:
                continue
            n = f" {tr(nombre.replace('{lugar}', self.lugar))} "
            d.put(win, y0 - oy, x0 - ox + 2, n, d.c("tenue", curses.A_BOLD), vista_w)
        # estaciones
        for nombre, (x, y, glifo, color, etiqueta, etapa) in L.ESTACIONES.items():
            sx, sy = x - ox, y - oy
            if not (0 <= sy < vista_h and 0 <= sx < vista_w):
                continue
            destacada = nombre == siguiente or (siguiente == "nanodrop" and nombre in ("gel", "bioanalizador"))
            hecha = etapa is not None and etapa < self.exp["etapa"]
            attr = d.c(color, curses.A_BOLD | (curses.A_REVERSE if destacada else 0))
            d.put(win, sy, sx, glifo, attr)
            d.put(win, sy, sx + 2, tr(etiqueta) + (" √ " if hecha else " "),
                  d.c("bien" if hecha else ("titulo" if destacada else "tenue")), vista_w)
        # jugador
        d.put(win, py - oy, px - ox, "@", d.c("titulo", curses.A_BOLD))
        if panel_w:
            self.panel(ancho - panel_w, panel_w, alto)
            yb = alto - 2
        else:
            yb = alto - 5
            self.panel_corto(yb)
        cerca = self.estacion_cerca()
        msg = (f"E/Enter: {L.ESTACIONES[cerca][4]}" if cerca else self.mensaje)
        d.put(win, alto - 2, 1, msg[: ancho - 2], d.c("agua", curses.A_BOLD))
        d.put(win, alto - 1, 1, "Flechas/WASD mover · E usar · N cuaderno · M manual · "
              "H ayuda · Q salir"[: ancho - 2], d.c("tenue"))
        win.refresh()

    def camara(self, px, py, vista_w, vista_h):
        """Esquina de la vista. Se queda quieta mientras el jugador no se
        acerque a un borde y entonces lo recentra: si se moviera en cada paso,
        toda la pantalla cambiaría y en Windows redibujarla entera es lento."""
        ox, oy = self._camara.get((vista_w, vista_h), (None, None))
        ox, oy = _eje(px, ox, vista_w, L.ANCHO), _eje(py, oy, vista_h, L.ALTO)
        self._camara[(vista_w, vista_h)] = (ox, oy)
        return ox, oy

    def panel(self, x, w, alto):
        win, exp, caso = self.win, self.exp, self.caso
        d.caja(win, 0, x, alto - 2, w, caso["titulo"][: w - 6])
        y = 1
        for l in d.envolver(caso["investigador"], w - 4)[:2]:
            d.put(win, y, x + 2, l, d.c("tenue"))
            y += 1
        y += 1
        d.put(win, y, x + 2, f"Día {exp['dia']}", d.c("texto", curses.A_BOLD))
        y += 1
        d.put(win, y, x + 2, f"${exp['gastado']:,} / ${self.tope:,}",
              d.c("bien" if exp["gastado"] <= self.tope else "mal"))
        y += 1
        d.barra(win, y, x + 2, w - 4, exp["gastado"], self.tope, d.c("titulo"))
        y += 1
        proy = X.proyeccion(exp, self.caso)
        d.put(win, y, x + 2, f"Proyectado: ${proy:,}",
              d.c("bien" if proy <= self.tope else "mal", curses.A_BOLD))
        y += 1
        if exp["ampliaciones"]:
            d.put(win, y, x + 2, f"Ampliaciones: +${sum(exp['ampliaciones']):,}", d.c("titulo"))
            y += 1
        y += 1
        d.put(win, y, x + 2, "ETAPAS", d.c("titulo", curses.A_BOLD))
        y += 1
        for i, (nombre, est, cuarto) in enumerate(L.ETAPAS):
            if i < exp["etapa"]:
                marca, color = "√", "bien"
            elif i == exp["etapa"]:
                marca, color = "►", "titulo"
            else:
                marca, color = "·", "oscuro"
            d.put(win, y, x + 2, f"{marca} {tr(nombre)}"[: w - 4],
                  d.c(color, curses.A_BOLD if i == exp["etapa"] else 0))
            y += 1
        y += 1
        if exp["etapa"] < len(L.ETAPAS):
            nombre, est, cuarto = L.ETAPAS[exp["etapa"]]
            for l in d.envolver(f"Siguiente: {L.ESTACIONES[est][4]} ({cuarto.replace('{lugar}', self.lugar.lower()).lower()})", w - 4):
                d.put(win, y, x + 2, l, d.c("agua"))
                y += 1
        y += 1
        d.put(win, y, x + 2, f"Pistas encontradas: {len(exp['hallazgos'])}", d.c("tenue"))

    def panel_corto(self, y):
        exp = self.exp
        marcas = "".join("√" if i < exp["etapa"] else ("►" if i == exp["etapa"] else "·")
                         for i in range(len(L.ETAPAS)))
        nombre = L.ETAPAS[min(exp["etapa"], 7)][0]
        d.put(self.win, y, 1, f"{self.caso['titulo']} · día {exp['dia']} · "
              f"${exp['gastado']:,}/${self.tope:,} · {marcas} {tr(nombre)}", d.c("titulo"))

    # ---------------------------------------------------------------- bucle
    def mover(self, dx, dy):
        x, y = self.exp["pos"]
        nx, ny = x + dx, y + dy
        if 0 <= nx < L.ANCHO and 0 <= ny < L.ALTO and self.plano[ny][nx] == ".":
            self.exp["pos"] = [nx, ny]
            if DEPURAR:
                with open(DEPURAR, "w") as f:
                    f.write(f"[{nx}, {ny}]")

    def usar(self):
        cerca = self.estacion_cerca()
        if not cerca:
            self.mensaje = "Aquí no hay nada. Acércate a una estación o persona."
            return
        etapa = L.ESTACIONES[cerca][5]
        if etapa is not None and etapa < self.exp["etapa"] and cerca in SIN_AVISO_PROPIO:
            # un Enter de más no debe rehacer (ni cobrar otra vez) una etapa terminada
            if d.menu(self.win, tr(f"{tr(L.ESTACIONES[cerca][4])}: esta etapa ya está hecha"),
                      ["No, sigo con lo que toca", "Sí, volver a abrirla"]) != 1:
                return
        ACCIONES[cerca](self)
        if cerca == "papel" and self.exp["etapa"] >= 1:
            self.mensaje = f"Siguiente: unidades en el {self.lugar.lower()}."

    def ayuda(self):
        d.visor(self.win, "Cómo se juega en el laboratorio", [
            "Muévete con las flechas o WASD. Junto a una estación o persona, pulsa <titulo!>E</> "
            "o Enter.",
            "",
            "<titulo!>Etapas</> (en orden; la estación que toca brilla):",
            "  1. <titulo>Papel de diseño</> (oficina): pregunta, hipótesis, unidad experimental, "
            "réplicas y qué anotar.",
            f"  2. <titulo>Unidades</> ({self.lugar.lower()}): asignar tratamientos y repartir "
            "en lotes.",
            "  3. <titulo>Campana</> (laboratorio húmedo): extraer el ARN.",
            "  4. <titulo>NanoDrop, gel y Bioanalyzer</> (cuarto de QC): revisar y decidir cada "
            "muestra.",
            "  5. <titulo>Estante de kits</>: la biblioteca.",
            "  6. <titulo>Secuenciador</>: plataforma, lectura, profundidad. Esperar.",
            "  7. <titulo>Computadora</> (bioinformática): análisis, resultados, decidir.",
            "  8. <titulo>Buzón</>: mandar al Revisor 2.",
            "",
            "<titulo!>Investigar</>: el investigador (☺ ), la Dra. Lazo (☻ ), el técnico, el "
            "calendario y el congelador tienen información que no viene en el encargo.",
            "",
            "Puedes regresar a cualquier etapa desde la computadora (cuesta días y dinero), "
            "o reescribir el diseño en el papel. N abre el cuaderno, donde también se exporta "
            "el protocolo.",
        ])

    def jugar(self):
        if not self.exp["hallazgos"] and self.exp["etapa"] == 0 and self.exp["dia"] == 1:
            self.win.erase()
            saludo = (f"Hola, <titulo!>{progreso.nombre(self.juego)}</>. Me dijeron en el "
                      "núcleo que tú te encargas de mi experimento.")
            d.dialogo(self.win, [saludo] + L.intro_sin_pista(self.caso),
                      f"{self.caso['titulo']} · {self.caso['investigador']}")
            if self.juego.get("ayuda_lab_vista") is None:
                self.ayuda()
                self.juego["ayuda_lab_vista"] = True
        while not self.terminar:
            self.dibujar()
            k = d.tecla(self.win)
            if d.es(k, curses.KEY_UP, "w"):
                self.mover(0, -1)
            elif d.es(k, curses.KEY_DOWN, "s"):
                self.mover(0, 1)
            elif d.es(k, curses.KEY_LEFT, "a"):
                self.mover(-1, 0)
            elif d.es(k, curses.KEY_RIGHT, "d"):
                self.mover(1, 0)
            elif d.es(k, "e") or k in d.ENTER or k == " ":
                self.usar()
            elif d.es(k, "n"):
                E.cuaderno(self)
            elif d.es(k, "m"):
                manual.mostrar(self.win)
            elif d.es(k, "h", "?"):
                self.ayuda()
            elif d.es(k, "q") or k == d.ESC:
                if d.menu(self.win, "¿Salir del laboratorio?",
                          ["No, sigo aquí", "Sí, guardar y volver al menú"]) == 1:
                    self.guardar()
                    return
        self.guardar()
