#!/usr/bin/env python3
"""REVISOR 2 — diseña experimentos de RNA-seq que sobrevivan a la revisión."""

import curses
import locale
import os

import animaciones as anim
import casos
import datos
import dibujo as d
import idioma
import laboratorio
import manual
import mesa
import metodos
import preguntas
import progreso
import revisor
import tutorial

FUENTE = {
    "R": ["█▀▀▄", "█▀▀▄", "█  █"], "E": ["█▀▀▀", "█▀▀ ", "█▄▄▄"],
    "V": ["█   █", "▀▄ ▄▀", " ▀█▀ "], "I": ["█", "█", "█"],
    "S": ["▄▀▀▀", " ▀▀▄", "▄▄▄▀"], "O": ["▄▀▀▄", "█  █", "▀▄▄▀"],
    "2": ["▀▀▀▄", "▄▀▀ ", "█▄▄▄"], " ": ["  ", "  ", "  "],
}
MENTORA = tutorial.MENTORA


def logo(palabra):
    filas = ["", "", ""]
    for letra in palabra:
        for i in range(3):
            filas[i] += FUENTE[letra][i] + " "
    return filas


def esperar_tamano(win):
    while True:
        alto, ancho = win.getmaxyx()
        if alto >= 24 and ancho >= 80:
            return
        win.erase()
        d.put(win, 0, 0, f"Agranda la terminal a 80×24 o más (ahora {ancho}×{alto}).")
        d.put(win, 1, 0, "Lo ideal: pantalla completa (F11).")
        win.refresh()
        d.tecla(win)


