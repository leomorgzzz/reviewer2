"""La mesa de diseño: el jugador arma el experimento, acomoda los lotes, lo
envía, ve los datos simulados (PCA y volcán) y recibe el dictamen del
Revisor 2."""

import curses
import math
import random

import animaciones as anim
import casos
import datos
import dibujo as d
from idioma import tr
import manual
import progreso
import protocolo
import revisor
import simulacion as sim

COLORES_LOTE = ["agua", "titulo", "mal", "bien", "g3", "g5", "g2", "g4"]
REVISOR = "Revisor 2"


def diseno_inicial(caso):
    """Lo que propondría un laboratorio sin asesoría: 2 réplicas, mucha
    profundidad y todo procesado en el orden de la lista."""
    dis = dict(biblioteca="polyA", lectura="PE100", profundidad=30, replicas=2, tecnicas=1,
               extras=[], ruta="star", entrada="crudas", prueba="deseq2", correccion="bh",
               formula="cond", lotes={})
    dis["lotes"] = sim.lotes_por_orden(dis, caso)
    return dis


# --------------------------------------------------------------- filas
# (tipo, clave, etiqueta, sección)
FILAS = [
    ("opcion", "biblioteca", "Biblioteca", "LABORATORIO"),
    ("numero", "replicas", "Réplicas biológicas por grupo", "LABORATORIO"),
    ("numero", "tecnicas", "Réplicas técnicas por muestra", "LABORATORIO"),
    ("lotes", "lotes", "Lotes de procesamiento", "LABORATORIO"),
    ("extra", "hebra", None, "LABORATORIO"),
    ("extra", "umi", None, "LABORATORIO"),
    ("extra", "ercc", None, "LABORATORIO"),
    ("opcion", "lectura", "Tipo de lectura", "SECUENCIACIÓN"),
    ("opcion", "profundidad", "Lecturas por muestra", "SECUENCIACIÓN"),
    ("opcion", "ruta", "Ruta de cuantificación", "ANÁLISIS"),
    ("opcion", "entrada", "Entrada al modelo", "ANÁLISIS"),
    ("opcion", "formula", "Fórmula de diseño", "ANÁLISIS"),
    ("opcion", "prueba", "Prueba estadística", "ANÁLISIS"),
    ("opcion", "correccion", "Pruebas múltiples", "ANÁLISIS"),
    ("extra", "filtro", None, "ANÁLISIS"),
    ("extra", "shrink", None, "ANÁLISIS"),
    ("extra", "splicing", None, "ANÁLISIS"),
    ("extra", "gsea", None, "ANÁLISIS"),
    ("extra", "decon", None, "ANÁLISIS"),
    ("enviar", None, "Enviar al Revisor 2", ""),
]

OPCIONES = {
    "biblioteca": (datos.ORDEN_BIBLIOTECAS, lambda k: datos.BIBLIOTECAS[k]["nombre"]),
    "lectura": (datos.ORDEN_LECTURAS, lambda k: datos.LECTURAS[k]["nombre"]),
    "profundidad": (datos.PROFUNDIDADES, lambda k: f"{k} M"),
    "ruta": (datos.ORDEN_RUTAS, lambda k: datos.RUTAS[k]["nombre"]),
    "entrada": (datos.ORDEN_ENTRADAS, lambda k: datos.ENTRADAS[k]["nombre"]),
    "formula": (datos.ORDEN_FORMULAS, lambda k: datos.FORMULAS[k]["nombre"]),
    "prueba": (datos.ORDEN_PRUEBAS, lambda k: datos.PRUEBAS[k]["nombre"]),
    "correccion": (datos.ORDEN_CORRECCIONES, lambda k: datos.CORRECCIONES[k]["nombre"]),
}


