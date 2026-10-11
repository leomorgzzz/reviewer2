"""El Revisor 2: lee el diseño, el caso y lo que salió de la simulación y
escribe su dictamen.

Cada comentario es dict(grav, texto, fuente) con grav:
  fatal  → el experimento no puede responder la pregunta (RECHAZADO)
  mayor  → hay que corregirlo (REVISIÓN MAYOR)
  menor  → mejorable (ACEPTADO CON CAMBIOS MENORES)
  bien   → algo que hiciste bien (el Revisor 2 también reconoce, a regañadientes)
"""

from idioma import tr
import datos
import simulacion as sim
from casos import ORDEN_LECTURA

DIFICULTADES = {
    "facil": dict(nombre="Fácil", presupuesto=1.3, meta=-0.1, pistas=True,
                  desc="Presupuesto +30 %, meta de sensibilidad más baja, pistas [P] con "
                       "lo que exige cada caso y la potencia estimada en la mesa."),
    "normal": dict(nombre="Normal", presupuesto=1.0, meta=0.0, pistas=False,
                   desc="Presupuesto del caso y potencia estimada en la mesa, sin pistas."),
    "dificil": dict(nombre="Difícil", presupuesto=0.85, meta=0.05, pistas=False,
                    desc="Presupuesto −15 %, meta más alta y sin potencia estimada: "
                         "decides como en la vida real, antes de ver los datos."),
}
ORDEN_DIFICULTAD = ["facil", "normal", "dificil"]

ORDEN_GRAV = {"fatal": 0, "mayor": 1, "menor": 2, "bien": 3}
# en series de tiempo «~ condición» y «~ tiempo» son la misma matriz
EQUIV = {"cond": "tiempo", "lote": "tiempo_lote"}


def presupuesto(caso, dif):
    return round(caso["presupuesto"] * DIFICULTADES[dif]["presupuesto"])


def meta(caso, dif):
    return max(0.0, caso["meta"] + DIFICULTADES[dif]["meta"])


_AREA = ["diseño"]


def _area(nombre):
    """Área a la que pertenecen los comentarios que siguen (para la calificación)."""
    _AREA[0] = nombre


def _c(grav, texto, fuente):
    return dict(grav=grav, texto=texto, fuente=fuente, area=_AREA[0])


