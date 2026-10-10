"""Datos del laboratorio explorable: el plano, las estaciones, lo que se
puede investigar en cada caso, métodos de extracción, plataformas de
secuenciación e hipótesis.

Cada caso de casos.py se completa aquí con lo que el jugador descubre
explorando (calendario, congelador, libreta, preguntas al investigador) y con
las opciones del papel de diseño (hipótesis y unidad experimental).
"""

from datos import cita

# ------------------------------------------------------------------ plano
# Cuartos: (nombre, x0, y0, x1, y1) en coordenadas del plano (incluyen muros).
ANCHO, ALTO = 150, 46
CUARTOS = [
    ("OFICINA", 0, 0, 36, 15),
    ("{lugar}", 36, 0, 78, 15),
    ("CUARTO DE QC", 78, 0, 114, 15),
    ("SECUENCIACIÓN", 114, 0, 149, 15),
    ("PASILLO", 0, 15, 149, 21),
    ("BUZÓN", 0, 21, 30, 45),
    ("LABORATORIO HÚMEDO", 30, 21, 96, 45),
    ("BIOINFORMÁTICA", 96, 21, 149, 45),
]
# huecos en los muros (x, y)
PUERTAS = [(x, 15) for x in (17, 18, 56, 57, 95, 96, 131, 132)] + \
          [(x, 21) for x in (14, 15, 62, 63, 122, 123)] + \
          [(36, y) for y in (7, 8)] + [(78, y) for y in (7, 8)] + [(96, y) for y in (32, 33)]

# estación -> (x, y, glifo, color, etiqueta, etapa que habilita o None)
ESTACIONES = {
    "papel":        (6, 4, "▤", "titulo", "papel de diseño", 0),
    "librero":      (6, 8, "▥", "agua", "librero", None),
    "investigador": (20, 10, "☺", "g2", "investigador", None),
    "replica":      (6, 12, "☻", "bien", "Dra. Lazo", None),
    "unidades":     (42, 4, "▦", "g4", "unidades", 1),
    "calendario":   (62, 4, "▣", "titulo", "calendario", None),
    "tecnico":      (38, 13, "☺", "g0", "técnico", None),
    "nanodrop":     (83, 4, "◫", "agua", "NanoDrop", 3),
    "gel":          (99, 4, "▤", "agua", "gel", 3),
    "bioanalizador": (83, 10, "◩", "agua", "Bioanalyzer", 3),
    "secuenciador": (120, 6, "◙", "g3", "secuenciador", 5),
    "buzon":        (8, 30, "≡", "mal", "buzón", 7),
    "campana":      (36, 26, "⌂", "g1", "campana de extracción", 2),
    "congelador":   (70, 26, "*", "agua", "congelador −80 °C", None),
    "kits":         (36, 38, "▥", "g5", "estante de kits", 4),
    "computadora":  (104, 27, "▣", "bien", "computadora", 6),
    "cuaderno":     (104, 37, "▤", "titulo", "cuaderno", None),
}
INICIO = (18, 18)


def _fila(x, y, texto, color):
    """Un mueble de una fila; los espacios de adentro también son mueble, para
    que no se cuele el piso entre las letras o las piezas."""
    return [(x + i, y, ch, color) for i, ch in enumerate(texto)]


