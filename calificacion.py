"""Calificación del manuscrito (0-100) y retroalimentación: qué se puede
mejorar aunque el experimento haya salido bien, comparando con el diseño que
haría la Dra. Lazo.

La calificación parte de 100 y descuenta:
  · cada comentario del Revisor 2 (fatal 25, mayor 10, menor 4), por área;
  · resultados: sensibilidad por debajo de la meta y FDR alto;
  · eficiencia: fondos extra pedidos, regresos a etapas anteriores y gasto
    muy por encima del diseño ideal.
Un caso queda resuelto con 60 o más y sin dictamen de RECHAZO.
"""

from idioma import tr
import datos
import lab_datos as L

DESCUENTO = {"fatal": 25, "mayor": 10, "menor": 4, "bien": 0}
AREAS = [("diseño", "Diseño"), ("laboratorio", "Laboratorio"), ("análisis", "Análisis"),
         ("resultados", "Resultados"), ("eficiencia", "Eficiencia")]
TOPE_AREA = {"diseño": 25, "laboratorio": 25, "análisis": 20, "resultados": 20,
             "eficiencia": 10}

# El diseño de la Dra. Lazo para cada caso: lo mínimo suficiente y bien hecho.
IDEALES = {
    "metformina": dict(biblioteca="polyA", lectura="SE75", profundidad=15, replicas=6,
                       formula="cond", prueba="deseq2", ruta="salmon", extraccion="trizol",
                       extras={"filtro", "shrink"}, plataforma="nextseq",
                       porque="Línea celular: poca variación, así que 6 cultivos "
                              "independientes a 15 M dan casi toda la potencia por menos de la "
                              "mitad del presupuesto."),
    "dieta": dict(biblioteca="polyA", lectura="SE75", profundidad=15, replicas=6,
                  formula="lote", prueba="deseq2", ruta="salmon", extraccion="trizol",
                  extras={"filtro", "shrink"}, plataforma="nextseq",
                  porque="6 ratones por grupo en 2 días balanceados (3+3 cada día), asignados "
                         "al azar, y el día en la fórmula."),
    "sequia": dict(biblioteca="polyA", lectura="SE75", profundidad=10, replicas=12,
                   formula="lote", prueba="deseq2", ruta="salmon", extraccion="ctab",
                   extras={"filtro", "gsea"}, plataforma="nextseq",
                   porque="Las 4 bancas llenas (24 plantas), cada banca con 3 de riego y 3 de "
                          "sequía al azar, banca en la fórmula, extracción con CTAB."),
    "pareado": dict(biblioteca="ribo", lectura="PE100", profundidad=25, replicas=10,
                    formula="par", prueba="deseq2", ruta="salmon", extraccion="trizol",
                    extras={"filtro", "shrink", "gsea"}, plataforma="nextseq",
                    porque="10 pacientes pareados, paciente en la fórmula y GSEA para "
                           "responder la pregunta de vías."),
    "ffpe": dict(biblioteca="ribo", lectura="PE100", profundidad=30, replicas=10,
                 formula="cond", prueba="deseq2", ruta="star", extraccion="ffpe",
                 extras={"filtro", "umi", "hebra"}, plataforma="nextseq",
                 porque="Kit FFPE, DV200 como control, ribodepleción con UMIs y 10 pacientes "
                        "por grupo: la variación entre personas es grande."),
    "antisentido": dict(biblioteca="ribo", lectura="PE100", profundidad=50, replicas=5,
                        formula="cond", prueba="deseq2", ruta="star", extraccion="trizol",
                        extras={"filtro", "hebra"}, plataforma="novaseq",
                        porque="ARN total ribodepletado con hebra, pareado y profundo, "
                               "alineado al genoma para ver transcritos no anotados."),
    "splicing": dict(biblioteca="polyA", lectura="PE150", profundidad=60, replicas=4,
                     formula="cond", prueba="deseq2", ruta="star", extraccion="trizol",
                     extras={"splicing", "hebra"}, plataforma="novaseq",
                     porque="PE 2×150 a 60 M con hebra, STAR y rMATS: los eventos necesitan "
                            "lecturas que crucen uniones."),
    "mirna": dict(biblioteca="small", lectura="SE50", profundidad=8, replicas=12,
                  formula="cond", prueba="deseq2", ruta="mirdeep", extraccion="mirna",
                  extras={"filtro", "umi"}, plataforma="nextseq",
                  porque="Kit para biofluidos, small RNA con UMIs a 8 M y el dinero "
                         "ahorrado en más pacientes."),
    "celula": dict(biblioteca="sc10x", lectura="PE100", profundidad=100, replicas=4,
                   formula="cond", prueba="deseq2", ruta="cr_pb", extraccion="disociacion",
                   extras={"umi"}, plataforma="novaseq",
                   porque="Disociación en frío, 4 donantes por grupo y pseudobulk por donante."),
    "tiempo": dict(biblioteca="polyA", lectura="SE75", profundidad=15, replicas=4,
                   formula="tiempo_lote", prueba="lrt", ruta="salmon", extraccion="trizol",
                   extras={"filtro"}, plataforma="nextseq",
                   porque="Cada tanda con todos los tiempos, tiempo como factor más la tanda "
                          "y LRT."),
    "novo": dict(biblioteca="polyA", lectura="PE150", profundidad=30, replicas=6,
                 formula="cond", prueba="deseq2", ruta="trinity", extraccion="trizol",
                 extras={"filtro", "hebra", "gsea"}, plataforma="novaseq",
                 porque="Trinity con PE 2×150 con hebra de todas las muestras, BUSCO y "
                        "anotación por homología."),
    "myc": dict(biblioteca="polyA", lectura="SE75", profundidad=15, replicas=4,
                formula="cond", prueba="deseq2", ruta="salmon", extraccion="trizol",
                extras={"filtro", "ercc"}, plataforma="nextseq", entrada="spike",
                porque="ERCC agregados por número de células y normalización con los "
                       "spike-ins."),
    "cribado": dict(biblioteca="tag3", lectura="SE75", profundidad=5, replicas=3,
                    formula="cond", prueba="deseq2", ruta="salmon", extraccion="columna",
                    extras={"filtro"}, plataforma="nextseq",
                    porque="3′ tag-seq multiplexado: 27 muestras por una fracción del costo."),
    "interaccion": dict(biblioteca="polyA", lectura="SE75", profundidad=15, replicas=5,
                        formula="inter", prueba="deseq2", ruta="salmon", extraccion="trizol",
                        extras={"filtro", "shrink"}, plataforma="nextseq",
                        porque="Factorial 2×2 con 5 réplicas y el término genotipo:tratamiento."),
}

