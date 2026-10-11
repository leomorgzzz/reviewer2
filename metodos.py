"""Catálogo de métodos de transcriptómica y Manual del laboratorio.

METODOS: todas las tecnologías para medir ARN, de los microarreglos a la
transcriptómica espacial, con su principio, cuándo usarlas y sus límites.
MANUAL: el protocolo completo de un experimento de RNA-seq, paso a paso, del
diseño al depósito de datos. Las claves de MANUAL son las que cada caso
desbloquea (casos.py, campo «manual»); todas se pueden leer desde el inicio.
"""

from datos import cita

# (categoría, nombre, principio, cuándo, límites, datos típicos, análisis, fuentes)
METODOS = [
    # ---------------------------------------------------------------- clásicos
    ("Por hibridación y PCR", "Northern blot",
     "El ARN se separa por tamaño en un gel, se transfiere a una membrana y se hibrida "
     "con una sonda marcada del gen de interés.",
     "Ver tamaño e integridad del transcrito de un gen; histórico (1977).",
     "Un gen a la vez, mucho ARN, poco sensible y laborioso.",
     "Microgramos de ARN por carril.",
     "Densitometría de la banda contra un control de carga (ARNr 28S).",
     ""),
    ("Por hibridación y PCR", "RT-PCR semicuantitativo",
     "Retrotranscripción y PCR de punto final; se compara la intensidad de la banda en "
     "gel contra un gen control (β-actina).",
     "Comprobaciones rápidas de presencia/ausencia (1989).",
     "Mide en la meseta de la PCR: poco cuantitativo.",
     "Pocos genes.",
     "Densitometría del gel normalizada al control.",
     ""),
    ("Etiquetas y extremos", "Differential display e hibridación sustractiva",
     "Differential display (1992): RT-PCR con primers arbitrarios y comparación de bandas "
     "entre muestras. Hibridación sustractiva (1996): se restan los cDNA comunes a dos "
     "muestras y quedan los específicos.",
     "Histórico: primeras búsquedas de genes que cambian sin saber cuáles.",
     "Muchos falsos positivos; semicuantitativos.",
     "Decenas a cientos de bandas o clonas.",
     "Clonar y secuenciar las bandas diferenciales.",
     ""),
    # ------------------------------------------------- hibridación y PCR
    ("Por hibridación y PCR", "RT-qPCR",
     "Retrotranscripción y PCR cuantitativa de unos pocos genes elegidos; se mide el "
     "ciclo en que la fluorescencia cruza un umbral (Cq).",
     "Validar unos cuantos genes de un RNA-seq, diagnóstico, muestras muy numerosas.",
     "Solo genes que ya conoces; depende de genes de referencia estables y de la "
     "eficiencia de cada par de primers.",
     "≥ 3 réplicas biológicas y 2-3 técnicas; eficiencia 90-110 %; ΔΔCq con ≥ 2 genes "
     "de referencia validados.",
     "ΔΔCq (Livak) o modelos con eficiencia (Pfaffl); reportar según MIQE.",
     "BUS09"),
    ("Por hibridación y PCR", "Microarreglos de expresión",
     "Miles de sondas (cDNA de 0.6-2.5 kb u oligos de 25-50 nt) fijas en una superficie; "
     "el cDNA marcado con fluorescencia hibrida con su sonda y la intensidad estima la "
     "abundancia.",
     "Organismos con arreglo comercial y preguntas de genes conocidos; hoy casi "
     "reemplazados por RNA-seq.",
     "Solo mide lo que tiene sonda; saturación arriba y ruido de fondo abajo (rango "
     "dinámico ~10³ contra ~10^5 del RNA-seq); hibridación cruzada.",
     "Una muestra por arreglo (o dos colores).",
     "RMA (fondo, normalización por cuantiles, resumen) → limma.",
     "SCN95 SHA96 WAN09"),
    ("Por hibridación y PCR", "NanoString nCounter",
     "Sondas con un código de barras de colores que se cuentan directamente, sin "
     "retrotranscripción ni amplificación.",
     "Paneles de 50-800 genes, muestras FFPE, clínica.",
     "Solo el panel elegido.",
     "100 ng de ARN, incluso degradado.",
     "nSolver / NanoStringNorm; normalización con controles positivos y genes de "
     "referencia.",
     "GEI08"),
    # ------------------------------------------------- etiquetas (pre-NGS)
    ("Etiquetas y extremos", "SAGE",
     "Se corta una etiqueta corta (10-14 pb) de cada transcrito, se concatenan y se "
     "secuencian por Sanger; contar etiquetas = contar transcritos.",
     "Histórico: la primera medición digital del transcriptoma (1995).",
     "Etiquetas cortas difíciles de asignar; caro por etiqueta.",
     "Decenas de miles de etiquetas por muestra.",
     "Conteo de etiquetas y pruebas de proporciones.",
     "VEL95"),
    ("Etiquetas y extremos", "CAGE",
     "Captura del extremo 5′ con caperuza (cap) del ARNm: marca el sitio exacto de "
     "inicio de la transcripción.",
     "Mapear promotores y sitios de inicio (TSS), promotores alternativos, "
     "potenciadores (eRNA).",
     "No cuantifica el cuerpo del gen ni isoformas internas.",
     "5-20 M lecturas.",
     "Agrupar TSS en clusters (CAGEr, paraclu) → DE por cluster.",
     "SHI03"),
    ("Etiquetas y extremos", "3′ tag-seq (QuantSeq, BRB-seq, DRUG-seq)",
     "Una sola lectura cerca del extremo 3′ de cada ARNm; con códigos de barras desde "
     "la retrotranscripción se juntan cientos de muestras.",
     "Cribados, series grandes, cuando solo importa el nivel de cada gen.",
     "Sin isoformas ni splicing; requiere buena anotación del 3′.",
     "3-10 M lecturas por muestra; SE 75.",
     "STAR/Salmon → cuentas (sin corrección por longitud) → DESeq2/edgeR.",
     "MOL14 ALP19"),
    # ------------------------------------------------- RNA-seq bulk
    ("RNA-seq de tejido (bulk)", "mRNA-seq con selección poli(A)",
     "Oligo-dT captura el ARN poliadenilado; fragmentación, cDNA con hexámeros, "
     "adaptadores, PCR y secuenciación corta.",
     "Expresión diferencial de genes codificantes con ARN íntegro.",
     "Pierde ARN sin cola; sesgo 3′ con ARN degradado (RIN < 7).",
     "10-30 M lecturas para genes (ENCODE: 30 M alineadas); 40-100 M para isoformas.",
     "QC → STAR/HISAT2 + featureCounts o Salmon → DESeq2/edgeR/limma.",
     "MOR08 CON16 ENC"),
    ("RNA-seq de tejido (bulk)", "ARN total con ribodepleción",
     "Se eliminan los ARNr con sondas (RNasa H o captura) y se secuencia el resto.",
     "FFPE y ARN degradado, lncRNA, ARN sin cola, bacterias, intrones (pre-ARNm).",
     "Más lecturas intrónicas; hace falta más profundidad.",
     "30-60 M lecturas; casi siempre con hebra.",
     "Igual que poli(A); se puede contar intrones (actividad transcripcional).",
     "ZHA14 CON16"),
    ("RNA-seq de tejido (bulk)", "Paneles dirigidos y captura (RNA Exome)",
     "Sondas de hibridación enriquecen exones de genes elegidos o de todo el "
     "exoma codificante.",
     "FFPE muy degradado, fusiones génicas en clínica.",
     "Solo lo que capturan las sondas; la eficiencia de captura varía.",
     "10-30 M lecturas.",
     "Igual que bulk; para fusiones STAR-Fusion / Arriba.",
     "STA19"),
    ("RNA-seq de tejido (bulk)", "small RNA-seq",
     "Ligación de adaptadores a extremos 3′-OH/5′-P y selección de tamaño (18-34 nt).",
     "miRNA, piRNA, fragmentos de tRNA; biofluidos.",
     "Sesgo de ligación por secuencia; no mide ARNm.",
     "2-10 M lecturas; SE 50.",
     "cutadapt → miRDeep2 / miRBase → DESeq2/edgeR.",
     "CON16 FRI12"),
    ("RNA-seq de tejido (bulk)", "Dual RNA-seq",
     "Se secuencia a la vez el ARN del huésped y del patógeno en la misma muestra.",
     "Infección: qué hace cada uno durante la interacción.",
     "El patógeno suele ser < 5 % de las lecturas: hace falta mucha profundidad y "
     "ribodepleción (las bacterias no tienen cola poli(A)).",
     "50-200 M lecturas.",
     "Alinear a un genoma combinado y analizar cada organismo por separado.",
     "WES12"),
    ("RNA-seq de tejido (bulk)", "Metatranscriptómica",
     "ARN total de una comunidad (microbiota, suelo) con ribodepleción.",
     "Qué genes y vías expresa una comunidad, no solo quién está.",
     "Sin un solo genoma de referencia; asignación taxonómica difícil.",
     "≥ 30 M lecturas por muestra.",
     "Ensamblaje o mapeo a catálogos de genes (HUMAnN) → abundancias.",
     "STA19"),
    # ------------------------------------------------- célula única
    ("Célula única y espacial", "scRNA-seq en gotas (10x Chromium 3′/5′)",
     "Cada célula entra en una gota con una perla de código de barras; cada molécula "
     "recibe un UMI.",
     "Composición y estados celulares, tipos raros, trayectorias.",
     "Captura ~10-50 % de las moléculas, sesgo 3′, dobletes, ARN ambiental.",
     "≥ 20 000 lecturas por célula; 5 000-10 000 células por canal.",
     "Cell Ranger/STARsolo → QC (genes, UMIs, % mito) → normalización → clustering → "
     "anotación → DE por pseudobulk.",
     "ZHE17 LUE19 SQU21"),
    ("Célula única y espacial", "Smart-seq2 / Smart-seq3",
     "Una célula por pozo; cDNA de longitud completa con template switching.",
     "Pocas células muy bien caracterizadas; isoformas y variantes en célula única.",
     "Pocas células; Smart-seq2 sin UMIs.",
     "~1 M lecturas por célula.",
     "STAR/Salmon por célula → mismo flujo que gotas.",
     "PIC14"),
    ("Célula única y espacial", "snRNA-seq (núcleos)",
     "Se aíslan núcleos, no células: funciona con tejido congelado.",
     "Cerebro, músculo, grasa, biobancos.",
     "Más intrones; no ve el ARN citoplasmático.",
     "Igual que gotas; contar intrones.",
     "Cell Ranger con --include-introns.",
     "LUE19"),
    ("Célula única y espacial", "Espacial por captura (Visium, Slide-seq, Stereo-seq)",
     "El corte de tejido se apoya sobre puntos con código de posición que capturan "
     "el ARN.",
     "Dónde se expresa cada gen; nichos, gradientes.",
     "Cada punto de Visium (55 µm) mezcla 1-10 células.",
     "~50 000 lecturas por punto.",
     "Space Ranger → genes espacialmente variables → deconvolución (cell2location).",
     "STH16"),
    ("Célula única y espacial", "Espacial por imagen (MERFISH, seqFISH, Xenium)",
     "Sondas de hibridación leídas en rondas de microscopía: posición subcelular de "
     "cada molécula.",
     "Resolución de célula única y subcelular en el tejido.",
     "Panel de cientos a miles de genes elegidos.",
     "Cientos de genes, millones de moléculas.",
     "Segmentación de células → matriz célula × gen → análisis tipo célula única.",
     "CHN15"),
    # ------------------------------------------------- lecturas largas
    ("Lecturas largas", "PacBio Iso-Seq (HiFi)",
     "cDNA completo leído en círculo muchas veces: lecturas muy exactas de 1-10 kb.",
     "Catálogo de isoformas completas, anotación de genomas nuevos.",
     "Menos lecturas por dólar; cuantificación menos precisa que la lectura corta.",
     "Millones de lecturas por celda SMRT.",
     "IsoSeq3 → SQANTI3 → cuantificación por isoforma.",
     "GOR15"),
    ("Lecturas largas", "Nanopore cDNA y ARN directo",
     "El ARN (o cDNA) pasa por un nanoporo y la corriente revela la secuencia; ARN "
     "directo sin retrotranscripción ni PCR.",
     "Isoformas, longitud de la cola poli(A), modificaciones (m6A) en ARN directo.",
     "Tasa de error mayor; ARN directo necesita mucho material.",
     "1-10 M lecturas.",
     "minimap2 → bambu/FLAIR/IsoQuant → DE por isoforma.",
     "GAR18"),
    # ------------------------------------------------- dinámica
    ("Dinámica y traducción", "ARN naciente (GRO-seq, PRO-seq)",
     "Run-on nuclear con nucleótidos marcados: solo el ARN que la Pol II está "
     "sintetizando en ese momento.",
     "Respuestas transcripcionales rápidas (minutos), pausa de la Pol II, eRNA.",
     "Muchas células y técnica laboriosa.",
     "20-50 M lecturas.",
     "Densidad de Pol II por gen, índice de pausa.",
     "COR08 KWA13"),
    ("Dinámica y traducción", "Marcaje metabólico (4sU, SLAM-seq)",
     "4-tiouridina se incorpora al ARN nuevo; la alquilación hace que se lea como C: "
     "se distingue el ARN nuevo del viejo.",
     "Síntesis y degradación (vida media) de cada ARN.",
     "El 4sU a dosis altas es tóxico.",
     "20-50 M lecturas.",
     "Conteo de conversiones T>C (SLAMdunk, GRAND-SLAM).",
     "HER17"),
    ("Dinámica y traducción", "Ribo-seq (perfil de ribosomas)",
     "Se digiere con nucleasa y se secuencian los fragmentos de ~30 nt protegidos "
     "por ribosomas.",
     "Qué se está traduciendo, eficiencia de traducción, ORF nuevos.",
     "Técnica delicada; hace falta un RNA-seq en paralelo para la eficiencia.",
     "20-50 M lecturas.",
     "Periodicidad de 3 nt (RiboWaltz) → eficiencia de traducción (Ribo/RNA).",
     "ING09"),
    ("Dinámica y traducción", "CLIP-seq (HITS-CLIP, iCLIP, eCLIP)",
     "Luz UV entrecruza proteína y ARN; se inmunoprecipita la proteína y se secuencia "
     "el ARN unido.",
     "Dónde se une una proteína de unión a ARN.",
     "Necesita buen anticuerpo y control (input).",
     "10-30 M lecturas.",
     "Picos de unión (CLIPper, PureCLIP) → motivos.",
     "ULE03"),
]