def revisar(dis, caso, res, dif="normal", exp=None):
    c = revisar_lab(exp, caso, res) if exp else []
    _area("diseño")
    costo = datos.costo_total(dis, caso)
    if not exp and costo > presupuesto(caso, dif):
        c.append(_c("fatal", f"El experimento cuesta ${costo:,} y el presupuesto es de "
                    f"${presupuesto(caso, dif):,}: la agencia no lo financia.", ""))
    obj = caso["objetivo"]
    lib = dis["biblioteca"]
    b = datos.BIBLIOTECAS[lib]
    reps, tec = sim.replicas_efectivas(dis, caso), dis["tecnicas"]
    formula = dis["formula"]
    if obj == "tiempo":
        formula = EQUIV.get(formula, formula)
    libre = caso.get("libre")

    # ------------------------------------------------------------ réplicas
    # si las réplicas se perdieron en el QC, el error es del laboratorio
    excluidas = dis["replicas"] > reps
    _area("laboratorio" if excluidas else "diseño")
    previo = (tr("Al excluir muestras en el QC, un grupo se quedó con menos réplicas. ")
              if excluidas else "")
    if reps == 1:
        c.append(_c("fatal", previo + tr("Una sola réplica biológica por grupo: no hay manera de "
                                         "estimar la variación entre individuos, así que ningún valor p es "
                                         "válido. Esto es un estudio exploratorio, no un experimento."),
                    "CON16 SCH16"))
    elif reps == 2:
        c.append(_c("mayor", previo + tr("Dos réplicas por grupo: la varianza de cada gen se estima "
                                         "con un grado de libertad. Mínimo 3; Schurch 2016 recomienda al "
                                         "menos 6."), "SCH16 CON16"))
    elif reps >= 6:
        c.append(_c("bien", f"{reps} réplicas biológicas por grupo: suficiente para "
                    "detectar la mayoría de los cambios moderados (Schurch 2016: ≥ 6, "
                    "≥ 12 si importan los cambios pequeños).", "SCH16"))
    _area("diseño")
    if tec > 1:
        c.append(_c("mayor", f"{tec} réplicas técnicas por muestra analizadas como si "
                    "fueran independientes (pseudoreplicación). La variación técnica del "
                    "RNA-seq es casi Poisson y pequeña: ese dinero rinde más en réplicas "
                    "biológicas. Si las haces, súmalas (collapseReplicates).",
                    "MAR08 AUE10 DESV"))

    # ------------------------------------------------------ lotes / bloques
    _area("diseño")
    conf = sim.confusion_lote(dis, caso)
    n_lotes = len(sim.tabla_lotes(dis, caso))
    tiene_lote = formula in ("lote", "par_lote", "tiempo_lote")
    if sim.sobrecupo(dis, caso):
        c.append(_c("fatal", f"Algún lote tiene más de {caso['capacidad']} muestras: el "
                    "laboratorio no puede procesarlas el mismo día.", ""))
    if conf == "total":
        c.append(_c("fatal", "Cada lote contiene un solo grupo: el efecto del lote y el de "
                    "la condición son idénticos en los datos. Ningún análisis puede "
                    "separarlos (confusión total). Repártelos: cada lote con muestras de "
                    "todos los grupos.", "LEE10 AUE10"))
    elif conf == "parcial":
        c.append(_c("mayor", "Algunos lotes tienen un solo grupo: el diseño está "
                    "parcialmente confundido. Balancea los lotes.", "LEE10 AUE10"))
    elif conf == "desbalance":
        c.append(_c("menor", "Los lotes tienen todos los grupos pero en proporciones "
                    "distintas; un diseño balanceado estima mejor el efecto.", "AUE10"))
    if n_lotes > 1 and conf in ("ninguna", "desbalance"):
        c.append(_c("bien", "Lotes bloqueados: cada lote lleva muestras de todos los "
                    "grupos.", "AUE10"))
        if not tiene_lote and not (caso.get("pareado") and formula == "par"):
            c.append(_c("mayor", "Hay varios lotes pero la fórmula no los incluye: la "
                        "variación del lote queda como ruido y se pierde potencia. Usa "
                        "~ lote + condición.", "LEE10 DESV"))
    if n_lotes == 1 and tiene_lote:
        c.append(_c("menor", "La fórmula incluye el lote pero todas las muestras están en "
                    "uno solo: el factor tiene un nivel y el programa dará error.",
                    "DESV"))

    # ------------------------------------------------------------ fórmula
    _area("análisis")
    if res["estado"] == "no_estimable":
        c.append(_c("fatal", f"El modelo no se puede ajustar: {res['motivo']}.", "DESV"))
    if caso.get("pareado") and formula not in ("par", "par_lote"):
        c.append(_c("mayor", "Las muestras están pareadas por paciente y la fórmula lo "
                    "ignora: la enorme variación entre personas se queda en el error. "
                    "Usa ~ donante + condición.", "DESV LOV14"))
    if not caso.get("pareado") and formula in ("par", "par_lote"):
        c.append(_c("fatal", "Pusiste «donante» en la fórmula, pero cada muestra viene "
                    "de un individuo distinto: el donante explica todo y no quedan "
                    "grados de libertad.", "DESV"))
    if obj == "interaccion":
        if formula == "aditivo":
            c.append(_c("fatal", "El modelo aditivo supone que el tratamiento hace lo "
                        "mismo en ambos genotipos: es justo lo que se quiere probar. "
                        "Falta el término genotipo:tratamiento.", "DESV"))
        elif formula == "inter":
            c.append(_c("bien", "Término de interacción genotipo:tratamiento: prueba la "
                        "«diferencia de diferencias».", "DESV"))
        elif formula == "cond":
            c.append(_c("bien", "Diseño por grupos con el contraste "
                        "(KO.LPS − KO.veh) − (WT.LPS − WT.veh): equivale a la interacción.",
                        "DESV"))
    ya = " ".join(x["texto"] for x in c)
    if formula not in caso["formulas_ok"] and not any(
            p in ya for p in ("fórmula", "modelo", "donante", "interacción", "lote")):
        c.append(_c("menor", f"La fórmula {datos.FORMULAS[formula]['nombre']} no es la "
                    "que mejor describe este diseño.", "DESV"))
    if obj == "tiempo" and dis["prueba"] != "lrt":
        c.append(_c("mayor", "Con cuatro tiempos, la prueba de Wald solo compara el "
                    "último nivel contra el primero (12 h vs 0 h): se pierden los genes "
                    "tempranos. Usa LRT con un modelo reducido sin el tiempo.",
                    "DESV LOV14"))
    if obj != "tiempo" and dis["prueba"] == "lrt" and len(caso["grupos"]) == 2 \
            and obj != "interaccion":
        c.append(_c("menor", "LRT con dos grupos equivale a una prueba de Wald; no hace "
                    "daño, pero no aporta nada.", "DESV"))

    # ------------------------------------------------------------- pruebas
    _area("análisis")
    if dis["prueba"] == "fc":
        c.append(_c("fatal", "Llamar diferencial a todo lo que cambia más de 2 veces "
                    "ignora la variación entre réplicas: un gen con 3 cuentas cambia 2× "
                    "por puro azar. Hace falta un modelo estadístico.", "CON16"))
    elif dis["prueba"] == "ttest":
        c.append(_c("mayor", "Prueba t por gen sin compartir información: con pocas "
                    "réplicas la varianza de cada gen es muy inestable. DESeq2, edgeR y "
                    "limma «toman prestada» información de todos los genes.",
                    "CON16 LOV14 LAW14"))
    if dis["correccion"] == "nada" and dis["prueba"] != "fc":
        c.append(_c("fatal", "Sin corrección por pruebas múltiples: con miles de genes y "
                    "p < 0.05 esperas cientos de falsos positivos aunque nada cambie. "
                    "Usa Benjamini-Hochberg.", "BH95"))
    elif dis["correccion"] == "bonf":
        c.append(_c("menor", "Bonferroni controla la probabilidad de un solo falso "
                    "positivo: en ómica es demasiado conservador. El estándar es el "
                    "FDR de Benjamini-Hochberg.", "BH95"))
    if dis["entrada"] == "tpm" and dis["prueba"] in ("deseq2", "edger", "lrt"):
        c.append(_c("mayor", "DESeq2 y edgeR modelan CUENTAS: darles TPM/FPKM rompe la "
                    "relación media-varianza. Dales cuentas crudas (o las estimadas por "
                    "Salmon vía tximport).", "DESV SON15"))

    # ----------------------------------------------------------- biblioteca
    _area("laboratorio")
    if caso["bib_ok"]:
        if lib in caso["bib_ok"]:
            c.append(_c("bien", f"{b['nombre']}: adecuada para esta pregunta.", b["fuente"]))
        elif lib in caso["bib_regular"]:
            c.append(_c("menor", f"{b['nombre']} sirve, pero no es la mejor opción para "
                        "esta pregunta.", b["fuente"]))
        elif res["medible"] < 0.8:
            c.append(_c("fatal", f"{b['nombre']} no puede medir lo que se pregunta "
                        f"(solo {res['medible']:.0%} de los rasgos de interés quedaron "
                        "medibles).", b["fuente"]))
        else:
            c.append(_c("fatal", f"{b['nombre']} no es adecuada para estas muestras: "
                        f"{b['malo']}", b["fuente"]))
    rin = caso.get("rin", 9)
    if lib == "polyA" and rin < 7:
        c.append(_c("mayor" if rin < 5 else "menor",
                    f"RIN {rin}: con ARN degradado la captura poli(A) se concentra en el "
                    "extremo 3′ y el sesgo varía entre muestras. Usa ribodepleción.",
                    "SCR06 ZHA14 ILL14"))
    if (b["larga"]) != (dis["lectura"] == "LARGA"):
        c.append(_c("fatal", "Esa combinación de biblioteca y lectura no existe: las "
                    "bibliotecas de lectura larga se leen con PacBio/ONT y las demás con "
                    "lectura corta.", "STA19"))

    # ---------------------------------------------------- lectura / profundidad
    _area("laboratorio")
    if dis["lectura"] in ORDEN_LECTURA:
        if ORDEN_LECTURA.index(dis["lectura"]) < ORDEN_LECTURA.index(caso["lectura_min"]):
            grav = "mayor" if obj in ("splicing", "novo", "antisentido") else "menor"
            c.append(_c(grav, f"Lectura {datos.LECTURAS[dis['lectura']]['nombre']}: para "
                        f"esta pregunta conviene al menos "
                        f"{datos.LECTURAS[caso['lectura_min']]['nombre']}.", "CON16"))
    prof = dis["profundidad"]
    if prof < caso["prof_min"]:
        c.append(_c("mayor" if prof < caso["prof_min"] / 2 else "menor",
                    f"{prof} M lecturas por muestra es poco para esta pregunta "
                    f"(≥ {caso['prof_min']} M).", "CON16 ENC"))
    elif prof > caso["prof_util"]:
        c.append(_c("menor", f"{prof} M lecturas: más allá de ~{caso['prof_util']} M "
                    "la ganancia es mínima. Ese dinero rinde más en réplicas.",
                    "LIU14"))
    if prof >= 50 and reps <= 3 and obj in ("genes", "global", "tiempo", "interaccion"):
        c.append(_c("menor", "Muchas lecturas y pocas réplicas: para expresión "
                    "diferencial de genes, más réplicas a menor profundidad da más "
                    "potencia.", "LIU14 CHI14"))
    if lib in ("sc10x", "snrna"):
        lpc = datos.lecturas_por_celula(prof)
        if lpc < 20000:
            c.append(_c("menor", f"~{lpc:,} lecturas por célula: 10x recomienda ≥ 20 000 "
                        "para expresión génica.", "ZHE17 LUE19"))

    # ------------------------------------------------------------- rutas
    _area("análisis")
    if dis["ruta"] not in caso["rutas_ok"]:
        r = datos.RUTAS[dis["ruta"]]
        if dis["ruta"] == "cr_cel":
            c.append(_c("fatal", "Comparar células individuales como réplicas es "
                        "pseudoreplicación: las células de un donante no son "
                        "independientes y aparecen miles de falsos positivos. Suma por "
                        "donante (pseudobulk) y usa a los donantes como réplicas.",
                        "SQU21 ZIM21 CRO20"))
        elif caso.get("sin_genoma") and dis["ruta"] in ("star", "hisat", "salmon"):
            c.append(_c("fatal", "No hay genoma ni transcriptoma de referencia: alinear a "
                        "una especie lejana pierde la mayoría de las lecturas. Ensambla "
                        "de novo.", "GRA11 CON16"))
        else:
            c.append(_c("mayor", f"{r['nombre']} no es la ruta adecuada para este "
                        "experimento.", r["fuente"]))
    if dis["ruta"] == "trinity" and not caso.get("sin_genoma"):
        c.append(_c("menor", "Ensamblar de novo cuando existe un buen genoma de "
                    "referencia gasta tiempo y genera transcritos fragmentados.", "CON16"))
    sc = lib in ("sc10x", "snrna", "smartseq")
    if sc and dis["ruta"] not in ("cr_pb", "cr_cel"):
        c.append(_c("mayor", "Biblioteca de célula única procesada como bulk: se pierde "
                    "la información de cada célula.", "LUE19"))
    if not sc and dis["ruta"] in ("cr_pb", "cr_cel"):
        c.append(_c("fatal", "Ruta de célula única con una biblioteca de bulk: no hay "
                    "códigos de barras celulares.", "LUE19"))
    if lib == "small" and dis["ruta"] != "mirdeep":
        c.append(_c("mayor", "Las lecturas de small RNA llevan el adaptador 3′ casi "
                    "completo: hay que recortarlo y cuantificar contra miRBase.",
                    "FRI12 MAR11"))

    # -------------------------------------------------------------- extras
    _area("laboratorio")
    for e in caso.get("requiere", ()):
        if e not in dis["extras"]:
            x = datos.EXTRAS[e]
            c.append(_c("fatal" if e in ("hebra", "splicing", "ercc") else "mayor",
                        f"Falta: {x['nombre']}. {x['texto']}", x["fuente"]))
        else:
            c.append(_c("bien", f"{datos.EXTRAS[e]['nombre']}: indispensable aquí.",
                        datos.EXTRAS[e]["fuente"]))
    for e in caso.get("recomienda", ()):
        if e not in dis["extras"]:
            x = datos.EXTRAS[e]
            c.append(_c("menor", f"Convendría: {x['nombre']}. {x['texto']}", x["fuente"]))
    if obj == "global" and dis["entrada"] != "spike":
        c.append(_c("fatal", "Normalizaste con razón de medianas: esa normalización "
                    "supone que la mayoría de los genes no cambia y borra el aumento "
                    "global de ARN. Normaliza con los spike-ins.", "LOV12 RIS14"))
    if dis["entrada"] == "spike" and "ercc" not in dis["extras"]:
        c.append(_c("fatal", "Elegiste normalizar con spike-ins pero no los agregaste.",
                    "JIA11"))
    if "ercc" in dis["extras"] and obj != "global":
        c.append(_c("bien", "Spike-ins ERCC: sirven de control de calidad (linealidad, "
                    "límite de detección).", "JIA11"))
    if "umi" in dis["extras"] and caso.get("poco_material"):
        c.append(_c("bien", "UMIs con poco material: los duplicados de PCR se quitan sin "
                    "perder duplicados biológicos.", "FU18"))
    if "hebra" in dis["extras"] and "hebra" not in caso.get("requiere", ()):
        c.append(_c("bien", "Biblioteca con hebra: casi gratis y evita ambigüedades.",
                    "LEV10"))
    if "splicing" in dis["extras"] and obj != "splicing" and lib in ("tag3", "small"):
        c.append(_c("menor", "Análisis de splicing con una biblioteca que no cubre los "
                    "exones internos: no habrá eventos que medir.", "SHE14"))
    if "shrink" in dis["extras"]:
        c.append(_c("bien", "log2FC encogidos con apeglm para ordenar y graficar.",
                    "ZHU19"))

    # ---------------------------------------------------------- resultados
    _area("resultados")
    if res["estado"] == "ok" and not libre:
        if res["fdr"] > 0.2 and res["sig"] >= 10:
            c.append(_c("mayor", f"De {res['sig']} genes que llamaste significativos, "
                        f"{res['fp']} son falsos ({res['fdr']:.0%}). El diseño o el "
                        "análisis está inflando los falsos positivos.", "BH95 LEE10"))
    return sorted(c, key=lambda x: ORDEN_GRAV[x["grav"]])