NOMBRES_CAMPO = {
    "biblioteca": ("Biblioteca", datos.BIBLIOTECAS),
    "lectura": ("Lectura", datos.LECTURAS),
    "ruta": ("Cuantificación", datos.RUTAS),
    "formula": ("Fórmula", datos.FORMULAS),
    "prueba": ("Prueba", datos.PRUEBAS),
    "entrada": ("Entrada al modelo", datos.ENTRADAS),
    "extraccion": ("Extracción", L.EXTRACCIONES),
    "plataforma": ("Plataforma", L.PLATAFORMAS),
}


def costo_ideal(caso):
    ideal = IDEALES.get(caso["id"])
    if not ideal:
        return None
    dis = dict(biblioteca=ideal["biblioteca"], lectura=ideal["lectura"],
               profundidad=ideal["profundidad"], replicas=ideal["replicas"], tecnicas=1,
               extras=list(ideal["extras"]), plataforma=ideal["plataforma"])
    return datos.costo_total(dis, caso)


def comparar(exp, caso):
    """Diferencias entre tu diseño y el ideal: [(campo, tuyo, ideal)]."""
    ideal = IDEALES.get(caso["id"])
    if not ideal:
        return []
    dis = exp["dis"]
    dif = []
    for campo, (nombre, tabla) in NOMBRES_CAMPO.items():
        tuyo = exp.get(campo) if campo in ("extraccion", "plataforma") else dis.get(campo)
        quiero = ideal.get(campo, "crudas" if campo == "entrada" else None)
        if quiero is None:
            continue
        if tuyo != quiero and not (campo == "formula" and caso["objetivo"] == "tiempo"
                                         and tuyo == "lote"):
            dif.append((nombre, tabla.get(tuyo, {}).get("nombre", "—") if tuyo else "—",
                        tabla[quiero]["nombre"]))
    reps = dis["replicas"]
    if reps < ideal["replicas"] or reps > ideal["replicas"] * 2:
        dif.append(("Réplicas por grupo", str(reps), str(ideal["replicas"])))
    prof = dis["profundidad"]
    if prof < ideal["profundidad"] * 0.6 or prof > ideal["profundidad"] * 2:
        dif.append(("Lecturas por muestra", f"{prof} M", f"{ideal['profundidad']} M"))
    faltan = ideal["extras"] - set(dis["extras"])
    sobran = {"hebra", "umi", "ercc", "splicing", "decon"} & set(dis["extras"]) - ideal["extras"]
    if faltan:
        dif.append(("Extras que faltaron", "", ", ".join(datos.EXTRAS[e]["nombre"] for e in sorted(faltan))))
    if sobran:
        dif.append(("Extras que no hacían falta", ", ".join(datos.EXTRAS[e]["nombre"]
                                                             for e in sorted(sobran)), ""))
    return dif


