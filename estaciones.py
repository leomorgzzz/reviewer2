"""Las estaciones del laboratorio: cada una es una etapa del experimento o un
lugar donde investigar.

  papel → unidades → campana → QC (NanoDrop, gel, Bioanalyzer) → kits →
  secuenciador → computadora → buzón del Revisor 2

Cada función recibe la Partida del laboratorio (laboratorio.Lab) y regresa
cuando el jugador se aleja de la estación.
"""

import curses
import math
import random

import animaciones as anim
import calificacion
import minijuegos as mj
import datos
import dibujo as d
from idioma import tr
import expediente as X
import lab_datos as L
import manual
import mesa
import progreso
import protocolo
import revisor
import simulacion as sim

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


def _decir(lab, texto, quien=MENTORA):
    lab.dibujar()
    d.popup(lab.win, texto, quien, ancho=72)


def _menu(lab, titulo, opciones, **kw):
    """Menú sobre el laboratorio recién dibujado (para que no se apilen)."""
    lab.dibujar()
    return d.menu(lab.win, titulo, opciones, **kw)


def _pagar(lab, monto, concepto):
    """Muestra el costo ANTES de gastar. Si no alcanza, ofrece pedir una
    ampliación al investigador (hasta +50 % del presupuesto) o volver a
    ajustar. Devuelve True si se pagó."""
    exp = lab.exp
    monto = round(monto)
    while True:
        queda = lab.tope - exp["gastado"]
        if monto <= queda:
            op = _menu(lab, f"{concepto}: ${monto:,}", [
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
        op = _menu(lab, f"{concepto}: ${monto:,} · solo te quedan ${queda:,}", opciones)
        if op == 0 and len(opciones) == 2:
            exp["ampliaciones"].append(falta)
            _decir(lab, f"El investigador consiguió ${falta:,} más, pero no le hizo gracia. "
                        "Los fondos extra cuentan en tu calificación final.",
                   lab.caso["investigador"])
            continue
        if falta > maximo:
            _decir(lab, "El investigador ya no tiene más dinero. Regresa a una etapa "
                        "anterior desde la computadora o el papel de diseño y recorta: "
                        "menos réplicas técnicas, menos lecturas por muestra o una "
                        "biblioteca más barata.", "Comité de finanzas")
        return False


def _cobrar(lab, etapa):
    nombres = {1: "Preparar las unidades experimentales", 2: "Reactivos de extracción",
               4: "Kits de biblioteca", 5: "Corrida de secuenciación"}
    return _pagar(lab, X.costo_etapa(lab.exp, lab.caso, etapa), nombres[etapa])


# ============================================================ investigación
def librero(lab):
    while True:
        op = _menu(lab, "Librero", ["Manual del laboratorio", "Catálogo de métodos",
                                         "Glosario", "Volver"])
        if op == 0:
            manual.mostrar(lab.win)
        elif op == 1:
            manual.catalogo(lab.win)
        elif op == 2:
            manual.glosario(lab.win)
        else:
            return


def investigador(lab):
    caso = lab.caso
    resp = L.respuestas(caso)
    preguntas = list(resp) + ["Cuéntame otra vez del proyecto", "Nada más, gracias"]
    while True:
        op = _menu(lab, caso["investigador"], preguntas)
        if op is None or op == len(preguntas) - 1:
            return
        if op == len(preguntas) - 2:
            d.dialogo(lab.win, L.intro_sin_pista(caso), caso["investigador"], fondo=lab.dibujar)
        else:
            lab.hallar(f"inv:{op}")
            _decir(lab, resp[preguntas[op]], caso["investigador"])


def replica(lab):
    exp = lab.exp
    etapa = min(exp["etapa"], len(L.ETAPAS) - 1)
    nombre, est, cuarto = L.ETAPAS[etapa]
    consejos = {
        0: "En el papel define la pregunta, una hipótesis que se pueda refutar, la unidad "
           "experimental y cuántas réplicas. Anota qué vas a registrar de cada muestra.",
        1: "Asigna los tratamientos al azar y reparte las unidades en los días o bancas "
           "para que cada bloque tenga todos los grupos.",
        2: "Elige el método de extracción según la muestra y lo que quieres medir. "
           "Trabaja libre de RNasas.",
        3: "Revisa cada muestra en NanoDrop, gel y Bioanalyzer. Íntegro, puro y sin ADN: "
           "si no, re-extrae o excluye.",
        4: "El kit depende de lo que quieres medir. Pocos ciclos de PCR y limpia los "
           "dímeros.",
        5: "Elige plataforma, lectura y profundidad. Todas las muestras en todos los "
           "carriles.",
        6: "Arma el análisis en la computadora. Primero mira la PCA; después decide.",
        7: "Si el análisis responde la pregunta, lleva el manuscrito al buzón.",
    }
    lab.hallar("replica")
    d.dialogo(lab.win, [
        f"<titulo!>{progreso.nombre(lab.juego)}</>, lo que me preocupa de este caso: "
        f"{L.pista_replica(lab.caso)}",
        f"<titulo!>Siguiente paso: {nombre}</> ({cuarto.replace('{lugar}', lab.lugar.lower())}). "
        + consejos.get(etapa, ""),
    ], MENTORA, fondo=lab.dibujar)


def tecnico(lab):
    lab.hallar("tecnico")
    _decir(lab, X.info(lab.caso)["tecnico"] or "Aquí ando, por si necesitas algo.", TECNICO)


def calendario(lab):
    lab.hallar("calendario")
    _decir(lab, X.info(lab.caso)["calendario"] or "Sin restricciones esta semana.",
           "Calendario de la pared")


def congelador(lab):
    lab.hallar("congelador")
    txt = X.info(lab.caso)["congelador"] or lab.caso["muestra"]
    _decir(lab, txt, "Congelador −80 °C")


def cuaderno(lab):
    """Resumen de todo lo decidido y exportar el protocolo."""
    exp, caso = lab.exp, lab.caso
    info = X.info(caso)
    dis = exp["dis"]
    l = [f"<titulo!>{caso['titulo']}</> · día {exp['dia']} · gastado ${exp['gastado']:,} de "
         f"${lab.tope:,}", ""]
    if exp["pregunta"] is not None:
        l.append(f"<agua>Pregunta:</> {lab.preguntas_papel()[exp['pregunta']]}")
    if exp["hipotesis"] is not None:
        l.append(f"<agua>Hipótesis:</> {info['hipotesis'][exp['hipotesis']]}"
                 + ("  <mal>(cambiada después de ver datos)</>" if exp["harking"] else ""))
    if exp["unidad"] is not None:
        l.append(f"<agua>Unidad experimental:</> {L.UNIDADES[info['lugar']][exp['unidad']]}")
    if exp["etapa"] >= 1:
        l.append(f"<agua>Réplicas:</> {dis['replicas']} biológicas por grupo · "
                 f"{dis['tecnicas']} técnica(s)")
    if exp["etapa"] >= 2:
        l.append(f"<agua>Asignación:</> {exp['asignacion'] or 'no aplica (observacional)'} · "
                 f"{len(sim.tabla_lotes(dis, caso))} {caso.get('lote_nombre', 'lote')}(s)")
    if exp["extraccion"]:
        l.append(f"<agua>Extracción:</> {L.EXTRACCIONES[exp['extraccion']]['nombre']}")
    if exp["qc"]:
        est = [q["estado"] for q in exp["qc"].values()]
        l.append(f"<agua>QC:</> {est.count('aprobada')} aprobadas · {est.count('excluida')} "
                 f"excluidas · {exp['reextracciones']} re-extracciones")
    if exp["etapa"] >= 5:
        l.append(f"<agua>Biblioteca:</> {datos.BIBLIOTECAS[dis['biblioteca']]['nombre']} · "
                 f"{exp['pcr']} ciclos · extras: "
                 + (", ".join(datos.EXTRAS[e]["nombre"] for e in dis["extras"]
                              if e in ("hebra", "umi", "ercc")) or "ninguno"))
    if exp["etapa"] >= 6:
        l.append(f"<agua>Secuenciación:</> {L.PLATAFORMAS[exp['plataforma']]['nombre']} · "
                 f"{datos.LECTURAS[dis['lectura']]['nombre']} · {dis['profundidad']} M")
    if exp["corridas"]:
        l.append(f"<agua>Análisis:</> {exp['corridas']} corrida(s) · "
                 f"{datos.RUTAS[dis['ruta']]['nombre']} · {datos.FORMULAS[dis['formula']]['nombre']}")
    l += ["", f"<tenue>Pistas encontradas: {len(exp['hallazgos'])}</>"]
    k = d.visor(lab.win, "Cuaderno de laboratorio", l,
                ayuda="P exportar protocolo · Esc volver", salir=["p"])
    if d.es(k, "p"):
        ruta = protocolo.generar(dis, caso, None, None, lab.dif, exp,
                                 progreso.nombre(lab.juego))
        lab.juego["protocolos"].append(ruta)
        progreso.guardar(lab.juego)
        d.popup(lab.win, f"Protocolo guardado en:\n\n<agua>{ruta}</>", "Protocolo", ancho=80)


# ===================================================== 0 · papel de diseño
def papel(lab):
    exp, caso = lab.exp, lab.caso
    info = X.info(caso)
    dis = exp["dis"]
    if exp["etapa"] > 0:
        if _menu(lab, "El diseño ya está firmado", ["Solo verlo", "Reescribirlo (todo lo "
                                                         "demás se rehace)"]) != 1:
            cuaderno(lab)
            return
        X.regresar(exp, 0)
    preguntas = lab.preguntas_papel()
    if exp["hipotesis_orden"] is None:
        orden = list(range(len(info["hipotesis"])))
        random.shuffle(orden)
        exp["hipotesis_orden"] = orden
    hip = [(i, info["hipotesis"][i]) for i in exp["hipotesis_orden"]]
    unidades = list(enumerate(L.UNIDADES[info["lugar"]]))

    def pon(clave):
        return lambda v: exp.__setitem__(clave, v)

    def reps(v):
        dis["replicas"] = v
        dis["lotes"] = sim.lotes_por_orden(dis, caso)

    def registro(clave):
        def get():
            return clave in exp["registros"]

        def set_(v):
            if v and clave not in exp["registros"]:
                exp["registros"].append(clave)
            elif not v and clave in exp["registros"]:
                exp["registros"].remove(clave)
        return get, set_

    filas = [
        dict(tipo="seccion", etiqueta="LA PREGUNTA"),
        dict(tipo="opcion", etiqueta="Pregunta de investigación",
             opciones=list(enumerate(preguntas)), get=lambda: exp["pregunta"],
             set=pon("pregunta"),
             ficha=lambda v: ["<titulo!>Pregunta de investigación</>",
                              preguntas[v] if v is not None else "Usa ←→.",
                              "", "Una buena pregunta compara condiciones concretas y se "
                              "puede responder midiendo ARN.",
                              f"<tenue>{datos.cita('CON16')}</>"]),
        dict(tipo="opcion", etiqueta="Hipótesis", opciones=hip, get=lambda: exp["hipotesis"],
             set=pon("hipotesis"),
             ficha=lambda v: ["<titulo!>Hipótesis</>",
                              info["hipotesis"][v] if v is not None else "Usa ←→.", "",
                              "Se escribe ANTES de ver datos. Debe decir qué esperas que "
                              "cambie y en qué dirección, para poder refutarla."]),
        dict(tipo="opcion", etiqueta="¿Qué vas a medir?", opciones=L.OBJETIVOS,
             get=lambda: exp["objetivo"], set=pon("objetivo"),
             ficha=lambda v: ["<titulo!>Qué vas a medir</>", "Decide la biblioteca, la "
                              "lectura y el análisis más adelante.",
                              f"<tenue>{datos.cita('CON16')}</>"]),
        dict(tipo="seccion", etiqueta="LAS RÉPLICAS"),
        dict(tipo="info", etiqueta="Grupos", texto=lambda: " · ".join(caso["grupos"])[:44]),
        dict(tipo="opcion", etiqueta="Unidad experimental", opciones=unidades,
             get=lambda: exp["unidad"], set=pon("unidad"),
             ficha=lambda v: ["<titulo!>Unidad experimental</>",
                              "Lo que recibe el tratamiento de forma independiente. Es tu "
                              "réplica biológica: si eliges algo que no es independiente, "
                              "las réplicas se parecen demasiado (pseudoreplicación).",
                              f"<tenue>{datos.cita('AUE10', 'CON16')}</>"]),
        dict(tipo="numero", etiqueta="Réplicas biológicas por grupo", min=1,
             max=caso["max_replicas"], get=lambda: dis["replicas"], set=reps,
             ficha=lambda v: ["<titulo!>Réplicas biológicas</>",
                              f"Disponibles: hasta {caso['max_replicas']} por grupo.",
                              "Mínimo 3; Schurch 2016 recomienda ≥ 6.",
                              f"<tenue>{datos.cita('SCH16', 'LIU14')}</>"]),
        dict(tipo="numero", etiqueta="Réplicas técnicas por muestra", min=1, max=3,
             get=lambda: dis["tecnicas"], set=lambda v: dis.__setitem__("tecnicas", v),
             ficha=lambda v: ["<titulo!>Réplicas técnicas</>", "La misma muestra medida "
                              "otra vez: solo ruido técnico, casi Poisson.",
                              f"<tenue>{datos.cita('MAR08')}</>"]),
        dict(tipo="info", etiqueta="Potencia aproximada",
             texto=lambda: f"{sim.potencia_aprox(dict(dis, profundidad=20), caso):.0%} "
                           "(a 20 M lecturas)",
             color="agua"),
        dict(tipo="seccion", etiqueta="HOJA DE MUESTRAS: QUÉ VAS A ANOTAR"),
    ]
    for clave, texto in L.REGISTROS:
        g, s = registro(clave)
        filas.append(dict(tipo="check", etiqueta=texto, get=g, set=s,
                          ficha=lambda v, t=texto: [f"<titulo!>{t}</>",
                                                    "Lo que no anotes hoy no se puede poner "
                                                    "en el modelo mañana.",
                                                    f"<tenue>{datos.cita('LEE10', 'FGED')}</>"]))
    filas.append(dict(tipo="accion", clave="firmar", etiqueta="Firmar el diseño"))
    def pie():
        proy = X.proyeccion(exp, caso)
        color = "bien" if proy <= lab.tope else "mal"
        return [f"Costo proyectado del experimento completo: <{color}!>${proy:,}</> de "
                f"${lab.tope:,} (se recalcula al cambiar réplicas; lecturas y kits se "
                "eligen después)"]

    form = Formulario(lab.win, "Papel de diseño experimental", filas, pie,
                      subtitulo=caso["pregunta"] if exp["hallazgos"] else
                      "Habla con el investigador antes de escribir.")
    while True:
        if form.jugar() is None:
            return
        faltan = [n for n, v in (("pregunta", exp["pregunta"]), ("hipótesis", exp["hipotesis"]),
                                 ("qué medir", exp["objetivo"]), ("unidad", exp["unidad"]))
                  if v is None]
        if faltan:
            _decir(lab, "Falta elegir: " + ", ".join(faltan) + ".")
            continue
        break
    dis["pseudo"] = exp["unidad"] != info["unidad"]
    exp["hipotesis_original"] = exp["hipotesis"]
    X.avanzar(exp, 0)
    lab.guardar()
    if lab.pistas:
        notas = []
        if exp["pregunta"] != 0:
            notas.append("La pregunta no compara condiciones concretas.")
        if exp["hipotesis"] != 0:
            notas.append("La hipótesis es vaga o no se puede poner a prueba con ARN.")
        if exp["unidad"] != info["unidad"]:
            notas.append("Esa unidad experimental no es independiente.")
        if exp["objetivo"] != L.objetivo_esperado(caso):
            notas.append("¿Seguro que eso es lo que quiere medir el investigador?")
        if dis["replicas"] < 3:
            notas.append("Menos de 3 réplicas no permite estadística.")
        if notas:
            _decir(lab, "Firmado. Pero ojo:\n\n" + "\n".join("· " + n for n in notas))
            return
    _decir(lab, f"Diseño firmado. Siguiente: las unidades experimentales en el "
                f"{lab.lugar.lower()}.")


# ================================================== 1 · unidades experimentales
def unidades(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 1)):
        _decir(lab, m)
        return
    info = X.info(caso)
    dis = exp["dis"]
    win = lab.win
    nombre_lote = caso.get("lote_nombre", "lote")
    if info["aleatorizable"]:
        op = _menu(lab, f"¿Cómo asignas los tratamientos a las {dis['replicas'] * len(caso['grupos'])} "
                         "unidades?",
                    ["Sorteo al azar (números aleatorios)",
                     "Por orden: las primeras al grupo 1, las siguientes al grupo 2…",
                     "A ojo: las que se ven más sanas/grandes al tratamiento",
                     "Volver"])
        if op is None or op == 3:
            return
        exp["asignacion"] = ["azar", "orden", "ojo"][op]
        dis["sesgo"] = [0.0, 0.3, 0.6][op]
        _animar_asignacion(lab, exp["asignacion"])
        if info["lugar"] == "cultivo":
            _decir(lab, "Ahora siembra los cultivos en la placa. Ojo: los pozos del borde "
                        "pierden más medio por evaporación.", TECNICO)
            db = mj.placa(lab, caso, dis)
            exp["minijuegos"]["placa"] = round(db, 2)
            dis["sesgo"] = dis.get("sesgo", 0.0) + 0.35 * max(0.0, db - 0.25)
    else:
        exp["asignacion"] = None
        dis["sesgo"] = 0.0
        _decir(lab, "Aquí no puedes asignar el tratamiento: la condición ya viene con cada "
                    "persona (estudio observacional). Lo que sí controlas: emparejar, "
                    "registrar covariables y repartir el procesamiento.")
    if caso.get("capacidad"):
        _decir(lab, f"Ahora reparte las unidades en {nombre_lote}s (máximo "
                    f"{caso['capacidad']} por {nombre_lote}). Así quedaron según el orden "
                    "de la lista.", TECNICO)
        while True:
            mesa.mesa_lotes(win, caso, dis, lab.pistas, lab.dif)
            if sim.sobrecupo(dis, caso):
                _decir(lab, f"Algún {nombre_lote} pasa la capacidad: no cabe.", TECNICO)
                continue
            break
    else:
        dis["lotes"] = {k: 0 for k in X.claves_bio(exp, caso)}
    if not _cobrar(lab, 1):
        return
    X.avanzar(exp, 1)
    exp["dia"] += max(0, len(sim.tabla_lotes(dis, caso)) - 1)
    lab.guardar()
    _decir(lab, "Unidades listas y etiquetadas. Siguiente: extraer el ARN en la campana del "
                "laboratorio húmedo.", TECNICO)


def _animar_asignacion(lab, modo):
    caso, dis = lab.caso, lab.exp["dis"]
    n = dis["replicas"] * len(caso["grupos"])
    grupos = [g for g in range(len(caso["grupos"])) for _ in range(dis["replicas"])]
    rng = random.Random()
    if modo == "azar":
        rng.shuffle(grupos)
    icono = {"bioterio": "ö", "cultivo": "¤", "clinica": "☺", "invernadero": "♣"}[
        X.info(caso)["lugar"]]
    cuadros = []
    por_fila = min(12, n)
    for paso in range(n + 1):
        c = []
        for i in range(n):
            y, x = 2 + (i // por_fila) * 2, 2 + (i % por_fila) * 5
            if i < paso:
                g = grupos[i]
                c.append((y, x, f"{icono} {caso['abrev'][g]}", d.COLORES_GRUPO[g % 6]))
            else:
                c.append((y, x, f"{icono} ?", "tenue"))
        texto = {"azar": "sorteo: cada unidad tiene la misma probabilidad",
                 "orden": "por orden de llegada…", "ojo": "las más grandes al tratamiento…"}[modo]
        c.append(anim._sub(texto, "bien" if modo == "azar" else "mal"))
        cuadros.append(c)
    anim.reproducir(lab.win, cuadros, lab.juego["velocidad"], "Asignación de tratamientos")


# ================================================================ 2 · campana
def campana(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 2)):
        _decir(lab, m)
        return
    if exp["etapa"] > 2:
        if _menu(lab, "Ya extrajiste el ARN", ["Volver", "Extraer todo otra vez "
                                                    "(se repite el QC)"]) != 1:
            return
        X.regresar(exp, 2)
    win = lab.win
    claves = L.ORDEN_EXTRACCIONES
    op = _menu(lab, "Campana de extracción · ¿qué método?",
                [L.EXTRACCIONES[k]["nombre"] for k in claves] + ["Volver"])
    if op is None or op == len(claves):
        return
    met = claves[op]
    exp["extraccion"] = met
    e = L.EXTRACCIONES[met]
    _decir(lab, f"{e['texto']}\n\n<tenue>{datos.cita(*e['fuente'].split())}</>", e["nombre"])
    p = {}
    if e["celulas"]:
        op = _menu(lab, "Disociación del tejido", ["En frío (4-6 °C), enzimas activas en frío, "
                                                     "≤ 30 min", "A 37 °C durante 1 h para "
                                                     "que se suelten bien"])
        p["calor"] = op == 1
        p["limpieza"] = True
        p["dnasa"] = True
        p["homogenizacion"] = 0.5
    else:
        op = _menu(lab, "Antes de empezar", [
            "Limpio la mesa con RNaseZap, guantes nuevos y puntas con filtro",
            "Así está bien: limpié ayer"])
        p["limpieza"] = op == 0
        p["homogenizacion"] = _barra_tiempo(
            lab, "Homogenización" if caso.get("rin", 9) >= 4 else "Digestión con proteinasa K",
            "Pulsa ESPACIO cuando el cursor esté en la zona verde: si te pasas el tejido se "
            "calienta y el ARN se degrada; si te quedas corto la lisis es incompleta.")
        if met in ("trizol", "ctab"):
            vol, ok = mj.deslizador(
                lab, "Agregar cloroformo",
                "Por cada 1 mL de TRIzol se agregan 0.2 mL de cloroformo. Detén la pipeta en "
                "el volumen correcto (ESPACIO).", 0.0, 0.6, "mL", (0.17, 0.23))
            p["cloroformo"] = round(vol, 2)
            if not ok:
                _decir(lab, ("<mal!>Muy poco cloroformo:</> las fases no se separan bien y "
                             "arrastras fenol y ADN." if vol < 0.17 else
                             "<mal!>Demasiado cloroformo:</> la fase acuosa queda más chica y "
                             "pierdes ARN."), TECNICO)
            p["fase"] = _fases(lab)
            al = _menu(lab, "Precipitación de la fase acuosa", [
                "Isopropanol, 10 min en hielo, centrifugar", "Etanol al 100 %",
                "No precipito: paso directo al tubo"])
            p["alcohol"] = ["isopropanol", "etanol100", "ninguno"][al or 0]
            if caso.get("poco_material"):
                p["glucogeno"] = _menu(lab, "Hay muy poco ARN…", [
                    "Agrego glucógeno como acarreador", "No hace falta"]) == 0
            sec = _menu(lab, "Lavado con etanol al 75 % y secado", [
                "Seco 5-10 min hasta que el pellet se vea transparente",
                "Seco hasta que el pellet esté blanco y quebradizo"])
            p["secado"] = "bien" if sec == 0 else "seco"
        else:
            p["fase"] = "acuosa"
            p["alcohol"] = "isopropanol"
        p["dnasa"] = _menu(lab, "¿Y el ADN genómico?", [
            "Tratamiento con DNasa I (en columna)", "No hace falta"]) == 0
    exp["pasos"] = p
    exp["dis"]["pierde_pequenos"] = not e["guarda_pequenos"]
    if not _cobrar(lab, 2):
        return
    exp["qc"] = X.calidad_muestras(exp, caso)
    exp["semilla"] = random.randrange(10 ** 9)
    X.avanzar(exp, 2)
    exp["dia"] += max(0, len(sim.tabla_lotes(exp["dis"], caso)) - 1)
    lab.guardar()
    _decir(lab, f"Listo: {len(exp['qc'])} muestras en tubos etiquetados en el hielo. Llévalas "
                "al cuarto de QC (NanoDrop, gel y Bioanalyzer).", TECNICO)


def _barra_tiempo(lab, titulo, explicacion):
    win = lab.win
    _decir(lab, explicacion, titulo)
    lab.dibujar()
    ancho_b = 40
    zona = (0.4, 0.7)
    pos, paso = 0.0, 0.025
    win.nodelay(True)
    curses.flushinp()
    try:
        while True:
            alto, ancho = win.getmaxyx()
            y0, x0 = alto // 2 - 3, (ancho - ancho_b - 6) // 2
            d.limpiar_area(win, y0, x0, 7, ancho_b + 6)
            d.caja(win, y0, x0, 7, ancho_b + 6, titulo)
            for i in range(ancho_b):
                v = i / ancho_b
                color = "bien" if zona[0] <= v <= zona[1] else ("mal" if v > zona[1] else "tenue")
                d.put(win, y0 + 2, x0 + 3 + i, "█" if zona[0] <= v <= zona[1] else "░",
                      d.c(color))
            d.put(win, y0 + 3, x0 + 3 + int(pos * (ancho_b - 1)), "▲", d.c("titulo", curses.A_BOLD))
            d.put(win, y0 + 5, x0 + 3, "ESPACIO para detener", d.c("tenue"))
            win.refresh()
            curses.napms(45)
            k = win.getch()
            if k == ord(" ") or k in (10, 13):
                break
            pos += paso
            if pos >= 1 or pos <= 0:
                paso = -paso
                pos = min(1, max(0, pos))
    finally:
        win.nodelay(False)
        curses.flushinp()
    if pos > zona[1]:
        msg = "<mal!>Te pasaste:</> el tubo se calentó."
    elif pos < zona[0]:
        msg = "<mal!>Muy poco:</> quedaron pedazos sin lisar."
    else:
        msg = "<bien!>Bien:</> lisado homogéneo y frío."
    _decir(lab, msg, titulo)
    return pos


def _fases(lab):
    tubo = [
        "        ┌────┐",
        "        │    │",
        "  1 ──► │░░░░│  fase superior, transparente",
        "        │░░░░│",
        "  2 ──► │────│  interfase blanca, delgada",
        "  3 ──► │▓▓▓▓│  fase inferior, rosa",
        "        │▓▓▓▓│",
        "        └─▓▓─┘",
        "",
        "Después de agregar cloroformo y centrifugar 15 min a 12 000 g a 4 °C, el tubo se "
        "separa en tres fases. ¿Cuál pipeteas para seguir?",
    ]
    lab.dibujar()
    d.popup(lab.win, "\n".join(tubo), "Separación de fases", ancho=62, esperar=False)
    op = d.menu(lab.win, "¿Qué fase tomas?", y=lab.win.getmaxyx()[0] - 7,
                opciones=["1 · Superior acuosa (transparente)",
                                               "2 · Interfase", "3 · Inferior orgánica (rosa)"])
    fase = ["acuosa", "interfase", "organica"][op or 0]
    exp_txt = {"acuosa": "<bien>Bien:</> el ARN queda en la fase acuosa.",
               "interfase": "<mal>La interfase tiene ADN y proteína.</>",
               "organica": "<mal>La fase orgánica tiene fenol, proteínas y lípidos.</>"}[fase]
    if lab.pistas:
        _decir(lab, exp_txt)
    return fase


# ================================================================== 3 · QC
def qc(lab, pestana=0):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 3)):
        _decir(lab, m)
        return
    win = lab.win
    claves = list(exp["qc"])
    sel = 0
    celulas = "viabilidad" in next(iter(exp["qc"].values()))
    planta = X.info(caso)["lugar"] == "invernadero"
    mjs = exp["minijuegos"]
    while True:
        if pestana == 0 and "nanodrop" not in mjs and not celulas:
            mjs["nanodrop"] = _mj_nanodrop(lab)
        if pestana == 1 and "gel" not in mjs and not celulas:
            mjs["gel"] = _mj_gel(lab)
        alto, ancho = win.getmaxyx()
        win.erase()
        nombres = ["1 NanoDrop", "2 Gel", "3 Bioanalyzer", "4 Decidir"]
        x = 1
        for i, n in enumerate(nombres):
            d.put(win, 0, x, f" {n} ", d.c("titulo", curses.A_BOLD | (curses.A_REVERSE if i == pestana else 0)))
            x += len(n) + 3
        d.put(win, 1, 1, "Cuarto de QC · ARN íntegro, puro y sin ADN contaminante",
              d.c("tenue"))
        if pestana == 0:
            _tabla_nanodrop(win, exp, caso, celulas)
        elif pestana == 1:
            _gel(win, exp, caso, celulas, planta)
        elif pestana == 2:
            _bioanalyzer(win, exp, caso, claves[sel], celulas, planta)
        else:
            _decisiones(win, exp, caso, claves, sel)
        pie = {0: "1-4 pestaña · Esc salir",
               1: "1-4 pestaña · Esc salir",
               2: "←→ muestra · 1-4 pestaña · Esc salir",
               3: "↑↓ muestra · A aprobar · R re-extraer · E excluir · T terminar QC · Esc salir"}
        d.put(win, alto - 1, 1, pie[pestana], d.c("tenue"))
        win.refresh()
        k = d.tecla(win)
        if isinstance(k, str) and k in "1234":
            pestana = int(k) - 1
        elif k == d.ESC or d.es(k, "q"):
            lab.guardar()
            return
        elif pestana == 2 and d.es(k, curses.KEY_RIGHT, "d"):
            sel = (sel + 1) % len(claves)
        elif pestana == 2 and d.es(k, curses.KEY_LEFT, "a"):
            sel = (sel - 1) % len(claves)
        elif pestana == 3:
            if d.es(k, curses.KEY_DOWN, "s", "j"):
                sel = (sel + 1) % len(claves)
            elif d.es(k, curses.KEY_UP, "w", "k"):
                sel = (sel - 1) % len(claves)
            elif d.es(k, "a"):
                exp["qc"][claves[sel]]["estado"] = "aprobada"
                sel = (sel + 1) % len(claves)
            elif d.es(k, "e"):
                exp["qc"][claves[sel]]["estado"] = "excluida"
                sel = (sel + 1) % len(claves)
            elif d.es(k, "r"):
                _reextraer(lab, claves[sel])
            elif d.es(k, "t"):
                if _terminar_qc(lab):
                    return