CATEGORIAS = list(dict.fromkeys(m[0] for m in METODOS))


def ficha_metodo(m):
    cat, nombre, principio, cuando, limites, datos_t, analisis, fuentes = m
    return [
        f"<titulo!>{nombre}</>   <tenue>{cat}</>",
        "",
        f"<agua!>Principio.</> {principio}",
        "",
        f"<bien!>Cuándo usarlo.</> {cuando}",
        "",
        f"<mal!>Límites.</> {limites}",
        "",
        f"<titulo!>Números típicos.</> {datos_t}",
        "",
        f"<agua!>Análisis.</> {analisis}",
        "",
        f"<tenue>Fuente: {cita(*fuentes.split())}</>",
    ]


# --------------------------------------------------------------- manual
# clave -> (título, sección, líneas)
MANUAL = {
    # ============================================================== FUNDAMENTOS
    "f_transcriptoma": ("1 · ¿Qué es el transcriptoma?", "Fundamentos", [
        "<titulo!>Transcriptómica</>: estudia el conjunto completo de ARN (transcritos) que se "
        "expresan en una célula, tejido u organismo <titulo>en un momento y condición "
        "determinados</>.",
        "",
        "  Genoma       → todo el ADN (instrucciones). Humano: ~3.2 Gb, ~20 000 genes;",
        "                 menos del 2 % codifica proteína.",
        "  Transcriptoma → lo que se transcribe en esa condición.",
        "  Proteoma     → las proteínas expresadas en esa condición.",
        "",
        "Quién transcribe qué:",
        "  <agua>Pol I</>   ARNr 18S / 28S",
        "  <agua>Pol II</>  ARNm, lncRNA, miRNA",
        "  <agua>Pol III</> ARNt, ARNr 5S, ARN pequeños",
        "",
        "El ARN total contiene distintas clases (ARNr, ARNm, sncRNA como miRNA, lncRNA): "
        "la estrategia de enriquecimiento depende del ARN que quieras estudiar.",
    ]),
    "f_regulacion": ("2 · Regulación de la expresión génica", "Fundamentos", [
        "Lo que mide un RNA-seq es el resultado de varias capas de regulación:",
        "",
        "<titulo!>Transcripcional</>",
        "  • Elementos en <titulo>cis</>: promotores, enhancers, silenciadores (expresión "
        "específica de tejido, tiempo o estímulo).",
        "  • Elementos en <titulo>trans</>: factores de transcripción y otras proteínas reguladoras.",
        "<titulo!>Postranscripcional</>",
        "  • <titulo>Splicing alternativo</>: un gen → varias isoformas (en Drosophila hay genes "
        "con más de 20 transcritos; en humano la mayoría de los genes codificantes).",
        "  • <titulo>Estabilidad del ARNm</>: regiones ricas en AU (ARE), tristetraprolina (TTP), "
        "desadenilasa CCR4-CAF, vías de MAPK.",
        "  • <titulo>miRNA</>: Pol II → pri-miRNA → DROSHA → pre-miRNA → DICER → 21-25 nt; "
        "degradan el ARNm blanco o inhiben su traducción.",
        "  • <titulo>lncRNA</>: antisentido que bloquean el inicio, señuelos de factores, "
        "estabilizan o degradan ARNm (STAU1), regulan splicing, secuestran miRNA.",
        "<titulo!>Epigenética</>",
        "  • Metilación del ADN (islas CpG de genes housekeeping casi siempre sin metilar).",
        "  • Modificaciones de histonas (acetilación, metilación, fosforilación) y "
        "remodelación de la cromatina: escritores, lectores y borradores.",
        "",
        "Por eso un experimento de transcriptómica puede preguntar por genes, isoformas, "
        "lncRNA o miRNA: cada capa pide una biblioteca distinta.",
    ]),
    "f_medir": ("3 · ¿Por qué medir la expresión génica?", "Fundamentos", [
        "La expresión génica es una <titulo>fotografía</> del estado molecular de la célula en "
        "una condición: cómo responde a un estímulo.",
        "",
        "El objetivo no es solo saber cuánto se expresa un gen, sino <titulo>cómo cambia</> y "
        "qué significado biológico tiene ese cambio.",
        "",
        "Preguntas que hay que hacerse siempre:",
        "  • ¿Un cambio en el perfil de expresión indica que algo está sucediendo?",
        "  • ¿Los transcritos más abundantes son los más importantes?",
        "  • ¿Los niveles de ARN corresponden a los niveles de proteína? (No siempre: hay "
        "regulación de la traducción y de la degradación de proteínas.)",
        "",
        "Flujo general: extracción de ARN total → síntesis de cDNA → análisis del cDNA "
        "(genes específicos o transcriptoma).",
    ]),
    "f_historia": ("4 · De un gen al transcriptoma", "Fundamentos", [
        "<titulo!>Genes individuales</>",
        "  1977  Northern blot",
        "  1989  RT-PCR semicuantitativo (gel contra un control como β-actina)",
        "        RT-PCR en tiempo real (RT-qPCR): fold change relativo",
        "<titulo!>Expresión masiva, inicios</>",
        "  1992  Differential display",
        "  1995  SAGE (etiquetas) y macroarreglos de ADN",
        "  1996  Hibridación sustractiva; microarreglos (Shalon, Smith y Brown)",
        "<titulo!>Transcriptómica</>",
        "  1996  Microarreglos de cDNA u oligonucleótidos (~10 000 sondas por cm²)",
        "  2006  Secuenciación masiva con 454 (Roche)",
        "  2008  Primeros RNA-seq: Denoeud (vid, Solexa 32 nt), Mortazavi (ratón, 32 nt), "
        "Nagalakshmi (levadura, Illumina 35 nt)",
        "  2010  DESeq (Anders & Huber): expresión diferencial de cuentas",
        "",
        "«Con la transcriptómica podemos perder resolución, pero ganamos en perspectiva.»",
    ]),
    "f_microarreglos": ("5 · Microarreglos", "Fundamentos", [
        "Un conjunto ordenado de sondas de secuencia conocida sobre una superficie con "
        "carga positiva (vidrio, plástico, silicio); el ADN tiene carga negativa.",
        "",
        "  • Sondas de <titulo>cDNA</>: genes conocidos (GenBank), largas (0.6-2.5 kb).",
        "  • Sondas de <titulo>oligonucleótidos</>: cortas (25-50 bases).",
        "",
        "Flujo: aislar ARN de las muestras A y B → cDNA marcado con fluoróforos (p. ej. rojo y "
        "verde) → hibridar en el arreglo → escanear: <mal>rojo</> A > B, <bien>verde</> B > A, "
        "<titulo>amarillo</> A = B.",
        "",
        "Aplicaciones: expresión génica, mutaciones, SNPs, splicing (con oligos especiales).",
        f"<tenue>Fuente: {cita('SHA96')}</>",
    ]),
    "f_comparacion": ("6 · Microarreglos vs RNA-seq", "Fundamentos", [
        "                         Microarreglos    RNA-seq",
        "  Principio              hibridación      secuenciación",
        "  De novo (sin genoma)   no               sí",
        "  Isoformas              limitado         sí",
        "  Genes nuevos           no               sí",
        "  Específico de hebra    no               sí",
        "  Reproducible           sí               sí",
        "  Costo                  medio            alto (equipo de cómputo)",
        "  Complejidad de análisis medio           alto",
        "",
        "<bien>Microarreglos</>: protocolo y análisis sencillos, menos almacenamiento, barato si "
        "ya existe un buen arreglo. <mal>Pero</>: hibridación cruzada, solo ves lo que tiene "
        "sonda, menor rango dinámico (lo bajo se confunde con el fondo, lo alto se satura).",
        "<bien>RNA-seq</>: alta sensibilidad y rango dinámico, sin hibridación cruzada, descubre "
        "transcritos e isoformas, sirve sin genoma (de novo). <mal>Pero</>: más complejidad "
        "bioinformática, datos y cómputo.",
    ]),
    "f_rnaseq": ("7 · ¿Qué es y para qué sirve el RNA-seq?", "Fundamentos", [
        "Secuenciar todos los transcritos de una muestra con secuenciación masiva (NGS).",
        "",
        "  1. Extraer el ARN total (ARNm, sncRNA como miRNA, lncRNA, ARNr).",
        "  2. Sintetizar cDNA y construir bibliotecas.",
        "  3. Secuenciar: millones de lecturas cortas de fragmentos de cDNA.",
        "",
        "Aplicaciones:",
        "  • Descubrir genes codificantes y no codificantes (mapeo a referencia o de novo).",
        "  • Anotar genomas: corregir modelos de genes, encontrar genes no predichos.",
        "  • Splicing alternativo: isoformas, exones alternativos, exon skipping.",
        "  • Mutaciones y SNPs en regiones expresadas.",
        "  • Perfiles de expresión (atlas transcripcionales); comparar tejidos, etapas "
        "o condiciones.",
        "  • Genes expresados diferencialmente.",
        "",
        "Perspectivas: más rendimiento y menor costo, integración de lectura corta y larga, "
        "célula única, métodos reproducibles.",
    ]),
    "f_plataformas": ("8 · Plataformas de secuenciación", "Fundamentos", [
        "Plataformas vistas en clase: Ion Torrent · 454/FLX+ · MiSeq · HiSeq/NextSeq/NovaSeq "
        "(Illumina) · PacBio · Nanopore.",
        "",
        "  <agua>Illumina</>   síntesis con terminadores reversibles; lecturas cortas "
        "(50-300 nt), muy exactas, cientos de millones a miles de millones por corrida. "
        "MiSeq: pocas muestras / amplicones; NextSeq: medianas; NovaSeq: proyectos grandes.",
        "  <agua>Ion Torrent</> detecta el H+ liberado al incorporar un nucleótido; lecturas de "
        "200-600 nt; errores en homopolímeros.",
        "  <agua>454</>         pirosecuenciación; lecturas largas para su época; descontinuada.",
        "  <agua>PacBio</>      molécula única en tiempo real; lecturas largas (típicamente "
        "hasta 4.5-5 kb); HiFi muy exactas.",
        "  <agua>Nanopore</>    corriente iónica en un nanoporo; lecturas muy largas (20-30 kb "
        "o mucho más), ARN directo.",
        "",
        "Tercera generación = secuenciación de molécula única. La tasa de error de ~16 % "
        "corresponde a las primeras versiones; las actuales son mucho menores.",
        f"<tenue>Fuente: {cita('STA19', 'GOO16')}</>",
    ]),
    "f_extraccion": ("9 · Extracción y calidad del ARN", "Fundamentos", [
        "Aislamiento de ARN total (célula, tejido animal o vegetal):",
        "  <titulo>Homogenización</> → <titulo>Lisis</> → <titulo>Separación</> → <titulo>Precipitación</>",
        "",
        "Antes de medir expresión hay que garantizar que el ARN sea <titulo!>íntegro, puro y libre "
        "de ADN</> contaminante.",
        "",
        "  • <agua>Electroforesis</>: bandas nítidas de ARNr (28S/18S en animal, 26S/18S en "
        "planta). Barrido = degradación; banda arriba = ADN genómico.",
        "  • <agua>Espectrofotometría</>: en ARN puro A260/A280 ≈ 2.0 (si baja de 1.8: proteína) y "
        "A260/A230 ≈ 2.0-2.2 (si baja: sales, fenol, guanidina, carbohidratos).",
        "  • <agua>Bioanalizador</> (microfluidos): electroferograma y <titulo>RIN</> de 0 "
        "(degradado) a 10 (intacto). Arriba de 8 se considera adecuado para RNA-seq.",
    ]),
    # ===================================================== DISEÑO
    "pregunta": ("11 · La pregunta manda", "Diseño", [
        "Todo diseño empieza por escribir la pregunta en una línea: <titulo>qué</> "
        "se compara, <titulo>en qué</> (organismo, tejido, tipo celular) y <titulo>qué "
        "se mide</> (nivel de gen, isoforma, splicing, miRNA, célula única, ubicación).",
        "",
        "La pregunta decide la biblioteca, la lectura, la profundidad y el análisis:",
        "  • ¿Cuánto cambia cada gen? → bulk poli(A) o 3′ tag, SE, 10-30 M.",
        "  • ¿Qué isoformas/exones? → PE 2×100-150, 40-100 M, o lecturas largas.",
        "  • ¿lncRNA, antisentido? → ARN total ribodepletado CON hebra.",
        "  • ¿miRNA? → small RNA-seq.",
        "  • ¿Qué tipo celular cambia? → célula única con varios donantes.",
        "  • ¿Dónde en el tejido? → espacial.",
        "  • ¿Síntesis o traducción? → ARN naciente, 4sU, Ribo-seq.",
        "",
        "Define también la unidad experimental: lo que recibe el tratamiento de forma "
        "independiente (un ratón, un paciente, un cultivo sembrado por separado). Esa "
        "es tu réplica.",
        f"<tenue>Fuente: {cita('CON16', 'AUE10')}</>",
    ]),
    "replicas": ("12 · Réplicas biológicas y técnicas", "Diseño", [
        "<titulo!>Réplica biológica</>: otra unidad experimental independiente (otro "
        "ratón, otro paciente, otro cultivo sembrado y tratado por separado). Captura "
        "la variación que importa para generalizar.",
        "<titulo!>Réplica técnica</>: la misma muestra medida otra vez. En RNA-seq la "
        "variación técnica es casi Poisson y pequeña frente a la biológica (Marioni "
        "2008): casi nunca vale la pena.",
        "",
        "¿Cuántas?",
        "  • Mínimo absoluto: 3 por grupo (sin réplicas no hay valor p válido).",
        "  • Schurch 2016 (48 réplicas de levadura): con 3 se detecta solo el 20-40 % "
        "de los genes DE; recomienda <bien!>≥ 6</>, y <bien!>≥ 12</> si importan los "
        "cambios pequeños.",
        "  • Humanos y tejidos varían más que líneas celulares: más réplicas.",
        "",
        "<mal!>Pseudoreplicación</>: tratar como independientes cosas que no lo son "
        "(pozos de un mismo cultivo, células de un mismo donante, réplicas técnicas). "
        "Encoge la varianza y fabrica falsos positivos.",
        f"<tenue>Fuente: {cita('SCH16', 'MAR08', 'CON16', 'SQU21')}</>",
    ]),
    "profundidad": ("13 · Profundidad de secuenciación", "Diseño", [
        "Más lecturas mejoran la medición de genes poco expresados, pero con "
        "rendimientos decrecientes.",
        "",
        "Liu 2014 (MCF7, 7 réplicas): pasado ~10 M lecturas casi no se ganan genes DE; "
        "pasar de 2 a 3 réplicas sí (+35 %).",
        "",
        "Guía práctica (lecturas por muestra):",
        "  • 3′ tag-seq: 3-10 M · small RNA: 2-10 M",
        "  • Genes, organismo bien anotado: 10-30 M (ENCODE pide 30 M alineadas)",
        "  • lncRNA, genes poco expresados: 40-60 M",
        "  • Isoformas y splicing: 50-100 M, pareadas",
        "  • De novo: 30-60 M pareadas por muestra",
        "  • Célula única: ≥ 20 000 lecturas por célula",
        "",
        "Una curva de saturación (submuestrear lecturas y contar genes detectados) "
        "dice si más profundidad ayudaría.",
        f"<tenue>Fuente: {cita('LIU14', 'CON16', 'ENC', 'ZHE17')}</>",
    ]),
    "potencia": ("14 · Potencia y tamaño de muestra", "Diseño", [
        "La <titulo>potencia</> es la probabilidad de detectar un cambio real. Depende "
        "de: tamaño del efecto (fold change), número de réplicas, variación biológica "
        "(dispersión), cuentas del gen (profundidad × expresión) y el umbral (FDR).",
        "",
        "Conesa 2016 (gen con 70 lecturas, α 5 %), potencia según réplicas 3 / 5 / 10:",
        "  cambio 1.25×:  17 % /  25 % /  44 %",
        "  cambio 1.5× :  43 % /  64 % /  91 %",
        "  cambio 2×   :  87 % /  98 % / 100 %",
        "",
        "Herramientas: RNASeqPower, Scotty, PROPER, ssizeRNA. Usa la dispersión de un "
        "piloto o de datos públicos parecidos (mismo tejido y especie).",
        "",
        "En la mesa de diseño el juego te muestra una potencia aproximada (no en "
        "Difícil).",
        f"<tenue>Fuente: {cita('CON16', 'HAR13', 'CHI14')}</>",
    ]),
    "lotes": ("15 · Efectos de lote", "Diseño", [
        "Un <titulo>lote</> es todo lo que se procesa junto: día de extracción, kit, "
        "persona, corrida de secuenciación, carril. Cada lote deja una huella en la "
        "expresión de miles de genes.",
        "",
        "Si los lotes coinciden con los grupos, el lote se hace pasar por biología "
        "(<mal!>confusión</>): ningún método lo arregla después.",
        "",
        "  <mal!>MAL</>     lunes: C C C C C C   martes: G G G G G G",
        "  <bien!>BIEN</>    lunes: C G G C C G   martes: G C G C C G",
        "",
        "Reglas:",
        "  1. Bloquea: cada lote con muestras de todos los grupos, en igual número.",
        "  2. Aleatoriza el orden dentro de cada lote.",
        "  3. Anota TODO (fecha, kit, operador, carril) en la hoja de muestras.",
        "  4. Pon el lote en la fórmula: ~ lote + condición.",
        "  5. Mira la PCA coloreada por lote antes de confiar en un resultado.",
        "Si no conoces los lotes: SVA o RUVSeq estiman factores ocultos. ComBat-seq "
        "corrige las cuentas (para visualizar; para la prueba es mejor la fórmula).",
        f"<tenue>Fuente: {cita('LEE10', 'AUE10', 'LEK07', 'RIS14', 'ZHN20')}</>",
    ]),
    "aleatorizar": ("16 · Aleatorizar y bloquear", "Diseño", [
        "Los tres principios de Fisher que Auer & Doerge 2010 llevaron al RNA-seq:",
        "  <titulo!>Réplica</>: varias unidades por grupo para estimar la variación.",
        "  <titulo!>Aleatorización</>: el azar decide qué unidad recibe qué tratamiento "
        "y en qué orden se procesa. Protege de sesgos que no conoces.",
        "  <titulo!>Bloqueo</>: agrupar unidades parecidas (mismo día, misma camada, "
        "mismo paciente) y comparar dentro del bloque.",
        "",
        "En secuenciación: con códigos de barras (multiplexado) todas las muestras van "
        "juntas en cada carril; si usas varios carriles, cada muestra en todos (o un "
        "diseño balanceado). Así el carril no se confunde con nada.",
        f"<tenue>Fuente: {cita('AUE10', 'CON16')}</>",
    ]),
    "formula": ("17 · La fórmula de diseño", "Diseño", [
        "La fórmula le dice al modelo qué explica la expresión de cada gen. El "
        "<titulo>último término</> es el que se prueba por defecto en DESeq2.",
        "",
        "  ~ condición                  dos o más grupos, nada más",
        "  ~ lote + condición           condición ajustada por lote",
        "  ~ donante + condición        pareado: cada donante su propio control",
        "  ~ genotipo * tratamiento     factorial con interacción",
        "  ~ tiempo (factor) + LRT      ¿cambia en algún momento?",
        "",
        "Reglas:",
        "  • Un factor que es combinación exacta de otros hace la matriz singular "
        "(«model matrix is not full rank»): pasa con lotes confundidos.",
        "  • Cada coeficiente necesita grados de libertad: n − parámetros > 0.",
        "  • Las covariables continuas (edad, RIN) se pueden incluir, centradas.",
        "",
        "Código R (DESeq2):",
        "  dds <- DESeqDataSetFromMatrix(cuentas, colData, design = ~ lote + condicion)",
        "  dds <- DESeq(dds)",
        "  res <- results(dds, contrast = c(\"condicion\", \"trat\", \"ctrl\"), alpha = 0.05)",
        f"<tenue>Fuente: {cita('DESV', 'LOV14')}</>",
    ]),
    "pareado": ("18 · Diseños pareados", "Diseño", [
        "Si cada individuo aporta una muestra de cada condición (tumor y normal; antes "
        "y después), la diferencia se mide dentro del individuo.",
        "",
        "La variación entre personas (genética, edad, dieta) suele ser mayor que el "
        "efecto que buscas; ponerla en el modelo la elimina del error:",
        "  design = ~ paciente + condicion",
        "",
        "Si ignoras el pareo, la variación entre personas queda como ruido y pierdes "
        "potencia. Si además un paciente solo tiene una de las dos muestras, aporta "
        "poco al contraste pero sí a la dispersión.",
        f"<tenue>Fuente: {cita('DESV', 'LOV14')}</>",
    ]),
    "factorial": ("19 · Diseños factoriales e interacción", "Diseño", [
        "Dos factores cruzados (genotipo × tratamiento) dan cuatro grupos.",
        "",
        "  efecto del tratamiento en WT  = WT.trat − WT.ctrl",
        "  efecto del tratamiento en KO  = KO.trat − KO.ctrl",
        "  <titulo!>interacción</>             = (KO.trat − KO.ctrl) − (WT.trat − WT.ctrl)",
        "",
        "  design = ~ genotipo + tratamiento + genotipo:tratamiento",
        "  results(dds, name = \"genotipoKO.tratamientoLPS\")",
        "",
        "Alternativa equivalente: un factor «grupo» con 4 niveles (~ grupo) y el "
        "contraste numérico de la diferencia de diferencias.",
        "",
        "Sin interacción (~ genotipo + tratamiento) supones que el tratamiento hace lo "
        "mismo en ambos genotipos. La interacción necesita más réplicas: es una "
        "diferencia de cuatro medias.",
        f"<tenue>Fuente: {cita('DESV', 'AUE10')}</>",
    ]),
    # ===================================================== LABORATORIO
    "muestreo": ("20 · Toma y conservación de la muestra", "Laboratorio", [
        "El ARN se degrada en minutos (RNasas). Lo que pase entre el animal y el "
        "congelador decide la calidad.",
        "",
        "  • Tiempo de isquemia corto y constante entre muestras (anótalo).",
        "  • Congelar en nitrógeno líquido, o RNAlater (penetra ~5 mm), o TRIzol "
        "directo. Guardar a −80 °C.",
        "  • Misma hora del día para todas (ritmo circadiano), mismo ayuno.",
        "  • Disociación para célula única: rápida y en frío; induce genes de estrés "
        "(FOS, JUN): considera núcleos o disociación en frío.",
        "  • FFPE: fijación estandarizada; cortar el bloque fresco.",
        "  • Hoja de muestras desde el día 1: ID, grupo, sexo, edad, fecha, operador, "
        "lote, RIN… es tu colData.",
        f"<tenue>Fuente: {cita('CON16', 'LUE19', 'VDB17')}</>",
    ]),
    "extraccion": ("21 · Extracción de ARN", "Laboratorio", [
        "Métodos:",
        "  • Fenol-cloroformo (TRIzol): alto rendimiento, conserva ARN pequeños.",
        "  • Columnas de sílice (RNeasy): limpio, pierde < 200 nt salvo kits miRNA.",
        "  • Perlas magnéticas: automatizable.",
        "",
        "Tratamiento con <titulo>DNasa I</> (en columna o después): el ADN genómico "
        "contamina sobre todo bibliotecas de ARN total.",
        "",
        "Trabajo libre de RNasas: guantes, puntas con filtro, superficies limpias, "
        "agua sin nucleasas.",
        "",
        "Extrae todas las muestras con el mismo kit y, si no caben en un día, en "
        "lotes balanceados.",
        f"<tenue>Fuente: {cita('CON16', 'CHO93')}</>",
    ]),
    "calidad_arn": ("22 · Control de calidad del ARN", "Laboratorio", [
        "<titulo!>Cantidad</>: Qubit (fluorescencia, específico de ARN) mejor que "
        "NanoDrop (absorbancia, cuenta ADN y sales).",
        "<titulo!>Pureza</> (NanoDrop): A260/280 ≈ 2.0 (proteína baja); A260/230 > 1.8 "
        "(sin fenol, guanidina ni carbohidratos).",
        "<titulo!>Integridad</> (Bioanalyzer / TapeStation):",
        "  • RIN (1-10) usa los picos 28S/18S y la forma del electroferograma. "
        "Poli(A) pide RIN ≥ 7-8.",
        "  • DV200 = % de fragmentos > 200 nt. Para FFPE el RIN no sirve; DV200 ≥ 30 % "
        "es el mínimo habitual (Illumina), 30-50 %: más entrada.",
        "",
        "Si el RIN difiere sistemáticamente entre grupos, es un lote disfrazado: "
        "considéralo como covariable.",
        f"<tenue>Fuente: {cita('SCR06', 'ILL14', 'CON16')}</>",
    ]),
    "bibliotecas": ("23 · Preparación de bibliotecas", "Laboratorio", [
        "Pasos de una biblioteca típica de Illumina:",
        "  1. Enriquecer: oligo-dT (poli(A)) o eliminar ARNr (ribodepleción).",
        "  2. Fragmentar el ARN (calor + Mg²+) a ~200-500 nt.",
        "  3. Primera hebra de cDNA con hexámeros al azar (sesgo en las primeras "
        "bases: Hansen 2010).",
        "  4. Segunda hebra (con dUTP si es con hebra).",
        "  5. Reparar extremos, cola A, ligar adaptadores con índices (códigos de "
        "barras), UMIs si aplica.",
        "  6. Degradar la hebra con U (UDG) si es con hebra.",
        "  7. PCR de pocos ciclos (los mínimos posibles).",
        "  8. Limpieza y selección de tamaño con perlas.",
        "",
        "Elegir (ver Catálogo): poli(A) · ribodepleción · 3′ tag · small RNA · célula "
        "única · lecturas largas · espacial.",
        "",
        "Spike-ins ERCC: se agregan al ARN (o por número de células) antes de "
        "preparar la biblioteca.",
        f"<tenue>Fuente: {cita('CON16', 'HAN10', 'ZHA14', 'JIA11')}</>",
    ]),
    "hebra": ("24 · Bibliotecas con hebra", "Laboratorio", [
        "Sin hebra, una lectura en una región con genes en ambas hebras es ambigua.",
        "",
        "Método dUTP: la segunda hebra lleva dUTP y se degrada antes del PCR; solo "
        "sobrevive la información de la hebra original (Levin 2010 lo señaló como "
        "el mejor de los evaluados).",
        "",
        "Con dUTP, la lectura 1 es antisentido al ARN: en featureCounts -s 2, en "
        "HTSeq --stranded=reverse, en Salmon libType ISR (lo detecta solo con -l A).",
        "Compruébalo con RSeQC infer_experiment.py: ~90 % o más de un lado.",
        "",
        "Imprescindible para lncRNA antisentido, genes solapados, de novo. Casi "
        "gratis en kits modernos: úsalo siempre que puedas.",
        f"<tenue>Fuente: {cita('LEV10', 'PAR09', 'WAN12')}</>",
    ]),
    "umi": ("25 · UMIs y duplicados", "Laboratorio", [
        "Un <titulo>UMI</> es una secuencia al azar pegada a cada molécula ANTES del "
        "PCR. Dos lecturas con la misma posición y el mismo UMI son copias de PCR; "
        "con distinto UMI son moléculas distintas.",
        "",
        "Sin UMIs, quitar duplicados por coordenadas borra señal real de los genes "
        "muy expresados (Fu 2018): en RNA-seq bulk normal NO se deduplica.",
        "",
        "Útiles con poco material, FFPE, small RNA y célula única (donde son estándar). "
        "Herramienta: UMI-tools (corrige errores de secuencia en el UMI).",
        f"<tenue>Fuente: {cita('KIV12', 'FU18', 'SMI17')}</>",
    ]),
    "spike": ("26 · Spike-ins (ERCC)", "Laboratorio", [
        "92 ARN sintéticos con cola poli(A), de 250-2 000 nt, en concentraciones "
        "conocidas que cubren ~10^6 veces (NIST SRM 2374). Mezclas 1 y 2 con razones "
        "conocidas entre subgrupos.",
        "",
        "Usos:",
        "  • QC: linealidad cuentas vs concentración, límite de detección, exactitud "
        "de los fold changes.",
        "  • Normalización cuando cambia el ARN total por célula (Lovén 2012, MYC): se "
        "agregan en proporción al NÚMERO DE CÉLULAS, no a la masa de ARN.",
        "",
        "En DESeq2: estimateSizeFactors(dds, controlGenes = es_ercc). En RUVSeq: "
        "RUVg con los ERCC como controles negativos.",
        f"<tenue>Fuente: {cita('JIA11', 'LOV12', 'RIS14')}</>",
    ]),
    "secuenciacion": ("27 · Secuenciación", "Laboratorio", [
        "QC de la biblioteca: tamaño (Bioanalyzer, pico ~300-400 pb), concentración "
        "molar (qPCR KAPA); sin dímeros de adaptador.",
        "",
        "Pooling equimolar de todas las muestras indexadas; usar índices dobles "
        "únicos (UDI) para evitar el salto de índices (index hopping).",
        "",
        "Illumina (síntesis con terminadores reversibles): se forman clusters en la "
        "flow cell y en cada ciclo se lee una base. PhiX al 1-5 % como control (más si "
        "la biblioteca es de baja diversidad, p. ej. small RNA o amplicones).",
        "",
        "Planear carriles: lecturas totales = muestras × profundidad / (1 − pérdidas).",
        "Demultiplexar con bcl-convert/bcl2fastq → un FASTQ por muestra (R1, R2).",
        f"<tenue>Fuente: {cita('CON16', 'STA19', 'GOO16')}</>",
    ]),
    "lecturas": ("28 · Tipo y longitud de lectura", "Laboratorio", [
        "  SE 50-75   genes en organismos bien anotados, small RNA, 3′ tag",
        "  PE 2×100   isoformas, splicing, mejor mapeo en regiones repetidas",
        "  PE 2×150   de novo, fusiones, variantes",
        "  Larga      isoformas completas (PacBio/ONT)",
        "",
        "Pareadas: los dos extremos de un mismo fragmento; ayudan a ubicar lecturas "
        "ambiguas y a ver uniones. Para expresión diferencial de genes la ganancia "
        "es pequeña frente a su costo.",
        f"<tenue>Fuente: {cita('CON16')}</>",
    ]),
    # ===================================================== ANÁLISIS
    "qc_lecturas": ("29 · Control de calidad de lecturas", "Análisis", [
        "FastQC por muestra y MultiQC para verlas todas juntas. Qué mirar:",
        "  • Calidad por posición (Phred ≥ 30 = 1 error en 1 000; suele caer al final).",
        "  • Contenido por base: las primeras ~10 bases oscilan por el sesgo de "
        "hexámeros (normal en RNA-seq).",
        "  • Duplicación: ALTA es normal en RNA-seq (genes muy expresados).",
        "  • Secuencias sobrerrepresentadas: adaptadores, ARNr, dímeros.",
        "  • GC por lectura: una segunda joroba sugiere contaminación.",
        "Lo importante: que todas las muestras se parezcan entre sí (Conesa: "
        "descartar las que difieren > 30 %).",
        "",
        "  fastqc -t 8 -o qc/ fastq/*.fastq.gz && multiqc qc/",
        f"<tenue>Fuente: {cita('AND10', 'EWE16', 'CON16', 'HAN10')}</>",
    ]),
    "recorte": ("30 · Recorte de adaptadores y calidad", "Análisis", [
        "Quitar adaptadores (si el fragmento es más corto que la lectura) y extremos "
        "de baja calidad; descartar lecturas muy cortas.",
        "",
        "  fastp -i R1.fq.gz -I R2.fq.gz -o R1.trim.fq.gz -O R2.trim.fq.gz \\",
        "        --detect_adapter_for_pe -q 20 -l 25 -h fastp.html",
        "  cutadapt -a AGATCGGAAGAGC -m 18 -M 30 small.fq.gz   (small RNA)",
        "",
        "Para alineadores con soft-clipping (STAR) o pseudoalineadores, el recorte "
        "agresivo ayuda poco; el de adaptadores sí es necesario en small RNA.",
        f"<tenue>Fuente: {cita('CHE18', 'MAR11', 'CON16')}</>",
    ]),
    "alineamiento": ("31 · Alineamiento y cuantificación", "Análisis", [
        "<titulo!>Contra el genoma</> (con splicing): STAR o HISAT2 → BAM → cuentas por gen "
        "con featureCounts/HTSeq. Permite QC de cobertura y descubrir uniones.",
        "  STAR --runThreadN 8 --genomeDir idx --readFilesIn R1 R2 \\",
        "       --readFilesCommand zcat --outSAMtype BAM SortedByCoordinate \\",
        "       --quantMode GeneCounts",
        "  featureCounts -p --countReadPairs -s 2 -a genes.gtf -o cuentas.txt *.bam",
        "",
        "<titulo!>Contra el transcriptoma</> (pseudoalineamiento): Salmon / kallisto, muy "
        "rápidos; estiman cuentas por transcrito con EM y corrigen sesgos de GC y "
        "posición. Resumir a gen con tximport.",
        "  salmon quant -i idx_con_señuelos -l A -1 R1 -2 R2 --validateMappings \\",
        "       --gcBias --seqBias -o salmon/muestra",
        "",
        "Usa SIEMPRE el mismo genoma y la misma anotación (versión de Ensembl/GENCODE) "
        "para todas las muestras; anótalo en métodos.",
        "Esperado en humano: 70-90 % de lecturas alineadas al genoma.",
        f"<tenue>Fuente: {cita('DOB13', 'KIM19', 'LIA14', 'PAT17', 'BRA16', 'SON15', 'CON16')}</>",
    ]),
    "qc_post": ("32 · Control de calidad después de alinear", "Análisis", [
        "RSeQC, Qualimap, Picard CollectRnaSeqMetrics. Qué mirar:",
        "  • % alineado (70-90 % en humano), % multimapeo.",
        "  • Distribución: exones / intrones / intergénico (poli(A): mayoría exónica; "
        "ARN total: más intrones).",
        "  • Cobertura a lo largo del gen: sesgo 3′ = ARN degradado (sobre todo poli(A)).",
        "  • Hebra (infer_experiment.py) correcta para tu kit.",
        "  • % ARNr y % mitocondrial.",
        "  • Saturación: ¿más lecturas darían más genes?",
        "",
        "Después de contar: correlación entre réplicas (ENCODE: Spearman > 0.9 "
        "isogénicas, > 0.8 entre donantes), PCA, agrupamiento jerárquico.",
        f"<tenue>Fuente: {cita('WAN12', 'OKO16', 'CON16', 'ENC')}</>",
    ]),
    "normalizacion": ("33 · Normalización", "Análisis", [
        "Las cuentas dependen de la profundidad, de la composición de cada "
        "biblioteca y de la longitud del gen.",
        "",
        "<titulo!>Dentro de una muestra</> (comparar genes entre sí): RPKM/FPKM y TPM. TPM "
        "suma lo mismo en todas las muestras; útil para gráficas, NO para modelos de "
        "conteo.",
        "<titulo!>Entre muestras</> (comparar un gen entre condiciones):",
        "  • DESeq2: razón de medianas (factor de tamaño = mediana de cuenta/media "
        "geométrica del gen).",
        "  • edgeR: TMM (media recortada de los log-cocientes).",
        "  • Las dos suponen que la MAYORÍA de los genes no cambia.",
        "  • Si cambia el ARN total por célula: spike-ins (Lovén 2012).",
        "  • Total de cuentas (CPM) falla cuando unos pocos genes acaparan lecturas.",
        "",
        "Para gráficas y PCA: transformación que estabiliza la varianza (vst, rlog) o "
        "log-CPM.",
        f"<tenue>Fuente: {cita('CON16', 'LOV14', 'TMM', 'LOV12')}</>",
    ]),
    "exploracion": ("34 · Exploración: PCA y agrupamiento", "Análisis", [
        "Antes de cualquier prueba:",
        "  vsd <- vst(dds, blind = TRUE)",
        "  plotPCA(vsd, intgroup = c(\"condicion\", \"lote\"))",
        "",
        "Qué buscar:",
        "  • ¿Las réplicas se agrupan por condición?",
        "  • ¿PC1 separa por lote, sexo, RIN o fecha? → covariable en la fórmula.",
        "  • ¿Alguna muestra lejos de todas? → revisar su QC antes de quitarla "
        "(nunca solo porque «no se ve bonita»).",
        "  • Mapa de calor de distancias entre muestras.",
        "",
        "En este juego, la PCA de resultados colorea cada muestra por grupo y le pone "
        "el número de su lote.",
        f"<tenue>Fuente: {cita('DESV', 'CON16')}</>",
    ]),
    "pruebas": ("35 · Expresión diferencial", "Análisis", [
        "Las cuentas son <titulo>binomiales negativas</>: varianza = μ + α·μ². Con 3-6 "
        "réplicas la α de cada gen se estima mal, así que DESeq2, edgeR y limma "
        "comparten información entre genes (shrinkage / bayes empírico).",
        "",
        "  • DESeq2: Wald para un coeficiente; LRT para comparar modelos (tiempo, >2 "
        "grupos). Detecta valores atípicos con la distancia de Cook.",
        "  • edgeR: QL F-test (glmQLFit/glmQLFTest).",
        "  • limma-voom: log-CPM con pesos; rápido, muy bueno con n ≥ 3 y diseños "
        "complejos (y con efectos aleatorios vía duplicateCorrelation/dream).",
        "  • Schurch 2016: con < 12 réplicas, edgeR y DESeq2 son las mejores.",
        "",
        "Evitar: t por gen sin moderar, umbrales de fold change sin estadística, "
        "pruebas sobre FPKM.",
        "",
        "  res <- results(dds, alpha = 0.05)",
        "  res <- lfcShrink(dds, coef = \"condicion_trat_vs_ctrl\", type = \"apeglm\")",
        f"<tenue>Fuente: {cita('LOV14', 'ROB10', 'LAW14', 'SCH16', 'ZHU19')}</>",
    ]),
    "bh": ("36 · Pruebas múltiples y FDR", "Análisis", [
        "Con 20 000 genes y p < 0.05, ~1 000 salen «significativos» aunque nada "
        "cambie.",
        "",
        "  • Bonferroni (p × m): controla la probabilidad de UN falso positivo. "
        "Demasiado estricto para ómicas.",
        "  • <bien!>Benjamini-Hochberg</>: controla la proporción esperada de falsos "
        "positivos entre los significativos (FDR). padj < 0.05 = se espera ≤ 5 % de "
        "falsos en la lista.",
        "",
        "Filtrado independiente (DESeq2 lo hace solo): quitar genes con cuentas bajas "
        "ANTES de corregir aumenta la potencia sin inflar el FDR, porque el filtro no "
        "mira la condición.",
        "",
        "Umbral de fold change: mejor probarlo (results(lfcThreshold = 1)) que "
        "filtrar después.",
        f"<tenue>Fuente: {cita('BH95', 'BOU10', 'DESV')}</>",
    ]),
    "visualizacion": ("37 · Gráficas de resultados", "Análisis", [
        "  • <titulo>MA</> (log2FC vs media de cuentas): los genes con pocas cuentas "
        "tienen fold changes enormes y ruidosos; con apeglm se encogen.",
        "  • <titulo>Volcán</> (log2FC vs −log10 p): a la vez tamaño y certeza.",
        "  • <titulo>Mapa de calor</> de los genes DE (vst, centrado por gen).",
        "  • Cuentas normalizadas de genes individuales por grupo (plotCounts).",
        "",
        "Reporta: número de genes probados, umbral (padj, |log2FC|), dirección, y la "
        "tabla completa como material suplementario.",
        f"<tenue>Fuente: {cita('DESV', 'ZHU19')}</>",
    ]),
    "enriquecimiento": ("38 · Enriquecimiento funcional", "Análisis", [
        "<titulo!>ORA</> (sobre-representación): ¿la lista de genes DE tiene más genes de "
        "una vía de lo esperado? Prueba hipergeométrica. El universo debe ser los "
        "genes PROBADOS, no el genoma. Sesgo: los genes largos se detectan más → "
        "goseq lo corrige.",
        "<titulo!>GSEA</>: ordena TODOS los genes (por estadístico o log2FC encogido) y "
        "busca vías acumuladas en un extremo; no necesita umbral (fgsea, clusterProfiler).",
        "",
        "Bases: GO (proceso, función, componente), KEGG, Reactome, MSigDB Hallmark.",
        "Corrige también por pruebas múltiples entre vías.",
        "Complementos: WGCNA (módulos de coexpresión), deconvolución (CIBERSORTx), "
        "factores de transcripción (DoRothEA/decoupleR).",
        f"<tenue>Fuente: {cita('SUB05', 'YOU10', 'LAN08', 'NEW19')}</>",
    ]),
    "splicing": ("39 · Isoformas y splicing", "Análisis", [
        "Tres niveles:",
        "  • Expresión diferencial de transcritos (DTE): Salmon + DESeq2/edgeR por "
        "transcrito (o swish de fishpond).",
        "  • Uso diferencial de transcritos (DTU): cambia la PROPORCIÓN de isoformas "
        "aunque el total del gen no cambie (DRIMSeq, DEXSeq sobre transcritos).",
        "  • Eventos de splicing: exón saltado, 5′/3′ alternativo, intrón retenido, "
        "exones mutuamente excluyentes (rMATS: ΔPSI; DEXSeq: uso de exones; "
        "LeafCutter: intrones).",
        "",
        "Requisitos: lecturas pareadas largas, 50-100 M, réplicas, alineamiento al "
        "genoma. Validación: RT-PCR con primers en exones flanqueantes.",
        f"<tenue>Fuente: {cita('SHE14', 'AND12', 'CON16')}</>",
    ]),
    "novo": ("40 · Transcriptoma de novo", "Análisis", [
        "Sin genoma de referencia:",
        "  1. Lecturas pareadas, con hebra, de buena calidad; recorte de adaptadores.",
        "  2. Ensamblar con TODAS las muestras juntas (Trinity; normalización in "
        "silico si hay demasiadas lecturas).",
        "  3. Evaluar: BUSCO (genes ortólogos de copia única completos), N50 de "
        "contigs, % de lecturas que vuelven a mapear.",
        "  4. Reducir redundancia (CD-HIT, EvidentialGene) y predecir ORF "
        "(TransDecoder).",
        "  5. Anotar por homología (BLAST/DIAMOND contra UniProt, Pfam, Trinotate).",
        "  6. Cuantificar cada muestra contra el ensamblaje (Salmon) y sumar a nivel "
        "de «gen» de Trinity → DESeq2/edgeR.",
        f"<tenue>Fuente: {cita('GRA11', 'CON16')}</>",
    ]),
    "celula_unica": ("41 · Análisis de célula única", "Análisis", [
        "  1. Cuentas: Cell Ranger / STARsolo / alevin-fry (UMIs por célula).",
        "  2. QC por célula: nº de UMIs, nº de genes, % mitocondrial; dobletes "
        "(scDblFinder); ARN ambiental (SoupX, CellBender).",
        "  3. Normalización (log-normalización o sctransform), genes variables, PCA.",
        "  4. Integración de muestras si hay efecto de lote (Harmony, scVI).",
        "  5. Vecinos → clusters (Leiden) → UMAP (solo para ver).",
        "  6. Anotación con marcadores o referencias.",
        "  7. <bien!>DE entre condiciones: pseudobulk</> — sumar cuentas por tipo celular y "
        "por muestra, y DESeq2/edgeR con las muestras como réplicas (muscat).",
        "  8. Composición: ¿cambia la proporción de un tipo? (propeller, scCODA).",
        "",
        "<mal!>Error clásico</>: Wilcoxon célula contra célula entre condiciones trata miles "
        "de células como réplicas → miles de falsos positivos (Squair 2021).",
        f"<tenue>Fuente: {cita('LUE19', 'SQU21', 'CRO20', 'WOL18', 'HAO21')}</>",
    ]),
    "validacion": ("42 · Validación", "Análisis", [
        "  • RT-qPCR de unos genes DE en muestras nuevas (réplicas biológicas "
        "independientes, no las mismas), siguiendo MIQE.",
        "  • Proteína (western, ELISA, inmunofluorescencia) si la conclusión es "
        "sobre proteína.",
        "  • Funcional: knockdown/sobreexpresión del gen candidato.",
        "  • Reanálisis en datos públicos (GEO, GTEx, TCGA).",
        f"<tenue>Fuente: {cita('BUS09')}</>",
    ]),
    "reproducible": ("43 · Reproducibilidad y depósito", "Análisis", [
        "  • Flujo de trabajo versionado: nf-core/rnaseq (Nextflow) o Snakemake, con "
        "contenedores (Docker/Singularity/conda).",
        "  • Registra versiones de software, genoma y anotación, y los parámetros.",
        "  • Código de análisis en un repositorio (git); sessionInfo() de R.",
        "  • Depósito: FASTQ crudos en SRA/ENA; cuentas y metadatos en GEO o "
        "ArrayExpress, siguiendo MINSEQE (descripción del diseño, protocolos, datos "
        "crudos y procesados, metadatos de cada muestra).",
        "  • Datos humanos: consentimiento y acceso controlado (dbGaP/EGA) si aplica.",
        f"<tenue>Fuente: {cita('EWE20', 'FGED')}</>",
    ]),
    "metodos": ("10 · Mapa de métodos de transcriptómica", "Diseño", [
        "La sección «Catálogo de métodos» de este manual tiene una ficha para cada "
        "tecnología:",
        "",
        "  <agua>Hibridación y PCR</>: RT-qPCR, microarreglos, NanoString",
        "  <agua>Etiquetas</>: SAGE, CAGE, 3′ tag-seq",
        "  <agua>Bulk</>: poli(A), ribodepleción, captura, small RNA, dual, "
        "metatranscriptómica",
        "  <agua>Célula única y espacial</>: gotas, Smart-seq, núcleos, Visium, MERFISH",
        "  <agua>Lecturas largas</>: Iso-Seq, Nanopore",
        "  <agua>Dinámica y traducción</>: GRO/PRO-seq, SLAM-seq, Ribo-seq, CLIP",
        "",
        "Historia corta: Northern → RT-qPCR → microarreglos (1995) y SAGE (1995) → "
        "RNA-seq (2008) → célula única → espacial y lecturas largas.",
        f"<tenue>Fuente: {cita('WAN09', 'STA19', 'MOR08')}</>",
    ]),
}