# Mobiliario (no se puede caminar encima): (x, y, carácter, color).
_COMUN = (
    # oficina: escritorio, sillas, plantas
    _fila(12, 2, "▄▄▄▄▄▄▄▄▄▄", "oscuro") + _fila(14, 3, "╨  ╨", "tenue")
    + [(1, 1, "♣", "bien"), (34, 1, "♣", "bien"), (34, 13, "♣", "bien")]
    + _fila(26, 13, "▄▄▄", "tenue")
    # cuarto de QC: mesadas
    + _fila(81, 6, "════════════════════════════", "tenue")
    + _fila(81, 12, "════════════════════════════", "tenue")
    + [(109, 2, "◎", "agua"), (111, 2, "◎", "agua")]
    # secuenciación: equipos y rack
    + _fila(130, 3, "▛▀▀▜ ▛▀▀▜", "g3") + _fila(130, 4, "▙▄▄▟ ▙▄▄▟", "g3")
    + _fila(119, 11, "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓", "oscuro")
    + _fila(119, 12, "· servidor de datos ·", "tenue")
    # buzón: sillas y mesita
    + _fila(4, 36, "▄▄▄▄▄▄", "oscuro") + _fila(4, 37, "╨    ╨", "tenue")
    + [(27, 23, "♣", "bien"), (2, 43, "♣", "bien")]
    # laboratorio húmedo: mesadas, tarja, centrífuga, termociclador
    + _fila(34, 30, "══════════════════════════════════════════════════════", "tenue")
    + _fila(34, 34, "══════════════════════════════════════════════════════", "tenue")
    + [(64, 26, "◎", "agua"), (66, 26, "◎", "agua")]
    + _fila(56, 38, "▙▟", "g5") + _fila(80, 38, "╰╯", "agua")
    + _fila(34, 42, "▒▒▒▒▒▒▒▒▒▒▒▒", "oscuro")
    # bioinformática: escritorios con monitores y servidores
    + _fila(122, 26, "▛▜  ▛▜  ▛▜", "agua") + _fila(122, 27, "▀▀▀▀▀▀▀▀▀▀", "oscuro")
    + _fila(122, 36, "▛▜  ▛▜  ▛▜", "agua") + _fila(122, 37, "▀▀▀▀▀▀▀▀▀▀", "oscuro")
    + [(146, y, "▓", "oscuro") for y in range(24, 43)]
)
# lo que hay en el cuarto de unidades depende del lugar
_LUGAR = {
    "bioterio": _fila(48, 8, "▦ ▦ ▦ ▦ ▦ ▦ ▦ ▦", "g4") + _fila(48, 9, "jaulas", "tenue")
                + _fila(66, 11, "▦ ▦ ▦ ▦", "g4"),
    "cultivo": _fila(66, 8, "▛▀▀▀▀▜", "agua") + _fila(66, 9, "▙▄▄▄▄▟", "agua")
               + _fila(66, 10, "incubadora", "tenue")
               + _fila(44, 8, "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀", "g4") + _fila(44, 9, "campana de cultivo", "tenue"),
    "clinica": _fila(66, 8, "▌▌▌▌▌▌", "agua") + _fila(66, 9, "racks −80", "tenue")
               + _fila(50, 11, "▄▄▄▄▄▄", "oscuro"),
    "invernadero": _fila(46, 7, "♣ ♣ ♣ ♣ ♣ ♣", "bien") + _fila(46, 8, "▒▒▒▒▒▒▒▒▒▒▒", "oscuro")
                   + _fila(62, 7, "♣ ♣ ♣ ♣ ♣ ♣", "bien") + _fila(62, 8, "▒▒▒▒▒▒▒▒▒▒▒", "oscuro")
                   + _fila(46, 11, "♣ ♣ ♣ ♣ ♣ ♣", "bien") + _fila(46, 12, "▒▒▒▒▒▒▒▒▒▒▒", "oscuro")
                   + _fila(62, 11, "♣ ♣ ♣ ♣ ♣ ♣", "bien") + _fila(62, 12, "▒▒▒▒▒▒▒▒▒▒▒", "oscuro"),
}


def _seguro(ch):
    """Caracteres que toda terminal dibuja en una celda: ASCII, cajas y bloques.
    Los demás (☺ ◎ ♣ ▣…) a veces salen de una fuente de emoji más ancha
    y tapan la celda de la derecha."""
    return ord(ch) < 0x2500 or 0x2500 <= ord(ch) <= 0x259F or ch in "·−°"


def mobiliario(lugar_clave):
    """Muebles del lugar más una celda vacía (no caminable) a la derecha de cada
    ícono ancho, para que no se encime con el piso, el jugador o una etiqueta."""
    muebles = _COMUN + _LUGAR.get(lugar_clave, [])
    ocupado = {(x, y) for x, y, _ch, _c in muebles}
    iconos = [(x, y, ch) for x, y, ch, _c in muebles] + \
             [(x, y, ch) for x, y, ch, *_r in ESTACIONES.values()]
    huecos = [(x + 1, y, " ", "oscuro") for x, y, ch in iconos
              if not _seguro(ch) and (x + 1, y) not in ocupado]
    return muebles + huecos