def revisar_lab(exp, caso, res):
    """Lo que el Revisor 2 lee en el cuaderno de laboratorio."""
    import expediente as X
    import lab_datos as L
    c = []
    info = X.info(caso)
    dis = exp["dis"]
    # hipótesis
    _area("diseño")
    if exp.get("harking"):
        if exp.get("exploratorio"):
            c.append(_c("menor", "Cambiaste la hipótesis después de ver los datos y lo "
                        "declaraste como análisis exploratorio: correcto, pero la nueva "
                        "hipótesis necesita un experimento confirmatorio independiente.",
                        "NOS18"))
        else:
            c.append(_c("fatal", "HARKing: la hipótesis del manuscrito no es la que "
                        "registraste antes del experimento; la escribiste después de ver "
                        "los resultados y la presentas como si fuera la original. Con los "
                        "mismos datos que la generaron no se puede ponerla a prueba.",
                        "KER98"))
    elif exp.get("hipotesis") not in (None, 0) and not caso.get("libre"):
        h = info["hipotesis"][exp["hipotesis"]]
        # la última opción de cada caso es una afirmación que el RNA-seq no mide
        if exp["hipotesis"] == len(info["hipotesis"]) - 1:
            c.append(_c("mayor", f"La hipótesis «{h}» no es algo que un RNA-seq pueda poner a "
                        "prueba: no predice qué genes cambian. Sin una hipótesis medible el "
                        "experimento no responde nada.", ""))
        else:
            # mayor y no menor: con una hipótesis vaga cualquier resultado la «confirma»
            c.append(_c("mayor", f"La hipótesis «{h}» es vaga o no se puede refutar. Una "
                        "buena hipótesis dice qué genes o vías esperas que cambien y en qué "
                        "dirección.", ""))
    # unidad experimental
    _area("diseño")
    if exp.get("unidad") not in (None, info["unidad"]):
        u = L.UNIDADES[info["lugar"]][exp["unidad"]]
        c.append(_c("fatal", f"Unidad experimental: «{u}». Esas réplicas no son "
                    "independientes (pseudoreplicación): comparten casi toda su variación "
                    "y los valores p salen artificialmente pequeños.", "AUE10 CON16"))
    # registros
    _area("diseño")
    n_lotes = len(sim.tabla_lotes(dis, caso))
    if n_lotes > 1 and "lote" not in exp.get("registros", []):
        c.append(_c("mayor", "Procesaste en varios lotes pero no anotaste qué muestra fue "
                    "en cuál: no puedes incluir el lote en el modelo ni revisarlo en la "
                    "PCA.", "LEE10"))
    # asignación
    _area("diseño")
    if info["aleatorizable"]:
        if exp.get("asignacion") == "azar":
            c.append(_c("bien", "Asignaste los tratamientos al azar.", "AUE10"))
        elif exp.get("asignacion") == "orden":
            c.append(_c("mayor", "Asignaste los tratamientos por orden (de llegada, de "
                        "jaula, de banca): cualquier cosa que varíe con ese orden se "
                        "confunde con el tratamiento. Hay que aleatorizar.", "AUE10"))
        elif exp.get("asignacion") == "ojo":
            c.append(_c("fatal", "Elegiste a ojo qué unidades recibían el tratamiento: "
                        "sesgo de selección. Las diferencias que causó tu elección se "
                        "confunden con el efecto del tratamiento.", "AUE10"))
    # extracción
    _area("laboratorio")
    met = exp.get("extraccion")
    if met and met not in info["extraccion"]:
        e = L.EXTRACCIONES[met]
        grav = "mayor"
        if L.EXTRACCIONES[met]["celulas"] != (dis["biblioteca"] in ("sc10x", "snrna", "smartseq")):
            grav = "fatal"
        c.append(_c(grav, f"Extracción con {e['nombre']}: no es la adecuada para estas "
                    "muestras o esta pregunta.", e["fuente"]))
    if met and dis["biblioteca"] == "small" and not L.EXTRACCIONES[met]["guarda_pequenos"]:
        c.append(_c("fatal", "La extracción que usaste pierde los ARN < 200 nt: los miRNA "
                    "se fueron por la columna.", "CON16"))
    p = exp.get("pasos", {})
    if p.get("calor"):
        c.append(_c("mayor", "Disociaste a 37 °C durante una hora: la disociación induce "
                    "genes de estrés (FOS, JUN, HSP) en todas las células y contamina los "
                    "perfiles. Disociación en frío y corta, o núcleos.", "LUE19"))
    h = p.get("homogenizacion")
    if h is not None and not 0.4 <= h <= 0.7:
        c.append(_c("menor", "Homogenización corta: la lisis quedó incompleta y bajó el "
                    "rendimiento." if h < 0.4 else "Homogenización de más: el tejido se "
                    "calentó y el ARN empezó a degradarse.", ""))
    if met and not L.EXTRACCIONES[met]["celulas"]:
        if not p.get("dnasa") and dis["biblioteca"] in ("ribo", "tag3", "polyA"):
            c.append(_c("menor", "Sin DNasa: el ADN genómico contamina la biblioteca "
                        "(sobre todo de ARN total).", "CON16"))
    # QC
    malas = [k for k, q in exp.get("qc", {}).items()
             if q["estado"] == "aprobada" and X.problemas(q, caso)]
    if malas:
        nombres = ", ".join(_nombre(k, caso) for k in malas[:6])
        c.append(_c("mayor",
                    f"Aprobaste en el QC muestras con problemas ({nombres}). El RNA-seq "
                    "necesita ARN íntegro, puro y sin ADN: hay que re-extraerlas o "
                    "excluirlas.", ""))
    excl = [k for k, q in exp.get("qc", {}).items() if q["estado"] == "excluida"]
    if excl:
        # si dejó un grupo con menos de 3 réplicas ya lo descuenta la regla de réplicas
        c.append(_c("bien", tr(f"Excluiste {len(excl)} muestra(s) por mala calidad y lo reportas.")
                    + ("" if sim.replicas_efectivas(dis, caso) >= 3 else
                       tr(" Re-extraer habría salvado la réplica, o diseñar con margen "
                          "(una o dos réplicas de más).")),
                    "CON16"))
    # biblioteca
    _area("laboratorio")
    if exp.get("pcr", 12) >= 16 and "umi" not in dis["extras"]:
        c.append(_c("menor", f"{exp['pcr']} ciclos de PCR: más duplicados y sesgo de "
                    "amplificación. Usa los mínimos que dé el rendimiento.", "CON16"))
    if not exp.get("limpieza", True):
        c.append(_c("menor", "Sin limpieza con perlas: los dímeros de adaptador se "
                    "secuenciaron y se perdió una parte de las lecturas.", "CON16"))
    # secuenciación
    _area("laboratorio")
    if exp.get("carriles") == "grupo":
        c.append(_c("mayor", "Cada grupo en su propio carril: el carril queda confundido "
                    "con la condición. Todas las muestras en todos los carriles.",
                    "AUE10 CON16"))
    # minijuegos
    mjs = exp.get("minijuegos", {})
    _area("laboratorio")
    if mjs.get("placa", 0) > 0.5:
        c.append(_c("mayor", f"En la placa, un grupo quedó mucho más en los pozos del borde que "
                    f"el otro (diferencia {mjs['placa']:.0%}). El efecto de borde (evaporación) "
                    "se confunde con el tratamiento: alterna o aleatoriza la posición.", "LUN03"))
    elif mjs.get("placa", 0) > 0.25:
        c.append(_c("menor", "La placa quedó algo desbalanceada entre borde y centro.", "LUN03"))
    clo = exp.get("pasos", {}).get("cloroformo")
    if clo is not None and not 0.17 <= clo <= 0.23:
        c.append(_c("menor", f"Usaste {clo:.2f} mL de cloroformo por mL de TRIzol (lo indicado "
                    "es 0.2): peor separación de fases o menos rendimiento.", "CHO93"))
    if mjs.get("nanodrop", 0) >= 2:
        c.append(_c("mayor" if mjs["nanodrop"] >= 4 else "menor",
                    "El procedimiento del NanoDrop tuvo varios errores (blanco, gota, "
                    "limpieza): las lecturas de pureza pierden confianza.", ""))
    if mjs.get("gel", 0) >= 2:
        c.append(_c("menor", "Varios carriles del gel se cargaron fuera del pozo: la "
                    "integridad de esas muestras no se puede juzgar bien.", ""))
    if mjs.get("biblioteca", 0) >= 2:
        c.append(_c("mayor" if mjs["biblioteca"] >= 4 else "menor",
                    f"Te equivocaste {mjs['biblioteca']} veces en el orden de los pasos de la "
                    "biblioteca: un paso fuera de orden arruina la biblioteca entera.",
                    "CON16"))
    if "perlas" in mjs and not 0.75 <= mjs["perlas"] <= 0.95:
        c.append(_c("menor", f"Limpieza con {mjs['perlas']:.2f}× perlas: fuera del rango que "
                    "quita dímeros sin perder biblioteca (~0.8-0.9×).", "DEA95"))
    if "carga" in mjs and not 85 <= mjs["carga"] <= 115:
        c.append(_c("menor" if 70 <= mjs["carga"] <= 130 else "mayor",
                    f"La celda se cargó al {mjs['carga']} % de lo recomendado: "
                    "perdiste lecturas.", "ILLDD"))
    # muchos descuidos juntos: el revisor ya no confía en el laboratorio
    descuidos = [x for x in c if x["area"] == "laboratorio" and x["grav"] == "menor"]
    if len(descuidos) >= 3:
        c.append(_c("mayor", f"{len(descuidos)} descuidos en la mesa (ver arriba). Cada uno "
                    "por separado es menor, pero juntos hacen dudar de todos los datos: "
                    "repite lo necesario con más cuidado.", ""))
    _area("análisis")
    s = mjs.get("hebra_s")
    if s is not None:
        correcto = 2 if "hebra" in exp["dis"]["extras"] else 0
        if s != correcto:
            c.append(_c("mayor" if exp["dis"].get("factor_hebra", 1) < 0.6 else "menor",
                        tr(f"Contaste con featureCounts -s {s}, pero tu biblioteca es ")
                        + tr("con hebra reversa (dUTP): era -s 2." if correcto == 2 else
                             "sin hebra: era -s 0.")
                        + tr(" Revisa siempre infer_experiment.py antes de contar."),
                        "WAN12 LIA14"))
    if mjs.get("formula_orden"):
        c.append(_c("menor", "En la fórmula la condición no quedó al final: DESeq2 prueba "
                    "por defecto el último término.", "DESV"))
    # análisis repetido hasta que salga
    _area("análisis")
    cambios = exp.get("cambios", [])
    if any(x in cambios for x in ("correccion", "prueba", "formula", "entrada")) and \
            exp.get("corridas", 0) >= 3:
        c.append(_c("menor", f"Corriste {exp['corridas']} análisis distintos después de "
                    f"ver resultados (cambiaste: {', '.join(sorted(set(cambios)))}). "
                    "Reporta todos y justifica el elegido, o es p-hacking.", "SIM11"))
    return c


