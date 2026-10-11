"""Etapas 0 y 1: el papel de diseño y las unidades experimentales."""

import random
import animaciones as anim
import minijuegos as mj
import datos
import dibujo as d
from idioma import tr
import expediente as X
import lab_datos as L
import mesa
import simulacion as sim
from est_investigacion import cuaderno
from estacion_comun import Formulario, TECNICO, cobrar, decir, menu


# ===================================================== 0 · papel de diseño
def papel(lab):
    exp, caso = lab.exp, lab.caso
    info = X.info(caso)
    dis = exp["dis"]
    if exp["etapa"] > 0:
        if menu(lab, "El diseño ya está firmado", ["Solo verlo", "Reescribirlo (todo lo "
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
                f"${lab.tope:,}, contando {exp['dis']['profundidad']} M lecturas por muestra "
                "(la profundidad y los kits se eligen después y pueden bajarlo)"]

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
            decir(lab, tr("Falta elegir: ") + ", ".join(tr(f) for f in faltan) + ".")
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
            decir(lab, tr("Firmado. Pero ojo:\n\n") + "\n".join("· " + tr(n) for n in notas))
            return
    decir(lab, f"Diseño firmado. Siguiente: las unidades experimentales en el "
                f"{lab.lugar.lower()}.")


# ================================================== 1 · unidades experimentales
def unidades(lab):
    exp, caso = lab.exp, lab.caso
    if (m := X.falta_para(exp, 1)):
        decir(lab, m)
        return
    info = X.info(caso)
    dis = exp["dis"]
    win = lab.win
    nombre_lote = caso.get("lote_nombre", "lote")
    if info["aleatorizable"]:
        op = menu(lab, f"¿Cómo asignas los tratamientos a las {dis['replicas'] * len(caso['grupos'])} "
                         "unidades?", barajar=True,
                    opciones=["Sorteo al azar (números aleatorios)",
                     "Por orden: las primeras al grupo 1, las siguientes al grupo 2…",
                     "A ojo: las que se ven más sanas/grandes al tratamiento",
                     "Volver"])
        if op is None or op == 3:
            return
        exp["asignacion"] = ["azar", "orden", "ojo"][op]
        dis["sesgo"] = [0.0, 0.3, 0.6][op]
        _animar_asignacion(lab, exp["asignacion"])
        if info["lugar"] == "cultivo":
            decir(lab, "Ahora siembra los cultivos en la placa. Ojo: los pozos del borde "
                        "pierden más medio por evaporación.", TECNICO)
            db = mj.placa(lab, caso, dis)
            exp["minijuegos"]["placa"] = round(db, 2)
            dis["sesgo"] = dis.get("sesgo", 0.0) + 0.35 * max(0.0, db - 0.25)
    else:
        exp["asignacion"] = None
        dis["sesgo"] = 0.0
        decir(lab, "Aquí no puedes asignar el tratamiento: la condición ya viene con cada "
                    "persona (estudio observacional). Lo que sí controlas: emparejar, "
                    "registrar covariables y repartir el procesamiento.")
    if caso.get("capacidad"):
        decir(lab, f"Ahora reparte las unidades en {nombre_lote}s (máximo "
                    f"{caso['capacidad']} por {nombre_lote}). Así quedaron según el orden "
                    "de la lista.", TECNICO)
        while True:
            mesa.mesa_lotes(win, caso, dis, lab.pistas, lab.dif)
            if sim.sobrecupo(dis, caso):
                decir(lab, f"Algún {nombre_lote} pasa la capacidad: no cabe.", TECNICO)
                continue
            break
    else:
        dis["lotes"] = {k: 0 for k in X.claves_bio(exp, caso)}
    if not cobrar(lab, 1):
        return
    X.avanzar(exp, 1)
    exp["dia"] += max(0, len(sim.tabla_lotes(dis, caso)) - 1)
    lab.guardar()
    decir(lab, "Unidades listas y etiquetadas. Siguiente: extraer el ARN en la campana del "
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