ETAPAS = [
    ("Diseño en papel", "papel", "Oficina"),
    ("Unidades experimentales", "unidades", "{lugar}"),
    ("Extracción de ARN", "campana", "Laboratorio húmedo"),
    ("Control de calidad", "nanodrop", "Cuarto de QC"),
    ("Biblioteca", "kits", "Laboratorio húmedo"),
    ("Secuenciación", "secuenciador", "Secuenciación"),
    ("Análisis", "computadora", "Bioinformática"),
    ("Revisión", "buzon", "Buzón"),
]

LUGARES = {
    "bioterio": "BIOTERIO",
    "cultivo": "CUARTO DE CULTIVO",
    "clinica": "BIOBANCO CLÍNICO",
    "invernadero": "INVERNADERO",
}

# ------------------------------------------------------- métodos de extracción
# guarda_pequenos: conserva ARN < 200 nt · celulas: entrega células/núcleos vivos
EXTRACCIONES = {
    "trizol": dict(nombre="TRIzol (fenol-guanidina) + cloroformo", celulas=False,
                   guarda_pequenos=True,
                   texto="Lisis con fenol-tiocianato de guanidina, separación de fases con "
                         "cloroformo y precipitación con isopropanol. Alto rendimiento; "
                         "conserva ARN pequeños.", fuente="CON16"),
    "columna": dict(nombre="Columna de sílice (tipo RNeasy)", celulas=False,
                    guarda_pequenos=False,
                    texto="El ARN se une a la sílice con sal caótropa y etanol; se lava y se "
                          "eluye. Limpio y rápido, pero pierde los ARN < 200 nt.",
                    fuente="CON16"),
    "mirna": dict(nombre="Kit para miRNA / biofluidos", celulas=False, guarda_pequenos=True,
                  texto="Columna con más etanol para retener ARN pequeños; acepta plasma y "
                        "suero. Agregar un spike-in sintético (cel-miR-39).", fuente="CON16"),
    "ffpe": dict(nombre="Kit FFPE (desparafinar + proteinasa K)", celulas=False,
                 guarda_pequenos=False,
                 texto="Desparafina, digiere con proteinasa K y calienta para revertir parte "
                       "de los entrecruzamientos de formalina.", fuente="ILL14"),
    "ctab": dict(nombre="CTAB / kit para plantas", celulas=False, guarda_pequenos=True,
                 texto="El CTAB y el PVP separan polisacáridos y polifenoles, que en plantas "
                       "co-precipitan con el ARN y bajan el A260/230.", fuente="general"),
    "disociacion": dict(nombre="Disociación a célula única (enzimas en frío)", celulas=True,
                        guarda_pequenos=False,
                        texto="Suspensión de células vivas para célula única: rápida y en frío "
                              "para no inducir genes de estrés; filtrar y contar viabilidad.",
                        fuente="LUE19"),
    "nucleos": dict(nombre="Aislamiento de núcleos", celulas=True, guarda_pequenos=False,
                    texto="Para tejido congelado: homogenizar en buffer con inhibidor de "
                          "RNasas, filtrar, lavar, teñir con DAPI y contar.", fuente="LUE19"),
}
ORDEN_EXTRACCIONES = list(EXTRACCIONES)