def portada(win, y0):
    alto, ancho = win.getmaxyx()
    filas = logo("REVISOR 2")
    x0 = (ancho - len(filas[0])) // 2
    for i, l in enumerate(filas):
        d.put(win, y0 + i, x0, l, d.c(["g0", "texto", "g1"][i], curses.A_BOLD))
    sub = "· diseña experimentos de RNA-seq que sobrevivan a la revisión ·"
    d.put(win, y0 + 4, (ancho - len(sub)) // 2, sub, d.c("titulo", curses.A_BOLD))
    lecturas = "@lectura_1  ACGTTGCAGGATCCATTGCA  +  IIIIIHHHGGFFF"
    d.put(win, y0 + 6, (ancho - len(lecturas)) // 2, lecturas, d.c("tenue"))
    if ancho < 120 or alto < 36:
        aviso = f"Consejo: pon la terminal en pantalla completa (F11). Ahora: {ancho}×{alto}"
        d.put(win, alto - 2, (ancho - len(aviso)) // 2, aviso, d.c("agua"))


def elegir_dificultad(win, actual="normal"):
    claves = revisor.ORDEN_DIFICULTAD
    sel = claves.index(actual)
    colores = {"facil": "bien", "normal": "titulo", "dificil": "mal"}
    while True:
        alto, ancho = win.getmaxyx()
        w = min(70, ancho - 2)
        h = 14
        y0, x0 = max(0, (alto - h) // 2), (ancho - w) // 2
        win.erase()
        d.caja(win, y0, x0, h, w, "Dificultad")
        for i, k in enumerate(claves):
            dif = revisor.DIFICULTADES[k]
            marca = "▸ " if i == sel else "  "
            attr = d.c(colores[k], curses.A_BOLD | (curses.A_REVERSE if i == sel else 0))
            d.put(win, y0 + 2 + i, x0 + 4, f"{marca}{dif['nombre']:<10}", attr)
        dif = revisor.DIFICULTADES[claves[sel]]
        for i, partes in enumerate(d.a_lineas([dif["desc"]], w - 6)[:5]):
            d.trozos(win, y0 + 6 + i, x0 + 3, partes, x0 + w - 2)
        d.put(win, y0 + h - 2, x0 + 3, "↑↓ elegir · Enter aceptar · Esc volver", d.c("tenue"))
        win.refresh()
        k = d.tecla(win)
        if d.es(k, curses.KEY_UP, "w", "k"):
            sel = (sel - 1) % len(claves)
        elif d.es(k, curses.KEY_DOWN, "s", "j"):
            sel = (sel + 1) % len(claves)
        elif k in d.ENTER:
            return claves[sel]
        elif k == d.ESC or d.es(k, "q"):
            return None
        elif isinstance(k, str) and k in "123":
            return claves[int(k) - 1]


def pedir_nombre(win, juego):
    """Pregunta cómo llamar al jugador; se puede cambiar en Opciones."""
    while True:
        win.erase()
        portada(win, max(1, win.getmaxyx()[0] // 2 - 9))
        txt = d.entrada(win, "¿Cómo te llamas?", juego.get("nombre") or "", largo=24)
        if txt:
            juego["nombre"] = txt
            progreso.guardar(juego)
            return
        if juego.get("nombre"):
            return


def titulo(win):
    hay = progreso.cargar() is not None
    while True:
        alto, _ = win.getmaxyx()
        win.erase()
        y0 = max(1, alto // 2 - 9)
        portada(win, y0)
        opciones = (["Continuar"] if hay else []) + ["Nueva partida", "Salir"]
        sel = d.menu(win, None, opciones, y=y0 + 9)
        if sel is None or opciones[sel] == "Salir":
            return None
        if opciones[sel] == "Nueva partida" and hay:
            if d.menu(win, "¿Borrar la partida guardada?", ["No", "Sí, empezar de cero"]) != 1:
                continue
        if opciones[sel] == "Continuar":
            juego = progreso.cargar()
            if not juego.get("nombre"):
                pedir_nombre(win, juego)
            return juego
        juego = progreso.nuevo_juego()
        win.erase()
        pedir_nombre(win, juego)
        nombre = progreso.nombre(juego)
        d.dialogo(win, [
            f"Hola, <titulo!>{nombre}</>. Te doy la bienvenida al <titulo!>Núcleo de "
            "Secuenciación</>. Soy la Dra. Lazo, responsable del núcleo.",
            "Cada semana llegan investigadores con una pregunta, un presupuesto y "
            "muestras. Tu trabajo: diseñar el experimento (biblioteca, réplicas, lotes, "
            "lecturas, análisis) para que responda la pregunta.",
            "Después el experimento se realiza (lo simulamos con datos de verdad) y la "
            "propuesta va al <mal!>Revisor 2</>. Ya sabes cómo es el Revisor 2.",
        ], MENTORA)
        juego["dificultad"] = elegir_dificultad(win, "normal") or "normal"
        progreso.guardar(juego)
        win.erase()
        if d.menu(win, "¿Tomar la capacitación? (recomendado la primera vez)",
                  ["Sí, explícame RNA-seq desde cero", "No, ya sé cómo funciona"]) == 0:
            tutorial.capacitacion(win, juego)
        return juego


def jugar_caso(win, juego, indice):
    caso = casos.CASOS[indice]
    expedientes = juego.setdefault("expedientes", {})
    exp = expedientes.get(caso["id"])
    win.erase()
    if exp and not exp.get("enviado"):
        op = d.menu(win, f"Caso {indice + 1}: {caso['titulo']}",
                    [f"Continuar el experimento (día {exp['dia']}, etapa {exp['etapa'] + 1}/8)",
                     "Empezar el experimento desde cero", "Volver"])
        if op is None or op == 2:
            return
        if op == 1:
            expedientes.pop(caso["id"], None)
    elif exp:
        if d.menu(win, f"Caso {indice + 1}: {caso['titulo']}",
                  ["Repetir el experimento desde cero", "Volver"]) != 0:
            return
        expedientes.pop(caso["id"], None)
    juego["caso_actual"] = caso["id"]
    laboratorio.Lab(win, juego, caso).jugar()
    progreso.guardar(juego)


def laboratorio_libre(win, juego):
    """El jugador describe su propio experimento y obtiene su protocolo."""
    win.erase()
    d.popup(win, "Laboratorio libre: describe TU experimento. Lo diseñas en la mesa, el "
                 "Revisor 2 lo critica con reglas generales (sin trampas escondidas) y "
                 "exportas el protocolo completo.", MENTORA, ancho=70)
    organismo = d.entrada(win, "Organismo y tejido (p. ej. Ratón, hígado)", largo=60)
    if not organismo:
        return
    objetivos = [("genes", "Expresión diferencial de genes"),
                 ("antisentido", "lncRNA / antisentido"),
                 ("splicing", "Isoformas y splicing"),
                 ("mirna", "miRNA y ARN pequeños"),
                 ("celulas", "Un tipo celular dentro de un tejido (célula única)"),
                 ("tiempo", "Serie de tiempo"),
                 ("interaccion", "Factorial genotipo × tratamiento (2×2)"),
                 ("global", "Cambio global del ARN por célula")]
    o = d.menu(win, "¿Qué quieres medir?", [t for _, t in objetivos])
    if o is None:
        return
    objetivo = objetivos[o][0]
    if objetivo == "interaccion":
        grupos = ["WT control", "WT tratado", "KO control", "KO tratado"]
    else:
        txt = d.entrada(win, "Grupos separados por coma (el primero es la referencia)",
                        "Control, Tratado" if objetivo != "tiempo" else "0 h, 2 h, 8 h, 24 h",
                        largo=70)
        if not txt:
            return
        grupos = [g.strip() for g in txt.split(",") if g.strip()][:6]
        if len(grupos) < 2:
            d.popup(win, "Hacen falta al menos dos grupos.", MENTORA)
            return
    pareado = d.menu(win, "¿Cada donante aporta una muestra de cada grupo (pareado)?",
                     ["No", "Sí"]) == 1
    cap_txt = d.entrada(win, "¿Cuántas muestras caben por lote? (vacío = sin límite)", "",
                        largo=6)
    capacidad = int(cap_txt) if cap_txt and cap_txt.isdigit() and int(cap_txt) > 0 else None
    pres_txt = d.entrada(win, "Presupuesto en USD", "20000", largo=8)
    presupuesto = int(pres_txt) if pres_txt and pres_txt.isdigit() else 20000
    rin_txt = d.entrada(win, "RIN esperado (1-10; FFPE ~2)", "8", largo=4)
    try:
        rin = float(rin_txt)
    except (TypeError, ValueError):
        rin = 8.0
    pregunta = f"{objetivos[o][1]}: {' vs '.join(grupos)}"
    caso = casos.caso_libre(organismo, grupos, objetivo, f"RIN {rin}", pareado,
                            capacidad, presupuesto, rin, pregunta)
    mesa.Mesa(win, juego, caso).jugar()


def ver_protocolos(win, juego):
    from protocolo import CARPETA
    rutas = [r for r in juego["protocolos"] if os.path.exists(r)]
    if not rutas:
        d.popup(win, f"Aún no exportas protocolos. Se guardan en:\n\n<agua>{CARPETA}</>",
                "Protocolos")
        return
    nombres = [os.path.basename(r) for r in rutas][::-1]
    sel = d.menu(win, f"Protocolos en {CARPETA}", nombres, ancho=min(90, win.getmaxyx()[1] - 2))
    if sel is None:
        return
    with open(rutas[::-1][sel], encoding="utf-8") as f:
        texto = f.read().split("\n")
    d.visor(win, nombres[sel], [l.replace("<", "‹") for l in texto], ancho_max=120)


def estado(win, juego, y, x):
    dif = revisor.DIFICULTADES[juego["dificultad"]]["nombre"]
    d.put(win, y - 1, x, f"Investigador(a): {progreso.nombre(juego)}", d.c("agua"))
    d.put(win, y, x, f"CASOS · récords en {dif}", d.c("titulo", curses.A_BOLD))
    for i, c in enumerate(casos.CASOS):
        if i > juego["desbloqueado"]:
            d.put(win, y + 1 + i, x, f"{i + 1:>2}. ???", d.c("oscuro"))
            continue
        m = progreso.mejor(juego, c["id"], juego["dificultad"])
        partes = [(f"{i + 1:>2}. ", "tenue"), (f"{c['titulo']:<28}", "texto")]
        if m:
            partes += [(d.estrellas(m["estrellas"]), "titulo")]
        elif progreso.mejor(juego, c["id"]):
            partes.append(("sin jugar aquí", "oscuro"))
        else:
            partes.append(("nuevo", "agua"))
        d.trozos(win, y + 1 + i, x, partes)
    yy = y + len(casos.CASOS) + 2
    if juego["examen"] is not None:
        d.put(win, yy, x, f"Examen: mejor {juego['examen']}/20"
              + ("  · Revisor 1" if juego["examen"] >= 16 else ""),
              d.c("bien" if juego["examen"] >= 16 else "tenue"))


def submenu(win, juego, titulo, opciones):
    """Menú secundario centrado sobre la portada. Devuelve la clave o None."""
    nombres = [n for n, _ in opciones]
    alto, _ = win.getmaxyx()
    sel = d.menu(win, titulo, nombres, y=min(alto - len(nombres) - 3, 12 if alto >= 34 else 5))
    return None if sel is None else opciones[sel][1]


def menu_jugar(win, juego):
    total = len(casos.CASOS)
    sig = min(juego["desbloqueado"], total - 1)
    ops = []
    actual = juego.get("caso_actual")
    exps = juego.get("expedientes", {})
    if actual in exps and exps[actual].get("etapa", 0) < 8 and not exps[actual].get("enviado"):
        i = next(i for i, c in enumerate(casos.CASOS) if c["id"] == actual)
        ops.append((f"Continuar: {casos.CASOS[i]['titulo']} (día {exps[actual]['dia']})",
                    ("caso", i)))
    if juego["desbloqueado"] < total:
        ops.append((f"Siguiente caso: {sig + 1}. {casos.CASOS[sig]['titulo']}", ("caso", sig)))
    ops += [("Elegir un caso", ("elegir",)),
            ("Laboratorio libre: diseña tu protocolo", ("libre",)),
            ("Capacitación (lecciones desde cero)", ("tutorial",)),
            ("Volver", None)]
    a = submenu(win, juego, "Jugar", ops)
    if not a:
        return
    if a[0] == "caso":
        jugar_caso(win, juego, a[1])
    elif a[0] == "elegir":
        hechos = list(range(min(juego["desbloqueado"] + 1, total)))
        nombres = []
        for i in hechos:
            m = progreso.mejor(juego, casos.CASOS[i]["id"])
            est = d.estrellas(m["estrellas"]) if m else ""
            nombres.append(f"{i + 1:>2}. {casos.CASOS[i]['titulo']:<30} {est}")
        s = d.menu(win, "Casos", nombres)
        if s is not None:
            jugar_caso(win, juego, hechos[s])
    elif a[0] == "libre":
        laboratorio_libre(win, juego)
    elif a[0] == "tutorial":
        tutorial.capacitacion(win, juego)


def menu_estudiar(win, juego):
    while True:
        a = submenu(win, juego, "Estudiar", [
            ("Manual del laboratorio", manual.mostrar),
            ("Catálogo de métodos de transcriptómica", manual.catalogo),
            ("Glosario", manual.glosario),
            ("Volver", None)])
        if not a:
            return
        a(win)


def menu_practicar(win, juego):
    a = submenu(win, juego, "Practicar", [("Repaso libre", preguntas.repaso),
                                          ("Examen de Comité (20 preguntas)", preguntas.examen),
                                          ("Volver", None)])
    if a:
        a(win, juego)


def menu_opciones(win, juego):
    while True:
        a = submenu(win, juego, "Opciones", [
            (f"Dificultad: {revisor.DIFICULTADES[juego['dificultad']]['nombre']}", "dif"),
            (f"Velocidad de animaciones: {juego['velocidad']}", "vel"),
            (f"Tu nombre: {progreso.nombre(juego)}", "nombre"),
            ("Idioma / Language: Español" if idioma.ACTUAL == "es" else
             "Idioma / Language: English", "idioma"),
            ("Volver", None)])
        if not a:
            return
        if a == "dif":
            nueva = elegir_dificultad(win, juego["dificultad"])
            if nueva:
                juego["dificultad"] = nueva
        elif a == "vel":
            orden = anim.ORDEN_VEL
            juego["velocidad"] = orden[(orden.index(juego["velocidad"]) + 1) % len(orden)]
        elif a == "nombre":
            pedir_nombre(win, juego)
        elif a == "idioma":
            idioma.cambiar("en" if idioma.ACTUAL == "es" else "es")
        progreso.guardar(juego)


def hub(win, juego):
    while True:
        alto, ancho = win.getmaxyx()
        win.erase()
        if alto < 34:
            filas = logo("REVISOR 2")
            for i, l in enumerate(filas):
                d.put(win, i, (ancho - len(filas[0])) // 2, l,
                      d.c(["g0", "texto", "g1"][i], curses.A_BOLD))
            y_menu = 4
        else:
            portada(win, 1)
            y_menu = 10
        opciones = ["Jugar", "Estudiar", "Practicar", "Protocolos exportados", "Opciones",
                    "Guardar y salir"]
        if not juego["tutorial"]:
            opciones.insert(0, "★  Capacitación: empieza aquí")
        ancho_menu = 36
        if ancho >= 96:
            xm = ancho // 2 - ancho_menu - 2
            estado(win, juego, y_menu, ancho // 2 + 2)
        else:
            xm = None
        sel = d.menu(win, "Núcleo de Secuenciación", opciones, y=y_menu, x=xm, ancho=ancho_menu)
        if sel is None:
            continue
        o = opciones[sel]
        if o.startswith("★"):
            tutorial.capacitacion(win, juego)
        elif o == "Jugar":
            menu_jugar(win, juego)
        elif o == "Estudiar":
            menu_estudiar(win, juego)
        elif o == "Practicar":
            menu_practicar(win, juego)
        elif o == "Protocolos exportados":
            ver_protocolos(win, juego)
        elif o == "Opciones":
            menu_opciones(win, juego)
        else:
            progreso.guardar(juego)
            return


def main(win):
    curses.curs_set(0)
    d.init_colores()
    win.keypad(True)
    # sin optimizaciones de insertar/borrar caracteres: con texto acentuado
    # algunas terminales se desfasan y dejan restos de líneas anteriores
    win.idcok(False)
    win.idlok(False)
    curses.set_escdelay(25)
    esperar_tamano(win)
    juego = titulo(win)
    if juego is None:
        return
    hub(win, juego)


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "")
    curses.wrapper(main)
