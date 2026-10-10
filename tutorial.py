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
        "El <titulo!>transcriptoma</> es el conjunto de ARN de una célula en un momento. "
        "Cambia con el tejido, la hora, el tratamiento: por eso se mide.",
        "",
        "El RNA-seq convierte el ARN en cDNA, lo corta en fragmentos, les pega "
        "adaptadores y los lee por millones. Luego cada lectura se asigna a un gen: "
        "<titulo>más lecturas de un gen = más ARN de ese gen</>.",
        "",
        "Es una medida <titulo>relativa</>: cada muestra recibe un número de lecturas y "
        "los genes se reparten ese total. Recuérdalo: vuelve en la lección 6.",
    ]),
    ("2 · El problema: la variación", [
        "  Gen X, cuentas normalizadas:",
        "",
        "  control  <g0!>●</>   <g0!>●</>        <g0!>●</>                   ",
        "  tratado          <g1!>●</>     <g1!>●</>      <g1!>●</>          ",
        "           ├────┼────┼────┼────┼────┤",
        "           0   100  200  300  400  500",
        "",
        "¿El tratamiento subió el gen X o fue suerte? Los individuos <titulo>varían</> "
        "aunque reciban lo mismo. Para responder hay que medir ESA variación, y solo se "
        "mide con <titulo!>réplicas biológicas</>: unidades independientes por grupo.",
        "",
        "  • Con 1 réplica: imposible saber (no hay valor p válido).",
        "  • Con 2: se estima muy mal.",
        "  • Con 3: mínimo aceptable. Con 6 o más: lo recomendado (Schurch 2016).",
        "",
        "Las <titulo>réplicas técnicas</> (la misma muestra medida dos veces) NO miden esa "
        "variación: solo el ruido del aparato, que en RNA-seq es pequeño (Marioni 2008).",
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
        "Cada lectura extra mide un poco mejor a los genes poco expresados, pero la "
        "ganancia se aplana pronto. Cada réplica extra mejora la estimación de la "
        "<titulo>variación</>, que es lo que limita la estadística.",
        "",
        "Regla práctica para genes: 10-30 M lecturas por muestra y el resto del dinero "
        "en réplicas. (Isoformas, lncRNA y de novo sí piden más profundidad.)",
    ]),
    ("4 · El enemigo silencioso: los lotes", [
        "  <mal!>MAL</>                               <bien!>BIEN</>",
        "  lunes   <g0!>C C C C C C</>                lunes   <g0!>C</> <g1!>G</> <g1!>G</> <g0!>C</> <g0!>C</> <g1!>G</>",
        "  martes  <g1!>G G G G G G</>                martes  <g1!>G</> <g0!>C</> <g1!>G</> <g0!>C</> <g0!>C</> <g1!>G</>",
        "",
        "Todo lo que se procesa junto (día, kit, persona, corrida) deja una huella en "
        "miles de genes: un <titulo>efecto de lote</>.",
        "",
        "Si el lunes van todos los controles y el martes todos los tratados, «martes» y "
        "«tratamiento» son la misma columna en los datos. Ninguna estadística los "
        "separa: es <mal!>confusión</>, y el experimento se tira.",
        "",
        "Solución de diseño: <titulo!>bloquear</> (cada lote con todos los grupos), "
        "<titulo!>aleatorizar</> el orden, y en el análisis poner el lote en la fórmula: "
        "~ lote + condición.",
        "",
        "En el juego: la mesa de lotes se abre con [L]. Ojo: por defecto el laboratorio "
        "procesa las muestras en el orden de la lista…",
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
        "El Catálogo [T] tiene la ficha de cada método de transcriptómica: RT-qPCR, "
        "microarreglos, CAGE, Ribo-seq, PRO-seq, SLAM-seq, CLIP, Nanopore…",
    ]),
    ("6 · De lecturas a genes", [
        "Paso a paso (la animación sigue después de esta página):",
        "",
        "  <titulo>FASTQ</> → FastQC/MultiQC → recortar adaptadores (fastp)",
        "       → alinear al genoma con splicing (<agua>STAR</>, <agua>HISAT2</>) y contar por gen",
        "         (<agua>featureCounts</>)  o  pseudoalinear al transcriptoma (<agua>Salmon</>)",
        "       → <titulo>matriz de cuentas</> genes × muestras",
        "",
        "<titulo!>Normalizar</>: cada muestra tiene distinta profundidad y composición. "
        "DESeq2 (razón de medianas) y edgeR (TMM) calculan un factor por muestra "
        "suponiendo que <titulo>la mayoría de los genes no cambia</>.",
        "",
        "Si el tratamiento cambia el ARN TOTAL de la célula (p. ej. MYC alto), ese "
        "supuesto falla: hacen falta <titulo>spike-ins</> agregados por número de células.",
        "",
        "TPM/FPKM sirven para comparar genes dentro de una muestra, no para darle a "
        "DESeq2: el modelo necesita cuentas crudas.",
    ]),
    ("7 · La estadística", [
        "  Var(cuentas) = μ + α·μ²      <tenue>(binomial negativa)</>",
        "",
        "Con 3-6 réplicas la variación de cada gen se estima mal, así que DESeq2, edgeR y "
        "limma-voom <titulo>comparten información entre genes</>. Una t de Student gen por "
        "gen no lo hace y pierde potencia; un umbral de fold change sin estadística no "
        "sabe nada de la variación.",
        "",
        "La <titulo!>fórmula</> describe el diseño:",
        "  ~ condición · ~ lote + condición · ~ donante + condición (pareado)",
        "  ~ genotipo + tratamiento + genotipo:tratamiento (interacción)",
        "  tiempo como factor + prueba LRT (¿cambia en algún momento?)",
        "",
        "Con 20 000 genes, p < 0.05 da ~1 000 falsos positivos. Se corrige con "
        "<bien!>Benjamini-Hochberg</> (FDR): padj < 0.05 = ≤ 5 % de falsos en la lista.",
    ]),
    ("8 · Cómo se juega", [
        "Cada caso es un investigador con una pregunta, un presupuesto y alguna trampa "
        "escondida. Lo resuelves en el <titulo!>laboratorio</>: te mueves con flechas/WASD y "
        "usas cada estación con E.",
        "",
        "  <titulo>Oficina</>      investigador ☺ y Dra. Lazo ☻ (investigar), papel de diseño",
        "  <titulo>Bioterio…</>    unidades experimentales, calendario, técnico",
        "  <titulo>Lab húmedo</>   campana de extracción, congelador, estante de kits",
        "  <titulo>Cuarto de QC</> NanoDrop, gel, Bioanalyzer",
        "  <titulo>Secuenciación</> plataforma, lectura y profundidad; esperar",
        "  <titulo>Bioinformática</> computadora: análisis, PCA, volcán; decidir",
        "  <titulo>Buzón</>        manuscrito al Revisor 2",
        "",
        "Las etapas van en orden y lo que hagas mal en una se arrastra a las demás: un ARN "
        "degradado que apruebes en el QC aparece como ruido en los resultados.",
        "",
        "Después de ver los datos decides: mandar al Revisor 2, cambiar el análisis, "
        "regresar a una etapa (cuesta días y dinero) o cambiar la hipótesis… y el Revisor 2 "
        "lee tu cuaderno.",
    ]),
]


def capacitacion(win, juego):
    win.erase()
    d.dialogo(win, [
        f"Hola, <titulo!>{progreso.nombre(juego)}</>. Soy la Dra. Lazo y te voy a enseñar "
        "a diseñar experimentos de RNA-seq que sobrevivan al <mal!>Revisor 2</>.",
        "El Revisor 2 lee cada propuesta buscando el error que la invalida. Casi "
        "siempre lo encuentra en el diseño, no en el análisis: lo que se hace mal en el "
        "laboratorio no lo arregla ningún programa.",
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
                         "investigador (☺ ), luego escribe el diseño en el papel (▤ ).",
                    MENTORA)
            juego["caso_actual"] = caso["id"]
            laboratorio.Lab(win, juego, caso, practica=True).jugar()
    juego["tutorial"] = True
    progreso.guardar(juego)