def _nombre(k, caso):
    g, r = k.split("-")
    return f"{caso['abrev'][int(g)]}{int(r) + 1}"


def dictamen(comentarios):
    gravs = [x["grav"] for x in comentarios]
    if "fatal" in gravs:
        return "RECHAZADO", "mal"
    if "mayor" in gravs:
        return "REVISIÓN MAYOR", "mal"
    if "menor" in gravs:
        return "ACEPTADO CON CAMBIOS MENORES", "titulo"
    return "ACEPTADO", "bien"


def calificar(dis, caso, res, comentarios, dif):
    """dict(aprobado, estrellas, dictamen, color)."""
    texto, color = dictamen(comentarios)
    gravs = [x["grav"] for x in comentarios]
    m = meta(caso, dif)
    alcanza = res["estado"] == "ok" and res["sens"] >= m and res["fdr"] <= 0.15
    aprobado = texto.startswith("ACEPTADO") and alcanza
    estrellas = 0
    if aprobado:
        estrellas = 1
        if gravs.count("menor") <= 1:
            estrellas += 1
        if res["sens"] >= m + 0.15 or datos.costo_total(dis, caso) <= 0.7 * presupuesto(caso, dif):
            estrellas += 1
    return dict(aprobado=aprobado, estrellas=estrellas, dictamen=texto, color=color,
                sens=round(res["sens"], 3), fdr=round(res["fdr"], 3), alcanza=alcanza)


def pistas(caso):
    """Lo que exige el caso (modo Fácil)."""
    p = []
    nom = lambda d, ks: ", ".join(d[k]["nombre"] for k in ks)
    p.append(f"Biblioteca: {nom(datos.BIBLIOTECAS, sorted(caso['bib_ok']))}")
    p.append(f"Lectura mínima: {datos.LECTURAS[caso['lectura_min']]['nombre']} · "
             f"profundidad {caso['prof_min']}-{caso['prof_util']} M")
    p.append(f"Ruta: {nom(datos.RUTAS, sorted(caso['rutas_ok']))}")
    p.append(f"Fórmula: {nom(datos.FORMULAS, sorted(caso['formulas_ok']))}")
    p.append(f"Prueba: {nom(datos.PRUEBAS, sorted(caso['pruebas_ok']))}")
    if caso.get("requiere"):
        p.append(f"Indispensable: {nom(datos.EXTRAS, sorted(caso['requiere']))}")
    if caso.get("capacidad"):
        p.append(f"Máximo {caso['capacidad']} muestras por lote: abre [L] y balancea.")
    return p