def _mj_nanodrop(lab):
    errores = mj.ordenar(lab, "NanoDrop", "Ordena el procedimiento para medir una muestra:", [
        "Limpiar el pedestal con agua y papel sin pelusa",
        "Blanco: 1.5 µL del mismo buffer en que eluiste el ARN",
        "Limpiar el pedestal",
        "Cargar 1.5 µL de la muestra",
        "Medir y anotar ng/µL, A260/280 y A260/230",
        "Limpiar el pedestal antes de la siguiente",
    ])
    while True:
        vol, ok = mj.deslizador(lab, "Gota en el pedestal",
                                "Pon 1-2 µL: si es menos, la gota no forma la columna de "
                                "líquido entre los pedestales y la lectura sale errática.",
                                0.0, 4.0, "µL", (1.0, 2.0))
        if ok:
            break
        errores += 1
        _decir(lab, ("<mal!>La gota no cerró la columna:</> lectura errática. Repite."
                     if vol < 1.0 else "<mal!>Gota demasiado grande:</> se escurre por el "
                                       "brazo y ensucia el pedestal. Limpia y repite."), TECNICO)
    return errores


def _mj_gel(lab):
    errores = 0
    for carril in ("marcador de peso", "primera muestra", "última muestra"):
        _pos, ok = mj.deslizador(lab, "Cargar el gel",
                                 f"Carga el {carril}: detén la punta justo sobre el pozo. Si "
                                 "picas el gel o cargas fuera, la muestra se sale.",
                                 0.0, 10.0, "mm", (4.6, 5.4), formato="{:.1f}")
        if not ok:
            errores += 1
            _decir(lab, "<mal!>Se salió del pozo.</> Ese carril se ve corrido; vuelves a "
                        "cargarlo con otra alícuota.", TECNICO)
    return errores


