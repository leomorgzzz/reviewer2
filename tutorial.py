"""Capacitación: lecciones ilustradas de RNA-seq desde cero y un caso de
práctica con pistas."""

import curses

import animaciones as anim
import casos
import dibujo as d
import laboratorio
import progreso

MENTORA = "Dra. Lazo"

LECCIONES = [
    ("1 · ¿Qué mide un RNA-seq?", [
        "  <tenue>célula</>        <tenue>ARN</>           <tenue>biblioteca</>      <tenue>secuenciador</>   <tenue>datos</>",
        "  ┌──────┐     <agua>~~~~</>          <titulo>═══▓▓▓═══</>      ┌──────────┐    <texto>@lectura1</>",
        "  │ <bien>ADN</>  │ ──► <agua>~~~~~~</>  ──►   <titulo>═══▓▓▓═══</>  ──► │ <A>A</><C>C</><G>G</><T>T</><A>A</><C>C</> │ ─► <texto>ACGTTGCA…</>",
        "  │ <bien>→ARN</> │     <agua>~~~</>           <titulo>═══▓▓▓═══</>      └──────────┘    <texto>+ calidad</>",
        "  └──────┘     <tenue>(extraer)</>     <tenue>(cDNA +</>                          ",
        "                             <tenue>adaptadores)</>                     ",
        "",
        "El RNA-seq lee por millones fragmentos del ARN de una muestra y asigna cada "
        "lectura a un gen: <titulo>más lecturas = más ARN de ese gen</>.",
        "",
        "Es una medida <titulo>relativa</>: los genes se reparten las lecturas de cada "
        "muestra (vuelve en la lección 6).",
    ]),
    ("2 · El problema: la variación", [
        "  Gen X, cuentas normalizadas:",
        "",
        "  control  <g0!>●</>   <g0!>●</>        <g0!>●</>                   ",
        "  tratado          <g1!>●</>     <g1!>●</>      <g1!>●</>          ",
        "           ├────┼────┼────┼────┼────┤",
        "           0   100  200  300  400  500",
        "",
        "¿Subió el gen X o fue suerte? Los individuos <titulo>varían</>, y esa variación "
        "solo se mide con <titulo!>réplicas biológicas</>: unidades independientes.",
        "",
        "  • 1-2 réplicas: no alcanza.  • 3: mínimo.  • 6 o más: lo ideal (Schurch 2016).",
        "",
        "Medir dos veces la misma muestra (<titulo>réplica técnica</>) no cuenta (Marioni 2008).",
    ]),
    ("3 · Réplicas o profundidad", [
        "  genes DE encontrados (esquema de Liu 2014)",
        "",
        "  <bien>réplicas ▲</>   <bien!>████████████████</>  7",
        "               <bien!>█████████████</>     5",
        "               <bien!>█████████</>         3",
        "               <bien!>██████</>            2",
        "  <agua>lecturas ▲</>   <agua!>██████████</>  30 M  (con 3 réplicas)",
        "               <agua!>█████████</>   10 M",
        "",
        "Más lecturas ayudan poco y pronto dejan de ayudar; más réplicas miden mejor la "
        "<titulo>variación</>, que es lo que limita la estadística.",
        "",
        "Para genes: 10-30 M lecturas por muestra y el resto del dinero en réplicas.",
    ]),
    ("4 · El enemigo silencioso: los lotes", [
        "  <mal!>MAL</>                               <bien!>BIEN</>",
        "  lunes   <g0!>C C C C C C</>                lunes   <g0!>C</> <g1!>G</> <g1!>G</> <g0!>C</> <g0!>C</> <g1!>G</>",
        "  martes  <g1!>G G G G G G</>                martes  <g1!>G</> <g0!>C</> <g1!>G</> <g0!>C</> <g0!>C</> <g1!>G</>",
        "",
        "Lo que se procesa junto (día, kit, persona) deja huella en miles de genes: un "
        "<titulo>efecto de lote</>. Si cada grupo va en su propio día, día y tratamiento "
        "no se pueden separar: <mal!>confusión</>.",
        "",
        "Solución: cada lote con todos los grupos, al azar, y ~ lote + condición en la "
        "fórmula. En el juego, la mesa de lotes se abre con [L].",
    ]),
    ("5 · Elegir la biblioteca", [
        "  ¿Qué quieres medir?             →  biblioteca",
        "  ─────────────────────────────────────────────────────",
        "  genes, ARN íntegro             →  <agua>poli(A)</> o <agua>3′ tag</> (barato)",
        "  ARN degradado / FFPE           →  <agua>ribodepleción</> (+ UMIs)",
        "  lncRNA, antisentido            →  <agua>ribodepleción + hebra</>",
        "  isoformas, splicing            →  <agua>PE 2×100-150</>, 50-100 M, o <agua>lecturas largas</>",
        "  miRNA                          →  <agua>small RNA-seq</>",
        "  un tipo celular raro           →  <agua>célula única</> (varios donantes)",
        "  dónde en el tejido             →  <agua>espacial</>",
        "  sin genoma de referencia       →  <agua>de novo</> (PE, con hebra)",
        "",
        "Otros métodos: Catálogo [T].",
    ]),
    ("6 · De lecturas a genes", [
        "Paso a paso (la animación sigue después de esta página):",
        "",
        "  <titulo>FASTQ</> → FastQC/MultiQC → recortar adaptadores (fastp)",
        "       → alinear al genoma con splicing (<agua>STAR</>, <agua>HISAT2</>) y contar por gen",
        "         (<agua>featureCounts</>)  o  pseudoalinear al transcriptoma (<agua>Salmon</>)",
        "       → <titulo>matriz de cuentas</> genes × muestras",
        "",
        "<titulo!>Normalizar</> corrige la profundidad de cada muestra suponiendo que "
        "<titulo>la mayoría de los genes no cambia</>; si cambia todo el ARN, hacen falta "
        "spike-ins.",
        "",
        "A DESeq2 se le dan cuentas crudas, no TPM ni FPKM.",
    ]),
    ("7 · La estadística", [
        "  Var(cuentas) = μ + α·μ²      <tenue>(binomial negativa)</>",
        "",
        "DESeq2, edgeR y limma-voom <titulo>comparten información entre genes</> para "
        "estimar la variación con pocas réplicas; una t gen por gen pierde potencia.",
        "",
        "La <titulo!>fórmula</> describe el diseño:",
        "  ~ condición · ~ lote + condición · ~ donante + condición (pareado)",
        "  ~ genotipo + tratamiento + genotipo:tratamiento (interacción)",
        "  tiempo como factor + prueba LRT (¿cambia en algún momento?)",
        "",
        "Con 20 000 genes, p < 0.05 da ~1 000 falsos: usa padj de <bien!>Benjamini-Hochberg</>.",
    ]),
    ("8 · Cómo se juega", [
        "Cada caso es una pregunta con presupuesto y una trampa. Muévete con flechas/WASD "
        "y usa cada estación con E.",
        "",
        "  <titulo>Oficina</>      investigador ☺ y Dra. Lazo ☻ (investigar), papel de diseño",
        "  <titulo>Bioterio…</>    unidades experimentales, calendario, técnico",
        "  <titulo>Lab húmedo</>   campana de extracción, congelador, estante de kits",
        "  <titulo>Cuarto de QC</> NanoDrop, gel, Bioanalyzer",
        "  <titulo>Secuenciación</> plataforma, lectura y profundidad; esperar",
        "  <titulo>Bioinformática</> computadora: análisis, PCA, volcán; decidir",
        "  <titulo>Buzón</>        manuscrito al Revisor 2",
        "",
        "Los errores se arrastran entre etapas, y el Revisor 2 lee tu cuaderno. Con "
        "<mal!>REVISIÓN MAYOR</> o menos de 60/100 el caso no se resuelve: corrige y reenvía.",
    ]),
]


