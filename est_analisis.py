"""Etapas 5 a 7: secuenciador, computadora de bioinformática y buzón del
Revisor 2."""

import random
import animaciones as anim
import calificacion
import minijuegos as mj
import datos
import dibujo as d
from idioma import tr
import expediente as X
import lab_datos as L
import mesa
import progreso
import protocolo
import revisor
from estacion_comun import Formulario, MENTORA, TECNICO, cobrar, decir, menu


# ======================================================= 5 · secuenciador
def secuenciador(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 5)):
        decir(lab, m)
        return
    if exp["etapa"] > 5:
        if menu(lab, "Ya secuenciaste", ["Volver", "Secuenciar otra vez"]) != 1:
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
                              tr("Disponibles en esta plataforma: ")
                              + ", ".join(tr(datos.LECTURAS[x]["nombre"]) for x in
                                          L.PLATAFORMAS[exp["plataforma"]]["lecturas"])]),
        dict(tipo="opcion", etiqueta="Lecturas por muestra",
             opciones=[(p, f"{p} M") for p in datos.PROFUNDIDADES],
             get=lambda: dis["profundidad"], set=lambda v: dis.__setitem__("profundidad", v),
             costo=lambda: dis["profundidad"] and
                           f"${datos.costo_secuenciacion(dis):,.0f} por muestra → "
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
        if dis["profundidad"] is None:
            decir(lab, "Primero elige cuántas lecturas por muestra vas a secuenciar.", TECNICO)
            continue
        if dis["lectura"] not in L.PLATAFORMAS[exp["plataforma"]]["lecturas"]:
            decir(lab, "Esa lectura no existe en esta plataforma.", TECNICO)
            continue
        if cobrar(lab, 5):
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
        decir(lab, ("<mal!>Celda subcargada:</> salieron muchas menos lecturas de las pedidas."
                     if carga < 85 else "<mal!>Celda sobrecargada:</> clusters encimados; "
                                        "el filtro de calidad tiró muchas lecturas."), TECNICO)
    n, _ = X.corridas_necesarias(exp, caso)
    anim.secuenciacion(lab.win, datos.n_muestras(dis, caso), lab.juego["velocidad"])
    dias = n * L.PLATAFORMAS[exp["plataforma"]]["dias"]
    exp["dia"] += dias
    X.avanzar(exp, 5)
    exp["semilla_sec"] = random.randrange(10 ** 9)
    lab.guardar()
    decir(lab, f"Pasaron {dias} días. Los FASTQ ya están en el servidor: ve a la computadora "
                "de bioinformática.", TECNICO)


# ====================================================== 6 · computadora
def computadora(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 6)):
        decir(lab, m)
        return
    dis = exp["dis"]
    formulas = list(datos.ORDEN_FORMULAS)

    def ficha_tabla(tabla, extra_fuente=None):
        def f(v):
            if v is None:
                return ["Usa ←→ para ver cada opción."]
            x = tabla[v]
            out = [f"<titulo!>{x['nombre']}</>", x["texto"]]
            if "fuente" in x:
                out.append(f"<tenue>{datos.cita(*x['fuente'].split())}</>")
            return out
        return f

    def set_formula(v):
        if v in ("lote", "par_lote", "tiempo_lote") and "lote" not in exp["registros"]:
            decir(lab, "No anotaste el lote de cada muestra en la hoja de muestras: no hay "
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
        if dis["ruta"] is None:
            decir(lab, "Primero elige la ruta de cuantificación.")
            continue
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
    op = menu(lab, "¿Tus datos apoyan tu hipótesis?", ["Sí", "No", "No es concluyente"], barajar=True,
                ayuda=resumen[:70])
    exp["apoyo"] = ["si", "no", "inconcluso"][op or 0]
    opciones = ["Escribir el manuscrito y llevarlo al buzón del Revisor 2",
                "Cambiar el análisis y volver a correrlo",
                "Regresar a una etapa del laboratorio",
                "Cambiar la hipótesis para que coincida con los datos",
                "Salir y pensarlo"]
    while True:
        op = menu(lab, f"Hipótesis: {h[:60]}…" if len(h) > 60 else f"Hipótesis: {h}", opciones)
        if op == 0:
            X.avanzar(exp, 6)
            decir(lab, "Manuscrito listo. Llévalo al buzón (cuarto de abajo a la izquierda).")
            return "buzon"
        if op == 1:
            return "otra"
        if op == 2:
            etapas = [L.ETAPAS[i][0] for i in range(6)]
            e = menu(lab, "¿A qué etapa regresas? (todo lo de después se rehace y se paga "
                            "otra vez)", etapas)
            if e is None:
                continue
            X.regresar(exp, e)
            lab.guardar()
            decir(lab, f"Regresaste a: {etapas[e]}. Ve a esa estación.")
            return "regreso"
        if op == 3:
            otras = [i for i in range(len(info["hipotesis"])) if i != exp["hipotesis"]]
            e = menu(lab, "Nueva hipótesis", [info["hipotesis"][i] for i in otras])
            if e is None:
                continue
            exp["hipotesis"] = otras[e]
            exp["harking"] = True
            exp["exploratorio"] = menu(lab, "¿Cómo lo reportas en el manuscrito?", barajar=True, opciones=[
                "Como si fuera la hipótesis original",
                "Como hallazgo exploratorio, aclarando que surgió de los datos"]) == 1
            continue
        return "salir"


# ============================================================== 7 · buzón
def buzon(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 7)):
        decir(lab, m)
        return
    if menu(lab, "Buzón del Revisor 2", ["Enviar el manuscrito", "Todavía no"]) != 0:
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
        op = menu(lab, "¿Ahora qué?", ["Exportar el protocolo completo",
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