def _nombre(caso, k):
    g, r = k.split("-")
    return f"{caso['abrev'][int(g)]}{int(r) + 1}"


def _tabla_nanodrop(win, exp, caso, celulas):
    y = 3
    if celulas:
        d.put(win, y, 2, "Contador de células · viabilidad (azul de tripano)", d.c("agua", curses.A_BOLD))
        y += 2
        for k, q in exp["qc"].items():
            d.trozos(win, y, 4, [(f"{_nombre(caso, k):<6}", "texto"),
                                 (f"{q['viabilidad']:>3} % viables", "agua")])
            y += 1
        return
    d.put(win, y, 2, "NanoDrop: absorbancia a 230, 260 y 280 nm (esperado 1.8-2.0 en ambos "
          "cocientes)", d.c("agua", curses.A_BOLD))
    if X.info(caso).get("biofluido"):
        d.put(win, y + 2 + len(exp["qc"]) + 3, 2, "Ojo: el ARN de plasma está por debajo del "
              "límite del NanoDrop y viene fragmentado: ni los cocientes ni el RIN son "
              "informativos. Se controla con el spike-in de extracción (cel-miR-39) y el perfil "
              "de ARN pequeño.", d.c("titulo"))
    y += 3
    d.put(win, y, 4, "muestra   ng/µL    A260/280   A260/230", d.c("titulo", curses.A_BOLD))
    y += 1
    alto = win.getmaxyx()[0]
    for k, q in list(exp["qc"].items())[: alto - y - 2]:
        d.trozos(win, y, 4, [(f"{_nombre(caso, k):<8}", "texto"), (f"{q['ng']:>7.1f}", "texto"),
                             (f"{q['r280']:>11.2f}", "texto"), (f"{q['r230']:>11.2f}", "texto")])
        y += 1