def capacitacion(win, juego):
    win.erase()
    d.dialogo(win, [
        "Lo básico antes del primer caso: cómo diseñar experimentos de RNA-seq que "
        "sobrevivan al <mal!>Revisor 2</>. Lo que se hace mal en el laboratorio no lo arregla "
        "ningún programa.",
    ], MENTORA)
    i = 0
    while 0 <= i < len(LECCIONES):
        titulo, lineas = LECCIONES[i]
        k = d.visor(win, f"Capacitación {i + 1}/{len(LECCIONES)} · {titulo}", lineas,
                    ayuda="→/Enter siguiente · ← anterior · Esc salir",
                    salir=[curses.KEY_RIGHT, curses.KEY_LEFT])
        if k == curses.KEY_LEFT:
            i = max(0, i - 1)
            continue
        if k == d.ESC or d.es(k, "q"):
            break
        if i == 5:
            anim.alineamiento(win, juego["velocidad"])
        i += 1
    else:
        juego["tutorial"] = True
        progreso.guardar(juego)
        win.erase()
        if d.menu(win, "¿Hacer un caso de práctica con pistas?",
                  ["Sí, el primer encargo con pistas", "No, a la oficina"]) == 0:
            caso = casos.CASOS[0]
            d.popup(win, "Te acompaño en el primer encargo con avisos después de cada "
                         "etapa. Empieza en la oficina: habla conmigo (☻ ) y con el "
                         "investigador (☺ ), luego escribe el diseño en el papel (▬ ).",
                    MENTORA)
            juego["caso_actual"] = caso["id"]
            laboratorio.Lab(win, juego, caso, practica=True).jugar()
    juego["tutorial"] = True
    progreso.guardar(juego)