# --------------------------------------------------------------- plataformas
# lecturas permitidas, M lecturas por corrida, días por corrida, costo por corrida (USD)
PLATAFORMAS = {
    "miseq": dict(nombre="Illumina MiSeq", lecturas=["SE50", "SE75", "PE150"], cap=25,
                  dias=2, corrida=1500,
                  texto="Pocas lecturas por corrida (~25 M): amplicones, pruebas piloto, "
                        "genomas pequeños."),
    "nextseq": dict(nombre="Illumina NextSeq 2000", lecturas=["SE50", "SE75", "PE100", "PE150"],
                    cap=400, dias=2, corrida=4500,
                    texto="Cientos de millones de lecturas: el caballo de batalla para "
                          "RNA-seq de decenas de muestras."),
    "novaseq": dict(nombre="Illumina NovaSeq X", lecturas=["SE50", "PE100", "PE150"],
                    cap=2500, dias=3, corrida=9000,
                    texto="Miles de millones de lecturas: proyectos grandes. Para pocas "
                          "muestras se compra una fracción de carril en un núcleo."),
    "iontorrent": dict(nombre="Ion Torrent (Ion GeneStudio S5)", lecturas=["SE75", "SE50"],
                       cap=80, dias=1, corrida=2200,
                       texto="Detecta H⁺: rápida, lecturas sencillas; errores en "
                             "homopolímeros. Solo lectura sencilla en este juego."),
    "pacbio": dict(nombre="PacBio Revio (HiFi)", lecturas=["LARGA"], cap=30, dias=2,
                   corrida=6000,
                   texto="Lecturas largas y exactas (HiFi): isoformas completas."),
    "nanopore": dict(nombre="Oxford Nanopore PromethION", lecturas=["LARGA"], cap=60, dias=3,
                     corrida=3500,
                     texto="Lecturas muy largas; cDNA o ARN directo (modificaciones)."),
}
ORDEN_PLATAFORMAS = list(PLATAFORMAS)
FUENTE_PLATAFORMAS = cita("STA19", "general")

# ---------------------------------------------------- unidades experimentales
UNIDADES = {
    "bioterio": ["Cada ratón", "Cada jaula de 4 ratones",
                 "Cada pedazo de hígado del mismo ratón", "Cada lectura secuenciada"],
    "cultivo": ["Cada cultivo sembrado y tratado por separado (otro día, otro pase)",
                "Cada pozo de una misma placa tratada a la vez",
                "Cada célula", "Cada réplica técnica de la biblioteca"],
    "clinica": ["Cada paciente o donante", "Cada fragmento de la misma biopsia",
                "Cada célula", "Cada carril de secuenciación"],
    "invernadero": ["Cada planta en su maceta", "Cada hoja de la misma planta",
                    "Cada banca completa", "Cada lectura secuenciada"],
}

