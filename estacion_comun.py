"""Lo que comparten las estaciones: el formulario de ←→, los diálogos con
la Dra. Lazo y el técnico, y el cobro de cada etapa."""

import curses
import dibujo as d
from idioma import tr
import expediente as X


MENTORA = "Dra. Lazo"
TECNICO = "Técnico del laboratorio"


# ================================================================ formulario
class Formulario:
    """Hoja con filas que se cambian con ←→ (como la mesa de diseño)."""

    def __init__(self, win, titulo, filas, pie=None, subtitulo=None):
        self.win, self.titulo, self.filas = win, titulo, filas
        self.pie, self.subtitulo = pie, subtitulo
        self.sel = next(i for i, f in enumerate(filas) if f["tipo"] != "seccion")

    @staticmethod
    def _ops(f):
        return f["opciones"]() if callable(f["opciones"]) else f["opciones"]

    def _valor(self, f):
        if f["tipo"] == "opcion":
            v = f["get"]()
            return next((t for k, t in self._ops(f) if k == v), "— elige —")
        if f["tipo"] == "numero":
            return str(f["get"]())
        if f["tipo"] == "check":
            return "[x]" if f["get"]() else "[ ]"
        if f["tipo"] == "info":
            return f["texto"]()
        return ""

    def _ficha(self, f):
        cabeza = []
        if f["tipo"] in ("opcion", "info"):
            # el valor completo: en la fila puede no caber
            completo = self._valor(f)
            if completo and completo != "— elige —":
                cabeza = [f"<agua!>Elegido:</> {completo}", ""]
        if "costo" in f:
            extra = f["costo"]()
            if extra:
                cabeza.append(f"<titulo!>Costo:</> {extra}")
                cabeza.append("")
        if "ficha" in f:
            v = f["get"]() if "get" in f else None
            return cabeza + f["ficha"](v)
        if f["tipo"] == "opcion":
            return cabeza + [f"<titulo!>{f['etiqueta']}</>", "Usa ←→ para elegir."]
        return cabeza + [f"<titulo!>{f['etiqueta']}</>"]

    def dibujar(self):
        win = self.win
        alto, ancho = win.getmaxyx()
        win.erase()
        d.put(win, 0, 1, self.titulo, d.c("titulo", curses.A_BOLD))
        if self.subtitulo:
            d.put(win, 1, 1, self.subtitulo, d.c("tenue"))
        ancho_izq = min(84, ancho - 2) if ancho >= 120 else ancho - 2
        largo = max([len(tr(f["etiqueta"])) for f in self.filas
                     if f["tipo"] in ("opcion", "numero", "info")] + [0])
        xv = 1 + min(max(34, largo + 4), ancho_izq // 2)
        y = 3
        pie = self.pie() if self.pie else []
        max_filas = alto - 5 - len(pie) - (0 if ancho >= 120 else 7)
        ini = max(0, min(self.sel - max_filas // 2, len(self.filas) - max_filas))
        for i, f in enumerate(self.filas[ini:ini + max_filas], start=ini):
            if f["tipo"] == "seccion":
                et = tr(f["etiqueta"])
                d.put(win, y, 1, f"── {et} " + "─" * max(0, ancho_izq - len(et) - 5), d.c("tenue"))
            else:
                es = i == self.sel
                marca = "► " if es else "  "
                if f["tipo"] == "accion":
                    d.put(win, y, 1, marca + tr(f["etiqueta"]),
                          d.c(f.get("color", "bien"), curses.A_BOLD | (curses.A_REVERSE if es else 0)))
                elif f["tipo"] == "check":
                    # la casilla va antes para que la etiqueta use todo el ancho
                    d.put(win, y, 1, marca, d.c("titulo", curses.A_BOLD))
                    d.put(win, y, 3, self._valor(f),
                          d.c("bien" if f["get"]() else "oscuro", curses.A_BOLD if es else 0))
                    d.put(win, y, 7, tr(f["etiqueta"]),
                          d.c("titulo", curses.A_BOLD) if es else d.c("texto"), ancho_izq)
                else:
                    d.put(win, y, 1, marca + tr(f["etiqueta"]),
                          d.c("titulo", curses.A_BOLD) if es else d.c("texto"), xv - 1)
                    val = tr(self._valor(f))
                    flechas = es and f["tipo"] in ("opcion", "numero")
                    color = f.get("color", "tenue") if f["tipo"] == "info" else "agua"
                    d.put(win, y, xv, ("◄ " if flechas else "  ") + val + (" ►" if flechas else ""),
                          d.c(color, curses.A_BOLD if es else 0), ancho_izq)
            y += 1
        if ancho >= 120:
            ix, iy, iw, ih = ancho_izq + 3, 3, ancho - ancho_izq - 5, alto - 5 - len(pie)
        else:
            ix, iy, iw, ih = 1, y + 1, ancho - 3, max(4, alto - y - 3 - len(pie))
        d.caja(win, iy, ix, ih, iw, "Ficha")
        for k, partes in enumerate(d.a_lineas(self._ficha(self.filas[self.sel]), iw - 4)[: ih - 2]):
            d.trozos(win, iy + 1 + k, ix + 2, partes, ix + iw - 2)
        for k, l in enumerate(pie):
            d.trozos(win, alto - 1 - len(pie) + k, 1, d.marcado(l, "tenue"), ancho - 1)
        d.put(win, alto - 1, 1, "↑↓ fila · ←→ cambiar · Espacio/Enter marcar o ejecutar · "
              "Esc salir"[: ancho - 2], d.c("tenue"))
        win.refresh()

    def mover(self, paso):
        n = len(self.filas)
        i = self.sel
        for _ in range(n):
            i = (i + paso) % n
            if self.filas[i]["tipo"] != "seccion":
                self.sel = i
                return

    def cambiar(self, paso):
        f = self.filas[self.sel]
        if f["tipo"] == "opcion":
            claves = [k for k, _ in self._ops(f)]
            v = f["get"]()
            i = claves.index(v) if v in claves else (-1 if paso > 0 else 0)
            f["set"](claves[(i + paso) % len(claves)])
        elif f["tipo"] == "numero":
            f["set"](max(f["min"], min(f["max"], f["get"]() + paso)))
        elif f["tipo"] == "check":
            f["set"](not f["get"]())

    def jugar(self):
        while True:
            self.dibujar()
            k = d.tecla(self.win)
            f = self.filas[self.sel]
            if d.es(k, curses.KEY_UP, "w", "k"):
                self.mover(-1)
            elif d.es(k, curses.KEY_DOWN, "s", "j"):
                self.mover(1)
            elif d.es(k, curses.KEY_LEFT, "a"):
                self.cambiar(-1)
            elif d.es(k, curses.KEY_RIGHT, "d"):
                self.cambiar(1)
            elif k == " " or k in d.ENTER:
                if f["tipo"] == "accion":
                    return f["clave"]
                self.cambiar(1)
            elif k == d.ESC or d.es(k, "q"):
                return None


def decir(lab, texto, quien=MENTORA):
    lab.dibujar()
    d.popup(lab.win, texto, quien, ancho=72)


def menu(lab, titulo, opciones, **kw):
    """Menú sobre el laboratorio recién dibujado (para que no se apilen)."""
    lab.dibujar()
    return d.menu(lab.win, titulo, opciones, **kw)


def pagar(lab, monto, concepto):
    """Muestra el costo ANTES de gastar. Si no alcanza, ofrece pedir una
    ampliación al investigador (hasta +50 % del presupuesto) o volver a
    ajustar. Devuelve True si se pagó."""
    exp = lab.exp
    monto = round(monto)
    while True:
        queda = lab.tope - exp["gastado"]
        if monto <= queda:
            op = menu(lab, tr(concepto) + f": ${monto:,}", [
                f"Pagar (te quedan ${queda - monto:,} de ${lab.tope:,})",
                "Todavía no: quiero ajustar"])
            if op != 0:
                return False
            exp["gastado"] += monto
            return True
        falta = monto - queda
        maximo = round(lab.tope_base * 0.5) - sum(exp["ampliaciones"])
        opciones = []
        if falta <= maximo:
            opciones.append(f"Pedir ${falta:,} más al investigador (queda en tu calificación)")
        opciones.append("Volver a ajustar el diseño (menos réplicas, menos lecturas…)")
        op = menu(lab, f"{concepto}: ${monto:,} · solo te quedan ${queda:,}", opciones)
        if op == 0 and len(opciones) == 2:
            exp["ampliaciones"].append(falta)
            decir(lab, f"El investigador consiguió ${falta:,} más, pero no le hizo gracia. "
                        "Los fondos extra cuentan en tu calificación final.",
                   lab.caso["investigador"])
            continue
        if falta > maximo:
            decir(lab, "El investigador ya no tiene más dinero. Regresa a una etapa "
                        "anterior desde la computadora o el papel de diseño y recorta: "
                        "menos réplicas técnicas, menos lecturas por muestra o una "
                        "biblioteca más barata.", "Comité de finanzas")
        return False


def cobrar(lab, etapa):
    nombres = {1: "Preparar las unidades experimentales", 2: "Reactivos de extracción",
               4: "Kits de biblioteca", 5: "Corrida de secuenciación"}
    return pagar(lab, X.costo_etapa(lab.exp, lab.caso, etapa), nombres[etapa])
