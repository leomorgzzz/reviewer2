"""Estado de la partida (guardado en ~/.reviewer2.json) y repaso espaciado."""

import json
import os

import idioma

ARCHIVO = idioma.migrar("~/.revisor2.json", "~/.reviewer2.json")


def nuevo_juego():
    return dict(
        desbloqueado=0,       # índice del caso más alto disponible
        mejores={},           # "metformina" -> {"normal": {estrellas, sens, fdr, …}}
        disenos={},           # último diseño enviado por caso (para retomarlo)
        fallos={},            # "banco:replicas1" -> n
        aciertos={},
        examen=None,          # mejor resultado (aciertos)
        velocidad="normal",
        dificultad="normal",
        tutorial=False,       # ya hizo la capacitación
        protocolos=[],        # rutas de los protocolos exportados
        expedientes={},       # caso -> expediente del laboratorio (ver expediente.py)
        caso_actual=None,
        nombre=None,          # cómo te llama el juego
    )


def guardar(juego):
    tmp = ARCHIVO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(juego, f, ensure_ascii=False, indent=1)
    os.replace(tmp, ARCHIVO)


def cargar():
    try:
        with open(ARCHIVO, encoding="utf-8") as f:
            juego = json.load(f)
    except (OSError, ValueError):
        return None
    for k, v in nuevo_juego().items():
        juego.setdefault(k, v)
    # versión anterior: un caso «ACEPTADO» con poca sensibilidad no desbloqueaba el
    # siguiente; con la calificación por puntos sí cuenta como resuelto
    import casos
    for i, c in enumerate(casos.CASOS):
        for m in juego["mejores"].get(c["id"], {}).values():
            if m.get("dictamen", "").startswith("ACEPTADO") and juego["desbloqueado"] <= i:
                juego["desbloqueado"] = i + 1
                m["aprobado"] = True
                m["estrellas"] = max(m.get("estrellas", 0), 1)
    return juego


def nombre(juego):
    return juego.get("nombre") or "colega"


def mejor(juego, caso_id, dificultad=None):
    por_dif = juego["mejores"].get(caso_id, {})
    if dificultad:
        return por_dif.get(dificultad)
    return max(por_dif.values(), key=lambda m: m["estrellas"], default=None)


def registrar(juego, clave, acierto):
    d = juego["aciertos"] if acierto else juego["fallos"]
    d[clave] = d.get(clave, 0) + 1


def peso(juego, clave):
    return max(0.5, 1 + 2 * juego["fallos"].get(clave, 0)
               - 0.5 * juego["aciertos"].get(clave, 0))
