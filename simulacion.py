"""Simulación de un experimento de RNA-seq y de su análisis.

Cómo se generan los datos (todo en escala de abundancia absoluta por célula):

  λ(gen, muestra) = μ_gen · 2^(efecto del grupo + efecto del lote + efecto del
                    donante) · Gamma(ruido biológico, dispersión α_gen)

La secuenciación reparte las lecturas de cada biblioteca en proporción a λ
(composición), y cada cuenta es Poisson. Así aparecen solos los fenómenos
reales: varianza binomial negativa, efectos de lote, sesgo de composición
(Lovén 2012) y réplicas técnicas que solo agregan ruido de Poisson
(Marioni 2008).

El análisis es un modelo lineal sobre log2 de cuentas normalizadas con la
varianza de cada gen encogida hacia la de todos (como limma/DESeq2/edgeR),
prueba t o F por gen y corrección por pruebas múltiples. Es una versión
didáctica: reproduce la dirección de cada efecto, no los números exactos de
DESeq2.
"""

import math
import random

import datos

# ---------------------------------------------------------------- muestras


def muestras(dis, caso):
    """Lista de bibliotecas: dict(grupo, rep, tec, donante, lote, nombre)."""
    salida = []
    pareado = caso.get("pareado", False)
    excluidas = set(dis.get("excluidas", ()))
    for g, nombre_g in enumerate(caso["grupos"]):
        for r in range(dis["replicas"]):
            clave = f"{g}-{r}"
            if clave in excluidas:
                continue
            for t in range(dis["tecnicas"]):
                salida.append(dict(
                    grupo=g, rep=r, tec=t,
                    donante=r if pareado else g * 100 + r,
                    lote=dis["lotes"].get(clave, 0),
                    nombre=f"{caso['abrev'][g]}{r + 1}" + ("" if dis["tecnicas"] == 1 else
                                                           "abc"[t]),
                ))
    return salida


def replicas_efectivas(dis, caso):
    """Réplicas biológicas del grupo más pequeño, sin contar las excluidas."""
    excluidas = set(dis.get("excluidas", ()))
    return min(sum(1 for r in range(dis["replicas"]) if f"{g}-{r}" not in excluidas)
               for g in range(len(caso["grupos"])))


def n_lotes_necesarios(dis, caso):
    cap = caso.get("capacidad")
    total = len(caso["grupos"]) * dis["replicas"]
    if not cap:
        return 1
    return max(1, math.ceil(total / cap))