SECCIONES = ["Fundamentos", "Diseño", "Laboratorio", "Análisis"]


def entradas():
    """Lista (título, contenido, color) en orden de lectura."""
    salida = []
    for sec in SECCIONES:
        del_sec = [(int(t.split(" ")[0]), k, t, l) for k, (t, s, l) in MANUAL.items() if s == sec]
        for _, clave, titulo, lineas in sorted(del_sec):
            salida.append((clave, titulo, lineas, sec))
    return salida


GLOSARIO = [
    ("ARNr", "ARN ribosomal: 80-90 % del ARN total. Se quita por poli(A) o ribodepleción."),
    ("BAM", "Archivo binario con las lecturas alineadas (SAM comprimido)."),
    ("BH / FDR", "Benjamini-Hochberg: controla la tasa de falsos descubrimientos."),
    ("Biblioteca", "El ADN listo para secuenciar: fragmentos con adaptadores e índices."),
    ("cDNA", "ADN complementario: copia del ARN hecha por la retrotranscriptasa."),
    ("Cuenta", "Número de lecturas (o UMIs) asignadas a un gen o transcrito."),
    ("Dispersión (α)", "Varianza extra sobre Poisson: Var = μ + α μ²."),
    ("DV200", "% de fragmentos de ARN de más de 200 nt; integridad para FFPE."),
    ("ERCC", "Spike-ins sintéticos de concentración conocida (NIST)."),
    ("FASTQ", "Archivo de lecturas con su calidad por base (Phred)."),
    ("FFPE", "Tejido fijado en formalina e incluido en parafina."),
    ("Fold change", "Cociente de expresión entre condiciones; se usa log2."),
    ("GTF/GFF", "Archivo de anotación: dónde están genes, exones y transcritos."),
    ("Índice", "Código de barras de la biblioteca para multiplexar muestras."),
    ("Lote", "Grupo de muestras procesadas juntas; deja una huella técnica."),
    ("Multiplexar", "Secuenciar varias muestras juntas distinguidas por índices."),
    ("padj", "Valor p ajustado por pruebas múltiples."),
    ("PE / SE", "Lectura pareada (ambos extremos) / sencilla (un extremo)."),
    ("Phred", "Calidad: Q30 = 1 error en 1 000 bases."),
    ("Pseudobulk", "Suma de cuentas de las células de un tipo por muestra."),
    ("Pseudoreplicación", "Tratar como independientes mediciones que no lo son."),
    ("RIN", "Número de integridad del ARN (1-10), del Bioanalyzer."),
    ("Shrinkage", "Encoger estimaciones ruidosas hacia un valor común."),
    ("Spike-in", "ARN exógeno agregado en cantidad conocida."),
    ("TPM", "Transcritos por millón: normaliza por longitud y profundidad."),
    ("UMI", "Identificador molecular único, puesto antes del PCR."),
    ("vst / rlog", "Transformaciones que estabilizan la varianza para PCA y gráficas."),
]