def _gel(win, exp, caso, celulas, planta):
    if celulas:
        d.put(win, 4, 4, "No hay ARN extraído: son células vivas. Mira la viabilidad en la "
              "pestaña 1.", d.c("tenue"))
        return
    ffpe = caso.get("rin", 9) < 4
    claves = list(exp["qc"])[:16]
    y0 = 4
    grande, chica = ("26S", "18S") if planta else ("28S", "18S")
    filas = [tr("pozo"), "     ", grande, "     ", chica, "     ", "     ", "  5S"]
    d.put(win, y0 - 1, 2, f"Gel de agarosa 1 % · bromuro de etidio · ARNr {grande}/{chica}",
          d.c("agua", curses.A_BOLD))
    for i, f in enumerate(filas):
        d.put(win, y0 + 1 + i, 2, f"{f:>5}", d.c("tenue"))
    for j, k in enumerate(claves):
        q = exp["qc"][k]
        x = 9 + j * 5
        d.put(win, y0, x, _nombre(caso, k)[:4], d.c("texto"))
        rin = 1.5 if ffpe else q["rin"]
        col = []
        col.append("▀▀▀" if q["gdna"] else "   ")
        col.append("   ")
        col.append("███" if rin >= 8 else ("▓▓▓" if rin >= 6 else ("▬▬▬" if rin >= 4 else "░░░")))
        col.append("░░░" if rin < 6 else "   ")
        col.append("▓▓▓" if rin >= 8 else ("▒▒▒" if rin >= 6 else ("▬▬▬" if rin >= 4 else "░░░")))
        col.append("░░░" if rin < 7 else "   ")
        col.append("▒▒▒" if rin < 5 else ("░░░" if rin < 7 else "   "))
        col.append("▬▬▬")
        for i, c in enumerate(col):
            d.put(win, y0 + 1 + i, x, c, d.c("texto" if c.strip() else "oscuro"))
    d.put(win, y0 + 11, 2, "Bandas nítidas (la grande ~2× la chica) = íntegro · barrido hacia "
          "abajo = degradado · banda en el pozo = ADN genómico", d.c("tenue"))