def lotes_por_orden(dis, caso):
    """La asignación «ingenua»: las muestras se procesan en el orden en que
    están en la lista (todas las de un grupo, luego las del siguiente)."""
    cap = caso.get("capacidad") or 10 ** 6
    lotes, i = {}, 0
    if caso.get("pareado"):
        # cada donante llega con sus dos muestras: se procesan juntas
        por_lote = max(1, cap // len(caso["grupos"]))
        for r in range(dis["replicas"]):
            for g in range(len(caso["grupos"])):
                lotes[f"{g}-{r}"] = r // por_lote
        return lotes
    for g in range(len(caso["grupos"])):
        for r in range(dis["replicas"]):
            lotes[f"{g}-{r}"] = i // cap
            i += 1
    return lotes


def lotes_balanceados(dis, caso, rng=None):
    """Bloques aleatorizados: cada lote recibe muestras de todos los grupos
    (en lo posible el mismo número) y el orden dentro del grupo es al azar."""
    rng = rng or random.Random()
    n = n_lotes_necesarios(dis, caso)
    lotes = {}
    if caso.get("pareado"):
        donantes = list(range(dis["replicas"]))
        rng.shuffle(donantes)
        for i, r in enumerate(donantes):
            for g in range(len(caso["grupos"])):
                lotes[f"{g}-{r}"] = i % n
        return lotes
    for g in range(len(caso["grupos"])):
        reps = list(range(dis["replicas"]))
        rng.shuffle(reps)
        for i, r in enumerate(reps):
            lotes[f"{g}-{r}"] = i % n
    return lotes


def tabla_lotes(dis, caso):
    """{lote: [n por grupo]} con las réplicas biológicas."""
    t = {}
    excluidas = set(dis.get("excluidas", ()))
    for g in range(len(caso["grupos"])):
        for r in range(dis["replicas"]):
            if f"{g}-{r}" in excluidas:
                continue
            l = dis["lotes"].get(f"{g}-{r}", 0)
            t.setdefault(l, [0] * len(caso["grupos"]))[g] += 1
    return dict(sorted(t.items()))


def confusion_lote(dis, caso):
    """'ninguna' (un lote o todos completos), 'parcial' o 'total' (algún
    grupo vive en lotes que no tiene ningún otro grupo)."""
    t = tabla_lotes(dis, caso)
    if len(t) <= 1:
        return "ninguna"
    completos = all(all(n > 0 for n in fila) for fila in t.values())
    if completos:
        desbalance = any(max(f) - min(f) > 1 for f in t.values())
        return "desbalance" if desbalance else "ninguna"
    # ¿se puede separar? hace falta que algún lote compare grupos
    mezclados = sum(1 for f in t.values() if sum(1 for n in f if n) > 1)
    return "total" if mezclados == 0 else "parcial"


def sobrecupo(dis, caso):
    cap = caso.get("capacidad")
    if not cap:
        return False
    return any(sum(f) > cap for f in tabla_lotes(dis, caso).values())


# ------------------------------------------------------------ capacidades
MEDIBLE = {
    # objetivo -> {biblioteca: fracción de rasgos que se pueden medir}
    "genes": dict(polyA=1, ribo=1, tag3=1, small=0, sc10x=1, smartseq=1, snrna=.9,
                  largo=1, espacial=.9),
    "mirna": dict(polyA=.03, ribo=.05, tag3=0, small=1, sc10x=0, smartseq=.03, snrna=0,
                  largo=0, espacial=0),
    "antisentido": dict(polyA=.55, ribo=1, tag3=.3, small=0, sc10x=.2, smartseq=.5,
                        snrna=.6, largo=.8, espacial=.2),
    "splicing": dict(polyA=1, ribo=1, tag3=.05, small=0, sc10x=.05, smartseq=.6,
                     snrna=.3, largo=1, espacial=.05),
    "celulas": dict(polyA=.15, ribo=.15, tag3=.15, small=0, sc10x=1, smartseq=.5,
                    snrna=.9, largo=.15, espacial=.5),
}
# fracción de las lecturas que cuentan para el rasgo de interés
EFICIENCIA = dict(polyA=1.0, ribo=.5, tag3=1.6, small=.6, sc10x=.5, smartseq=.6,
                  snrna=.35, largo=.9, espacial=.4)


def perfil(dis, caso):
    """Qué tan bien mide este diseño lo que pide el caso."""
    obj = caso["objetivo"]
    if obj in ("global", "tiempo", "interaccion"):
        obj_base = "genes"
    elif obj == "novo":
        obj_base = "genes"
    else:
        obj_base = obj
    lib = dis["biblioteca"]
    frac = MEDIBLE[obj_base][lib]
    eff = EFICIENCIA[lib]
    disp_extra = 1.0
    fp_extra = 0.0
    rin = caso.get("rin", 9)
    if lib == "polyA" and rin < 7:
        # ARN degradado: oligo-dT solo agarra el extremo 3′, y distinto en cada muestra
        eff *= max(0.1, (rin - 1) / 8)
        disp_extra = 1 + (7 - rin) * 0.6
    if lib == "tag3" and rin < 5:
        eff *= 0.7
    if obj == "antisentido" and "hebra" not in dis["extras"]:
        frac *= 0.35
        fp_extra = 0.12
    if obj == "splicing":
        frac *= min(1.0, datos.LECTURAS[dis["lectura"]]["iso"])
        if "splicing" not in dis["extras"] and lib != "largo":
            frac = 0.0
        if lib == "largo" and dis["ruta"] != "isoseq":
            frac *= 0.4
        eff *= 0.08 if lib != "largo" else 0.5
    if obj == "mirna" and dis["ruta"] != "mirdeep":
        frac *= 0.3
    if obj == "mirna" and dis.get("pierde_pequenos"):
        frac *= 0.05         # la columna dejó pasar los ARN < 200 nt
    if obj == "novo" and dis["ruta"] != "trinity" and dis["ruta"] != "isoseq":
        frac *= 0.35          # se mapea contra una especie pariente
    if lib in ("sc10x", "snrna", "smartseq") and dis["ruta"] not in ("cr_pb", "cr_cel"):
        eff *= 0.6            # sin cuentas por célula se pierde la señal del tipo celular
    if dis["biblioteca"] != "largo" and dis["lectura"] == "LARGA":
        frac = 0.0            # combinación imposible
    if dis["biblioteca"] == "largo" and dis["lectura"] != "LARGA":
        frac = 0.0
    if "umi" in dis["extras"] and caso.get("poco_material"):
        disp_extra *= 0.8
    return dict(frac=frac, eff=eff, disp_extra=disp_extra, fp_extra=fp_extra)


# ------------------------------------------------------------ utilidades


def poisson(rng, lam):
    if lam <= 0:
        return 0
    if lam > 40:
        return max(0, round(rng.gauss(lam, math.sqrt(lam))))
    l, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= l:
            return k
        k += 1


def _betacf(a, b, x):
    m_max, eps = 200, 3e-14
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, m_max + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(1 + aa / c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(1 + aa / c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1) < eps:
            break
    return h


def betainc(a, b, x):
    """Beta incompleta regularizada I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    ln = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
          + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return math.exp(ln) * _betacf(a, b, x) / a
    return 1 - math.exp(ln) * _betacf(b, a, 1 - x) / b


def p_t(t, df):
    if df <= 0:
        return 1.0
    return betainc(df / 2, 0.5, df / (df + t * t))


def p_f(f, d1, d2):
    if d2 <= 0 or f <= 0:
        return 1.0
    return betainc(d2 / 2, d1 / 2, d2 / (d2 + d1 * f))


def invertir(m):
    """Inversa por Gauss-Jordan; None si es singular."""
    n = len(m)
    a = [list(fila) + [1.0 if i == j else 0.0 for j in range(n)] for i, fila in enumerate(m)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[piv][col]) < 1e-9:
            return None
        a[col], a[piv] = a[piv], a[col]
        p = a[col][col]
        a[col] = [v / p for v in a[col]]
        for r in range(n):
            if r != col and a[r][col]:
                f = a[r][col]
                a[r] = [vr - f * vc for vr, vc in zip(a[r], a[col])]
    return [fila[n:] for fila in a]


def ajustar_p(ps, metodo):
    n = len(ps)
    if metodo == "nada":
        return list(ps)
    if metodo == "bonf":
        return [min(1.0, p * n) for p in ps]
    orden = sorted(range(n), key=lambda i: ps[i])
    ajust = [0.0] * n
    previo = 1.0
    for rango in range(n, 0, -1):
        i = orden[rango - 1]
        previo = min(previo, ps[i] * n / rango)
        ajust[i] = previo
    return ajust


# ------------------------------------------------------- matriz de diseño


def matriz_diseno(formula, caso, mts):
    """Devuelve (X, nombres de columnas, índices de las columnas de interés,
    contraste o None, error o None)."""
    k = len(caso["grupos"])
    fac = caso.get("factores")
    cols, nombres = [[1.0] * len(mts)], ["intercepto"]
    interes, contraste = [], None

    def dummies(valores, prefijo):
        niveles = sorted(set(valores))
        idx = []
        for nv in niveles[1:]:
            cols.append([1.0 if v == nv else 0.0 for v in valores])
            nombres.append(f"{prefijo}{nv}")
            idx.append(len(cols) - 1)
        return idx

    grupos = [m["grupo"] for m in mts]
    if formula in ("inter", "aditivo"):
        if not fac:
            return None, None, None, None, "el caso no tiene dos factores (genotipo y tratamiento)"
        gen = [fac["genotipo"][g] for g in grupos]
        tra = [fac["tratamiento"][g] for g in grupos]
        cols.append([float(v) for v in gen]); nombres.append("genotipo")
        cols.append([float(v) for v in tra]); nombres.append("tratamiento")
        if formula == "inter":
            cols.append([float(a * b) for a, b in zip(gen, tra)])
            nombres.append("genotipo:tratamiento")
            interes = [3]
        else:
            interes = [2]
    else:
        if formula in ("par", "par_lote"):
            dummies([m["donante"] for m in mts], "donante")
        if formula in ("lote", "par_lote", "tiempo_lote"):
            dummies([m["lote"] for m in mts], "lote")
        interes = dummies(grupos, "grupo")
        if fac:
            # factorial analizado como grupos: la interacción es un contraste
            pos = {}
            for g in range(k):
                pos[(fac["genotipo"][g], fac["tratamiento"][g])] = g
            vec = [0.0] * len(cols)
            for (gg, tt), g in pos.items():
                signo = 1 if gg == tt else -1
                if g > 0:
                    vec[interes[g - 1]] += signo
            contraste = vec
    x = [list(fila) for fila in zip(*cols)]
    return x, nombres, interes, contraste, None


# ------------------------------------------------------------- simulación


def _verdad(caso, rng, n_genes):
    """Efectos verdaderos (log2) por gen y grupo, y qué genes cuentan como
    'diferenciales' para evaluar."""
    s = caso["sim"]
    k = len(caso["grupos"])
    efectos, es_de = [], []
    for _ in range(n_genes):
        e = [0.0] * k
        de = False
        obj = caso["objetivo"]
        if obj == "interaccion":
            fac = caso["factores"]
            u = rng.random()
            a = rng.choice((-1, 1)) * (s["lfc_min"] + abs(rng.gauss(0, s["lfc_sd"])))
            for g in range(k):
                gg, tt = fac["genotipo"][g], fac["tratamiento"][g]
                if u < 0.12:                      # efecto del tratamiento (igual en ambos)
                    e[g] = a * tt
                elif u < 0.2:                     # efecto del genotipo
                    e[g] = a * gg
                elif u < 0.2 + s["frac_de"]:      # interacción: solo en un genotipo
                    e[g] = a * tt * (1 - gg)
            de = 0.2 <= u < 0.2 + s["frac_de"]
        elif obj == "tiempo":
            if rng.random() < s["frac_de"]:
                a = rng.choice((-1, 1)) * (s["lfc_min"] + abs(rng.gauss(0, s["lfc_sd"])))
                pico = rng.randrange(1, k)
                forma = rng.choice(("pulso", "sube"))
                for g in range(1, k):
                    if forma == "pulso":
                        e[g] = a * max(0.0, 1 - abs(g - pico) * 0.7)
                    else:
                        e[g] = a * min(1.0, g / pico)
                de = True
        else:
            if rng.random() < s["frac_de"]:
                a = rng.choice((-1, 1)) * (s["lfc_min"] + abs(rng.gauss(0, s["lfc_sd"])))
                for g in range(1, k):
                    e[g] = a
                de = True
            if obj == "global":
                for g in range(1, k):
                    e[g] += s.get("cambio_global", 1.0)
                de = True
        efectos.append(e)
        es_de.append(de)
    return efectos, es_de


def simular(dis, caso, rng=None):
    rng = rng or random.Random()
    s = caso["sim"]
    pf = perfil(dis, caso)
    mts = muestras(dis, caso)
    n = len(mts)
    G = s.get("genes", 1200)
    efectos, es_de = _verdad(caso, rng, G)
    # rasgos que este diseño no puede medir: no llevan señal
    medible = [rng.random() < pf["frac"] for _ in range(G)]
    mu = [math.exp(rng.gauss(s.get("log_mu", 3.2), 1.6)) for _ in range(G)]
    alfa = [s["disp"] * pf["disp_extra"] * math.exp(rng.gauss(0, 0.5)) for _ in range(G)]
    # señal falsa por solapamiento de hebras (biblioteca sin hebra)
    falsos = {}
    if pf["fp_extra"]:
        de_idx = [i for i in range(G) if es_de[i]]
        for i in range(G):
            if not es_de[i] and de_idx and rng.random() < pf["fp_extra"]:
                falsos[i] = efectos[rng.choice(de_idx)]
    # efectos de lote y de donante por gen
    lotes = sorted({m["lote"] for m in mts})
    ef_lote = {(l, i): (rng.gauss(0, s.get("sd_lote", 0.0)) if l else 0.0)
               for l in lotes for i in range(G)}
    donantes = sorted({m["donante"] for m in mts})
    sd_don = s.get("sd_donante", 0.0)
    ef_don = {(d_, i): rng.gauss(0, sd_don) for d_ in donantes for i in range(G)}
    # ruido biológico: lo comparten las réplicas técnicas de una misma muestra.
    # Si la «réplica» no es una unidad experimental independiente (pozos de la
    # misma placa, hojas de la misma planta), casi todo el ruido biológico es
    # común a todo el grupo: las réplicas se parecen demasiado entre sí.
    bio = {}
    comun = {}
    for m in mts:
        clave = (m["grupo"], m["rep"])
        if clave in bio:
            continue
        if dis.get("pseudo"):
            if m["grupo"] not in comun:
                comun[m["grupo"]] = [rng.gammavariate(1 / a, a) for a in alfa]
            bio[clave] = [c * rng.gammavariate(1 / (a * 0.1), a * 0.1)
                          for c, a in zip(comun[m["grupo"]], alfa)]
        else:
            bio[clave] = [rng.gammavariate(1 / a, a) for a in alfa]
    # confusores ocultos: asignación no aleatoria y carriles por grupo
    sesgo = dis.get("sesgo", 0.0)
    ef_sesgo = [rng.gauss(0, sesgo) if sesgo and rng.random() < 0.15 else 0.0
                for _ in range(G)]
    # calidad de cada muestra (extracción y QC del laboratorio)
    calidad = dis.get("calidad", {})
    lib = dis["biblioteca"]
    ruido_q, eff_q = {}, {}
    for m in mts:
        clave = f"{m['grupo']}-{m['rep']}"
        if clave in ruido_q:
            continue
        q = calidad.get(clave)
        if not q:
            ruido_q[clave], eff_q[clave] = None, 1.0
            continue
        rin = q.get("rin", 9)
        mala = max(0.0, 7 - rin)
        sd = mala * (0.18 if lib == "polyA" else 0.06)
        ruido_q[clave] = [2 ** rng.gauss(0, sd) for _ in range(G)] if sd else None
        e = 1.0
        if lib == "polyA" and rin < 7:
            e *= max(0.15, (rin - 1) / 6)
        if q.get("r230", 2.0) < 1.6:
            e *= 0.6                 # sales/fenol inhiben la retrotranscripción
        if q.get("gdna") and lib in ("ribo", "tag3"):
            e *= 0.8                 # lecturas perdidas en ADN genómico
        eff_q[clave] = e
    # spike-ins: misma cantidad absoluta por célula en todas las muestras
    n_spk = 30 if "ercc" in dis["extras"] else 0
    spk_mu = [math.exp(rng.gauss(3.0, 1.5)) for _ in range(n_spk)]
    prof = dis["profundidad"] * 1e6 * pf["eff"]
    if dis.get("dimeros"):
        prof *= 0.75                 # lecturas gastadas en dímeros de adaptador
    # minijuegos: biblioteca perdida en perlas, carga de la celda, -s de featureCounts
    prof *= dis.get("factor_lecturas", 1.0) * dis.get("factor_hebra", 1.0)
    cuentas, cuentas_spk = [], []
    for m in mts:
        clave = f"{m['grupo']}-{m['rep']}"
        rq = ruido_q[clave]
        lam = []
        for i in range(G):
            e = efectos[i][m["grupo"]] if medible[i] else 0.0
            if i in falsos:
                e = falsos[i][m["grupo"]]
            if m["grupo"] > 0:
                e += ef_sesgo[i]
            v = mu[i] * 2 ** (e + ef_lote[(m["lote"], i)] + ef_don[(m["donante"], i)])
            v *= bio[(m["grupo"], m["rep"])][i]
            if rq:
                v *= rq[i]
            lam.append(v)
        total = sum(lam) + sum(spk_mu)
        # el total simulado representa 1/10 del transcriptoma: se reescala
        escala = prof * eff_q[clave] / (total * 10)
        cuentas.append([poisson(rng, l * escala) for l in lam])
        cuentas_spk.append([poisson(rng, l * escala) for l in spk_mu])
    return analizar(dis, caso, mts, cuentas, cuentas_spk, efectos, es_de, medible, rng)


# --------------------------------------------------------------- análisis


def factores_tamano(cuentas, filas=None):
    """Razón de medianas (DESeq2) sobre los genes sin ceros."""
    n = len(cuentas)
    G = len(cuentas[0])
    filas = range(G) if filas is None else filas
    sf = []
    validos = [i for i in filas if all(cuentas[j][i] > 0 for j in range(n))]
    if len(validos) < 5:
        tot = [sum(c) or 1 for c in cuentas]
        med = sorted(tot)[n // 2]
        return [t / med for t in tot]
    geo = {i: sum(math.log(cuentas[j][i]) for j in range(n)) / n for i in validos}
    for j in range(n):
        r = sorted(math.log(cuentas[j][i]) - geo[i] for i in validos)
        sf.append(math.exp(r[len(r) // 2]))
    return sf


def analizar(dis, caso, mts, cuentas, cuentas_spk, efectos, es_de, medible, rng):
    n = len(mts)
    if n < 2:
        res = dict(estado="sin_replicas", n=n, notas=["No quedaron muestras suficientes."],
                   medible=0.0)
        return _evaluar(res, {}, {}, es_de, medible, [], efectos, caso)
    G = len(cuentas[0])
    res = dict(estado="ok", n=n, notas=[], medible=sum(medible) / G)
    # normalización
    entrada = dis["entrada"]
    if entrada == "spike" and not cuentas_spk[0]:
        res["notas"].append("Pediste normalizar con spike-ins pero no agregaste ERCC: "
                            "se usó la razón de medianas.")
        entrada = "crudas"
    if entrada == "spike":
        sf = factores_tamano(cuentas_spk)
    elif entrada == "tpm":
        tot = [sum(c) or 1 for c in cuentas]
        med = sorted(tot)[n // 2]
        sf = [t / med for t in tot]
    else:
        sf = factores_tamano(cuentas)
    norm = [[c / sf[j] for c in cuentas[j]] for j in range(n)]
    media = [sum(norm[j][i] for j in range(n)) / n for i in range(G)]
    genes = list(range(G))
    if "filtro" in dis["extras"]:
        genes = [i for i in genes if media[i] >= 5]
    else:
        genes = [i for i in genes if media[i] > 0]
    y = {i: [math.log2(norm[j][i] + 0.5) for j in range(n)] for i in genes}
    res["pca"] = pca(y, genes, mts)
    # ¿hay réplicas?
    reps_bio = dis["replicas"]
    if dis["ruta"] == "cr_cel" and dis["biblioteca"] in ("sc10x", "snrna", "smartseq"):
        return _celula_a_celula(dis, caso, mts, cuentas, efectos, es_de, medible, res, rng)
    formula = dis["formula"]
    prueba = dis["prueba"]
    if prueba == "ttest":
        formula = "cond" if not caso.get("factores") else "inter"
    x, nombres, interes, contraste, error = matriz_diseno(formula, caso, mts)
    if error:
        res.update(estado="no_estimable", motivo=error)
        return _evaluar(res, {}, {}, es_de, medible, genes, efectos, caso)
    p = len(x[0])
    xtx = [[sum(x[r][a] * x[r][b] for r in range(n)) for b in range(p)] for a in range(p)]
    inv = invertir(xtx)
    if inv is None:
        res.update(estado="no_estimable",
                   motivo="las columnas de la matriz de diseño son linealmente dependientes "
                          "(un factor está completamente confundido con otro)")
        return _evaluar(res, {}, {}, es_de, medible, genes, efectos, caso)
    df = n - p
    # coeficiente que responde la pregunta
    obj = caso["objetivo"]
    usar_contraste = contraste is not None and obj == "interaccion" and formula in (
        "cond", "lote", "par", "tiempo", "tiempo_lote", "par_lote")
    if obj == "interaccion" and formula == "aditivo":
        res["notas"].append("El modelo aditivo no tiene término de interacción: se probó "
                            "el efecto del tratamiento.")
    h = [[sum(inv[a][b] * x[r][b] for b in range(p)) for r in range(n)] for a in range(p)]
    betas, s2s = {}, {}
    for i in genes:
        yi = y[i]
        b = [sum(h[a][r] * yi[r] for r in range(n)) for a in range(p)]
        ajuste = [sum(x[r][a] * b[a] for a in range(p)) for r in range(n)]
        rss = sum((yi[r] - ajuste[r]) ** 2 for r in range(n))
        betas[i] = b
        s2s[i] = rss / df if df > 0 else float("nan")
    lfc, pvals = {}, {}
    if df <= 0:
        res.update(estado="sin_replicas")
        for i in genes:
            lfc[i] = _efecto(betas[i], interes, contraste if usar_contraste else None)
        return _evaluar(res, lfc, {}, es_de, medible, genes, efectos, caso,
                        solo_fc=prueba == "fc")
    d0 = 0 if prueba in ("ttest", "fc") else 4
    validos = sorted(v for v in s2s.values() if v > 0)
    s0 = validos[len(validos) // 2] if validos else 1.0
    multinivel = prueba == "lrt" and len(interes) > 1 and not usar_contraste
    for i in genes:
        s2 = s2s[i]
        s2p = (d0 * s0 + df * s2) / (d0 + df)
        s2p = max(s2p, 1e-8)
        if multinivel:
            # prueba F de todos los coeficientes de interés a la vez
            sub = [[inv[a][b] for b in interes] for a in interes]
            sinv = invertir(sub)
            bb = [betas[i][a] for a in interes]
            q = sum(bb[a] * sinv[a][c] * bb[c] for a in range(len(bb)) for c in range(len(bb)))
            f = q / len(bb) / s2p
            pvals[i] = p_f(f, len(bb), df + d0)
            lfc[i] = max((betas[i][a] for a in interes), key=abs)
        else:
            if usar_contraste:
                c = contraste
                est = sum(c[a] * betas[i][a] for a in range(p))
                var = sum(c[a] * inv[a][b] * c[b] for a in range(p) for b in range(p))
            else:
                j = interes[-1]
                est, var = betas[i][j], inv[j][j]
            t = est / math.sqrt(s2p * var)
            pvals[i] = p_t(t, df + d0)
            lfc[i] = est
    if prueba == "fc":
        return _evaluar(res, lfc, {}, es_de, medible, genes, efectos, caso, solo_fc=True)
    padj = ajustar_p([pvals[i] for i in genes], dis["correccion"])
    padj = dict(zip(genes, padj))
    res["pvals"] = pvals
    return _evaluar(res, lfc, padj, es_de, medible, genes, efectos, caso)


def _efecto(b, interes, contraste):
    if contraste:
        return sum(c * v for c, v in zip(contraste, b))
    return b[interes[-1]] if interes else 0.0


def _celula_a_celula(dis, caso, mts, cuentas, efectos, es_de, medible, res, rng):
    """Cada célula tratada como réplica: se generan 40 «células» por muestra a
    partir del perfil de su donante y se comparan con una prueba de dos
    grupos de n grande."""
    G = len(cuentas[0])
    celulas = {0: [], 1: []}
    for j, m in enumerate(mts):
        if m["grupo"] > 1:
            continue
        tot = sum(cuentas[j]) or 1
        for _ in range(40):
            celulas[m["grupo"]].append(
                [math.log2(1 + poisson(rng, 4000 * c / tot * rng.gammavariate(3, 1 / 3)))
                 for c in cuentas[j]])
    lfc, pvals = {}, {}
    genes = list(range(G))
    for i in genes:
        a = [c[i] for c in celulas[0]]
        b = [c[i] for c in celulas[1]]
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        va = sum((v - ma) ** 2 for v in a) / (len(a) - 1)
        vb = sum((v - mb) ** 2 for v in b) / (len(b) - 1)
        se = math.sqrt(va / len(a) + vb / len(b)) or 1e-6
        t = (mb - ma) / se
        pvals[i] = math.erfc(abs(t) / math.sqrt(2))
        lfc[i] = (mb - ma) * 3
    padj = dict(zip(genes, ajustar_p([pvals[i] for i in genes], dis["correccion"])))
    res["pvals"] = pvals
    res["notas"].append(f"Se compararon {len(celulas[0])} contra {len(celulas[1])} células "
                        "como si fueran réplicas independientes.")
    return _evaluar(res, lfc, padj, es_de, medible, genes, efectos, caso)


def _evaluar(res, lfc, padj, es_de, medible, genes, efectos, caso, solo_fc=False):
    k = len(caso["grupos"])

    def signo_real(i):
        e = efectos[i]
        if caso["objetivo"] == "interaccion":
            fac = caso["factores"]
            vals = {(fac["genotipo"][g], fac["tratamiento"][g]): e[g] for g in range(k)}
            d = (vals[(1, 1)] - vals[(1, 0)]) - (vals[(0, 1)] - vals[(0, 0)])
        else:
            d = max(e[1:], key=abs) if k > 1 else 0
        return (d > 0) - (d < 0)

    sig = set()
    if solo_fc:
        sig = {i for i in lfc if abs(lfc[i]) > 1}
    elif padj:
        sig = {i for i in padj if padj[i] < 0.05}
    tp = sum(1 for i in sig if es_de[i] and (signo_real(i) == ((lfc[i] > 0) - (lfc[i] < 0))
                                             or caso["objetivo"] in ("tiempo",)))
    fp = len(sig) - tp
    n_verdad = sum(1 for i in range(len(es_de)) if es_de[i])
    res.update(
        sig=len(sig), tp=tp, fp=fp, verdad=n_verdad, probados=len(genes),
        sens=tp / n_verdad if n_verdad else 0.0,
        fdr=fp / len(sig) if sig else 0.0,
        subidos=sum(1 for i in sig if lfc[i] > 0), bajados=sum(1 for i in sig if lfc[i] < 0),
    )
    # puntos para el volcán
    vol = []
    for i in genes:
        if i in lfc and i in res.get("pvals", {}):
            vol.append((lfc[i], res["pvals"][i], i in sig, es_de[i]))
    res["volcan"] = vol
    return res


# --------------------------------------------------------------------- PCA


def pca(y, genes, mts, top=300):
    n = len(mts)
    if n < 3 or not genes:
        return None
    var = []
    for i in genes:
        m = sum(y[i]) / n
        var.append((sum((v - m) ** 2 for v in y[i]) / (n - 1), i))
    sel = [i for _, i in sorted(var, reverse=True)[:top]]
    filas = []
    for i in sel:
        m = sum(y[i]) / n
        filas.append([v - m for v in y[i]])
    # matriz de Gram entre muestras
    k = [[sum(f[a] * f[b] for f in filas) for b in range(n)] for a in range(n)]
    traza = sum(k[a][a] for a in range(n)) or 1
    vecs, vals = [], []
    for _ in range(2):
        v = [((a * 7919) % 13) - 6.0 for a in range(n)]
        lam = 0.0
        for _ in range(200):
            w = [sum(k[a][b] * v[b] for b in range(n)) for a in range(n)]
            for u in vecs:
                pr = sum(wi * ui for wi, ui in zip(w, u))
                w = [wi - pr * ui for wi, ui in zip(w, u)]
            norma = math.sqrt(sum(wi * wi for wi in w)) or 1
            v = [wi / norma for wi in w]
            lam = norma
        vecs.append(v)
        vals.append(lam)
    coords = [(vecs[0][a] * math.sqrt(vals[0]), vecs[1][a] * math.sqrt(vals[1]))
              for a in range(n)]
    return dict(coords=coords, var=[vals[0] / traza, vals[1] / traza])


def potencia_aprox(dis, caso):
    """Potencia aproximada para un gen típico con el cambio mínimo del caso
    (aproximación normal sobre log, como RNASeqPower de Hart 2013)."""
    s = caso["sim"]
    pf = perfil(dis, caso)
    cuentas = math.exp(s.get("log_mu", 3.2)) * dis["profundidad"] * pf["eff"] * 1.4
    cuentas = max(cuentas * pf["frac"], 0.01)
    cv2 = 1 / cuentas + s["disp"] * pf["disp_extra"] + s.get("sd_lote", 0) ** 2 * 0.3
    if caso.get("pareado") and dis["formula"] not in ("par", "par_lote"):
        cv2 += s.get("sd_donante", 0) ** 2 * 0.48
    n = dis["replicas"]
    if n < 2:
        return 0.0
    efecto = (s["lfc_min"] + 0.6 * s["lfc_sd"]) * math.log(2)
    z = efecto / math.sqrt(2 * cv2 / n) - 3.0      # α ≈ 0.003 por pruebas múltiples
    return 0.5 * math.erfc(-z / math.sqrt(2))
