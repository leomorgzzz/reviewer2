"""Los casos: investigadores que llegan al Núcleo de Secuenciación con una
pregunta, un presupuesto y alguna trampa escondida.

Campos que lee el Revisor 2 (revisor.py):
  bib_ok / bib_regular   bibliotecas correctas / aceptables con reparos
  rutas_ok               rutas de análisis correctas
  formulas_ok            fórmulas que responden la pregunta
  pruebas_ok             pruebas estadísticas adecuadas
  lectura_min            lectura mínima ("SE50" < "SE75" < "PE100" < "PE150")
  prof_min, prof_util    profundidad mínima y a partir de cuál ya no rinde (M)
  requiere / recomienda  extras indispensables / deseables
  meta                   sensibilidad mínima para dar el caso por resuelto
sim: parámetros de simulacion.simular (ver ese módulo).
"""

CASOS = [
    # 1 ---------------------------------------------------------------------
    dict(
        id="metformina", titulo="El primer encargo", investigador="Dr. Ojeda · farmacología",
        organismo="Humano (línea celular HepG2)", muestra="Células en cultivo, ARN íntegro (RIN 9.5)",
        pregunta="¿Qué genes cambia la metformina (24 h) en hepatocitos?",
        grupos=["Vehículo", "Metformina"], abrev=["V", "M"], objetivo="genes",
        capacidad=None, presupuesto=4200, max_replicas=12, rin=9.5,
        intro=[
            "Buenos días. Soy el Dr. Ojeda. Tengo <titulo!>HepG2</> tratadas con "
            "<titulo>metformina</> o con vehículo durante 24 h y quiero saber qué genes "
            "cambian.",
            "Tengo un presupuesto de <titulo!>$4 200</>. Mi colega dice que hay que "
            "secuenciar a <titulo>100 millones de lecturas</> para que salga algo. Yo "
            "pensaba en dos placas de cada cosa. Usted dirá.",
            "<tenue>Pista de la Dra. Lazo:</> en una línea celular la variación "
            "biológica es pequeña, pero NO es cero. Piensa qué compra más potencia: "
            "lecturas o réplicas.",
        ],
        sim=dict(frac_de=0.10, lfc_min=0.35, lfc_sd=0.7, disp=0.03, sd_lote=0.0),
        bib_ok={"polyA", "tag3"}, bib_regular={"ribo"},
        rutas_ok={"star", "hisat", "salmon"}, formulas_ok={"cond"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="SE50",
        prof_min=8, prof_util=40, requiere=set(), recomienda={"filtro"},
        meta=0.55,
        leccion="Réplicas biológicas antes que profundidad: pasar de 2 a 3 réplicas da "
                "más genes que duplicar las lecturas (Liu 2014). Con línea celular, 3-6 "
                "réplicas y 10-20 M lecturas suelen bastar para genes.",
        fuentes="LIU14 SCH16 CON16",
        manual=["replicas", "profundidad", "normalizacion", "bh"],
    ),
    # 2 ---------------------------------------------------------------------
    dict(
        id="dieta", titulo="Dos días de cosecha", investigador="Dra. Saldívar · metabolismo",
        organismo="Ratón C57BL/6J", muestra="Hígado congelado en nitrógeno, RIN 8.5",
        pregunta="¿Qué cambia en el hígado con dieta alta en grasa (12 semanas)?",
        grupos=["Dieta control", "Dieta alta en grasa"], abrev=["C", "G"], objetivo="genes",
        capacidad=6, presupuesto=5600, max_replicas=10, rin=8.5,
        intro=[
            "Hola. Tengo ratones con <titulo>dieta alta en grasa</> y controles, "
            "hasta 10 por grupo.",
            "Problema: en el laboratorio solo podemos sacrificar y extraer "
            "<titulo!>6 hígados por día</>. Mi técnico propone el lunes todos los "
            "controles y el martes todos los de dieta, para no confundirse.",
            "<tenue>Pista de la Dra. Lazo:</> abre la mesa de lotes con [L] y mira "
            "qué día le toca a cada ratón. ¿Podrás separar «dieta» de «martes»?",
        ],
        sim=dict(frac_de=0.10, lfc_min=0.4, lfc_sd=0.8, disp=0.08, sd_lote=0.65),
        bib_ok={"polyA", "tag3"}, bib_regular={"ribo"},
        rutas_ok={"star", "hisat", "salmon"}, formulas_ok={"lote"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="SE50",
        prof_min=8, prof_util=40, requiere=set(), recomienda={"filtro"},
        meta=0.45,
        leccion="Si cada condición se procesa en su propio lote, el efecto del día y el "
                "de la dieta son matemáticamente inseparables. Bloquear (cada día tiene "
                "ratones de ambos grupos), aleatorizar el orden y poner el lote en la "
                "fórmula (~ lote + condición).",
        fuentes="LEE10 AUE10 CON16",
        manual=["lotes", "aleatorizar", "formula"],
    ),
    # 3 ---------------------------------------------------------------------
    dict(
        id="sequia", titulo="Sequía en el invernadero", investigador="Dra. Valenzuela · fitomejoramiento",
        organismo="Tomate (Solanum lycopersicum)", muestra="Hoja joven congelada en nitrógeno · RIN 7.8",
        pregunta="¿Qué genes responden a 10 días de sequía en la hoja de tomate?",
        grupos=["Riego normal", "Sequía"], abrev=["R", "S"], objetivo="genes",
        capacidad=6, presupuesto=6500, max_replicas=12, rin=7.8, lote_nombre="banca",
        intro=[
            "Hola. Trabajo en mejoramiento de tomate para el desierto de Sonora. Quiero saber "
            "qué genes se encienden con <titulo>sequía</> en la hoja.",
            "Tengo plantas de la misma variedad, sembradas el mismo día. El invernadero tiene "
            "<titulo!>4 bancas de 6 macetas</>.",
            "<tenue>Pista de la Dra. Lazo:</> en un invernadero la luz, el viento y la "
            "temperatura cambian de banca a banca. ¿Qué pasa si todas las plantas en sequía "
            "quedan en la banca más soleada?",
        ],
        sim=dict(frac_de=0.12, lfc_min=0.45, lfc_sd=0.9, disp=0.12, sd_lote=0.6),
        bib_ok={"polyA", "tag3"}, bib_regular={"ribo"},
        rutas_ok={"star", "hisat", "salmon"}, formulas_ok={"lote"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="SE50",
        prof_min=8, prof_util=40, requiere=set(), recomienda={"filtro", "gsea"},
        meta=0.45,
        leccion="Diseño en bloques completos al azar: cada banca (bloque) lleva plantas de "
                "ambos tratamientos, asignadas al azar dentro de la banca, y la banca entra "
                "en la fórmula (~ banca + tratamiento). En plantas, los polifenoles y "
                "polisacáridos bajan el A260/230: extracción con CTAB o kit para plantas.",
        fuentes="AUE10",
        manual=["aleatorizar", "lotes", "f_extraccion"],
    ),
    # 4 ---------------------------------------------------------------------
    dict(
        id="pareado", titulo="Los gemelos del tumor", investigador="Dra. Ibarra · oncología",
        organismo="Humano (pacientes)", muestra="Tumor colorrectal y mucosa normal adyacente, RIN 7.5",
        pregunta="¿Qué vías cambian en el tumor respecto a la mucosa sana del mismo paciente?",
        grupos=["Mucosa normal", "Tumor"], abrev=["N", "T"], objetivo="genes",
        pareado=True, capacidad=8, presupuesto=7000, max_replicas=12, rin=7.5,
        intro=[
            "De cada paciente operado tengo <titulo!>dos muestras</>: el tumor y la mucosa "
            "normal adyacente. Tengo hasta 12 pacientes.",
            "Las personas varían muchísimo entre sí: edad, dieta, microbiota, "
            "medicamentos. Me interesan las <titulo>vías</>, no solo una lista de genes.",
            "<tenue>Pista de la Dra. Lazo:</> cada paciente puede ser su propio "
            "control. ¿Cómo se le dice eso al modelo?",
        ],
        sim=dict(frac_de=0.12, lfc_min=0.4, lfc_sd=0.9, disp=0.12, sd_lote=0.3,
                 sd_donante=0.75),
        bib_ok={"polyA", "ribo"}, bib_regular={"tag3"},
        rutas_ok={"star", "hisat", "salmon"}, formulas_ok={"par", "par_lote"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="SE50",
        prof_min=15, prof_util=50, requiere={"gsea"}, recomienda={"filtro", "shrink"},
        meta=0.5,
        leccion="En un diseño pareado la variación entre donantes se elimina al poner al "
                "donante en la fórmula (~ donante + condición). La comparación se hace "
                "dentro de cada persona, como una t pareada.",
        fuentes="DESV LOV14 CON16",
        manual=["pareado", "formula", "enriquecimiento"],
    ),
    # 4 ---------------------------------------------------------------------
    dict(
        id="ffpe", titulo="El archivo de patología", investigador="Dr. Montaño · patología",
        organismo="Humano (biopsias de melanoma)", muestra="FFPE de 2015-2020 · RIN 2.3 · DV200 45 %",
        pregunta="¿Qué distingue a quienes respondieron a anti-PD-1 de quienes no?",
        grupos=["No respondedores", "Respondedores"], abrev=["N", "R"], objetivo="genes",
        capacidad=None, presupuesto=9000, max_replicas=14, rin=2.3, poco_material=True,
        intro=[
            "Tengo un tesoro: <titulo!>biopsias en parafina (FFPE)</> de pacientes con "
            "melanoma tratados con anti-PD-1. Ya sabemos quién respondió.",
            "El Bioanalyzer dice <mal!>RIN 2.3</>. El técnico dice que no sirven. Pero el "
            "<titulo>DV200</> (el % de fragmentos de más de 200 nt) es del 45 %.",
            "<tenue>Pista de la Dra. Lazo:</> la formalina rompe el ARN y le quita la "
            "cola poli(A) a muchos fragmentos. ¿Qué biblioteca no depende de la cola?",
        ],
        sim=dict(frac_de=0.08, lfc_min=0.5, lfc_sd=0.8, disp=0.25, sd_lote=0.0),
        bib_ok={"ribo"}, bib_regular={"tag3"},
        rutas_ok={"star", "hisat", "salmon"}, formulas_ok={"cond"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="SE75",
        prof_min=20, prof_util=60, requiere=set(), recomienda={"umi", "filtro"},
        meta=0.33,
        leccion="Con ARN degradado (FFPE) el RIN no sirve: se usa el DV200 (≥ 30 % "
                "mínimo). La ribodepleción con sondas no necesita la cola poli(A); los "
                "UMIs separan duplicados de PCR de duplicados biológicos.",
        fuentes="ILL14 ZHA14 FU18",
        manual=["calidad_arn", "bibliotecas", "umi"],
    ),
    # 5 ---------------------------------------------------------------------
    dict(
        id="antisentido", titulo="La hebra perdida", investigador="Dra. Castañeda · neurociencias",
        organismo="Humano (neuronas derivadas de iPSC)", muestra="ARN íntegro (RIN 9.2)",
        pregunta="¿Qué lncRNA antisentido cambian al eliminar el regulador de cromatina CHD8?",
        grupos=["Control isogénico", "CHD8 KO"], abrev=["C", "K"], objetivo="antisentido",
        capacidad=None, presupuesto=7000, max_replicas=10, rin=9.2,
        intro=[
            "Estudio <titulo>lncRNA antisentido</>: se transcriben de la hebra opuesta "
            "de un gen codificante y se solapan con él.",
            "Muchos no tienen cola poli(A) y se expresan poquito. Tengo neuronas KO de "
            "CHD8 y su control isogénico.",
            "<tenue>Pista de la Dra. Lazo:</> si una lectura cae en una región donde "
            "hay gen en ambas hebras, ¿cómo sabes de cuál vino?",
        ],
        sim=dict(frac_de=0.10, lfc_min=0.5, lfc_sd=0.8, disp=0.05, sd_lote=0.0,
                 log_mu=2.0),
        bib_ok={"ribo"}, bib_regular={"polyA", "largo"},
        rutas_ok={"star", "hisat"}, formulas_ok={"cond"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="PE100",
        prof_min=40, prof_util=120, requiere={"hebra"}, recomienda={"filtro"},
        meta=0.4,
        leccion="Sin biblioteca con hebra (dUTP) no se distingue el sentido del "
                "antisentido. La ribodepleción conserva lncRNA sin cola; como se expresan "
                "poco, hace falta más profundidad. Para descubrir transcritos conviene "
                "alinear al genoma (STAR/HISAT2), no pseudoalinear a una anotación.",
        fuentes="LEV10 PAR09 CON16",
        manual=["hebra", "bibliotecas", "alineamiento"],
    ),
    # 6 ---------------------------------------------------------------------
    dict(
        id="splicing", titulo="El empalme", investigador="Dr. Villaseñor · hematología",
        organismo="Humano (células K562 isogénicas)", muestra="ARN íntegro (RIN 9.6)",
        pregunta="¿Qué eventos de splicing alterna la mutación SF3B1 K700E?",
        grupos=["SF3B1 silvestre", "SF3B1 K700E"], abrev=["W", "K"], objetivo="splicing",
        capacidad=None, presupuesto=6500, max_replicas=8, rin=9.6,
        intro=[
            "SF3B1 es parte del espliceosoma. La mutación K700E, frecuente en "
            "síndromes mielodisplásicos, hace que se usen <titulo>sitios 3′ "
            "alternativos</>.",
            "No me importa tanto si el gen sube o baja: quiero saber qué "
            "<titulo!>exones o uniones</> cambian.",
            "<tenue>Pista de la Dra. Lazo:</> para ver una unión exón-exón la lectura "
            "tiene que atravesarla. Y contar uniones es contar MUCHAS menos lecturas "
            "que contar genes.",
        ],
        sim=dict(frac_de=0.10, lfc_min=0.6, lfc_sd=0.8, disp=0.04, sd_lote=0.0),
        bib_ok={"polyA", "ribo", "largo"}, bib_regular=set(),
        rutas_ok={"star", "hisat", "isoseq"}, formulas_ok={"cond"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="PE100",
        prof_min=40, prof_util=150, requiere={"splicing"}, recomienda={"hebra"},
        meta=0.4,
        leccion="Isoformas y splicing piden lecturas pareadas y largas (PE 2×100-150), "
                "40-100 M lecturas y herramientas de eventos (rMATS) o de uso de exones "
                "(DEXSeq). Las lecturas largas (Iso-Seq/ONT) ven la isoforma completa.",
        fuentes="CON16 SHE14 AND12",
        manual=["lecturas", "splicing", "metodos"],
    ),
    # 7 ---------------------------------------------------------------------
    dict(
        id="mirna", titulo="Gotas de plasma", investigador="Dra. Leyva · ginecoobstetricia",
        organismo="Humano (plasma)", muestra="500 µL de plasma · ~5 ng de ARN total",
        pregunta="¿Qué miRNA circulantes distinguen la preeclampsia del embarazo normal?",
        grupos=["Embarazo normal", "Preeclampsia"], abrev=["E", "P"], objetivo="mirna",
        capacidad=None, presupuesto=5000, max_replicas=16, rin=6, poco_material=True,
        intro=[
            "Quiero <titulo!>microARN</> en el plasma de embarazadas. Son de 21-23 nt. "
            "Tengo muy poco ARN: unos 5 ng por muestra.",
            "Me ofrecieron un paquete de «RNA-seq estándar» con poli(A) a 30 M lecturas.",
            "<tenue>Pista de la Dra. Lazo:</> ¿los miRNA maduros tienen cola poli(A)? "
            "¿Cuántos tipos distintos de miRNA hay? (unos 2 000 en miRBase humano, no "
            "20 000).",
        ],
        sim=dict(frac_de=0.10, lfc_min=0.5, lfc_sd=0.8, disp=0.2, sd_lote=0.0, genes=600),
        bib_ok={"small"}, bib_regular=set(),
        rutas_ok={"mirdeep"}, formulas_ok={"cond"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="SE50",
        prof_min=4, prof_util=20, requiere=set(), recomienda={"umi", "filtro"},
        meta=0.5,
        leccion="small RNA-seq: selección de 18-34 nt, SE 50, 2-10 M lecturas. Con muy "
                "poco material los UMIs quitan duplicados de PCR. El dinero que sobra va "
                "a más réplicas: la variación entre personas es grande.",
        fuentes="CON16 FU18 FRI12",
        manual=["bibliotecas", "umi", "replicas"],
    ),
    # 8 ---------------------------------------------------------------------
    dict(
        id="celula", titulo="La célula rara", investigador="Dr. Arredondo · neumología",
        organismo="Humano (pulmón)", muestra="Tejido fresco de trasplante y donantes · RIN 8",
        pregunta="¿Qué cambia en las células epiteliales «transicionales» de pulmones con fibrosis?",
        grupos=["Donante sano", "Fibrosis pulmonar"], abrev=["S", "F"], objetivo="celulas",
        capacidad=None, presupuesto=22000, max_replicas=6, rin=8,
        intro=[
            "En la fibrosis pulmonar idiopática aparece un tipo de célula epitelial "
            "<titulo>transicional</> (KRT5−/KRT17+) que es solo el ~5 % del tejido.",
            "Un RNA-seq de tejido completo diluye su señal en el 95 % restante.",
            "Tengo 6 pulmones con fibrosis y 6 sanos. Mi estudiante ya hizo un análisis "
            "piloto con 3 contra 3: «miles de genes con p < 10^-50, cada célula es un "
            "dato».",
            "<tenue>Pista de la Dra. Lazo:</> 10 000 células de una persona siguen "
            "siendo UNA persona.",
        ],
        sim=dict(frac_de=0.10, lfc_min=0.7, lfc_sd=0.9, disp=0.06, sd_lote=0.0,
                 sd_donante=0.2),
        bib_ok={"sc10x", "snrna"}, bib_regular={"smartseq", "espacial"},
        rutas_ok={"cr_pb"}, formulas_ok={"cond"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="SE50",
        prof_min=60, prof_util=200, requiere=set(), recomienda={"umi"},
        meta=0.45,
        leccion="Las células de un donante no son réplicas independientes "
                "(pseudoreplicación): probar célula a célula da miles de falsos "
                "positivos. Se suman las células de cada tipo por donante (pseudobulk) y "
                "se usa DESeq2/edgeR con los donantes como réplicas.",
        fuentes="SQU21 ZIM21 CRO20",
        manual=["celula_unica", "replicas", "metodos"],
    ),
    # 9 ---------------------------------------------------------------------
    dict(
        id="tiempo", titulo="El reloj de la inflamación", investigador="Dra. Quintero · inmunología",
        organismo="Ratón (macrófagos de médula ósea)", muestra="ARN íntegro (RIN 9.3)",
        pregunta="¿Qué genes responden en algún momento tras estimular con LPS (0, 1, 4 y 12 h)?",
        grupos=["0 h", "1 h", "4 h", "12 h"], abrev=["0", "1", "4", "X"], objetivo="tiempo",
        capacidad=8, presupuesto=6200, max_replicas=6, rin=9.3,
        intro=[
            "Estimulo macrófagos con <titulo>LPS</> y cosecho a las 0, 1, 4 y 12 h. Hay "
            "genes tempranos (TNF, a la hora) y tardíos (a las 12 h).",
            "Solo caben <titulo!>8 extracciones por tanda</>.",
            "<tenue>Pista de la Dra. Lazo:</> la prueba de Wald compara DOS niveles. "
            "Si quieres saber si un gen cambia en CUALQUIER momento, compara modelos.",
        ],
        sim=dict(frac_de=0.15, lfc_min=0.6, lfc_sd=1.0, disp=0.04, sd_lote=0.5),
        bib_ok={"polyA", "tag3"}, bib_regular={"ribo"},
        rutas_ok={"star", "hisat", "salmon"}, formulas_ok={"tiempo_lote"},
        pruebas_ok={"lrt"}, lectura_min="SE50",
        prof_min=8, prof_util=40, requiere=set(), recomienda={"filtro"},
        meta=0.5,
        leccion="Series de tiempo: el tiempo como factor y una prueba de razón de "
                "verosimilitud (LRT) del modelo completo contra el reducido detecta "
                "genes que cambian en cualquier punto. Las tandas se bloquean: cada tanda "
                "lleva todos los tiempos.",
        fuentes="DESV LOV14 AUE10",
        manual=["formula", "lotes", "pruebas"],
    ),
    # 10 --------------------------------------------------------------------
    dict(
        id="novo", titulo="La especie sin mapa", investigador="Dr. Peralta · ecología evolutiva",
        organismo="Caracol de agua dulce endémico (sin genoma ensamblado)",
        muestra="Pie y glándula digestiva · RIN 8",
        pregunta="¿Qué genes responden al calor (34 °C) en una especie sin genoma de referencia?",
        grupos=["22 °C", "34 °C"], abrev=["F", "C"], objetivo="novo", sin_genoma=True,
        capacidad=None, presupuesto=6000, max_replicas=8, rin=8,
        intro=[
            "Mi caracol vive en un solo manantial y nadie le ha secuenciado el genoma. "
            "El pariente más cercano con genoma divergió hace ~100 millones de años.",
            "Quiero comparar animales a <titulo>22 °C</> y a <titulo>34 °C</>.",
            "<tenue>Pista de la Dra. Lazo:</> sin genoma no hay a dónde alinear. Hay "
            "que armar el rompecabezas sin la foto de la caja.",
        ],
        sim=dict(frac_de=0.10, lfc_min=0.5, lfc_sd=0.9, disp=0.12, sd_lote=0.0),
        bib_ok={"polyA", "ribo", "largo"}, bib_regular=set(),
        rutas_ok={"trinity", "isoseq"}, formulas_ok={"cond"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="PE100",
        prof_min=25, prof_util=80, requiere={"hebra"}, recomienda={"filtro", "gsea"},
        meta=0.4,
        leccion="Sin genoma: ensamblaje de novo (Trinity) con lecturas pareadas y con "
                "hebra, juntando todas las muestras; luego se cuantifica cada muestra "
                "contra el ensamblaje y se anota por homología (BLAST, Trinotate).",
        fuentes="GRA11 CON16",
        manual=["novo", "lecturas", "hebra"],
    ),
    # 11 --------------------------------------------------------------------
    dict(
        id="myc", titulo="La amplificación de MYC", investigador="Dra. Robles · biología del cáncer",
        organismo="Humano (células P493-6)", muestra="Mismo número de células por muestra · RIN 9.4",
        pregunta="¿MYC alto cambia unos genes, o sube la transcripción de casi todo?",
        grupos=["MYC bajo", "MYC alto"], abrev=["B", "A"], objetivo="global",
        capacidad=None, presupuesto=4500, max_replicas=8, rin=9.4,
        intro=[
            "Con <titulo>MYC alto</> las células son más grandes y tienen MÁS ARN total "
            "por célula. Sospecho que MYC amplifica casi todos los genes activos.",
            "Cuento las células y extraigo de exactamente <titulo!>un millón</> por "
            "muestra.",
            "<tenue>Pista de la Dra. Lazo:</> DESeq2 y TMM suponen que la mayoría de "
            "los genes NO cambia. ¿Y si todos cambian?",
        ],
        sim=dict(frac_de=0.15, lfc_min=0.5, lfc_sd=0.6, disp=0.03, sd_lote=0.0, cambio_global=1.0),
        bib_ok={"polyA", "ribo"}, bib_regular={"tag3"},
        rutas_ok={"star", "hisat", "salmon"}, formulas_ok={"cond"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="SE50",
        prof_min=8, prof_util=40, requiere={"ercc"}, recomienda={"filtro"},
        meta=0.5,
        leccion="La normalización por razón de medianas o TMM asume que la mayoría de "
                "los genes no cambia; si el ARN total por célula cambia, borra el efecto "
                "global. Spike-ins (ERCC) agregados por número de células permiten "
                "normalizar a cantidad por célula.",
        fuentes="LOV12 JIA11 RIS14",
        manual=["normalizacion", "spike"],
    ),
    # 12 --------------------------------------------------------------------
    dict(
        id="cribado", titulo="El cribado", investigador="Dr. Navarro · química medicinal",
        organismo="Humano (línea A549)", muestra="Placa de 96 pozos · RIN 9",
        pregunta="¿Qué genes cambia cada uno de 8 compuestos frente a DMSO?",
        grupos=["DMSO", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
        abrev=["D", "1", "2", "3", "4", "5", "6", "7", "8"], objetivo="genes",
        capacidad=None, presupuesto=3000, max_replicas=6, rin=9,
        intro=[
            "Tengo <titulo>8 compuestos</> nuevos y DMSO. Quiero el perfil "
            "transcripcional de cada uno.",
            "Presupuesto: <mal!>$3 000</> en total. Me dijeron que una muestra de RNA-seq "
            "cuesta más de $200…",
            "<tenue>Pista de la Dra. Lazo:</> si solo quieres contar genes, ¿hace falta "
            "secuenciar el transcrito completo?",
        ],
        sim=dict(frac_de=0.08, lfc_min=0.5, lfc_sd=0.8, disp=0.04, sd_lote=0.0, genes=900),
        bib_ok={"tag3"}, bib_regular={"polyA"},
        rutas_ok={"star", "hisat", "salmon"}, formulas_ok={"cond"},
        pruebas_ok={"deseq2", "edger", "limma"}, lectura_min="SE50",
        prof_min=3, prof_util=15, requiere=set(), recomienda={"filtro"},
        meta=0.45,
        leccion="3′ tag-seq (QuantSeq, BRB-seq): códigos de barras desde la "
                "retrotranscripción, todas las muestras en un tubo, 3-10 M lecturas. "
                "Cuesta una fracción del RNA-seq completo y basta para expresión "
                "diferencial de genes.",
        fuentes="ALP19 MOL14",
        manual=["bibliotecas", "profundidad"],
    ),
    # 13 --------------------------------------------------------------------
    dict(
        id="interaccion", titulo="Genotipo por tratamiento", investigador="Dra. Fuentes · inmunogenética",
        organismo="Ratón (macrófagos peritoneales)", muestra="ARN íntegro (RIN 9.1)",
        pregunta="¿Qué genes responden a LPS de forma DISTINTA cuando falta IL-10?",
        grupos=["WT vehículo", "WT LPS", "Il10 KO vehículo", "Il10 KO LPS"],
        abrev=["w", "W", "k", "K"], objetivo="interaccion",
        factores=dict(genotipo=[0, 0, 1, 1], tratamiento=[0, 1, 0, 1]),
        capacidad=None, presupuesto=6000, max_replicas=8, rin=9.1,
        intro=[
            "Tengo macrófagos <titulo>silvestres</> y <titulo>Il10 KO</>, con y sin LPS: "
            "cuatro grupos.",
            "No me interesan los genes que responden a LPS (ya los conocemos), sino los "
            "que responden <titulo!>diferente</> según el genotipo.",
            "<tenue>Pista de la Dra. Lazo:</> «la respuesta al tratamiento depende del "
            "genotipo» tiene un nombre en estadística.",
        ],
        sim=dict(frac_de=0.08, lfc_min=0.7, lfc_sd=0.9, disp=0.04, sd_lote=0.0),
        bib_ok={"polyA", "tag3"}, bib_regular={"ribo"},
        rutas_ok={"star", "hisat", "salmon"}, formulas_ok={"inter", "cond"},
        pruebas_ok={"deseq2", "edger", "limma", "lrt"}, lectura_min="SE50",
        prof_min=8, prof_util=40, requiere=set(), recomienda={"filtro", "shrink"},
        meta=0.4,
        leccion="Diseño factorial 2×2: el término de interacción genotipo:tratamiento "
                "mide la diferencia de las diferencias. Una interacción necesita más "
                "réplicas que un efecto principal porque compara cuatro grupos.",
        fuentes="DESV LOV14 AUE10",
        manual=["formula", "factorial"],
    ),
]

POR_ID = {c["id"]: c for c in CASOS}

ORDEN_LECTURA = ["SE50", "SE75", "PE100", "PE150", "LARGA"]

_GEN = dict(bib_ok={"polyA", "ribo", "tag3"}, bib_regular={"largo"},
            rutas_ok={"star", "hisat", "salmon"}, formulas_ok={"cond"},
            lectura_min="SE50", prof_min=10, prof_util=50, requiere=set(),
            recomienda={"filtro", "shrink", "gsea"})
PERFILES_LIBRES = {
    "genes": _GEN,
    "global": dict(_GEN, requiere={"ercc"}),
    "tiempo": dict(_GEN, formulas_ok={"tiempo"}, pruebas_ok={"lrt"}),
    "interaccion": dict(_GEN, formulas_ok={"inter", "cond"}),
    "antisentido": dict(bib_ok={"ribo"}, bib_regular={"polyA", "largo"},
                        rutas_ok={"star", "hisat"}, formulas_ok={"cond"},
                        lectura_min="PE100", prof_min=40, prof_util=120,
                        requiere={"hebra"}, recomienda={"filtro"}),
    "splicing": dict(bib_ok={"polyA", "ribo", "largo"}, bib_regular=set(),
                     rutas_ok={"star", "hisat", "isoseq"}, formulas_ok={"cond"},
                     lectura_min="PE100", prof_min=40, prof_util=150,
                     requiere={"splicing"}, recomienda={"hebra"}),
    "mirna": dict(bib_ok={"small"}, bib_regular=set(), rutas_ok={"mirdeep"},
                  formulas_ok={"cond"}, lectura_min="SE50", prof_min=4, prof_util=20,
                  requiere=set(), recomienda={"umi", "filtro"}),
    "celulas": dict(bib_ok={"sc10x", "snrna"}, bib_regular={"smartseq", "espacial"},
                    rutas_ok={"cr_pb"}, formulas_ok={"cond"}, lectura_min="SE50",
                    prof_min=60, prof_util=200, requiere=set(), recomienda={"umi"}),
}


def caso_libre(organismo, grupos, objetivo, muestra, pareado=False, capacidad=None,
               presupuesto=20000, rin=9.0, pregunta="(experimento propio)"):
    """Caso para el Laboratorio libre: el jugador describe su experimento y
    se simula con parámetros genéricos de tejido."""
    abrev = []
    for g in grupos:
        a = g[:1].upper() or "X"
        while a in abrev:
            a = chr(ord(a) + 1)
        abrev.append(a)
    factorial = objetivo == "interaccion"
    caso = dict(
        id="libre", titulo="Laboratorio libre", investigador="Tú",
        organismo=organismo, muestra=muestra, pregunta=pregunta,
        grupos=grupos, abrev=abrev, objetivo=objetivo, pareado=pareado,
        capacidad=capacidad, presupuesto=presupuesto, max_replicas=20, rin=rin,
        intro=[],
        sim=dict(frac_de=0.1, lfc_min=0.5, lfc_sd=0.8, disp=0.1, sd_lote=0.4,
                 sd_donante=0.6 if pareado else 0.0),
        pruebas_ok={"deseq2", "edger", "limma", "lrt"}, meta=0.0,
        leccion="", fuentes="CON16", manual=[], libre=True,
    )
    caso.update(PERFILES_LIBRES[objetivo])
    if pareado:
        caso["formulas_ok"] = {"par", "par_lote"}
    elif capacidad:
        caso["formulas_ok"] = {"tiempo_lote"} if objetivo == "tiempo" else {"lote"}
    if rin < 6:
        caso["bib_ok"] = (caso["bib_ok"] - {"polyA"}) | {"ribo"} if "polyA" in caso["bib_ok"] \
            else caso["bib_ok"]
        caso["recomienda"] = caso["recomienda"] | {"umi"}
        caso["poco_material"] = True
    if factorial:
        caso["factores"] = dict(genotipo=[0, 0, 1, 1], tratamiento=[0, 1, 0, 1])
    return caso