class Mesa:
    def __init__(self, win, juego, caso, dis=None, practica=False):
        self.win = win
        self.juego = juego
        self.caso = caso
        self.dif = juego["dificultad"]
        self.dis = dis or diseno_inicial(caso)
        self.sel = 0
        self.practica = practica
        self.pistas = revisor.DIFICULTADES[self.dif]["pistas"] or practica
        self.vel = juego["velocidad"]

    # ---------------------------------------------------------- textos
    def valor(self, fila):
        tipo, clave, _, _ = fila
        dis = self.dis
        if tipo == "opcion":
            return OPCIONES[clave][1](dis[clave])
        if tipo == "numero":
            return str(dis[clave])
        if tipo == "extra":
            return "[x]" if clave in dis["extras"] else "[ ]"
        if tipo == "lotes":
            t = sim.tabla_lotes(dis, self.caso)
            partes = []
            for l, fila_n in t.items():
                partes.append(f"L{l + 1}:" + "".join(
                    f"{self.caso['abrev'][g]}{n}" for g, n in enumerate(fila_n) if n))
            return " · ".join(partes)[:40] + "  [Enter]"
        return ""

    def etiqueta(self, fila):
        tipo, clave, et, _ = fila
        if tipo == "extra":
            return datos.EXTRAS[clave]["nombre"]
        return et

    def info(self, fila):
        """Líneas de explicación de la opción seleccionada."""
        tipo, clave, _, _ = fila
        dis = self.dis
        if tipo == "opcion":
            if clave == "biblioteca":
                b = datos.BIBLIOTECAS[dis[clave]]
                return [f"<titulo!>{b['nombre']}</>  <tenue>${b['costo']} por muestra</>",
                        b["resumen"], "", f"<bien>Cuándo:</> {b['cuando']}",
                        f"<mal>Ojo:</> {b['malo']}",
                        f"<tenue>{datos.cita(*b['fuente'].split())}</>"]
            if clave == "lectura":
                l_ = datos.LECTURAS[dis[clave]]
                return [f"<titulo!>{l_['nombre']}</>  <tenue>${l_['costo']} por millón</>",
                        l_["texto"], f"<tenue>{datos.cita('CON16')}</>"]
            if clave == "profundidad":
                extra = ""
                if dis["biblioteca"] in ("sc10x", "snrna"):
                    extra = (f" ≈ {datos.lecturas_por_celula(dis['profundidad']):,} lecturas "
                             f"por célula ({datos.SC_CELULAS:,} células por muestra).")
                return ["<titulo!>Lecturas por muestra</>",
                        "Más lecturas = más cuentas por gen, con rendimientos decrecientes. "
                        "Guía: 3′ tag 3-10 M · small RNA 2-10 M · genes 10-30 M · lncRNA "
                        "40-60 M · isoformas 50-100 M." + extra,
                        f"<tenue>{datos.cita('LIU14', 'CON16', 'ENC')}</>"]
            tablas = {"ruta": datos.RUTAS, "entrada": datos.ENTRADAS, "formula": datos.FORMULAS,
                      "prueba": datos.PRUEBAS, "correccion": datos.CORRECCIONES}
            x = tablas[clave][dis[clave]]
            lineas = [f"<titulo!>{x['nombre']}</>", x["texto"]]
            if "fuente" in x:
                lineas.append(f"<tenue>{datos.cita(*x['fuente'].split())}</>")
            elif clave == "formula":
                lineas.append(f"<tenue>{datos.cita('DESV')}</>")
            return lineas
        if tipo == "numero":
            if clave == "replicas":
                return ["<titulo!>Réplicas biológicas</>",
                        "Unidades experimentales independientes por grupo (animales, "
                        "pacientes, cultivos separados). Sin ellas no hay estadística. "
                        "Mínimo 3; Schurch 2016 recomienda ≥ 6.",
                        f"Disponibles en este caso: hasta {self.caso['max_replicas']}.",
                        f"<tenue>{datos.cita('SCH16', 'CON16')}</>"]
            return ["<titulo!>Réplicas técnicas</>",
                    "La misma muestra preparada o secuenciada otra vez. Solo miden ruido "
                    "técnico (casi Poisson).", f"<tenue>{datos.cita('MAR08')}</>"]
        if tipo == "extra":
            x = datos.EXTRAS[clave]
            costo = f"  <tenue>+${x['costo']} por muestra</>" if x["costo"] else ""
            return [f"<titulo!>{x['nombre']}</>{costo}", x["texto"],
                    f"<tenue>{datos.cita(*x['fuente'].split())}</>"]
        if tipo == "lotes":
            cap = self.caso.get("capacidad")
            return ["<titulo!>Lotes de procesamiento</>",
                    (f"El laboratorio procesa como máximo {cap} muestras por lote "
                     f"(extracción y biblioteca el mismo día). Necesitas "
                     f"{sim.n_lotes_necesarios(self.dis, self.caso)} lote(s)."
                     if cap else "No hay límite: todas las muestras caben en un lote."),
                    "Enter abre la mesa de lotes: ahí ves qué muestra va en qué día.",
                    f"<tenue>{datos.cita('LEE10', 'AUE10')}</>"]
        return ["<titulo!>Enviar</>", "El experimento se «realiza» (simulación) y el "
                "Revisor 2 dictamina.", "Puedes corregir y reenviar las veces que quieras."]

    # ---------------------------------------------------------- dibujo
    def dibujar(self):
        win = self.win
        alto, ancho = win.getmaxyx()
        win.erase()
        caso, dis = self.caso, self.dis
        costo = datos.costo_total(dis, caso)
        tope = revisor.presupuesto(caso, self.dif)
        d.put(win, 0, 1, f"{caso['titulo']} · {caso['investigador']}",
              d.c("titulo", curses.A_BOLD))
        d.put(win, 1, 1, caso["pregunta"], d.c("texto"))
        d.put(win, 2, 1, f"{caso['organismo']} · {caso['muestra']}", d.c("tenue"))
        ancho_izq = min(78, ancho - 2) if ancho >= 120 else ancho - 2
        y = 4
        seccion = None
        self.posiciones = []
        visibles_max = alto - (6 if ancho >= 120 else 13)
        # ventana de filas que se ven
        todas = []
        for i, fila in enumerate(FILAS):
            if fila[3] != seccion and fila[3]:
                todas.append(("sec", fila[3]))
                seccion = fila[3]
            todas.append(("fila", i))
        pos_sel = next(j for j, t in enumerate(todas) if t == ("fila", self.sel))
        ini = max(0, min(pos_sel - visibles_max // 2, len(todas) - visibles_max))
        for t in todas[ini:ini + visibles_max]:
            if t[0] == "sec":
                d.put(win, y, 1, f"── {t[1]} " + "─" * max(0, ancho_izq - len(t[1]) - 5),
                      d.c("tenue"))
            else:
                i = t[1]
                fila = FILAS[i]
                marca = "► " if i == self.sel else "  "
                if fila[0] == "enviar":
                    color = "bien" if costo <= tope else "mal"
                    d.put(win, y, 1, marca + fila[2],
                          d.c(color, curses.A_BOLD | (curses.A_REVERSE if i == self.sel else 0)))
                else:
                    et = self.etiqueta(fila)
                    val = self.valor(fila)
                    attr_e = d.c("titulo", curses.A_BOLD) if i == self.sel else d.c("texto")
                    flechas = "◄ " if fila[0] in ("opcion", "numero") and i == self.sel else "  "
                    xv = 1 + min(36, ancho_izq // 2)
                    d.put(win, y, 1, f"{marca}{et}", attr_e, xv - 1)
                    if fila[0] == "lotes":
                        self._lotes_corto(y, xv)
                    else:
                        d.put(win, y, xv, flechas + val + (" ►" if flechas.strip() else ""),
                              d.c("agua" if fila[0] != "extra" else
                                  ("bien" if fila[1] in dis["extras"] else "oscuro"),
                                  curses.A_BOLD if i == self.sel else 0), ancho_izq)
            y += 1
        # panel de información
        if ancho >= 120:
            ix, iy, iw, ih = ancho_izq + 3, 4, ancho - ancho_izq - 5, alto - 8
        else:
            ix, iy, iw, ih = 1, y + 1, ancho - 3, alto - y - 4
        d.caja(win, iy, ix, ih, iw, "Ficha")
        lineas = d.a_lineas(self.info(FILAS[self.sel]), iw - 4)
        if self.pistas and ih > 14 and ancho >= 120:
            lineas += [[]] + d.a_lineas(["<agua!>Pistas del caso [P]</>"]
                                         + ["· " + p for p in revisor.pistas(caso)], iw - 4)
        for k, partes in enumerate(lineas[: ih - 2]):
            d.trozos(win, iy + 1 + k, ix + 2, partes, ix + iw - 2)
        # pie: presupuesto y potencia
        yb = alto - 3
        d.put(win, yb, 1, "Presupuesto ", d.c("tenue"))
        d.barra(win, yb, 13, 30, costo, max(tope, costo), d.c("bien" if costo <= tope else "mal"))
        d.put(win, yb, 45, f"${costo:,} / ${tope:,}  ·  {datos.n_muestras(dis, caso)} bibliotecas",
              d.c("bien" if costo <= tope else "mal", curses.A_BOLD))
        if self.dif != "dificil":
            pot = sim.potencia_aprox(dis, caso)
            s = caso["sim"]
            fc = 2 ** (s["lfc_min"] + 0.6 * s["lfc_sd"])
            d.put(win, yb + 1, 1, "Potencia ", d.c("tenue"))
            d.barra(win, yb + 1, 13, 30, pot, 1, d.c("agua"))
            d.put(win, yb + 1, 45, f"{pot:.0%} (gen típico que cambia {fc:.1f}×)",
                  d.c("agua", curses.A_BOLD))
        ayuda = (tr("↑↓ fila · ←→ cambiar · Espacio marcar · L lotes · C caso · M manual · "
                    "T catálogo · ") + (tr("P pistas · ") if self.pistas else "") + tr("Q salir"))
        d.put(win, alto - 1, 1, ayuda[: ancho - 2], d.c("tenue"))
        win.refresh()

    def _lotes_corto(self, y, x):
        t = sim.tabla_lotes(self.dis, self.caso)
        conf = sim.confusion_lote(self.dis, self.caso)
        xx = x + 2
        for l, fila_n in t.items():
            d.put(self.win, y, xx, f"L{l + 1}:", d.c(COLORES_LOTE[l % 8], curses.A_BOLD))
            xx += len(f"L{l + 1}:")
            for g, n in enumerate(fila_n):
                if n:
                    txt = f"{self.caso['abrev'][g]}{n}"
                    d.put(self.win, y, xx, txt, d.c(d.COLORES_GRUPO[g % 6]))
                    xx += len(txt)
            xx += 2
        if self.pistas and conf in ("total", "parcial"):
            d.put(self.win, y, xx, "¡confundido!", d.c("mal", curses.A_BOLD))
        elif sim.sobrecupo(self.dis, self.caso):
            d.put(self.win, y, xx, "¡sobrecupo!", d.c("mal", curses.A_BOLD))

    # ---------------------------------------------------------- cambios
    def cambiar(self, paso):
        tipo, clave, _, _ = FILAS[self.sel]
        dis = self.dis
        if tipo == "opcion":
            lista = OPCIONES[clave][0]
            i = lista.index(dis[clave]) if dis[clave] in lista else 0
            dis[clave] = lista[(i + paso) % len(lista)]
            if clave == "biblioteca":
                larga = datos.BIBLIOTECAS[dis[clave]]["larga"]
                if larga and dis["lectura"] != "LARGA":
                    dis["lectura"] = "LARGA"
                elif not larga and dis["lectura"] == "LARGA":
                    dis["lectura"] = "PE100"
        elif tipo == "numero":
            tope = self.caso["max_replicas"] if clave == "replicas" else 3
            dis[clave] = max(1, min(tope, dis[clave] + paso))
            if clave == "replicas":
                dis["lotes"] = sim.lotes_por_orden(dis, self.caso)
        elif tipo == "extra":
            self.alternar(clave)

    def alternar(self, clave):
        if clave in self.dis["extras"]:
            self.dis["extras"].remove(clave)
        else:
            self.dis["extras"].append(clave)

    # ---------------------------------------------------------- bucle
    def jugar(self):
        """Devuelve el resultado de calificar() del último envío o None."""
        self.ultimo = None
        while True:
            self.dibujar()
            k = d.tecla(self.win)
            fila = FILAS[self.sel]
            if d.es(k, curses.KEY_UP, "w", "k"):
                self.sel = (self.sel - 1) % len(FILAS)
            elif d.es(k, curses.KEY_DOWN, "s", "j"):
                self.sel = (self.sel + 1) % len(FILAS)
            elif d.es(k, curses.KEY_LEFT, "a"):
                self.cambiar(-1)
            elif d.es(k, curses.KEY_RIGHT, "d"):
                self.cambiar(1)
            elif d.es(k, "l"):
                self.mesa_lotes()
            elif k == " " or k in d.ENTER:
                if fila[0] == "extra":
                    self.alternar(fila[1])
                elif fila[0] == "lotes":
                    self.mesa_lotes()
                elif fila[0] == "enviar":
                    if self.enviar() == "salir":
                        return self.ultimo
                elif k == " ":
                    self.cambiar(1)
            elif d.es(k, "c"):
                d.dialogo(self.win, self.caso["intro"] or ["(experimento propio)"],
                          self.caso["investigador"], fondo=self.dibujar)
            elif d.es(k, "m"):
                manual.mostrar(self.win, self.juego)
            elif d.es(k, "t"):
                manual.catalogo(self.win)
            elif d.es(k, "p") and self.pistas:
                d.popup(self.win, "\n".join("· " + p for p in revisor.pistas(self.caso)),
                        "Pistas del caso", ancho=76)
            elif d.es(k, "q") or k == d.ESC:
                if d.menu(self.win, "¿Salir de la mesa?", ["Seguir diseñando",
                                                            "Volver a la oficina"]) == 1:
                    self.juego["disenos"][self.caso["id"]] = self.dis
                    progreso.guardar(self.juego)
                    return self.ultimo

    # ------------------------------------------------------- mesa de lotes
    def mesa_lotes(self):
        mesa_lotes(self.win, self.caso, self.dis, self.pistas, self.dif)

    # -------------------------------------------------------------- envío
    def enviar(self):
        caso, dis = self.caso, self.dis
        win = self.win
        costo = datos.costo_total(dis, caso)
        tope = revisor.presupuesto(caso, self.dif)
        if costo > tope:
            d.popup(win, f"El diseño cuesta <mal!>${costo:,}</> y el presupuesto es de "
                         f"${tope:,}. Recorta antes de enviarlo.", "Comité de finanzas")
            return None
        anim.secuenciacion(win, datos.n_muestras(dis, caso), self.vel)
        res = sim.simular(dis, caso, random.Random())
        comentarios = revisor.revisar(dis, caso, res, self.dif)
        cal = revisor.calificar(dis, caso, res, comentarios, self.dif)
        self.juego["disenos"][caso["id"]] = {k: (list(v) if isinstance(v, list) else
                                                 dict(v) if isinstance(v, dict) else v)
                                             for k, v in dis.items()}
        pantalla_resultados(win, caso, dis, res)
        anim.sello(win, cal["dictamen"], cal["color"], self.vel)
        mostrar_dictamen(win, caso, comentarios, cal, revisor.meta(caso, self.dif),
                         libre=caso.get("libre"))
        self.ultimo = cal
        if cal["aprobado"] and caso in casos.CASOS and not self.practica:
            i = casos.CASOS.index(caso)
            self.juego["desbloqueado"] = max(self.juego["desbloqueado"], i + 1)
        if not caso.get("libre") and not self.practica:
            previo = progreso.mejor(self.juego, caso["id"], self.dif)
            if previo is None or (cal["estrellas"], cal["sens"]) > (previo["estrellas"], previo["sens"]):
                self.juego["mejores"].setdefault(caso["id"], {})[self.dif] = cal
        progreso.guardar(self.juego)
        if cal["aprobado"] and caso.get("leccion"):
            d.popup(win, f"<bien!>Lección del caso.</> {caso['leccion']}\n\n"
                         f"<tenue>{datos.cita(*caso['fuentes'].split())}</>",
                    "Dra. Lazo", ancho=74)
        while True:
            op = d.menu(win, "¿Ahora qué?", ["Ajustar el diseño y reenviar",
                                             "Exportar el protocolo completo",
                                             "Ver otra vez los datos y el dictamen",
                                             "Volver a la oficina"])
            if op == 1:
                ruta = protocolo.generar(dis, caso, comentarios, res, self.dif,
                                         autor=progreso.nombre(self.juego))
                self.juego["protocolos"].append(ruta)
                progreso.guardar(self.juego)
                d.popup(win, f"Protocolo guardado en:\n\n<agua>{ruta}</>\n\nIncluye la hoja de "
                             "muestras (CSV), comandos, código de R, criterios de QC, "
                             "el dictamen y las referencias.", "Protocolo", ancho=80)
            elif op == 2:
                pantalla_resultados(win, caso, dis, res)
                mostrar_dictamen(win, caso, comentarios, cal, revisor.meta(caso, self.dif),
                                 libre=caso.get("libre"))
            elif op == 3:
                return "salir"
            else:
                return cal


def mesa_lotes(win, caso, dis, pistas=False, dif="normal", titulo=None):
    """Pantalla para repartir las réplicas biológicas en lotes (días de
    procesamiento, bancas…). Modifica dis["lotes"]."""
    nombre = caso.get("lote_nombre", "lote")
    col, fil = 0, 0
    while True:
        n_lotes = max(sim.n_lotes_necesarios(dis, caso),
                      max(dis["lotes"].values(), default=0) + 1)
        if not caso.get("capacidad"):
            n_lotes = max(n_lotes, 1)
        columnas = [[] for _ in range(n_lotes)]
        excluidas = set(dis.get("excluidas", ()))
        for g in range(len(caso["grupos"])):
            for r in range(dis["replicas"]):
                if f"{g}-{r}" not in excluidas:
                    columnas[dis["lotes"].get(f"{g}-{r}", 0)].append((g, r))
        col = min(col, n_lotes - 1)
        fil = min(fil, max(0, len(columnas[col]) - 1))
        alto, ancho = win.getmaxyx()
        win.erase()
        d.put(win, 0, 1, titulo or f"Mesa de {nombre}s", d.c("titulo", curses.A_BOLD))
        cap = caso.get("capacidad")
        d.put(win, 1, 1, (f"Capacidad: {cap} muestras por {nombre}." if cap else
                          "Sin límite de capacidad.") +
              (" Cada par de muestras de un donante va junta." if caso.get("pareado") else ""),
              d.c("tenue"))
        ancho_col = max(14, min(22, (ancho - 4) // max(1, n_lotes)))
        for li, muestras in enumerate(columnas):
            x = 1 + li * ancho_col
            lleno = len(muestras) * dis["tecnicas"]
            d.caja(win, 3, x, min(alto - 9, max(len(muestras), 3) + 3), ancho_col - 1,
                   f"{nombre.capitalize()} {li + 1}", color_titulo=COLORES_LOTE[li % 8])
            d.put(win, 4, x + 2, f"{lleno}/{cap}" if cap else f"{lleno}",
                  d.c("mal" if cap and lleno > cap else "tenue"))
            for j, (g, r) in enumerate(muestras[: alto - 14]):
                marca = "►" if (li == col and j == fil) else " "
                etiqueta = f"{caso['abrev'][g]}{r + 1} {caso['grupos'][g]}"[: ancho_col - 5]
                attr = d.c(d.COLORES_GRUPO[g % 6],
                           curses.A_REVERSE if (li == col and j == fil) else 0)
                d.put(win, 5 + j, x + 1, marca + etiqueta, attr)
        conf = sim.confusion_lote(dis, caso)
        mensajes = {
            "total": (f"Cada {nombre} tiene un solo grupo: {nombre} y condición confundidos.",
                      "mal"),
            "parcial": (f"Hay {nombre}s con un solo grupo: confusión parcial.", "mal"),
            "desbalance": (f"Todos los {nombre}s tienen todos los grupos, pero "
                           "desbalanceados.", "titulo"),
            "ninguna": (f"Sin confusión entre {nombre} y condición.", "bien"),
        }
        if pistas or dif != "dificil":
            txt, color = mensajes[conf]
            d.put(win, alto - 4, 1, txt, d.c(color, curses.A_BOLD))
        if sim.sobrecupo(dis, caso):
            d.put(win, alto - 5, 1, f"Algún {nombre} pasa la capacidad.",
                  d.c("mal", curses.A_BOLD))
        d.put(win, alto - 2, 1, (f"←→↑↓ elegir · Enter mover al {nombre} siguiente · "
                                 f"B bloques al azar · O por orden · + otro {nombre} · "
                                 "Esc terminar")[: ancho - 2], d.c("tenue"))
        win.refresh()
        k = d.tecla(win)
        if d.es(k, curses.KEY_LEFT, "a", "h"):
            col = (col - 1) % n_lotes
        elif d.es(k, curses.KEY_RIGHT, "d", "l"):
            col = (col + 1) % n_lotes
        elif d.es(k, curses.KEY_UP, "w", "k"):
            fil = max(0, fil - 1)
        elif d.es(k, curses.KEY_DOWN, "s", "j"):
            fil += 1
        elif (k in d.ENTER or k == " ") and columnas[col]:
            g, r = columnas[col][fil]
            destino = (col + 1) % n_lotes
            claves = [f"{gg}-{r}" for gg in range(len(caso["grupos"]))] \
                if caso.get("pareado") else [f"{g}-{r}"]
            for cl in claves:
                dis["lotes"][cl] = destino
        elif d.es(k, "b"):
            dis["lotes"] = sim.lotes_balanceados(dis, caso)
        elif d.es(k, "o"):
            dis["lotes"] = sim.lotes_por_orden(dis, caso)
        elif k == "+" and n_lotes < 8:
            # un lote vacío nuevo: se mueve ahí la muestra elegida
            if columnas[col]:
                g, r = columnas[col][fil]
                dis["lotes"][f"{g}-{r}"] = n_lotes
        elif k == d.ESC or d.es(k, "q"):
            # compactar: que no queden lotes vacíos en medio
            usados = sorted(set(dis["lotes"].values()))
            ren = {v: i for i, v in enumerate(usados)}
            dis["lotes"] = {kk: ren[v] for kk, v in dis["lotes"].items()}
            return


# ------------------------------------------------------------ resultados
def _lienzo(h, w):
    return [[(" ", "oscuro") for _ in range(w)] for _ in range(h)]


def grafica_pca(caso, dis, pca, h, w):
    """Devuelve filas de partes con la PCA: letra = grupo, color = lote."""
    mts = sim.muestras(dis, caso)
    lz = _lienzo(h, w)
    xs = [c[0] for c in pca["coords"]]
    ys = [c[1] for c in pca["coords"]]
    def esc(v, lo, hi, n):
        return 0 if hi - lo < 1e-9 else round((v - lo) / (hi - lo) * (n - 1))
    for j, m in enumerate(mts):
        cx = esc(xs[j], min(xs), max(xs), w)
        cy = h - 1 - esc(ys[j], min(ys), max(ys), h)
        lz[cy][cx] = (caso["abrev"][m["grupo"]], COLORES_LOTE[m["lote"] % 8])
    return [[(ch, col, curses.A_BOLD) for ch, col in fila] for fila in lz]


def grafica_volcan(volcan, h, w):
    lz = _lienzo(h, w)
    prio = {"oscuro": 0, "agua": 1, "bien": 2, "mal": 3}
    ymax = max([-math.log10(max(p, 1e-300)) for _, p, _, _ in volcan] + [5])
    ymax = min(ymax, 60)
    for lfc, p, sig, real in volcan:
        x = round((max(-4, min(4, lfc)) + 4) / 8 * (w - 1))
        y = h - 1 - round(min(-math.log10(max(p, 1e-300)), ymax) / ymax * (h - 1))
        if sig and real:
            ch, col = "•", "bien"
        elif sig:
            ch, col = "×", "mal"
        elif real:
            ch, col = "°", "agua"
        else:
            ch, col = "·", "oscuro"
        if prio[col] >= prio[lz[y][x][1]] or lz[y][x][0] == " ":
            lz[y][x] = (ch, col)
    mid = (w - 1) // 2
    for y in range(h):
        if lz[y][mid][0] == " ":
            lz[y][mid] = ("¦", "oscuro")
    return lz


def pantalla_resultados(win, caso, dis, res):
    while True:
        alto, ancho = win.getmaxyx()
        win.erase()
        d.put(win, 0, 1, "Los datos llegaron", d.c("titulo", curses.A_BOLD))
        y = 2
        if res["estado"] == "no_estimable":
            d.put(win, y, 1, f"El modelo no se pudo ajustar: {res['motivo']}.",
                  d.c("mal", curses.A_BOLD))
            y += 2
        elif res["estado"] == "sin_replicas":
            d.put(win, y, 1, "Sin réplicas no quedan grados de libertad: no hay valores p.",
                  d.c("mal", curses.A_BOLD))
            y += 2
        else:
            partes = [("Significativos: ", "tenue"), (f"{res['sig']}", "texto", curses.A_BOLD),
                      ("  (↑", "tenue"), (f"{res['subidos']}", "texto"), (" ↓", "tenue"),
                      (f"{res['bajados']}", "texto"), (")   verdaderos: ", "tenue"),
                      (f"{res['tp']}", "bien", curses.A_BOLD), ("   falsos: ", "tenue"),
                      (f"{res['fp']}", "mal", curses.A_BOLD)]
            d.trozos(win, y, 1, partes)
            partes = [("Sensibilidad (lo real que encontraste): ", "tenue"),
                      (f"{res['sens']:.0%}", "agua", curses.A_BOLD),
                      (f" de {res['verdad']}", "tenue"),
                      ("   FDR observado: ", "tenue"),
                      (f"{res['fdr']:.0%}", "mal" if res["fdr"] > 0.1 else "bien", curses.A_BOLD)]
            d.trozos(win, y + 1, 1, partes)
            y += 3
        for nota in res["notas"]:
            d.put(win, y, 1, "· " + nota, d.c("titulo"))
            y += 1
        gh = max(8, min(16, alto - y - 6))
        if ancho >= 110:
            gw = (ancho - 8) // 2
            pos = [(y, 1), (y, gw + 5)]
        else:
            gw = ancho - 6
            gh = max(6, (alto - y - 8) // 2)
            pos = [(y, 1), (y + gh + 3, 1)]
        # PCA
        py, px = pos[0]
        if res.get("pca"):
            var = res["pca"]["var"]
            d.put(win, py, px, f"PCA · PC1 {var[0]:.0%} (horizontal) · PC2 {var[1]:.0%}",
                  d.c("titulo", curses.A_BOLD))
            for i, fila in enumerate(grafica_pca(caso, dis, res["pca"], gh, gw - 2)):
                d.put(win, py + 1 + i, px, "│", d.c("oscuro"))
                d.trozos(win, py + 1 + i, px + 1, fila)
            ley = [("letra = grupo: ", "tenue")]
            for g, n in enumerate(caso["grupos"][:6]):
                ley.append((f"{caso['abrev'][g]} {n}  ", "texto"))
            d.trozos(win, py + gh + 1, px, ley, px + gw)
            ley = [("color = lote: ", "tenue")]
            for l in range(len(sim.tabla_lotes(dis, caso))):
                ley.append((f"L{l + 1} ", COLORES_LOTE[l % 8], curses.A_BOLD))
            d.trozos(win, py + gh + 2, px, ley, px + gw)
        # volcán
        vy, vx = pos[1]
        if res.get("volcan"):
            d.put(win, vy, vx, "Volcán · log2FC (−4…4) vs −log10 p",
                  d.c("titulo", curses.A_BOLD))
            for i, fila in enumerate(grafica_volcan(res["volcan"], gh, gw - 2)):
                d.put(win, vy + 1 + i, vx, "│", d.c("oscuro"))
                d.trozos(win, vy + 1 + i, vx + 1, fila)
            d.trozos(win, vy + gh + 1, vx, [("• ", "bien"), ("verdadero  ", "tenue"),
                                            ("× ", "mal"), ("falso positivo  ", "tenue"),
                                            ("° ", "agua"), ("real no detectado  ", "tenue"),
                                            ("· ", "oscuro"), ("sin cambio", "tenue")])
        d.put(win, alto - 1, 1, "En un experimento real no sabrías qué es verdadero: aquí sí. "
              "[Enter] ver el dictamen"[: ancho - 2], d.c("tenue"))
        win.refresh()
        k = d.tecla(win)
        if k != curses.KEY_RESIZE:
            return


def mostrar_dictamen(win, caso, comentarios, cal, meta, libre=False, nombre=None,
                     con_nota=False):
    nombres = {"fatal": ("FATAL", "mal"), "mayor": ("MAYOR", "mal"),
               "menor": ("menor", "titulo"), "bien": ("bien", "bien")}
    lineas = [f"<{cal['color']}!>{cal['dictamen']}</>", ""]
    if con_nota:
        lineas.append("<tenue>Tu calificación y la retroalimentación vienen en la siguiente "
                      "pantalla.</>")
        lineas.append("")
    elif not libre:
        if cal["alcanza"]:
            lineas.append(f"<bien>Resultados: sensibilidad {cal['sens']:.0%} (meta "
                          f"{meta:.0%}) con FDR {cal['fdr']:.0%}.</>")
        else:
            lineas.append(f"<mal>Resultados: sensibilidad {cal['sens']:.0%} (meta {meta:.0%}), "
                          f"FDR {cal['fdr']:.0%} (máximo 15 %).</>")
        if cal["aprobado"]:
            lineas.append(tr("<titulo!>Caso resuelto ") + d.estrellas(cal["estrellas"]) + "</>")
        lineas.append("")
    for x in comentarios:
        et, color = nombres[x["grav"]]
        fuente = datos.cita(*x["fuente"].split())
        lineas.append(f"<{color}!>[{et}]</> {x['texto']}"
                      + (f" <tenue>({fuente})</>" if fuente else ""))
        lineas.append("")
    titulo = f"Dictamen del {REVISOR} para {nombre}" if nombre else f"Dictamen del {REVISOR}"
    d.visor(win, titulo, lineas, ayuda="Enter/Esc continuar")