def _bioanalyzer(win, exp, caso, k, celulas, planta):
    if celulas:
        d.put(win, 4, 4, "No aplica a células vivas.", d.c("tenue"))
        return
    q = exp["qc"][k]
    ffpe = caso.get("rin", 9) < 4
    alto, ancho = win.getmaxyx()
    h, w = min(14, alto - 8), min(70, ancho - 8)
    y0, x0 = 4, 6
    grande = "26S" if planta else "28S"
    d.put(win, y0 - 1, 2, f"Bioanalyzer · muestra {_nombre(caso, k)} · "
          + (f"DV200 {q['dv200']} %" if ffpe else f"RIN {q['rin']}"),
          d.c("agua", curses.A_BOLD))
    rin = q["rin"]
    pts = []
    for i in range(w):
        nt = 25 * (6000 / 25) ** (i / (w - 1))          # eje logarítmico 25-6000 nt
        v = 0.0
        v += 3.0 * math.exp(-((math.log(nt) - math.log(25)) / 0.08) ** 2)       # marcador
        inte = max(0.0, (rin - 2) / 8)
        v += 6 * inte * math.exp(-((math.log(nt) - math.log(1900)) / 0.09) ** 2)
        v += 9 * inte * math.exp(-((math.log(nt) - math.log(4000)) / 0.09) ** 2)
        deg = max(0.0, (8 - rin) / 7)
        v += 2.5 * deg * math.exp(-((math.log(nt) - math.log(250)) / 0.9) ** 2)
        pts.append(v)
    mx = max(max(pts), 9.5)            # escala fija: lo degradado se ve bajo
    for i, v in enumerate(pts):
        alto_c = round(v / mx * (h - 1))
        for yy in range(alto_c):
            d.put(win, y0 + h - 1 - yy, x0 + i, "█" if yy < alto_c - 1 else "▄", d.c("agua"))
    d.put(win, y0 + h, x0, "25", d.c("tenue"))
    d.put(win, y0 + h, x0 + w // 2 - 2, "500", d.c("tenue"))
    d.put(win, y0 + h, x0 + w - 6, "6000 nt", d.c("tenue"))
    d.put(win, y0 + h + 1, x0, f"Picos: marcador (25 nt) · 18S (~1.9 kb) · {grande} (~4 kb). "
          "Sin picos y con barrido bajo = degradado.", d.c("tenue"))
    d.put(win, y0 + h + 2, x0, "RIN 0 degradado → 10 intacto; arriba de 8 es adecuado para "
          "RNA-seq.", d.c("tenue"))


def _decisiones(win, exp, caso, claves, sel):
    y = 3
    d.put(win, y, 2, "Decide qué pasa con cada muestra. Mira las otras pestañas.",
          d.c("agua", curses.A_BOLD))
    y += 2
    colores = {"pendiente": "tenue", "aprobada": "bien", "excluida": "mal"}
    alto = win.getmaxyx()[0]
    ini = max(0, min(sel - (alto - 10) // 2, len(claves) - (alto - 10)))
    for i, k in enumerate(claves[ini: ini + alto - 9], start=ini):
        q = exp["qc"][k]
        marca = "► " if i == sel else "  "
        d.trozos(win, y, 4, [(marca, "titulo"), (f"{_nombre(caso, k):<6}", "texto"),
                             (f"{q['estado']:<10}", colores[q["estado"]], curses.A_BOLD)])
        y += 1


def _reextraer(lab, k):
    exp, caso = lab.exp, lab.caso
    if not _pagar(lab, datos.EXTRACCION, f"Re-extraer {_nombre(caso, k)}"):
        return
    nueva = X.calidad_muestras(exp, caso, random.Random())
    q = nueva[k]
    if q.get("rin", 9) < exp["qc"][k].get("rin", 9) - 2.5:
        q["rin"] = exp["qc"][k]["rin"]           # no hay mala suerte dos veces
    exp["qc"][k] = q
    exp["reextracciones"] += 1
    exp["dia"] += 1
    _decir(lab, f"{_nombre(caso, k)} re-extraída (+1 día, ${datos.EXTRACCION}). Revisa sus "
                "nuevos valores.", TECNICO)


def _terminar_qc(lab):
    exp, caso = lab.exp, lab.caso
    pend = [k for k, q in exp["qc"].items() if q["estado"] == "pendiente"]
    if pend:
        _decir(lab, f"Faltan {len(pend)} muestras por decidir.")
        return False
    X.aplicar_qc(exp, caso)
    if sim.replicas_efectivas(exp["dis"], caso) < 2:
        _decir(lab, "Te quedaste con menos de 2 réplicas en algún grupo: no hay estadística "
                    "posible. Re-extrae en vez de excluir.")
        return False
    if lab.pistas:
        malas = [_nombre(caso, k) for k, q in exp["qc"].items()
                 if q["estado"] == "aprobada" and X.problemas(q, caso)]
        buenas_fuera = [_nombre(caso, k) for k, q in exp["qc"].items()
                        if q["estado"] == "excluida" and not X.problemas(q, caso)]
        if malas or buenas_fuera:
            txt = []
            if malas:
                txt.append(f"Aprobaste muestras con problemas: {', '.join(malas)}.")
            if buenas_fuera:
                txt.append(f"Excluiste muestras que estaban bien: {', '.join(buenas_fuera)}.")
            _decir(lab, " ".join(txt) + " (Lo verás en el dictamen.)")
    X.avanzar(exp, 3)
    lab.guardar()
    _decir(lab, "QC terminado y anotado. Siguiente: la biblioteca, en el estante de kits del "
                "laboratorio húmedo.", TECNICO)
    return True


# ============================================================== 4 · kits
def kits(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 4)):
        _decir(lab, m)
        return
    if exp["etapa"] > 4:
        if _menu(lab, "Las bibliotecas ya están hechas", ["Volver", "Rehacer las "
                                                               "bibliotecas"]) != 1:
            return
        X.regresar(exp, 4)
    dis = exp["dis"]
    met = L.EXTRACCIONES[exp["extraccion"]]

    def extra(e):
        return (lambda: e in dis["extras"],
                lambda v: (dis["extras"].append(e) if v and e not in dis["extras"] else
                           dis["extras"].remove(e) if not v and e in dis["extras"] else None))

    def ficha_kit(v):
        b = datos.BIBLIOTECAS[v]
        return [f"<titulo!>{b['nombre']}</>  <tenue>${b['costo']} por muestra</>", b["resumen"],
                "", f"<bien>Cuándo:</> {b['cuando']}", f"<mal>Ojo:</> {b['malo']}",
                f"<tenue>{datos.cita(*b['fuente'].split())}</>"]

    filas = [dict(tipo="seccion", etiqueta="KIT"),
             dict(tipo="opcion", etiqueta="Caja del estante",
                  opciones=[(k, datos.BIBLIOTECAS[k]["nombre"]) for k in datos.ORDEN_BIBLIOTECAS],
                  get=lambda: dis["biblioteca"], set=lambda v: dis.__setitem__("biblioteca", v),
                  costo=lambda: f"${datos.BIBLIOTECAS[dis['biblioteca']]['costo']} por muestra"
                                f" → ${X.costo_etapa(exp, caso, 4):,} esta etapa",
                  ficha=ficha_kit),
             dict(tipo="seccion", etiqueta="AGREGADOS")]
    for e in ("hebra", "umi", "ercc"):
        g, s = extra(e)
        x = datos.EXTRAS[e]
        n_lib = lambda: datos.n_muestras(dis, caso) - len(dis.get("excluidas", ())) * dis["tecnicas"]
        filas.append(dict(tipo="check", etiqueta=x["nombre"], get=g, set=s,
                          costo=lambda x=x: f"+${x['costo']} por muestra × {n_lib()} = "
                                            f"+${x['costo'] * n_lib():,}",
                          ficha=lambda v, x=x: [f"<titulo!>{x['nombre']}</>  <tenue>+${x['costo']}</>",
                                                x["texto"], f"<tenue>{datos.cita(*x['fuente'].split())}</>"]))
    filas += [
        dict(tipo="seccion", etiqueta="PREPARACIÓN"),
        dict(tipo="opcion", etiqueta="Ciclos de PCR",
             opciones=[(c, f"{c} ciclos") for c in (8, 10, 12, 14, 16, 18)],
             get=lambda: exp["pcr"], set=lambda v: exp.__setitem__("pcr", v),
             ficha=lambda v: ["<titulo!>Ciclos de PCR</>", "Los mínimos que den suficiente "
                              "biblioteca: cada ciclo extra aumenta duplicados y sesgo.",
                              f"<tenue>{datos.cita('CON16')}</>"]),
        dict(tipo="accion", clave="hacer", etiqueta="Preparar las bibliotecas"),
    ]
    pie = lambda: [f"Costo de esta etapa: <titulo>${X.costo_etapa(exp, caso, 4):,.0f}</> · "
                   f"gastado ${exp['gastado']:,} de ${lab.tope:,} · proyectado total "
                   f"${X.proyeccion(exp, caso):,}"]
    if Formulario(lab.win, "Estante de kits de biblioteca", filas, pie).jugar() != "hacer":
        return
    sc = dis["biblioteca"] in ("sc10x", "snrna", "smartseq")
    if sc != met["celulas"]:
        _decir(lab, ("Para célula única necesitas células o núcleos vivos, no ARN extraído."
                     if sc else "Tienes una suspensión de células, no ARN: ese kit necesita ARN "
                                "extraído.") + " Regresa a la campana.", TECNICO)
        return
    if datos.BIBLIOTECAS[dis["biblioteca"]]["larga"]:
        dis["lectura"] = "LARGA"
    elif dis["lectura"] == "LARGA":
        dis["lectura"] = "PE100"
    if not _cobrar(lab, 4):
        return
    exp["minijuegos"]["biblioteca"] = mj.ordenar(
        lab, "Preparar la biblioteca", f"{datos.BIBLIOTECAS[dis['biblioteca']]['nombre']}: "
        "pon los pasos en orden.", PASOS_BIBLIOTECA.get(dis["biblioteca"], PASOS_BIBLIOTECA["polyA"]))
    exp["limpieza"] = _traza_biblioteca(lab)
    dis["dimeros"] = not exp["limpieza"]
    if exp["limpieza"]:
        ratio, ok = mj.deslizador(
            lab, "Limpieza con perlas",
            "Las perlas SPRI retienen el ADN más largo que un corte que depende de cuántas "
            "perlas agregas (× el volumen de la biblioteca). Elige un volumen que tire los "
            "dímeros de ~125 pb sin perder la biblioteca.", 0.4, 1.8, "×", (0.75, 0.95))
        exp["minijuegos"]["perlas"] = round(ratio, 2)
        if ratio < 0.75:
            dis["factor_lecturas"] = dis.get("factor_lecturas", 1.0) * 0.6
            _decir(lab, "<mal!>Muy pocas perlas:</> también tiraste buena parte de la "
                        "biblioteca. Saldrán menos lecturas útiles.", TECNICO)
        elif ratio > 0.95:
            dis["dimeros"] = True
            _decir(lab, "<mal!>Demasiadas perlas:</> los dímeros se quedaron pegados con la "
                        "biblioteca.", TECNICO)
        else:
            _decir(lab, "<bien!>Bien:</> sin dímeros y sin perder biblioteca.", TECNICO)
    X.avanzar(exp, 4)
    lab.guardar()
    _decir(lab, "Bibliotecas listas, cuantificadas e indexadas. Siguiente: el secuenciador.",
           TECNICO)


PASOS_BIBLIOTECA = {
    "polyA": ["Capturar el ARN poli(A) con perlas oligo-dT", "Fragmentar el ARN (calor + Mg²+)",
              "Primera hebra de cDNA con hexámeros al azar", "Segunda hebra (con dUTP si es con hebra)",
              "Reparar extremos y agregar cola A", "Ligar adaptadores con índices",
              "PCR de enriquecimiento", "Limpieza con perlas"],
    "ribo": ["Hibridar sondas contra el ARNr", "Digerir el ARNr con RNasa H",
             "Fragmentar el ARN", "Primera hebra de cDNA", "Segunda hebra con dUTP",
             "Ligar adaptadores con índices", "PCR de enriquecimiento", "Limpieza con perlas"],
    "tag3": ["Retrotranscribir con oligo-dT con código de barras", "Juntar todas las muestras",
             "Segunda hebra / tagmentación", "PCR con índice de placa", "Limpieza con perlas"],
    "small": ["Ligar el adaptador 3′", "Ligar el adaptador 5′", "Retrotranscribir",
              "PCR con índices", "Seleccionar tamaño (18-34 nt de inserto)"],
    "sc10x": ["Cargar células, perlas y aceite en el chip", "Formar las gotas (GEMs)",
              "Retrotranscribir dentro de las gotas", "Romper la emulsión y amplificar cDNA",
              "Fragmentar y ligar adaptadores", "PCR con índice de muestra"],
}
PASOS_BIBLIOTECA["snrna"] = PASOS_BIBLIOTECA["sc10x"]


def _traza_biblioteca(lab):
    """Muestra el perfil de la biblioteca con un pico de dímeros y deja que el
    jugador lo reconozca."""
    win = lab.win
    traza = ["  FU",
             "   │                    ▄█▄",
             "   │                   ▐███▌",
             "   │   ▄▄              █████▄",
             "   │   █▌             ▐██████▌",
             "   │   █▌           ▄▐████████▌▄",
             "   └──────────────────────────────────── pb",
             "      125         300   400   600   1000"]
    lab.dibujar()
    d.popup(win, "\n".join(traza) + "\n\nPerfil de una biblioteca en el Bioanalyzer "
                 "(High Sensitivity DNA).", "QC de la biblioteca", ancho=66, esperar=False)
    op = d.menu(win, "¿Qué ves?", y=win.getmaxyx()[0] - 7,
                opciones=["Un pico pequeño a ~125 pb: dímeros de adaptador",
                                   "Todo bien: un solo pico a 300-400 pb",
                                   "ARN degradado"])
    if op == 0:
        limpia = _menu(lab, "¿Qué haces?", ["Otra limpieza con perlas 0.8×",
                                             "Secuenciar así"]) == 0
        _decir(lab, "Bien visto: los dímeros se secuencian igual y gastan lecturas."
               + (" Con la limpieza desaparecen." if limpia else ""), TECNICO)
        return limpia
    _decir(lab, "Mira el pico de ~125 pb: son dímeros de adaptador (adaptador pegado a "
                "adaptador, sin inserto). Se van a secuenciar y gastar lecturas.", TECNICO)
    return False


# ======================================================= 5 · secuenciador
def secuenciador(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 5)):
        _decir(lab, m)
        return
    if exp["etapa"] > 5:
        if _menu(lab, "Ya secuenciaste", ["Volver", "Secuenciar otra vez"]) != 1:
            return
        X.regresar(exp, 5)
    dis = exp["dis"]
    larga = datos.BIBLIOTECAS[dis["biblioteca"]]["larga"]
    plats = [k for k in L.ORDEN_PLATAFORMAS if ("LARGA" in L.PLATAFORMAS[k]["lecturas"]) == larga]
    if exp["plataforma"] not in plats:
        exp["plataforma"] = plats[0]

    def pon_plat(v):
        exp["plataforma"] = v
        dis["plataforma"] = v
        if dis["lectura"] not in L.PLATAFORMAS[v]["lecturas"]:
            dis["lectura"] = L.PLATAFORMAS[v]["lecturas"][0]

    dis["plataforma"] = exp["plataforma"]
    filas = [
        dict(tipo="opcion", etiqueta="Plataforma",
             opciones=[(k, L.PLATAFORMAS[k]["nombre"]) for k in plats],
             get=lambda: exp["plataforma"], set=pon_plat,
             ficha=lambda v: [f"<titulo!>{L.PLATAFORMAS[v]['nombre']}</>",
                              L.PLATAFORMAS[v]["texto"],
                              f"~{L.PLATAFORMAS[v]['cap']} M lecturas por corrida · "
                              f"{L.PLATAFORMAS[v]['dias']} días",
                              f"<tenue>{L.FUENTE_PLATAFORMAS}</>"]),
        dict(tipo="opcion", etiqueta="Tipo de lectura",
             opciones=lambda: [(k, datos.LECTURAS[k]["nombre"])
                               for k in L.PLATAFORMAS[exp["plataforma"]]["lecturas"]],
             get=lambda: dis["lectura"], set=lambda v: dis.__setitem__("lectura", v),
             ficha=lambda v: [f"<titulo!>{datos.LECTURAS[v]['nombre']}</>", datos.LECTURAS[v]["texto"],
                              "Disponibles en esta plataforma: "
                              + ", ".join(datos.LECTURAS[x]["nombre"] for x in
                                          L.PLATAFORMAS[exp["plataforma"]]["lecturas"])]),
        dict(tipo="opcion", etiqueta="Lecturas por muestra",
             opciones=[(p, f"{p} M") for p in datos.PROFUNDIDADES],
             get=lambda: dis["profundidad"], set=lambda v: dis.__setitem__("profundidad", v),
             costo=lambda: f"${datos.costo_secuenciacion(dis):,.0f} por muestra → "
                           f"${X.costo_etapa(exp, caso, 5):,} la corrida",
             ficha=lambda v: ["<titulo!>Profundidad</>", "3′ tag 3-10 M · small RNA 2-10 M · "
                              "genes 10-30 M · lncRNA 40-60 M · isoformas 50-100 M · célula "
                              "única ≥ 20 000 lecturas por célula.",
                              f"<tenue>{datos.cita('LIU14', 'CON16', 'ENC')}</>"]),
        dict(tipo="opcion", etiqueta="Carriles",
             opciones=[("todos", "todas las muestras en todos los carriles"),
                       ("grupo", "un grupo por carril")],
             get=lambda: exp["carriles"], set=lambda v: exp.__setitem__("carriles", v),
             ficha=lambda v: ["<titulo!>Carriles</>", "Con códigos de barras todas las "
                              "muestras pueden ir juntas en cada carril.",
                              f"<tenue>{datos.cita('AUE10')}</>"]),
        dict(tipo="accion", clave="correr", etiqueta="Cargar la celda e iniciar la corrida"),
    ]

    def pie():
        n, total = X.corridas_necesarias(exp, caso)
        pl = L.PLATAFORMAS[exp["plataforma"]]
        return [f"Total ≈ {total:,} M lecturas → {n} corrida(s) · {n * pl['dias']} días · "
                f"costo <titulo>${X.costo_etapa(exp, caso, 5):,.0f}</> · quedan "
                f"${lab.tope - exp['gastado']:,}"]

    while True:
        if Formulario(lab.win, "Secuenciador", filas, pie).jugar() != "correr":
            return
        if dis["lectura"] not in L.PLATAFORMAS[exp["plataforma"]]["lecturas"]:
            _decir(lab, "Esa lectura no existe en esta plataforma.", TECNICO)
            continue
        if _cobrar(lab, 5):
            break
    dis["sesgo"] = max(dis.get("sesgo", 0.0), 0.15 if exp["carriles"] == "grupo" else 0.0)
    carga, ok = mj.deslizador(
        lab, "Cargar la celda",
        "Diluye el pool a la concentración que recomienda el fabricante para este equipo "
        "(100 % = la recomendada). Poca carga da pocos clusters; demasiada los enciman y "
        "el secuenciador descarta las lecturas.", 0, 200, "%", (85, 115), formato="{:.0f}")
    exp["minijuegos"]["carga"] = round(carga)
    if not ok:
        dis["factor_lecturas"] = dis.get("factor_lecturas", 1.0) * (0.6 if carga < 85 else 0.7)
        _decir(lab, ("<mal!>Celda subcargada:</> salieron muchas menos lecturas de las pedidas."
                     if carga < 85 else "<mal!>Celda sobrecargada:</> clusters encimados; "
                                        "el filtro de calidad tiró muchas lecturas."), TECNICO)
    n, _ = X.corridas_necesarias(exp, caso)
    anim.secuenciacion(lab.win, datos.n_muestras(dis, caso), lab.juego["velocidad"])
    dias = n * L.PLATAFORMAS[exp["plataforma"]]["dias"]
    exp["dia"] += dias
    X.avanzar(exp, 5)
    exp["semilla_sec"] = random.randrange(10 ** 9)
    lab.guardar()
    _decir(lab, f"Pasaron {dias} días. Los FASTQ ya están en el servidor: ve a la computadora "
                "de bioinformática.", TECNICO)


# ====================================================== 6 · computadora
def computadora(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 6)):
        _decir(lab, m)
        return
    dis = exp["dis"]
    formulas = list(datos.ORDEN_FORMULAS)

    def ficha_tabla(tabla, extra_fuente=None):
        def f(v):
            x = tabla[v]
            out = [f"<titulo!>{x['nombre']}</>", x["texto"]]
            if "fuente" in x:
                out.append(f"<tenue>{datos.cita(*x['fuente'].split())}</>")
            return out
        return f

    def set_formula(v):
        if v in ("lote", "par_lote", "tiempo_lote") and "lote" not in exp["registros"]:
            _decir(lab, "No anotaste el lote de cada muestra en la hoja de muestras: no hay "
                        "columna «lote» que poner en el modelo.")
            return
        dis["formula"] = v

    filas = [dict(tipo="seccion", etiqueta="PREPROCESAMIENTO"),
             dict(tipo="opcion", etiqueta="Cuantificación",
                  opciones=[(k, datos.RUTAS[k]["nombre"]) for k in datos.ORDEN_RUTAS],
                  get=lambda: dis["ruta"], set=lambda v: dis.__setitem__("ruta", v),
                  ficha=ficha_tabla(datos.RUTAS)),
             dict(tipo="seccion", etiqueta="MODELO"),
             dict(tipo="opcion", etiqueta="Entrada al modelo",
                  opciones=[(k, datos.ENTRADAS[k]["nombre"]) for k in datos.ORDEN_ENTRADAS],
                  get=lambda: dis["entrada"], set=lambda v: dis.__setitem__("entrada", v),
                  ficha=ficha_tabla(datos.ENTRADAS)),
             dict(tipo="info", etiqueta="Fórmula de diseño",
                  texto=lambda: (datos.FORMULAS[dis["formula"]]["nombre"]
                                 if exp.get("formula_escrita") else "— por elegir —"),
                  color="agua",
                  ficha=lambda v: ["<titulo!>Fórmula de diseño</>",
                                   "Se elige en R, en la terminal: «Elegir la fórmula en R».",
                                   "", "Ejemplos: ~ condicion · ~ lote + condicion · "
                                   "~ donante + condicion · ~ genotipo + tratamiento + genotipo:tratamiento",
                                   f"<tenue>{datos.cita('DESV')}</>"]),
             dict(tipo="accion", clave="formula", etiqueta="Elegir la fórmula en R",
                  color="agua"),
             dict(tipo="opcion", etiqueta="Prueba estadística",
                  opciones=[(k, datos.PRUEBAS[k]["nombre"]) for k in datos.ORDEN_PRUEBAS],
                  get=lambda: dis["prueba"], set=lambda v: dis.__setitem__("prueba", v),
                  ficha=ficha_tabla(datos.PRUEBAS)),
             dict(tipo="opcion", etiqueta="Pruebas múltiples",
                  opciones=[(k, datos.CORRECCIONES[k]["nombre"]) for k in datos.ORDEN_CORRECCIONES],
                  get=lambda: dis["correccion"], set=lambda v: dis.__setitem__("correccion", v),
                  ficha=ficha_tabla(datos.CORRECCIONES)),
             dict(tipo="seccion", etiqueta="EXTRAS")]
    for e in ("filtro", "shrink", "splicing", "gsea", "decon"):
        x = datos.EXTRAS[e]
        filas.append(dict(tipo="check", etiqueta=x["nombre"],
                          get=lambda e=e: e in dis["extras"],
                          set=lambda v, e=e: (dis["extras"].append(e) if v and e not in dis["extras"]
                                              else dis["extras"].remove(e) if not v and e in dis["extras"]
                                              else None),
                          ficha=lambda v, x=x: [f"<titulo!>{x['nombre']}</>", x["texto"],
                                                f"<tenue>{datos.cita(*x['fuente'].split())}</>"]))
    filas.append(dict(tipo="accion", clave="correr", etiqueta="Correr el análisis"))
    campos = ("ruta", "entrada", "formula", "prueba", "correccion")
    while True:
        accion = Formulario(lab.win, "Computadora de bioinformática", filas,
                            subtitulo="FASTQ → QC → cuantificación → modelo → resultados").jugar()
        if accion == "formula":
            _terminal_formula(lab)
            continue
        if accion != "correr":
            lab.guardar()
            return
        if dis["ruta"] in ("star", "hisat") and \
                exp["minijuegos"].get("hebra_para") != [dis["ruta"], "hebra" in dis["extras"]]:
            if not _terminal_hebra(lab):
                continue
        if not exp.get("formula_escrita"):
            if not _terminal_formula(lab):
                continue
        foto = {c: dis[c] for c in campos}
        foto["extras"] = sorted(dis["extras"])
        if exp["ultimo_analisis"] and exp["resultado_visto"]:
            cambiados = [c for c in foto if foto[c] != exp["ultimo_analisis"].get(c)]
            exp["cambios"] += cambiados
        exp["ultimo_analisis"] = foto
        exp["corridas"] += 1
        res = lab.analizar()
        _multiqc(lab)
        mesa.pantalla_resultados(lab.win, caso, dis, res)
        exp["resultado_visto"] = True
        exp["dia"] += 1
        decision = _decidir(lab, res)
        lab.guardar()
        if decision != "otra":
            return