# --------------------------------------------- información de cada caso
# lugar · aleatorizable (¿el investigador asigna el tratamiento?) · unidad
# correcta (índice en UNIDADES[lugar]) · extracción correcta · hipótesis (la
# primera es la buena) · objetivo de medición · respuestas del investigador.
INFO = {
    "metformina": dict(
        lugar="cultivo", aleatorizable=True, unidad=0, extraccion={"trizol", "columna"},
        hipotesis=["La metformina reprime genes de la gluconeogénesis (PCK1, G6PC) y "
                   "cambia genes del metabolismo energético",
                   "La metformina cambia algunos genes",
                   "No habrá diferencias entre tratamientos",
                   "La metformina cura la diabetes"],
        congelador="Pellets de HepG2 en TRIzol, −80 °C, etiquetados por placa.",
        calendario="La campana está libre toda la semana: todo cabe en un solo día.",
        tecnico="Yo siempre siembro todas las placas el mismo día del mismo matraz… "
                "¿eso cuenta como réplicas?",
        preguntas={
            "¿Cuántos cultivos puedes hacer?": "Puedo sembrar hasta 12 cultivos "
            "independientes por condición, en pases distintos.",
            "¿Qué esperas encontrar?": "Que baje la gluconeogénesis: PCK1, G6PC. Por eso le "
            "dan metformina a pacientes con diabetes.",
        }),
    "dieta": dict(
        lugar="bioterio", aleatorizable=True, unidad=0, extraccion={"trizol", "columna"},
        hipotesis=["La dieta alta en grasa induce genes de lipogénesis e inflamación y "
                   "reprime la β-oxidación en el hígado",
                   "Los ratones gordos tienen hígados distintos",
                   "No habrá diferencias",
                   "La dieta alta en grasa causa cáncer de hígado en 12 semanas"],
        congelador="Hígados congelados en nitrógeno; RIN de las pruebas: ~8.5.",
        calendario="<mal!>Bioterio y campana: máximo 6 hígados por día.</> El técnico propuso: "
                   "lunes controles, martes dieta.",
        tecnico="Los ratones de dieta ya están en el cuarto 2 y los controles en el cuarto 1. "
                "Yo los sacrifico por cuarto, es más fácil.",
        preguntas={
            "¿Cuántos ratones hay?": "Hasta 10 por grupo, machos de la misma edad.",
            "¿Cómo se asignaron a la dieta?": "Todavía no se asignan: llegan mañana del "
                                               "proveedor, todos iguales.",
        }),
    "pareado": dict(
        lugar="clinica", aleatorizable=False, unidad=0, extraccion={"trizol", "columna"},
        hipotesis=["En el tumor se activan vías de proliferación (ciclo celular, MYC, "
                   "Wnt) respecto a la mucosa del mismo paciente",
                   "El tumor es diferente",
                   "No habrá diferencias",
                   "El tumor causa la enfermedad del paciente"],
        congelador="Pares tumor/normal congelados en quirófano; RIN 7-8.",
        calendario="Máximo 8 muestras por día de extracción (4 pacientes).",
        tecnico="Las muestras de cada paciente llegan juntas el día de su cirugía.",
        preguntas={
            "¿Cuántos pacientes?": "Hasta 12, cada uno con tumor y mucosa normal adyacente.",
            "¿Por qué pareadas?": "Porque cada persona es distinta: edad, dieta, "
                                  "medicamentos…",
        }),
    "ffpe": dict(
        lugar="clinica", aleatorizable=False, unidad=0, extraccion={"ffpe"},
        hipotesis=["Los respondedores tienen más genes de células T citotóxicas e "
                   "interferón-γ en el tumor",
                   "Los respondedores son distintos",
                   "No habrá diferencias",
                   "El anti-PD-1 funciona en todos"],
        congelador="<mal!>No hay tejido congelado</>: solo bloques de parafina (FFPE) "
                   "de 2015-2020 en el archivo de patología. RIN de prueba: 2.3; "
                   "DV200: 45 %.",
        calendario="Sin límite de extracción.",
        tecnico="Del FFPE sale poquito ARN y muy roto. Yo usaría el kit especial.",
        preguntas={
            "¿Cuántos pacientes?": "Hasta 14 por grupo.",
            "¿Hay tejido fresco?": "No, solo parafina.",
        }),
    "antisentido": dict(
        lugar="cultivo", aleatorizable=True, unidad=0, extraccion={"trizol"},
        hipotesis=["Al eliminar CHD8 cambian lncRNA antisentido que regulan a sus genes "
                   "vecinos del neurodesarrollo",
                   "CHD8 cambia genes",
                   "No habrá diferencias",
                   "CHD8 causa autismo"],
        congelador="Pellets de neuronas iPSC en TRIzol; RIN 9.",
        calendario="Sin límite.",
        tecnico="Ojo: muchos lncRNA no tienen cola poli(A).",
        preguntas={
            "¿Qué lncRNA te interesan?": "Los que se transcriben en la hebra opuesta de "
                                         "genes codificantes y se solapan con ellos.",
        }),
    "splicing": dict(
        lugar="cultivo", aleatorizable=True, unidad=0, extraccion={"trizol", "columna"},
        hipotesis=["SF3B1 K700E aumenta el uso de sitios 3′ de splicing alternativos",
                   "La mutación cambia la expresión",
                   "No habrá diferencias",
                   "La mutación causa leucemia"],
        congelador="Pellets de K562 isogénicas; RIN 9.6.",
        calendario="Sin límite.",
        tecnico="Para ver uniones exón-exón la lectura tiene que cruzarlas…",
        preguntas={"¿Te importa el nivel del gen?": "No tanto: quiero ver qué exones o "
                                                    "uniones cambian."}),
    "mirna": dict(
        lugar="clinica", aleatorizable=False, unidad=0, extraccion={"mirna", "trizol"},
        biofluido=True,
        hipotesis=["Ciertos miRNA placentarios (cluster C19MC) están elevados en el plasma "
                   "de la preeclampsia",
                   "La preeclampsia cambia la sangre",
                   "No habrá diferencias",
                   "Los miRNA causan la preeclampsia"],
        congelador="Alícuotas de 500 µL de plasma (EDTA). ~5 ng de ARN por alícuota.",
        calendario="Sin límite.",
        tecnico="Las columnas normales pierden todo lo menor de 200 nt…",
        preguntas={"¿Cuántas pacientes?": "Hasta 16 por grupo.",
                   "¿Qué tan largos son los miRNA?": "21-23 nt."}),
    "celula": dict(
        lugar="clinica", aleatorizable=False, unidad=0, extraccion={"disociacion", "nucleos"},
        hipotesis=["Las células epiteliales transicionales de la fibrosis activan genes de "
                   "senescencia y de matriz extracelular",
                   "La fibrosis cambia el pulmón",
                   "No habrá diferencias",
                   "Cada célula es una réplica"],
        congelador="Hay tejido fresco de cada trasplante el día de la cirugía y piezas "
                   "congeladas.",
        calendario="Una cirugía por semana: cada donante se procesa el día que llega.",
        tecnico="Si disocias a 37 °C una hora, se prenden FOS y JUN en todas las células.",
        preguntas={"¿Cuántos donantes?": "6 con fibrosis y 6 sanos.",
                   "¿Qué tan abundante es esa célula?": "~5 % del tejido."}),
    "tiempo": dict(
        lugar="cultivo", aleatorizable=True, unidad=0, extraccion={"trizol", "columna"},
        hipotesis=["Tras LPS hay una ola temprana (TNF, 1 h) y una tardía (genes de "
                   "interferón, 4-12 h)",
                   "El LPS cambia genes",
                   "No habrá diferencias",
                   "El LPS mata a los macrófagos"],
        congelador="Pellets de macrófagos de médula ósea; RIN 9.3.",
        calendario="<mal!>Máximo 8 extracciones por tanda.</>",
        tecnico="Lo práctico sería extraer todos los de 0 h y 1 h juntos y luego los demás.",
        preguntas={"¿Cuántos ratones donantes?": "Hasta 6 por tiempo."}),
    "novo": dict(
        lugar="bioterio", aleatorizable=True, unidad=0, extraccion={"trizol"},
        hipotesis=["El calor induce chaperonas (HSP70, HSP90) y reprime genes del "
                   "metabolismo en el caracol",
                   "El calor cambia al caracol",
                   "No habrá diferencias",
                   "El caracol se adapta al calor"],
        congelador="Caracoles enteros en RNAlater.",
        calendario="Sin límite.",
        tecnico="Nadie ha secuenciado el genoma de este caracol; el pariente más cercano "
                "divergió hace ~100 millones de años.",
        preguntas={"¿Hay genoma de referencia?": "No.", "¿Cuántos caracoles?": "8 por "
                                                                              "temperatura."}),
    "myc": dict(
        lugar="cultivo", aleatorizable=True, unidad=0, extraccion={"trizol", "columna"},
        hipotesis=["MYC alto amplifica la transcripción de casi todos los genes activos",
                   "MYC prende unos genes y apaga otros",
                   "No habrá diferencias",
                   "MYC es un oncogén"],
        congelador="Pellets de exactamente un millón de células (contadas).",
        calendario="Sin límite.",
        tecnico="Las células con MYC alto son más grandes y tienen más ARN por célula.",
        preguntas={"¿Cuántas células por muestra?": "Exactamente 10⁶, contadas."}),
    "cribado": dict(
        lugar="cultivo", aleatorizable=True, unidad=0, extraccion={"trizol", "columna"},
        hipotesis=["Cada compuesto tiene una firma transcripcional distinta que revela su "
                   "mecanismo",
                   "Los compuestos cambian genes",
                   "No habrá diferencias",
                   "El mejor compuesto es el C3"],
        congelador="Placas de 96 pozos lisadas.",
        calendario="Sin límite.",
        tecnico="Con $3 000 y 27 muestras… el RNA-seq completo no alcanza.",
        preguntas={}),
    "interaccion": dict(
        lugar="bioterio", aleatorizable=True, unidad=0, extraccion={"trizol", "columna"},
        hipotesis=["Sin IL-10 la respuesta inflamatoria a LPS es más intensa y prolongada "
                   "(interacción genotipo × tratamiento)",
                   "El KO responde a LPS",
                   "No habrá diferencias",
                   "IL-10 es antiinflamatoria"],
        congelador="Macrófagos peritoneales en TRIzol; RIN 9.1.",
        calendario="Sin límite.",
        tecnico="Ya sabemos qué genes responden a LPS en el silvestre.",
        preguntas={}),
    "sequia": dict(
        lugar="invernadero", aleatorizable=True, unidad=0, extraccion={"ctab", "trizol"},
        hipotesis=["La sequía induce genes de respuesta a ABA y de protección (LEA, "
                   "dehidrinas) en la hoja de tomate",
                   "La sequía cambia la planta",
                   "No habrá diferencias",
                   "Las plantas regadas crecen más"],
        congelador="Hojas congeladas en nitrógeno. <mal!>Hojas de tomate: muchos polifenoles "
                   "y polisacáridos.</>",
        calendario="El invernadero tiene <mal!>4 bancas de 6 macetas</>. La del lado sur "
                   "recibe más sol que la del norte.",
        tecnico="Lo fácil es poner todas las de sequía juntas en las bancas del sur, así "
                "no se riegan por error.",
        preguntas={"¿Cuántas plantas?": "Hasta 12 por tratamiento.",
                   "¿Por qué importa la banca?": "Luz y temperatura cambian de banca a "
                                                  "banca."}),
}

