"""El expediente de un experimento en el laboratorio: en qué etapa vas, días,
dinero gastado, lo que decidiste en cada estación y la calidad de cada
muestra. Se guarda en la partida para poder salir y volver.

El diseño que lee la simulación (dis) se va llenando etapa por etapa.
"""

import random

import datos
import lab_datos as L
import simulacion as sim

# días que toma cada etapa
DIAS = {0: 1, 1: 2, 2: 1, 3: 1, 4: 2, 5: 0, 6: 1, 7: 0}


def nuevo(caso):
    dis = dict(biblioteca="polyA", lectura="PE100", profundidad=30, replicas=3, tecnicas=1,
               extras=[], ruta="star", entrada="crudas", prueba="deseq2", correccion="bh",
               formula="cond", lotes={}, excluidas=[], calidad={})
    dis["lotes"] = sim.lotes_por_orden(dis, caso)
    return dict(
        caso=caso["id"], etapa=0, dia=1, gastado=0, dis=dis,
        pos=list(L.INICIO),
        # papel de diseño
        pregunta=None, hipotesis=None, hipotesis_orden=None, unidad=None, objetivo=None,
        registros=["lote"] if caso.get("capacidad") else [],
        # unidades
        asignacion=None,
        # extracción
        extraccion=None, pasos={},
        # QC
        qc={},                       # "g-r" -> dict(rin, r280, r230, gdna, ng, estado)
        reextracciones=0,
        # biblioteca
        pcr=12, limpieza=True,
        # secuenciación
        plataforma=None, carriles="todos",
        # análisis
        corridas=0, cambios=[], ultimo_analisis=None, resultado=None,
        apoyo=None, harking=False, exploratorio=False, hipotesis_original=None,
        hallazgos=[], regresos=0, enviado=False, resultado_visto=False,
        semilla=1, semilla_sec=0, ampliaciones=[], minijuegos={},
    )


def info(caso):
    return L.INFO.get(caso["id"], dict(lugar="cultivo", aleatorizable=True, unidad=0,
                                       extraccion={"trizol", "columna"},
                                       hipotesis=["(hipótesis propia)"], congelador="",
                                       calendario="", tecnico="", preguntas={}))


def lugar(caso):
    return L.LUGARES[info(caso)["lugar"]]


def claves_bio(exp, caso):
    return [f"{g}-{r}" for g in range(len(caso["grupos"]))
            for r in range(exp["dis"]["replicas"])]


def gastar(exp, monto, caso, tope):
    """Cobra si alcanza el presupuesto. Devuelve True si se pudo."""
    if exp["gastado"] + monto > tope:
        return False
    exp["gastado"] += round(monto)
    return True


def avanzar(exp, etapa):
    """Marca la etapa como hecha (si era la siguiente) y suma sus días."""
    if exp["etapa"] == etapa:
        exp["etapa"] = etapa + 1
    exp["dia"] += DIAS.get(etapa, 1)


def regresar(exp, etapa):
    """Vuelve a una etapa: todo lo posterior se tiene que rehacer."""
    exp["etapa"] = min(exp["etapa"], etapa)
    exp["regresos"] += 1
    exp["resultado"] = None
    exp["resultado_visto"] = False
    exp["ultimo_analisis"] = None
    mjs = exp.setdefault("minijuegos", {})
    dis = exp["dis"]
    if etapa <= 5:
        mjs.pop("carga", None)
        dis.pop("factor_lecturas", None)
    if etapa <= 4:
        for k in ("biblioteca", "perlas"):
            mjs.pop(k, None)
        dis.pop("dimeros", None)
    if etapa <= 3:
        mjs.pop("nanodrop", None)
        mjs.pop("gel", None)
    if etapa <= 1:
        mjs.pop("placa", None)
    if etapa <= 2:
        exp["qc"] = {}
        exp["dis"]["excluidas"] = []
        exp["dis"]["calidad"] = {}


