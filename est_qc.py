"""Etapa 3: control de calidad del ARN (NanoDrop, gel y Bioanalyzer)."""

import curses
import math
import random
import minijuegos as mj
import datos
import dibujo as d
from idioma import tr
import expediente as X
import simulacion as sim
from estacion_comun import TECNICO, decir, pagar


# ================================================================== 3 · QC
def qc(lab, pestana=0):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 3)):
        decir(lab, m)
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
        "Quitar el blanco del pedestal con papel",
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
        decir(lab, ("<mal!>La gota no cerró la columna:</> lectura errática. Repite."
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
            decir(lab, "<mal!>Se salió del pozo.</> Ese carril se ve corrido; vuelves a "
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
    d.put(win, y, 2, "NanoDrop: absorbancia a 230, 260 y 280 nm (ARN puro: ~2.0 en ambos "
          "cocientes; preocupa por debajo de 1.8)", d.c("agua", curses.A_BOLD))
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
    d.put(win, y0 - 1, 2, tr(f"Bioanalyzer · muestra {_nombre(caso, k)} · ")
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


def _medidas(q, caso):
    """Lo medido de una muestra, para decidir sin ir y venir entre pestañas
    (sin juzgarlo: eso le toca al jugador)."""
    if "viabilidad" in q:
        return f"viabilidad {q['viabilidad']} %"
    partes = [f"{q['ng']:>6.1f} ng/µL", f"260/280 {q['r280']:.2f}", f"260/230 {q['r230']:.2f}"]
    if caso.get("rin", 9) < 4:                 # FFPE: el DV200 importa más que el RIN
        partes.append(f"DV200 {q['dv200']} %")
    if "rin" in q:
        partes.append(f"RIN {q['rin']}")
    return "   ".join(partes)


def _decisiones(win, exp, caso, claves, sel):
    y = 3
    d.put(win, y, 2, "Decide qué pasa con cada muestra. El gel (pestaña 2) muestra si hay ADN genómico.",
          d.c("agua", curses.A_BOLD))
    y += 2
    colores = {"pendiente": "tenue", "aprobada": "bien", "excluida": "mal"}
    alto = win.getmaxyx()[0]
    ini = max(0, min(sel - (alto - 10) // 2, len(claves) - (alto - 10)))
    for i, k in enumerate(claves[ini: ini + alto - 9], start=ini):
        q = exp["qc"][k]
        marca = "► " if i == sel else "  "
        d.trozos(win, y, 4, [(marca, "titulo"), (f"{_nombre(caso, k):<6}", "texto"),
                             (f"{q['estado']:<10}", colores[q["estado"]], curses.A_BOLD),
                             (_medidas(q, caso), "tenue")])
        y += 1


def _reextraer(lab, k):
    exp, caso = lab.exp, lab.caso
    if not pagar(lab, datos.EXTRACCION, f"Re-extraer {_nombre(caso, k)}"):
        return
    nueva = X.calidad_muestras(exp, caso, random.Random())
    q = nueva[k]
    if q.get("rin", 9) < exp["qc"][k].get("rin", 9) - 2.5:
        q["rin"] = exp["qc"][k]["rin"]           # no hay mala suerte dos veces
    exp["qc"][k] = q
    exp["reextracciones"] += 1
    exp["dia"] += 1
    decir(lab, f"{_nombre(caso, k)} re-extraída (+1 día, ${datos.EXTRACCION}). Revisa sus "
                "nuevos valores.", TECNICO)


def _terminar_qc(lab):
    exp, caso = lab.exp, lab.caso
    pend = [k for k, q in exp["qc"].items() if q["estado"] == "pendiente"]
    if pend:
        decir(lab, f"Faltan {len(pend)} muestras por decidir.")
        return False
    X.aplicar_qc(exp, caso)
    if sim.replicas_efectivas(exp["dis"], caso) < 2:
        decir(lab, "Te quedaste con menos de 2 réplicas en algún grupo: no hay estadística "
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
            decir(lab, " ".join(tr(t) for t in txt) + tr(" (Lo verás en el dictamen.)"))
    X.avanzar(exp, 3)
    lab.guardar()
    decir(lab, "QC terminado y anotado. Siguiente: la biblioteca, en el estante de kits del "
                "laboratorio húmedo.", TECNICO)
    return True
