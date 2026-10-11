"""Etapas 2 y 4 del laboratorio húmedo: extracción de ARN en la campana y
preparación de bibliotecas en el estante de kits."""

import curses
import random
import time
import minijuegos as mj
import datos
import dibujo as d
from idioma import tr
import expediente as X
import lab_datos as L
import simulacion as sim
from estacion_comun import Formulario, TECNICO, cobrar, decir, menu


# ================================================================ 2 · campana
def campana(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 2)):
        decir(lab, m)
        return
    if exp["etapa"] > 2:
        if menu(lab, "Ya extrajiste el ARN", ["Volver", "Extraer todo otra vez "
                                                    "(se repite el QC)"]) != 1:
            return
        X.regresar(exp, 2)
    win = lab.win
    claves = L.ORDEN_EXTRACCIONES
    op = menu(lab, "Campana de extracción · ¿qué método?", barajar=True,
                opciones=[L.EXTRACCIONES[k]["nombre"] for k in claves] + ["Volver"])
    if op is None or op == len(claves):
        return
    met = claves[op]
    exp["extraccion"] = met
    e = L.EXTRACCIONES[met]
    decir(lab, f"{e['texto']}\n\n<tenue>{datos.cita(*e['fuente'].split())}</>", e["nombre"])
    p = {}
    if e["celulas"]:
        op = menu(lab, "Disociación del tejido", barajar=True, opciones=["En frío (4-6 °C), enzimas activas en frío, "
                                                     "≤ 30 min", "A 37 °C durante 1 h para "
                                                     "que se suelten bien"])
        p["calor"] = op == 1
        p["limpieza"] = True
        p["dnasa"] = True
        p["homogenizacion"] = 0.5
    else:
        op = menu(lab, "Antes de empezar", barajar=True, opciones=[
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
                decir(lab, ("<mal!>Muy poco cloroformo:</> las fases no se separan bien y "
                             "arrastras fenol y ADN." if vol < 0.17 else
                             "<mal!>Demasiado cloroformo:</> la fase acuosa queda más chica y "
                             "pierdes ARN."), TECNICO)
            p["fase"] = _fases(lab)
            al = menu(lab, "Precipitación de la fase acuosa", barajar=True, opciones=[
                "Isopropanol, 10 min en hielo, centrifugar", "Etanol al 100 %",
                "No precipito: paso directo al tubo"])
            p["alcohol"] = ["isopropanol", "etanol100", "ninguno"][al or 0]
            if caso.get("poco_material"):
                p["glucogeno"] = menu(lab, "Hay muy poco ARN…", barajar=True, opciones=[
                    "Agrego glucógeno como acarreador", "No hace falta"]) == 0
            sec = menu(lab, "Lavado con etanol al 75 % y secado", barajar=True, opciones=[
                "Seco 5-10 min hasta que el pellet se vea transparente",
                "Seco hasta que el pellet esté blanco y quebradizo"])
            p["secado"] = "bien" if sec == 0 else "seco"
        else:
            p["fase"] = "acuosa"
            p["alcohol"] = "isopropanol"
        p["dnasa"] = menu(lab, "¿Y el ADN genómico?", barajar=True, opciones=[
            "Tratamiento con DNasa I (en columna)", "No hace falta"]) == 0
    exp["pasos"] = p
    exp["dis"]["pierde_pequenos"] = not e["guarda_pequenos"]
    if not cobrar(lab, 2):
        return
    exp["qc"] = X.calidad_muestras(exp, caso)
    exp["semilla"] = random.randrange(10 ** 9)
    X.avanzar(exp, 2)
    exp["dia"] += max(0, len(sim.tabla_lotes(exp["dis"], caso)) - 1)
    lab.guardar()
    decir(lab, f"Listo: {len(exp['qc'])} muestras en tubos etiquetados en el hielo. Llévalas "
                "al cuarto de QC (NanoDrop, gel y Bioanalyzer).", TECNICO)


def _barra_tiempo(lab, titulo, explicacion):
    win = lab.win
    decir(lab, explicacion, titulo)
    lab.dibujar()
    ancho_b = 40
    zona = (0.4, 0.7)
    pos, paso = random.random(), random.choice((0.025, -0.025))
    inicio = time.monotonic()
    win.nodelay(True)
    curses.flushinp()
    try:
        while True:
            t = time.monotonic()
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
            d.pausa(45, t)
            k = win.getch()
            if mj.detener(k, inicio):
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
    decir(lab, msg, titulo)
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
    d.popup(lab.win, "\n".join(tr(l) for l in tubo), "Separación de fases", ancho=62, esperar=False)
    op = d.menu(lab.win, "¿Qué fase tomas?", barajar=True, y=lab.win.getmaxyx()[0] - 7,
                opciones=["1 · Superior acuosa (transparente)",
                                               "2 · Interfase", "3 · Inferior orgánica (rosa)"])
    fase = ["acuosa", "interfase", "organica"][op or 0]
    exp_txt = {"acuosa": "<bien>Bien:</> el ARN queda en la fase acuosa.",
               "interfase": "<mal>La interfase tiene ADN y proteína.</>",
               "organica": "<mal>La fase orgánica tiene fenol, proteínas y lípidos.</>"}[fase]
    if lab.pistas:
        decir(lab, exp_txt)
    return fase


# ============================================================== 4 · kits
def kits(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 4)):
        decir(lab, m)
        return
    if exp["etapa"] > 4:
        if menu(lab, "Las bibliotecas ya están hechas", ["Volver", "Rehacer las "
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
        if v is None:
            return ["<titulo!>Kit de biblioteca</>", "Usa ←→ para ver cada caja: qué mide, "
                    "cuánto cuesta y cuándo conviene."]
        b = datos.BIBLIOTECAS[v]
        return [f"<titulo!>{b['nombre']}</>  <tenue>${b['costo']} por muestra</>", b["resumen"],
                "", f"<bien>Cuándo:</> {b['cuando']}", f"<mal>Ojo:</> {b['malo']}",
                f"<tenue>{datos.cita(*b['fuente'].split())}</>"]

    filas = [dict(tipo="seccion", etiqueta="KIT"),
             dict(tipo="opcion", etiqueta="Caja del estante",
                  opciones=[(k, datos.BIBLIOTECAS[k]["nombre"]) for k in datos.ORDEN_BIBLIOTECAS],
                  get=lambda: dis["biblioteca"], set=lambda v: dis.__setitem__("biblioteca", v),
                  costo=lambda: dis["biblioteca"] and
                                f"${datos.BIBLIOTECAS[dis['biblioteca']]['costo']} por muestra"
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
    while True:
        if Formulario(lab.win, "Estante de kits de biblioteca", filas, pie).jugar() != "hacer":
            return
        if dis["biblioteca"] is not None:
            break
        decir(lab, "Primero elige qué kit vas a usar.", TECNICO)
    sc = dis["biblioteca"] in ("sc10x", "snrna", "smartseq")
    if sc != met["celulas"]:
        decir(lab, ("Para célula única necesitas células o núcleos vivos, no ARN extraído."
                     if sc else "Tienes una suspensión de células, no ARN: ese kit necesita ARN "
                                "extraído.") + " Regresa a la campana.", TECNICO)
        return
    if datos.BIBLIOTECAS[dis["biblioteca"]]["larga"]:
        dis["lectura"] = "LARGA"
    elif dis["lectura"] == "LARGA":
        dis["lectura"] = "PE100"
    if not cobrar(lab, 4):
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
            decir(lab, "<mal!>Muy pocas perlas:</> también tiraste buena parte de la "
                        "biblioteca. Saldrán menos lecturas útiles.", TECNICO)
        elif ratio > 0.95:
            dis["dimeros"] = True
            decir(lab, "<mal!>Demasiadas perlas:</> los dímeros se quedaron pegados con la "
                        "biblioteca.", TECNICO)
        else:
            decir(lab, "<bien!>Bien:</> sin dímeros y sin perder biblioteca.", TECNICO)
    X.avanzar(exp, 4)
    lab.guardar()
    decir(lab, "Bibliotecas listas, cuantificadas e indexadas. Siguiente: el secuenciador.",
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
    d.popup(win, "\n".join(traza) + "\n\n" + tr("Perfil de una biblioteca en el Bioanalyzer "
                                                 "(High Sensitivity DNA)."), "QC de la biblioteca", ancho=66, esperar=False)
    op = d.menu(win, "¿Qué ves?", barajar=True, y=win.getmaxyx()[0] - 7,
                opciones=["Un pico pequeño a ~125 pb: dímeros de adaptador",
                                   "Todo bien: un solo pico a 300-400 pb",
                                   "ARN degradado"])
    if op == 0:
        limpia = menu(lab, "¿Qué haces?", barajar=True, opciones=["Otra limpieza con perlas 0.8×",
                                             "Secuenciar así"]) == 0
        decir(lab, tr("Bien visto: los dímeros se secuencian igual y gastan lecturas.")
               + (tr(" Con la limpieza desaparecen.") if limpia else ""), TECNICO)
        return limpia
    decir(lab, "Mira el pico de ~125 pb: son dímeros de adaptador (adaptador pegado a "
                "adaptador, sin inserto). Se van a secuenciar y gastar lecturas.", TECNICO)
    return False