def _terminal_hebra(lab):
    """featureCounts necesita saber la hebra de la biblioteca (-s 0/1/2). Se
    ve la salida de RSeQC infer_experiment.py y se elige el valor."""
    exp, dis = lab.exp, lab.exp["dis"]
    hebra = "hebra" in dis["extras"]
    pe = dis["lectura"].startswith("PE")
    if hebra:
        a, b, c = 0.02, 0.05, 0.93
    else:
        a, b, c = 0.03, 0.49, 0.48
    if pe:
        salida = [f'  Fraction of reads failed to determine: {a:.4f}',
                  f'  Fraction of reads explained by "1++,1--,2+-,2-+": {b:.4f}',
                  f'  Fraction of reads explained by "1+-,1-+,2++,2--": {c:.4f}']
    else:
        salida = [f'  Fraction of reads failed to determine: {a:.4f}',
                  f'  Fraction of reads explained by "++,--": {b:.4f}',
                  f'  Fraction of reads explained by "+-,-+": {c:.4f}']
    contexto = ["<tenue>$ infer_experiment.py -r anotacion.bed -i muestra1.bam</>",
                "  This is " + ("PairEnd" if pe else "SingleEnd") + " Data"] + salida + [
                "", "<tenue>¿Con qué -s cuenta featureCounts esta biblioteca?</>", ""]
    opciones = [("0", "Sin hebra: cuenta la lectura en el gen sin importar en qué hebra cayó."),
                ("1", "Misma hebra: la lectura (la 1 si son pareadas) tiene la secuencia del ARN."),
                ("2", "Hebra contraria: la lectura 1 es el complemento del ARN (kits con dUTP, "
                      "como TruSeq Stranded).")]

    def validar(txt):
        txt = txt.replace("-s", "").strip()
        if txt not in ("0", "1", "2"):
            return None, "Escribe 0, 1 o 2."
        s = int(txt)
        correcto = 2 if hebra else 0
        exp["minijuegos"]["hebra_para"] = [dis["ruta"], hebra]
        exp["minijuegos"]["hebra_s"] = s
        if s == correcto:
            dis["factor_hebra"] = 1.0
            return s, "Assigned: 87.6 %  ·  Unassigned_NoFeatures: 6.1 %"
        if hebra and s == 1:
            dis["factor_hebra"] = 0.06
            return s, "Assigned: 5.3 %  ·  Unassigned_NoFeatures: 88.4 %  (¿esto es normal?)"
        if hebra and s == 0:
            dis["factor_hebra"] = 0.92
            return s, ("Assigned: 81.2 %  ·  Unassigned_Ambiguity: 11.9 %  (se pierde la "
                       "información de hebra)")
        dis["factor_hebra"] = 0.5
        return s, "Assigned: 44.1 %  ·  Unassigned_NoFeatures: 49.7 %  (¿esto es normal?)"

    valor, errores = mj.terminal(lab, "Terminal · contar lecturas", contexto,
                                 "featureCounts -T 8 -a anotacion.gtf -s ", opciones, validar,
                                 "2" if hebra else "0")
    return valor is not None


