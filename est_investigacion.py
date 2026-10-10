"""Estaciones para investigar el caso: librero, investigador, Dra. Lazo,
técnico, calendario, congelador y cuaderno."""

import datos
import dibujo as d
from idioma import tr
import expediente as X
import lab_datos as L
import manual
import progreso
import protocolo
import simulacion as sim
from estacion_comun import MENTORA, TECNICO, decir, menu


# ============================================================ investigación
def librero(lab):
    while True:
        op = menu(lab, "Librero", ["Manual del laboratorio", "Catálogo de métodos",
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
        op = menu(lab, caso["investigador"], preguntas)
        if op is None or op == len(preguntas) - 1:
            return
        if op == len(preguntas) - 2:
            d.dialogo(lab.win, L.intro_sin_pista(caso), caso["investigador"], fondo=lab.dibujar)
        else:
            lab.hallar(f"inv:{op}")
            decir(lab, resp[preguntas[op]], caso["investigador"])


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
        # se traducen por separado: la plantilla no coincide con el consejo pegado
        tr(f"<titulo!>Siguiente paso: {nombre}</> ({cuarto.replace('{lugar}', lab.lugar.lower())}). ")
        + tr(consejos.get(etapa, "")),
    ], MENTORA, fondo=lab.dibujar)


def tecnico(lab):
    lab.hallar("tecnico")
    decir(lab, X.info(lab.caso)["tecnico"] or "Aquí ando, por si necesitas algo.", TECNICO)


def calendario(lab):
    lab.hallar("calendario")
    decir(lab, X.info(lab.caso)["calendario"] or "Sin restricciones esta semana.",
           "Calendario de la pared")


def congelador(lab):
    lab.hallar("congelador")
    txt = X.info(lab.caso)["congelador"] or lab.caso["muestra"]
    decir(lab, txt, "Congelador −80 °C")


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
        l.append(tr(f"<agua>Hipótesis:</> {info['hipotesis'][exp['hipotesis']]}")
                 + (tr("  <mal>(cambiada después de ver datos)</>") if exp["harking"] else ""))
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
        l.append(tr(f"<agua>Biblioteca:</> {datos.BIBLIOTECAS[dis['biblioteca']]['nombre']} · "
                    f"{exp['pcr']} ciclos · extras: ")
                 + (", ".join(tr(datos.EXTRAS[e]["nombre"]) for e in dis["extras"]
                              if e in ("hebra", "umi", "ercc")) or tr("ninguno")))
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