def calificar(exp, caso, res, comentarios, meta):
    """dict(total, letra, por_area, descuentos, resuelto, estrellas)."""
    por_area = {a: TOPE_AREA[a] for a, _ in AREAS}
    descuentos = []
    for c in comentarios:
        d = DESCUENTO[c["grav"]]
        if d:
            area = c.get("area", "diseño")
            por_area[area] -= d
            descuentos.append((area, -d, c["texto"]))
    # resultados
    if res["estado"] != "ok":
        por_area["resultados"] = 0
        descuentos.append(("resultados", -TOPE_AREA["resultados"],
                           "El análisis no produjo resultados válidos."))
    else:
        if res["sens"] < meta:
            d = round(min(20, (meta - res["sens"]) * 60))
            por_area["resultados"] -= d
            descuentos.append(("resultados", -d, f"Sensibilidad {res['sens']:.0%}: la meta del "
                               f"caso era {meta:.0%}. Te faltó potencia (réplicas, "
                               "profundidad o un diseño que quite ruido)."))
        if res["fdr"] > 0.1:
            d = round(min(15, (res["fdr"] - 0.1) * 60))
            por_area["resultados"] -= d
            descuentos.append(("resultados", -d, f"FDR observado {res['fdr']:.0%}: más falsos "
                               "positivos de los que prometía la corrección."))
    # eficiencia
    amp = sum(exp.get("ampliaciones", []))
    if amp:
        d = min(6, 2 + len(exp["ampliaciones"]) * 2)
        por_area["eficiencia"] -= d
        descuentos.append(("eficiencia", -d, f"Pediste ${amp:,} de fondos extra."))
    if exp.get("regresos"):
        d = min(4, exp["regresos"] * 2)
        por_area["eficiencia"] -= d
        descuentos.append(("eficiencia", -d, f"Regresaste {exp['regresos']} vez(veces) a una "
                           "etapa anterior: cuesta días y dinero."))
    ideal = costo_ideal(caso)
    if ideal and exp["gastado"] > ideal * 1.6:
        d = 3
        por_area["eficiencia"] -= d
        descuentos.append(("eficiencia", -d, f"Gastaste ${exp['gastado']:,}; el diseño ideal "
                           f"costaba ~${ideal:,}. El resto pudo ir a más réplicas o a otro "
                           "experimento."))
    for a in por_area:
        por_area[a] = max(0, por_area[a])
    total = sum(por_area.values())
    letra = ("A" if total >= 90 else "B" if total >= 80 else "C" if total >= 70 else
             "D" if total >= 60 else "F")
    rechazado = any(c["grav"] == "fatal" for c in comentarios)
    resuelto = total >= 60 and not rechazado
    estrellas = 0 if not resuelto else (3 if total >= 90 else 2 if total >= 75 else 1)
    return dict(total=total, letra=letra, por_area=por_area, descuentos=descuentos,
                resuelto=resuelto, estrellas=estrellas, rechazado=rechazado)