def _parsear_formula(texto, caso, exp):
    """'~ lote + condicion' → clave de datos.FORMULAS, o (None, mensaje)."""
    t = texto.replace("design", "").replace("=", "").strip().lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        t = t.replace(a, b)
    if not t.startswith("~"):
        return None, "Una fórmula de R empieza con ~ (por ejemplo: ~ condicion)."
    cuerpo = t[1:].replace(" ", "")
    if not cuerpo:
        return None, "Falta el lado derecho de la fórmula."
    sinon = {"condicion": "cond", "grupo": "cond", "tratamiento": "trat", "tiempo": "cond",
             "lote": "lote", "dia": "lote", "banca": "lote", "tanda": "lote", "bloque": "lote",
             "donante": "don", "paciente": "don", "individuo": "don", "genotipo": "gen"}
    terminos = []
    for parte in cuerpo.split("+"):
        if "*" in parte:
            a, _, b = parte.partition("*")
            terminos += [a, b, f"{a}:{b}"]
        else:
            terminos.append(parte)
    norm = []
    for term in terminos:
        piezas = term.split(":")
        if any(p not in sinon for p in piezas):
            desconocido = next(p for p in piezas if p not in sinon)
            return None, (f"«{desconocido}» no es una columna de tu hoja de muestras. "
                          "Columnas: condicion, lote, donante, genotipo, tratamiento, tiempo.")
        norm.append(":".join(sorted(sinon[p] for p in piezas)))
    s = set(norm)
    if "lote" in s and "lote" not in exp.get("registros", []):
        return None, "No anotaste el lote en la hoja de muestras: esa columna no existe."
    if caso.get("factores") and "gen" in str(s) and "trat" in str(s):
        clave = "inter" if "gen:trat" in s else "aditivo"
    elif "trat" in s and not caso.get("factores"):
        s = {("cond" if x == "trat" else x) for x in s}
        clave = None
    else:
        clave = None
    if clave is None:
        if "cond" not in s:
            return None, "Falta la variable de interés (condicion) en la fórmula."
        resto = s - {"cond"}
        tabla = {frozenset(): "cond", frozenset({"lote"}): "lote", frozenset({"don"}): "par",
                 frozenset({"don", "lote"}): "par_lote"}
        clave = tabla.get(frozenset(resto))
        if clave is None:
            return None, "No reconozco esa combinación de términos."
        if caso["objetivo"] == "tiempo":
            clave = {"cond": "tiempo", "lote": "tiempo_lote"}.get(clave, clave)
    ultimo = norm[-1]
    aviso = ""
    if clave not in ("inter", "aditivo") and ultimo != "cond":
        aviso = " Ojo: DESeq2 prueba por defecto el ÚLTIMO término; pon la condición al final."
        exp["minijuegos"]["formula_orden"] = True
    else:
        exp["minijuegos"].pop("formula_orden", None)
    return clave, f"dds <- DESeqDataSetFromMatrix(cuentas, coldata, design = {texto.strip()})" + aviso