# --------------------------------------------- distractores del papel de diseño
PREGUNTAS_MALAS = [
    "¿Qué genes se expresan en {org}?",
    "¿{grupo} es mejor que {ref}?",
]
OBJETIVOS = [
    ("genes", "Cuánto cambia cada gen"),
    ("antisentido", "lncRNA y transcritos antisentido"),
    ("splicing", "Isoformas y splicing"),
    ("mirna", "miRNA y ARN pequeños"),
    ("celulas", "Un tipo celular dentro del tejido"),
    ("tiempo", "Cambios a lo largo del tiempo"),
    ("interaccion", "Si un efecto depende de otro factor"),
    ("global", "Cambios globales del ARN por célula"),
    ("novo", "Genes de una especie sin genoma"),
]
REGISTROS = [
    ("lote", "Día / lote de procesamiento"),
    ("donante", "Donante o paciente"),
    ("sexo", "Sexo y edad"),
    ("rin", "RIN y concentración de cada muestra"),
    ("operador", "Persona que procesó"),
]


def objetivo_esperado(caso):
    return {"novo": "novo"}.get(caso["objetivo"], caso["objetivo"])


def respuestas(caso):
    """Preguntas para el investigador: las del caso más las genéricas."""
    info = INFO.get(caso["id"], {})
    r = {"¿Cuál es exactamente tu pregunta?": caso["pregunta"],
         "¿Qué muestras tienes?": f"{caso['organismo']}. Grupos: "
                                  f"{', '.join(caso['grupos'])}.",
         "¿Cuál es el presupuesto?": f"${caso['presupuesto']:,} para todo el experimento."}
    r.update(info.get("preguntas", {}))
    return r


def pista_replica(caso):
    """La pista que antes venía en la introducción."""
    from idioma import tr
    for p in caso["intro"]:
        if "Pista de la Dra. Lazo" in p:
            return tr(p).split("</>", 1)[1].strip()
    return "Lee con calma lo que te dicen el investigador, el técnico, el calendario y el " \
           "congelador: ahí están las trampas."


def intro_sin_pista(caso):
    return [p for p in caso["intro"] if "Pista de la Dra. Lazo" not in p]