# ------------------------------------------------------------- extracción
def calidad_muestras(exp, caso, rng=None):
    """Genera RIN, pureza y rendimiento de cada muestra según el caso y lo que
    se hizo en la campana."""
    rng = rng or random.Random()
    p = exp["pasos"]
    met = exp["extraccion"]
    base = caso.get("rin", 9.0)
    ffpe = base < 4
    planta = info(caso)["lugar"] == "invernadero"
    celulas = L.EXTRACCIONES[met]["celulas"]
    salida = {}
    claves = claves_bio(exp, caso)
    mala_suerte = rng.choice(claves) if len(claves) > 4 else None
    for k in claves:
        rin = base + rng.gauss(0, 0.35)
        r280 = 2.02 + rng.gauss(0, 0.04)
        r230 = 2.05 + rng.gauss(0, 0.08)
        ng = rng.uniform(120, 400) if not caso.get("poco_material") else rng.uniform(3, 12)
        gdna = False
        if not p.get("limpieza"):
            rin -= rng.uniform(0.5, 2.5)
        h = p.get("homogenizacion", 0.5)
        if h > 0.85:
            rin -= rng.uniform(1.0, 2.5)      # se calentó de más
        elif h < 0.3:
            ng *= 0.4                        # lisis incompleta
        fase = p.get("fase", "acuosa")
        if fase == "interfase":
            gdna = True
            r280 -= rng.uniform(0.15, 0.3)
        elif fase == "organica":
            r230 -= rng.uniform(0.6, 1.0)
            r280 -= rng.uniform(0.1, 0.3)
        clo = p.get("cloroformo")
        if clo is not None and clo < 0.17:
            r230 -= rng.uniform(0.3, 0.6)
            gdna = gdna or rng.random() < 0.5
        elif clo is not None and clo > 0.23:
            ng *= 0.7
        if p.get("alcohol") == "etanol100":
            ng *= 0.7
        elif p.get("alcohol") == "ninguno":
            ng *= 0.05
        if caso.get("poco_material") and not p.get("glucogeno") and met not in ("mirna", "ffpe"):
            ng *= 0.4
        if p.get("secado") == "seco":
            ng *= 0.6
            r230 -= 0.2
        if not p.get("dnasa"):
            gdna = gdna or rng.random() < 0.6
        if planta and met != "ctab":
            r230 -= rng.uniform(0.5, 0.9)    # polisacáridos y polifenoles
        if ffpe and met != "ffpe":
            ng *= 0.15
            rin = min(rin, 1.8)
        if celulas:
            # viabilidad en vez de RIN
            via = 92 - (25 if p.get("calor") else 0) + rng.gauss(0, 3)
            salida[k] = dict(viabilidad=round(max(30, min(99, via))), rin=8.5 if via > 80 else 6,
                             r280=2.0, r230=2.0, gdna=False, ng=0, estado="pendiente")
            continue
        if k == mala_suerte:
            rin -= rng.uniform(2.5, 4.0)     # un tubo que se descongeló: pasa en la vida real
        rin = round(max(1.0, min(10.0, rin)), 1)
        dv200 = round(max(10, min(95, 20 + rin * 9 + rng.gauss(0, 4))))
        salida[k] = dict(rin=rin, r280=round(r280, 2), r230=round(max(0.3, r230), 2),
                         gdna=gdna, ng=round(ng, 1), dv200=dv200, estado="pendiente")
    return salida


def problemas(q, caso):
    """Lista de problemas de una muestra (para el QC y el Revisor 2)."""
    out = []
    if "viabilidad" in q:
        if q["viabilidad"] < 80:
            out.append("viabilidad < 80 %")
        return out
    if info(caso).get("biofluido"):
        # ARN circulante: fragmentado por naturaleza y por debajo del límite del
        # NanoDrop; el control es el spike-in de extracción y el perfil de ARN pequeño
        return ["ADN genómico"] if q["gdna"] else []
    ffpe = caso.get("rin", 9) < 4
    if ffpe:
        if q["dv200"] < 30:
            out.append("DV200 < 30 %")
    elif q["rin"] < 7:
        out.append(f"RIN {q['rin']} (< 7)")
    if q["r280"] < 1.8:
        out.append("A260/280 bajo (proteína/fenol)")
    if q["r230"] < 1.7:
        out.append("A260/230 bajo (sales, fenol o carbohidratos)")
    if q["gdna"]:
        out.append("ADN genómico")
    if q["ng"] < 1 and not caso.get("poco_material"):
        out.append("rendimiento muy bajo")
    return out


def aplicar_qc(exp, caso):
    """Lleva las decisiones del QC al diseño que simula."""
    dis = exp["dis"]
    dis["excluidas"] = [k for k, q in exp["qc"].items() if q["estado"] == "excluida"]
    dis["calidad"] = {k: dict(rin=q["rin"], r230=q["r230"], gdna=q["gdna"])
                      for k, q in exp["qc"].items() if q["estado"] != "excluida"}


def costo_etapa(exp, caso, etapa):
    dis = exp["dis"]
    n_bio = len(caso["grupos"]) * dis["replicas"]
    n_lib = datos.n_muestras(dis, caso)
    if etapa == 1:
        return n_bio * 15
    if etapa == 2:
        return n_bio * datos.EXTRACCION
    if etapa == 4:
        b = datos.BIBLIOTECAS[dis["biblioteca"]]
        extra = sum(datos.EXTRAS[e]["costo"] for e in dis["extras"])
        n_ok = n_lib - len(dis.get("excluidas", ())) * dis["tecnicas"]
        return n_ok * (b["costo"] + extra)
    if etapa == 5:
        n_ok = n_lib - len(dis.get("excluidas", ())) * dis["tecnicas"]
        return n_ok * datos.costo_secuenciacion(dis)
    return 0


def costo_restante(exp, caso):
    """Lo que falta por pagar con el diseño actual (etapas aún no hechas)."""
    total = 0
    dis = exp["dis"]
    plataforma = dis.get("plataforma")
    if not plataforma:
        dis["plataforma"] = "nextseq"
    for etapa in (1, 2, 4, 5):
        if exp["etapa"] <= etapa:
            total += costo_etapa(exp, caso, etapa)
    if not plataforma:
        dis.pop("plataforma", None)
    return round(total)


def proyeccion(exp, caso):
    return exp["gastado"] + costo_restante(exp, caso)


def corridas_necesarias(exp, caso):
    dis = exp["dis"]
    pl = L.PLATAFORMAS.get(exp["plataforma"] or "novaseq")
    n_lib = datos.n_muestras(dis, caso) - len(dis.get("excluidas", ())) * dis["tecnicas"]
    total = n_lib * dis["profundidad"] * 1.1
    return max(1, -(-int(total) // pl["cap"])), round(total)


def falta_para(exp, etapa):
    """Mensaje si la estación todavía no se puede usar."""
    if exp["etapa"] < etapa:
        nombre, _, cuarto = L.ETAPAS[exp["etapa"]]
        return f"Todavía no. Siguiente paso: {nombre}."
    return None