def _terminal_formula(lab):
    exp, caso, dis = lab.exp, lab.caso, lab.exp["dis"]
    cols = ["id", "grupo", "replica_biologica"] + [{"lote": "lote", "donante": "donante",
                                                    "sexo": "sexo", "rin": "rin",
                                                    "operador": "operador"}[r]
                                                   for r in exp.get("registros", [])]
    if caso.get("pareado") and "donante" not in cols:
        cols.append("donante")
    if caso.get("factores"):
        cols += ["genotipo", "tratamiento"]
    var = "tiempo" if caso["objetivo"] == "tiempo" else "condicion"
    contexto = ["<tenue>> head(coldata)</>",
                "  " + "  ".join(cols + [var]),
                "  ...", "",
                "<tenue>Elige la fórmula de diseño del modelo (DESeq2).</>", ""]
    # solo se ofrecen términos con columna en la hoja de muestras
    opciones = {"cond": (f"~ {var}", datos.FORMULAS["tiempo" if var == "tiempo" else "cond"]["texto"])}
    if "lote" in cols:
        opciones["lote"] = (f"~ lote + {var}",
                            datos.FORMULAS["tiempo_lote" if var == "tiempo" else "lote"]["texto"])
        opciones["orden"] = (f"~ {var} + lote", "Los mismos términos con la variable de interés "
                             "antes que el lote. DESeq2 prueba por defecto el ÚLTIMO término.")
    if "donante" in cols:
        opciones["par"] = (f"~ donante + {var}", datos.FORMULAS["par"]["texto"])
        if "lote" in cols:
            opciones["par_lote"] = (f"~ donante + lote + {var}", datos.FORMULAS["par_lote"]["texto"])
    if caso.get("factores"):
        opciones["aditivo"] = ("~ genotipo + tratamiento", datos.FORMULAS["aditivo"]["texto"])
        opciones["inter"] = ("~ genotipo + tratamiento + genotipo:tratamiento",
                             datos.FORMULAS["inter"]["texto"])
    clave_sol = {"tiempo": "cond", "tiempo_lote": "lote"}
    sol = next((opciones[clave_sol.get(k, k)][0] for k in sorted(caso["formulas_ok"] or {"cond"}, key=lambda k: k == "cond")
                if clave_sol.get(k, k) in opciones), opciones["cond"][0])
    valor, _ = mj.terminal(lab, "Terminal · R", contexto, "design = ", list(opciones.values()),
                           lambda t: _parsear_formula(t, caso, exp), sol)
    if valor is None:
        return False
    dis["formula"] = valor
    exp["formula_escrita"] = True
    return True


def _multiqc(lab):
    exp, caso, dis = lab.exp, lab.caso, lab.exp["dis"]
    rins = [q.get("rin", 9) for k, q in exp["qc"].items() if q["estado"] != "excluida"]
    rin = sum(rins) / len(rins) if rins else 9
    lib = dis["biblioteca"]
    mapeo = 88 - (25 if caso.get("sin_genoma") and dis["ruta"] not in ("trinity", "isoseq") else 0) \
        - (8 if lib == "ribo" else 0)
    dup = 15 + (exp["pcr"] - 10) * 3 + (15 if caso.get("poco_material") else 0)
    sesgo3 = "fuerte" if lib == "polyA" and rin < 6 else ("leve" if rin < 7.5 else "no")
    rrna = 2 if lib == "polyA" else (6 if lib == "ribo" else 3)
    dimer = 18 if dis.get("dimeros") else 1
    hebra = "≈ 92 % reversa (dUTP)" if "hebra" in dis["extras"] else "≈ 50/50 (sin hebra)"
    lineas = [
        "<titulo!>MultiQC</> · resumen de todas las muestras",
        "",
        f"  Lecturas por muestra       {dis['profundidad']} M (pedidas)",
        f"  Calidad (Q30)              92 %",
        f"  Adaptadores / dímeros      {dimer} %",
        f"  Alineadas                  {mapeo} %   (esperado 70-90 % en humano)",
        f"  Duplicación                {dup} %   (alta es normal en RNA-seq)",
        f"  ARNr                       {rrna} %",
        f"  Sesgo 3′ (cobertura)       {sesgo3}",
        f"  Hebra (infer_experiment)   {hebra}",
        "",
        f"<tenue>{datos.cita('EWE16', 'WAN12', 'CON16')}</>",
    ]
    d.visor(lab.win, "Reporte de control de calidad", lineas, ayuda="Enter ver resultados")


def _decidir(lab, res):
    exp, caso = lab.exp, lab.caso
    info = X.info(caso)
    win = lab.win
    h = info["hipotesis"][exp["hipotesis"]] if exp["hipotesis"] is not None else "—"
    if res["estado"] == "ok":
        resumen = (f"{res['sig']} genes significativos (↑{res['subidos']} ↓{res['bajados']}).")
    else:
        resumen = "El análisis no dio resultados válidos."
    op = _menu(lab, "¿Tus datos apoyan tu hipótesis?", ["Sí", "No", "No es concluyente"],
                ayuda=resumen[:70])
    exp["apoyo"] = ["si", "no", "inconcluso"][op or 0]
    opciones = ["Escribir el manuscrito y llevarlo al buzón del Revisor 2",
                "Cambiar el análisis y volver a correrlo",
                "Regresar a una etapa del laboratorio",
                "Cambiar la hipótesis para que coincida con los datos",
                "Salir y pensarlo"]
    while True:
        op = _menu(lab, f"Hipótesis: {h[:60]}…" if len(h) > 60 else f"Hipótesis: {h}", opciones)
        if op == 0:
            X.avanzar(exp, 6)
            _decir(lab, "Manuscrito listo. Llévalo al buzón (cuarto de abajo a la izquierda).")
            return "buzon"
        if op == 1:
            return "otra"
        if op == 2:
            etapas = [L.ETAPAS[i][0] for i in range(6)]
            e = _menu(lab, "¿A qué etapa regresas? (todo lo de después se rehace y se paga "
                            "otra vez)", etapas)
            if e is None:
                continue
            X.regresar(exp, e)
            lab.guardar()
            _decir(lab, f"Regresaste a: {etapas[e]}. Ve a esa estación.")
            return "regreso"
        if op == 3:
            otras = [i for i in range(len(info["hipotesis"])) if i != exp["hipotesis"]]
            e = _menu(lab, "Nueva hipótesis", [info["hipotesis"][i] for i in otras])
            if e is None:
                continue
            exp["hipotesis"] = otras[e]
            exp["harking"] = True
            exp["exploratorio"] = _menu(lab, "¿Cómo lo reportas en el manuscrito?", [
                "Como si fuera la hipótesis original",
                "Como hallazgo exploratorio, aclarando que surgió de los datos"]) == 1
            continue
        return "salir"


# ============================================================== 7 · buzón
def buzon(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 7)):
        _decir(lab, m)
        return
    if _menu(lab, "Buzón del Revisor 2", ["Enviar el manuscrito", "Todavía no"]) != 0:
        return
    res = lab.analizar()
    dis = exp["dis"]
    comentarios = revisor.revisar(dis, caso, res, lab.dif, exp)
    cal = revisor.calificar(dis, caso, res, comentarios, lab.dif)
    meta = revisor.meta(caso, lab.dif)
    nota = calificacion.calificar(exp, caso, res, comentarios, meta)
    anim.sello(lab.win, cal["dictamen"], cal["color"], lab.juego["velocidad"])
    mesa.mostrar_dictamen(lab.win, caso, comentarios, cal, meta,
                          libre=caso.get("libre"), nombre=progreso.nombre(lab.juego),
                          con_nota=True)
    calificacion.pantalla(lab.win, exp, caso, res, comentarios, nota,
                          progreso.nombre(lab.juego))
    exp["enviado"] = True
    juego = lab.juego
    cal.update(aprobado=nota["resuelto"], estrellas=nota["estrellas"], nota=nota["total"],
               letra=nota["letra"], dias=exp["dia"], gastado=exp["gastado"])
    previo = progreso.mejor(juego, caso["id"], lab.dif)
    if previo is None or (cal["estrellas"], cal.get("nota", 0)) > (previo["estrellas"],
                                                                   previo.get("nota", 0)):
        juego["mejores"].setdefault(caso["id"], {})[lab.dif] = cal
    if cal["aprobado"]:
        import casos
        i = casos.CASOS.index(caso)
        nuevo_caso = i + 1 > juego["desbloqueado"] and i + 1 < len(casos.CASOS)
        juego["desbloqueado"] = max(juego["desbloqueado"], i + 1)
        if nuevo_caso:
            d.popup(lab.win, f"<bien!>Nuevo caso desbloqueado:</> {casos.CASOS[i + 1]['titulo']}"
                             " (Jugar → Siguiente caso).", MENTORA, ancho=74)
        d.popup(lab.win, f"<bien!>Lección del caso.</> {caso['leccion']}\n\n"
                         f"<tenue>{datos.cita(*caso['fuentes'].split())}</>", MENTORA, ancho=74)
    lab.guardar()
    while True:
        op = _menu(lab, "¿Ahora qué?", ["Exportar el protocolo completo",
                                             "Seguir en el laboratorio (corregir y reenviar)",
                                             "Terminar el caso y volver al menú"])
        if op == 0:
            ruta = protocolo.generar(dis, caso, comentarios, res, lab.dif, exp,
                                     progreso.nombre(lab.juego))
            juego["protocolos"].append(ruta)
            progreso.guardar(juego)
            d.popup(lab.win, f"Protocolo guardado en:\n\n<agua>{ruta}</>", "Protocolo", ancho=80)
        elif op == 1:
            exp["etapa"] = 6
            return
        else:
            lab.terminar = True
            return