def pantalla(win, exp, caso, res, comentarios, nota, nombre):
    """Boleta con la calificación, el desglose y la retroalimentación."""
    import dibujo as d
    colores = {"A": "bien", "B": "bien", "C": "titulo", "D": "titulo", "F": "mal"}
    l = [f"<{colores[nota['letra']]}!>{nota['total']}/100 · {nota['letra']}</>   "
         + d.estrellas(nota["estrellas"]), ""]
    if nota["resuelto"]:
        l.append(f"<bien!>Caso resuelto.</> Buen trabajo, {nombre}.")
    elif nota["rechazado"]:
        l.append("<mal!>Caso no resuelto:</> el Revisor 2 rechazó el manuscrito (hay un error "
                 "FATAL). Corrígelo y reenvía.")
    else:
        l.append("<mal!>Caso no resuelto:</> hace falta 60/100. Revisa abajo dónde perdiste "
                 "puntos y reenvía.")
    l += ["", "<titulo!>Desglose</>"]
    for a, nombre_a in AREAS:
        v, tope = nota["por_area"][a], TOPE_AREA[a]
        barra = "█" * round(20 * v / tope) + "░" * (20 - round(20 * v / tope))
        color = "bien" if v >= tope * 0.85 else "titulo" if v >= tope * 0.5 else "mal"
        l.append(f"  {tr(nombre_a):<12} <{color}>{barra}</> {v}/{tope}")
    if nota["descuentos"]:
        l += ["", "<titulo!>Dónde perdiste puntos</>"]
        for area, pts, texto in sorted(nota["descuentos"], key=lambda x: x[1]):
            l.append(f"  <mal>{pts:>3}</> <tenue>[{tr(area)}]</> {tr(texto)}")
    dif = comparar(exp, caso)
    ideal = IDEALES.get(caso["id"])
    if ideal:
        l += ["", "<titulo!>Cómo lo habría hecho la Dra. Lazo</>", ideal["porque"]]
        if dif:
            l.append("")
            for campo, tuyo, mejor in dif:
                if tuyo and mejor:
                    l.append(f"  · {campo}: tú <tenue>{tuyo}</> → ideal <bien>{mejor}</>")
                elif mejor:
                    l.append(f"  · {campo}: <bien>{mejor}</>")
                else:
                    l.append(f"  · {campo}: <tenue>{tuyo}</>")
        else:
            l.append("  Tu diseño coincide con el ideal en lo esencial.")
        ci = costo_ideal(caso)
        if ci:
            l.append(tr(f"  Costo del ideal: ~${ci:,} · tú gastaste ${exp['gastado']:,}")
                     + (tr(f" (+${sum(exp['ampliaciones']):,} de ampliación)")
                        if exp.get("ampliaciones") else ""))
    menores = [c for c in comentarios if c["grav"] == "menor"]
    if menores and nota["resuelto"]:
        l += ["", "<titulo!>Para la próxima (aunque salió bien)</>"]
        for c in menores:
            l.append(f"  · {tr(c['texto'])}")
    l += ["", f"<tenue>Días de experimento: {exp['dia']} · gastado ${exp['gastado']:,}</>"]
    d.visor(win, f"Calificación · {caso['titulo']}", l, ayuda="Enter continuar")
