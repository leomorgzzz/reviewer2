"""Opciones de diseño de un experimento de transcriptómica, sus costos y las
fuentes bibliográficas del juego.

Cada explicación lleva su cita (clave de FUENTES). Los costos son
aproximados y sirven para comparar opciones entre sí, no para cotizar: los
precios reales cambian por proveedor, país y año.
"""

FUENTES = {
    "CON16": "Conesa et al. 2016 — A survey of best practices for RNA-seq data analysis. Genome Biol 17:13",
    "SCH16": "Schurch et al. 2016 — How many biological replicates are needed in an RNA-seq experiment… RNA 22:839",
    "LIU14": "Liu, Zhou & White 2014 — RNA-seq differential expression studies: more sequence or more replication? Bioinformatics 30:301",
    "CHI14": "Ching, Huang & Garmire 2014 — Power analysis and sample size estimation for RNA-Seq differential expression. RNA 20:1684",
    "HAR13": "Hart et al. 2013 — Calculating sample size estimates for RNA sequencing data (RNASeqPower). J Comput Biol 20:970",
    "ENC": "ENCODE Consortium — ENCODE4 bulk RNA-seq data standards (encodeproject.org)",
    "AUE10": "Auer & Doerge 2010 — Statistical design and analysis of RNA sequencing data. Genetics 185:405",
    "LEE10": "Leek et al. 2010 — Tackling the widespread and critical impact of batch effects. Nat Rev Genet 11:733",
    "MAR08": "Marioni et al. 2008 — RNA-seq: an assessment of technical reproducibility… Genome Res 18:1509",
    "MOR08": "Mortazavi et al. 2008 — Mapping and quantifying mammalian transcriptomes by RNA-Seq. Nat Methods 5:621",
    "WAN09": "Wang, Gerstein & Snyder 2009 — RNA-Seq: a revolutionary tool for transcriptomics. Nat Rev Genet 10:57",
    "STA19": "Stark, Grzelak & Hadfield 2019 — RNA sequencing: the teenage years. Nat Rev Genet 20:631",
    "SEQ14": "SEQC/MAQC-III Consortium 2014 — A comprehensive assessment of RNA-seq accuracy… Nat Biotechnol 32:903",
    "LOV14": "Love, Huber & Anders 2014 — DESeq2. Genome Biol 15:550",
    "DESV": "Love, Anders & Huber — Analyzing RNA-seq data with DESeq2 (viñeta de Bioconductor)",
    "ROB10": "Robinson, McCarthy & Smyth 2010 — edgeR. Bioinformatics 26:139",
    "TMM": "Robinson & Oshlack 2010 — A scaling normalization method (TMM). Genome Biol 11:R25",
    "LAW14": "Law et al. 2014 — voom: precision weights… Genome Biol 15:R29",
    "BH95": "Benjamini & Hochberg 1995 — Controlling the false discovery rate. J R Stat Soc B 57:289",
    "BOU10": "Bourgon, Gentleman & Huber 2010 — Independent filtering increases detection power. PNAS 107:9546",
    "ZHU19": "Zhu, Ibrahim & Love 2019 — apeglm: heavy-tailed prior for fold changes. Bioinformatics 35:2084",
    "LOV12": "Lovén et al. 2012 — Revisiting global gene expression analysis. Cell 151:476",
    "JIA11": "Jiang et al. 2011 — Synthetic spike-in standards for RNA-seq experiments (ERCC). Genome Res 21:1543",
    "RIS14": "Risso et al. 2014 — Normalization of RNA-seq data using factor analysis of control genes (RUVSeq). Nat Biotechnol 32:896",
    "LEK07": "Leek & Storey 2007 — Capturing heterogeneity in gene expression studies by SVA. PLoS Genet 3:e161",
    "ZHN20": "Zhang, Parmigiani & Johnson 2020 — ComBat-seq. NAR Genom Bioinform 2:lqaa078",
    "SQU21": "Squair et al. 2021 — Confronting false discoveries in single-cell differential expression. Nat Commun 12:5692",
    "ZIM21": "Zimmerman, Espeland & Langefeld 2021 — A practical solution to pseudoreplication bias in single-cell studies. Nat Commun 12:738",
    "CRO20": "Crowell et al. 2020 — muscat: multi-sample multi-condition scRNA-seq. Nat Commun 11:6077",
    "LUE19": "Luecken & Theis 2019 — Current best practices in single-cell RNA-seq analysis. Mol Syst Biol 15:e8746",
    "ZHE17": "Zheng et al. 2017 — Massively parallel digital transcriptional profiling of single cells (10x). Nat Commun 8:14049",
    "PIC14": "Picelli et al. 2014 — Full-length RNA-seq from single cells using Smart-seq2. Nat Protoc 9:171",
    "WOL18": "Wolf, Angerer & Theis 2018 — SCANPY. Genome Biol 19:15",
    "HAO21": "Hao et al. 2021 — Integrated analysis of multimodal single-cell data (Seurat v4). Cell 184:3573",
    "FU18": "Fu et al. 2018 — Elimination of PCR duplicates in RNA-seq and small RNA-seq using UMIs. BMC Genomics 19:531",
    "KIV12": "Kivioja et al. 2012 — Counting absolute numbers of molecules using UMIs. Nat Methods 9:72",
    "SMI17": "Smith, Heger & Sudbery 2017 — UMI-tools. Genome Res 27:491",
    "LEV10": "Levin et al. 2010 — Comprehensive comparative analysis of strand-specific RNA sequencing methods. Nat Methods 7:709",
    "PAR09": "Parkhomchuk et al. 2009 — Transcriptome analysis by strand-specific sequencing (dUTP). Nucleic Acids Res 37:e123",
    "ZHA14": "Zhao et al. 2014 — Comparison of RNA-Seq by poly(A) capture, ribosomal RNA depletion, and microarray. PLoS One 9:e78644",
    "SCR06": "Schroeder et al. 2006 — The RIN: an RNA integrity number. BMC Mol Biol 7:3",
    "ILL14": "Illumina 2014 — Evaluating RNA quality from FFPE samples (nota técnica, DV200)",
    "HAN10": "Hansen, Brenner & Dudoit 2010 — Biases in Illumina transcriptome sequencing caused by random hexamer priming. Nucleic Acids Res 38:e131",
    "DOB13": "Dobin et al. 2013 — STAR: ultrafast universal RNA-seq aligner. Bioinformatics 29:15",
    "KIM19": "Kim et al. 2019 — Graph-based genome alignment and genotyping with HISAT2. Nat Biotechnol 37:907",
    "PAT17": "Patro et al. 2017 — Salmon. Nat Methods 14:417",
    "BRA16": "Bray et al. 2016 — Near-optimal probabilistic RNA-seq quantification (kallisto). Nat Biotechnol 34:525",
    "LIA14": "Liao, Smyth & Shi 2014 — featureCounts. Bioinformatics 30:923",
    "SON15": "Soneson, Love & Robinson 2015 — Differential analyses for RNA-seq: transcript-level estimates improve gene-level inferences (tximport). F1000Research 4:1521",
    "GRA11": "Grabherr et al. 2011 — Full-length transcriptome assembly without a reference genome (Trinity). Nat Biotechnol 29:644",
    "SHE14": "Shen et al. 2014 — rMATS. PNAS 111:E5593",
    "AND12": "Anders, Reyes & Huber 2012 — Detecting differential usage of exons (DEXSeq). Genome Res 22:2008",
    "SUB05": "Subramanian et al. 2005 — Gene set enrichment analysis. PNAS 102:15545",
    "YOU10": "Young et al. 2010 — Gene ontology analysis for RNA-seq: accounting for selection bias (goseq). Genome Biol 11:R14",
    "LAN08": "Langfelder & Horvath 2008 — WGCNA. BMC Bioinformatics 9:559",
    "NEW19": "Newman et al. 2019 — Determining cell type abundance and expression from bulk tissues (CIBERSORTx). Nat Biotechnol 37:773",
    "AND10": "Andrews 2010 — FastQC (Babraham Bioinformatics)",
    "EWE16": "Ewels et al. 2016 — MultiQC. Bioinformatics 32:3047",
    "CHE18": "Chen et al. 2018 — fastp. Bioinformatics 34:i884",
    "MAR11": "Martin 2011 — Cutadapt removes adapter sequences. EMBnet.journal 17:10",
    "WAN12": "Wang, Wang & Li 2012 — RSeQC. Bioinformatics 28:2184",
    "OKO16": "Okonechnikov, Conesa & García-Alcalde 2016 — Qualimap 2. Bioinformatics 32:292",
    "EWE20": "Ewels et al. 2020 — The nf-core framework. Nat Biotechnol 38:276",
    "BUS09": "Bustin et al. 2009 — The MIQE guidelines. Clin Chem 55:611",
    "FGED": "FGED Society — MINSEQE: Minimum Information about a high-throughput SEQuencing Experiment",
    "FRI12": "Friedländer et al. 2012 — miRDeep2. Nucleic Acids Res 40:37",
    "STH16": "Ståhl et al. 2016 — Visualization and analysis of gene expression in tissue sections by spatial transcriptomics. Science 353:78",
    "CHN15": "Chen et al. 2015 — Spatially resolved, highly multiplexed RNA profiling in single cells (MERFISH). Science 348:aaa6090",
    "ING09": "Ingolia et al. 2009 — Genome-wide analysis in vivo of translation with ribosome profiling. Science 324:218",
    "COR08": "Core, Waterfall & Lis 2008 — Nascent RNA sequencing (GRO-seq). Science 322:1845",
    "KWA13": "Kwak et al. 2013 — Precise maps of RNA polymerase reveal… (PRO-seq). Science 339:950",
    "HER17": "Herzog et al. 2017 — Thiol-linked alkylation of RNA (SLAM-seq). Nat Methods 14:1198",
    "GAR18": "Garalde et al. 2018 — Highly parallel direct RNA sequencing on an array of nanopores. Nat Methods 15:201",
    "GOR15": "Gordon et al. 2015 — Widespread polycistronic transcripts in fungi revealed by single-molecule mRNA sequencing (Iso-Seq). PLoS One 10:e0132628",
    "SCN95": "Schena et al. 1995 — Quantitative monitoring of gene expression patterns with a cDNA microarray. Science 270:467",
    "VEL95": "Velculescu et al. 1995 — Serial analysis of gene expression (SAGE). Science 270:484",
    "SHI03": "Shiraki et al. 2003 — Cap analysis gene expression (CAGE). PNAS 100:15776",
    "GEI08": "Geiss et al. 2008 — Direct multiplexed measurement of gene expression with color-coded probe pairs (NanoString). Nat Biotechnol 26:317",
    "ULE03": "Ule et al. 2003 — CLIP identifies Nova-regulated RNA networks in the brain. Science 302:1212",
    "ALP19": "Alpern et al. 2019 — BRB-seq: ultra-affordable high-throughput transcriptomics. Genome Biol 20:71",
    "MOL14": "Moll et al. 2014 — QuantSeq 3′ mRNA sequencing for RNA quantification. Nat Methods 11:i–iii",
    "WES12": "Westermann, Gorski & Vogel 2012 — Dual RNA-seq of pathogen and host. Nat Rev Microbiol 10:618",
    "SHA96": "Shalon, Smith & Brown 1996 — A DNA microarray system for analyzing complex DNA samples. Genome Res 6:639",
    "LUN03": "Lundholt, Scudder & Pagliaro 2003 — A simple technique for reducing edge effect in cell-based assays. J Biomol Screen 8:566",
    "KER98": "Kerr 1998 — HARKing: Hypothesizing After the Results are Known. Pers Soc Psychol Rev 2:196",
    "NOS18": "Nosek et al. 2018 — The preregistration revolution. PNAS 115:2600",
    "SIM11": "Simmons, Nelson & Simonsohn 2011 — False-positive psychology: undisclosed flexibility in data collection and analysis. Psychol Sci 22:1359",
    "CHO93": "Chomczynski 1993 — A reagent for the single-step simultaneous isolation of RNA, DNA and proteins (TRIzol). BioTechniques 15:532",
    "DEA95": "DeAngelis, Wang & Hawkins 1995 — Solid-phase reversible immobilization for the isolation of PCR products (SPRI). Nucleic Acids Res 23:4742",
    "ILLDD": "Illumina — Guía «Denature and Dilute Libraries» de cada secuenciador (documentación del fabricante)",
    "CHA93": "Chang, Puryear & Cairney 1993 — A simple and efficient method for isolating RNA from pine trees (CTAB). Plant Mol Biol Rep 11:113",
    "KRU11": "Krueger, Andrews & Osborne 2011 — Large scale loss of data in low-diversity Illumina sequencing libraries can be recovered by deferred cluster calling. PLoS One 6:e16607",
    "ROT11": "Rothberg et al. 2011 — An integrated semiconductor device enabling non-optical genome sequencing (Ion Torrent). Nature 475:348",
    "GOO16": "Goodwin, McPherson & McCombie 2016 — Coming of age: ten years of next-generation sequencing technologies. Nat Rev Genet 17:333",
}

_CORTOS = {
    "CON16": "Conesa 2016", "SCH16": "Schurch 2016", "LIU14": "Liu 2014", "CHI14": "Ching 2014",
    "HAR13": "Hart 2013", "ENC": "ENCODE4", "AUE10": "Auer & Doerge 2010", "LEE10": "Leek 2010",
    "MAR08": "Marioni 2008", "MOR08": "Mortazavi 2008", "WAN09": "Wang 2009", "STA19": "Stark 2019",
    "SEQ14": "SEQC 2014", "LOV14": "Love 2014", "DESV": "viñeta DESeq2", "ROB10": "Robinson 2010",
    "TMM": "Robinson & Oshlack 2010", "LAW14": "Law 2014", "BH95": "Benjamini & Hochberg 1995",
    "BOU10": "Bourgon 2010", "ZHU19": "Zhu 2019", "LOV12": "Lovén 2012", "JIA11": "Jiang 2011",
    "RIS14": "Risso 2014", "LEK07": "Leek & Storey 2007", "ZHN20": "Zhang 2020",
    "SQU21": "Squair 2021", "ZIM21": "Zimmerman 2021", "CRO20": "Crowell 2020",
    "LUE19": "Luecken & Theis 2019", "ZHE17": "Zheng 2017", "PIC14": "Picelli 2014",
    "WOL18": "Wolf 2018", "HAO21": "Hao 2021", "FU18": "Fu 2018", "KIV12": "Kivioja 2012",
    "SMI17": "Smith 2017", "LEV10": "Levin 2010", "PAR09": "Parkhomchuk 2009", "ZHA14": "Zhao 2014",
    "SCR06": "Schroeder 2006", "ILL14": "Illumina 2014", "HAN10": "Hansen 2010", "DOB13": "Dobin 2013",
    "KIM19": "Kim 2019", "PAT17": "Patro 2017", "BRA16": "Bray 2016", "LIA14": "Liao 2014",
    "SON15": "Soneson 2015", "GRA11": "Grabherr 2011", "SHE14": "Shen 2014", "AND12": "Anders 2012",
    "SUB05": "Subramanian 2005", "YOU10": "Young 2010", "LAN08": "Langfelder 2008",
    "NEW19": "Newman 2019", "AND10": "FastQC", "EWE16": "Ewels 2016", "CHE18": "Chen 2018",
    "MAR11": "Martin 2011", "WAN12": "Wang 2012", "OKO16": "Okonechnikov 2016", "EWE20": "Ewels 2020",
    "BUS09": "Bustin 2009", "FGED": "MINSEQE", "FRI12": "Friedländer 2012", "STH16": "Ståhl 2016",
    "CHN15": "Chen 2015", "ING09": "Ingolia 2009", "COR08": "Core 2008", "KWA13": "Kwak 2013",
    "HER17": "Herzog 2017", "GAR18": "Garalde 2018", "GOR15": "Gordon 2015", "SCN95": "Schena 1995",
    "VEL95": "Velculescu 1995", "SHI03": "Shiraki 2003", "GEI08": "Geiss 2008", "ULE03": "Ule 2003",
    "ALP19": "Alpern 2019", "MOL14": "Moll 2014", "WES12": "Westermann 2012",
    "SHA96": "Shalon 1996", "LUN03": "Lundholt 2003",
    "KER98": "Kerr 1998", "NOS18": "Nosek 2018", "SIM11": "Simmons 2011",
    "CHO93": "Chomczynski 1993", "DEA95": "DeAngelis 1995", "ILLDD": "guía de dilución de Illumina",
    "CHA93": "Chang 1993", "KRU11": "Krueger 2011", "ROT11": "Rothberg 2011",
    "GOO16": "Goodwin 2016",
}


def cita(*refs):
    """cita('CON16', 'LOV14') → 'Conesa 2016 · Love 2014'."""
    salida = []
    for r in refs:
        clave, _, pag = r.partition(":")
        salida.append(f"{_CORTOS[clave]} p.{pag}" if pag else _CORTOS[clave])
    return " · ".join(salida)


def claves_fuente(texto):
    """'CON16 LOV14' → ['CON16', 'LOV14'] (para la lista de referencias)."""
    return [r.partition(":")[0] for r in texto.split()]


# ------------------------------------------------------------ bibliotecas
# lect: lecturas que admite · cap: qué puede medir (1 = bien, 0 = nada)
# costo: USD por muestra (extracción + preparación de la biblioteca)
BIBLIOTECAS = {
    "polyA": dict(
        nombre="mRNA-seq poli(A)", corto="poli(A)", costo=170, larga=False,
        resumen="Captura con oligo-dT: solo ARN con cola poli(A) (sobre todo ARNm). "
                "Casi todas las lecturas caen en exones: rinde mucho por lectura.",
        cuando="Expresión diferencial de genes codificantes con ARN íntegro (RIN ≥ 7-8).",
        malo="Pierde ARN sin cola (histonas replicativas, muchos lncRNA, ARN nacientes). "
             "Con ARN degradado la captura se carga al extremo 3′ y se pierden lecturas.",
        fuente="CON16 ZHA14",
    ),
    "ribo": dict(
        nombre="ARN total con ribodepleción", corto="ribodepleción", costo=220, larga=False,
        resumen="Se elimina el ARNr (≈80-90 % del ARN total) con sondas (RNasa H o "
                "captura) y se secuencia todo lo demás: ARNm, lncRNA, ARN sin cola, "
                "intrones de pre-ARNm.",
        cuando="ARN degradado o FFPE (DV200), lncRNA y ARN no poliadenilados, "
               "bacterias (no tienen cola poli(A) estable).",
        malo="Muchas lecturas intrónicas: hace falta más profundidad para la misma "
             "señal exónica.",
        fuente="CON16 ZHA14",
    ),
    "tag3": dict(
        nombre="3′ tag-seq (QuantSeq / BRB-seq)", corto="3′ tag", costo=45, larga=False,
        resumen="Una sola lectura por transcrito cerca del extremo 3′. Una molécula = "
                "una cuenta (no depende de la longitud del gen). Con códigos de barras "
                "tempranos se juntan cientos de muestras en un tubo.",
        cuando="Muchas muestras y pregunta solo de nivel de gen (cribados de fármacos, "
               "series grandes). Basta con 3-10 M lecturas por muestra.",
        malo="No ve isoformas, splicing ni la secuencia completa; necesita buena "
             "anotación del extremo 3′.",
        fuente="MOL14 ALP19",
    ),
    "small": dict(
        nombre="small RNA-seq", corto="small RNA", costo=150, larga=False,
        resumen="Selección por tamaño (18-34 nt) y ligación de adaptadores a los "
                "extremos 3′-OH y 5′-P de miRNA, piRNA, tRF.",
        cuando="miRNA y otros ARN pequeños, incluso en biofluidos (plasma, exosomas).",
        malo="No mide ARNm. Sesgo de ligación por secuencia; UMIs ayudan con poco "
             "material. Profundidad típica 2-10 M lecturas.",
        fuente="CON16 FU18",
    ),
    "sc10x": dict(
        nombre="scRNA-seq en gotas (10x 3′)", corto="scRNA gotas", costo=2200, larga=False,
        resumen="Miles de células por canal, cada una con su código de barras y UMIs. "
                "Mide pocos transcritos por célula (captura ~10-50 %).",
        cuando="Tejidos heterogéneos, tipos celulares raros, composición celular.",
        malo="Caro por muestra, sesgo 3′, abandonos (dropouts). Las células de un mismo "
             "donante NO son réplicas independientes.",
        fuente="ZHE17 LUE19 CON16",
    ),
    "smartseq": dict(
        nombre="Smart-seq2/3 (célula única, completa)", corto="Smart-seq", costo=2600, larga=False,
        resumen="Células en placas (96/384), cDNA de longitud completa con "
                "template switching. Más genes por célula, isoformas.",
        cuando="Pocas células muy caracterizadas, isoformas o SNV en célula única.",
        malo="Poco rendimiento (cientos de células) y caro por célula; sin UMIs en "
             "Smart-seq2.",
        fuente="PIC14",
    ),
    "snrna": dict(
        nombre="snRNA-seq (núcleos)", corto="snRNA", costo=2300, larga=False,
        resumen="Se aíslan núcleos en vez de células: sirve para tejido congelado y "
                "células que no sobreviven a la disociación (neuronas, adipocitos).",
        cuando="Banco de tejido congelado, cerebro, músculo, grasa.",
        malo="Más lecturas intrónicas (pre-ARNm): hay que contar intrones. No ve el "
             "ARN citoplasmático.",
        fuente="LUE19",
    ),
    "largo": dict(
        nombre="Lecturas largas (Iso-Seq / ONT)", corto="lect. largas", costo=900, larga=True,
        resumen="PacBio Iso-Seq (cDNA completo, HiFi) u Oxford Nanopore (cDNA o ARN "
                "directo, que además ve modificaciones). Una lectura = un transcrito "
                "completo.",
        cuando="Isoformas completas, fusiones, transcriptomas nuevos, poliadenilación "
               "alternativa.",
        malo="Menos lecturas por dólar: cuantificar genes poco expresados cuesta más.",
        fuente="GOR15 GAR18 STA19",
    ),
    "espacial": dict(
        nombre="Transcriptómica espacial (Visium)", corto="espacial", costo=6500, larga=False,
        resumen="Cortes de tejido sobre una lámina con puntos de captura con código de "
                "posición: expresión con coordenadas.",
        cuando="Dónde se expresan los genes dentro del tejido (nichos, gradientes).",
        malo="Cada punto mezcla varias células (hay que deconvolucionar). Caro.",
        fuente="STH16",
    ),
}
ORDEN_BIBLIOTECAS = list(BIBLIOTECAS)

# ------------------------------------------------------------- lecturas
# costo: USD por millón de lecturas (o pares) · ventaja en isoformas/splicing
LECTURAS = {
    "SE50": dict(nombre="SE 50", costo=2.0, iso=0.3,
                 texto="Sencilla de 50 nt: barata, basta para contar genes en organismos "
                       "bien anotados y para small RNA."),
    "SE75": dict(nombre="SE 75", costo=2.5, iso=0.4,
                 texto="Sencilla de 75 nt: algo mejor mapeo que 50."),
    "PE100": dict(nombre="PE 2×100", costo=4.0, iso=0.85,
                  texto="Pareada de 2×100: los dos extremos del fragmento ayudan a "
                        "mapear y a ver uniones exón-exón e isoformas."),
    "PE150": dict(nombre="PE 2×150", costo=5.0, iso=1.0,
                  texto="Pareada de 2×150: la mejor de lectura corta para isoformas, "
                        "fusiones y ensamblaje de novo."),
    "LARGA": dict(nombre="larga (≥1 kb)", costo=30.0, iso=1.2,
                  texto="Solo con bibliotecas de lecturas largas: cada lectura cubre el "
                        "transcrito entero. El costo por millón es mucho mayor."),
}
ORDEN_LECTURAS = list(LECTURAS)

PROFUNDIDADES = [1, 2, 5, 10, 20, 30, 50, 80, 100]

# --------------------------------------------------------- fórmulas
# columnas que necesita cada fórmula (ver simulacion.matriz_diseno)
FORMULAS = {
    "cond": dict(nombre="~ condición", texto="Solo la condición. Supone que nada más "
                 "cambia sistemáticamente entre las muestras."),
    "lote": dict(nombre="~ lote + condición", texto="Agrega el lote como covariable: "
                 "la prueba de la condición se hace DENTRO de cada lote. Solo funciona si "
                 "cada lote tiene muestras de todas las condiciones."),
    "par": dict(nombre="~ donante + condición", texto="Diseño pareado: cada donante es "
                "su propio control. Quita la variación entre personas."),
    "par_lote": dict(nombre="~ donante + lote + condición",
                     texto="Pareado y con lote. Exige que el lote no esté anidado en "
                           "el donante."),
    "inter": dict(nombre="~ genotipo + tratamiento + genotipo:tratamiento",
                  texto="Factorial con interacción: el término genotipo:tratamiento "
                        "prueba si el efecto del tratamiento CAMBIA según el genotipo."),
    "aditivo": dict(nombre="~ genotipo + tratamiento", texto="Factorial sin "
                    "interacción: supone que el tratamiento hace lo mismo en los dos "
                    "genotipos."),
    "tiempo": dict(nombre="~ tiempo (factor)", texto="El tiempo como factor de varios "
                   "niveles. Con prueba LRT/F se pregunta si el gen cambia en ALGÚN "
                   "momento."),
    "tiempo_lote": dict(nombre="~ lote + tiempo", texto="Tiempo como factor más el lote."),
}
ORDEN_FORMULAS = list(FORMULAS)

# ------------------------------------------------------ rutas de análisis
RUTAS = {
    "star": dict(nombre="STAR + featureCounts", fuente="DOB13 LIA14",
                 texto="Alineador con splicing contra el genoma; luego se cuentan "
                       "lecturas por gen. Permite descubrir uniones nuevas y hacer QC "
                       "de cobertura. Necesita ~32 GB de RAM para humano."),
    "hisat": dict(nombre="HISAT2 + featureCounts", fuente="KIM19 LIA14",
                  texto="Alineador con splicing de poca memoria (~8 GB). Mismo uso que "
                        "STAR."),
    "salmon": dict(nombre="Salmon / kallisto → tximport", fuente="PAT17 BRA16 SON15",
                   texto="Pseudoalineamiento contra el transcriptoma: muy rápido, "
                         "estima cuentas por transcrito (corrige sesgo de GC y de "
                         "posición) y tximport las resume por gen. No descubre "
                         "transcritos nuevos."),
    "trinity": dict(nombre="Trinity de novo → Salmon", fuente="GRA11 CON16",
                    texto="Ensambla el transcriptoma sin genoma de referencia y luego "
                          "cuantifica contra lo ensamblado. Para organismos sin genoma."),
    "cr_pb": dict(nombre="Cell Ranger/STARsolo → pseudobulk", fuente="ZHE17 SQU21 CRO20",
                  texto="Cuenta UMIs por célula; luego SUMA las células de cada tipo "
                        "celular por muestra (pseudobulk) y prueba con DESeq2/edgeR "
                        "usando a los donantes como réplicas."),
    "cr_cel": dict(nombre="Cell Ranger → Wilcoxon célula a célula", fuente="SQU21 ZIM21",
                   texto="Compara células individuales como si cada una fuera una "
                         "réplica (FindMarkers por defecto)."),
    "mirdeep": dict(nombre="cutadapt + miRDeep2 / miRBase", fuente="FRI12 MAR11",
                    texto="Recorta el adaptador 3′, filtra por tamaño (18-30 nt) y "
                          "cuantifica miRNA conocidos y predice nuevos."),
    "isoseq": dict(nombre="IsoSeq3/minimap2 → SQANTI → cuantificación", fuente="GOR15",
                   texto="Agrupa lecturas largas en isoformas, las clasifica contra la "
                         "anotación y cuenta lecturas por isoforma."),
    "spaceranger": dict(nombre="Space Ranger → deconvolución", fuente="STH16",
                        texto="Cuentas por punto con coordenadas; luego se estima qué "
                              "tipos celulares hay en cada punto."),
}
ORDEN_RUTAS = list(RUTAS)

# ---------------------------------------------------------- entrada / prueba
ENTRADAS = {
    "crudas": dict(nombre="cuentas crudas (normaliza la herramienta)",
                   texto="DESeq2 (razón de medianas) y edgeR (TMM) esperan cuentas "
                         "enteras sin normalizar; ellos calculan el factor de tamaño "
                         "de cada muestra.", fuente="LOV14 TMM"),
    "tpm": dict(nombre="TPM / FPKM",
                texto="Corrigen por longitud y profundidad: sirven para comparar genes "
                      "DENTRO de una muestra, no para modelos de conteo. Dárselos a "
                      "DESeq2/edgeR rompe su modelo de varianza.", fuente="CON16 DESV"),
    "spike": dict(nombre="cuentas crudas + factores de spike-in",
                  texto="Los factores de tamaño se calculan con los ERCC agregados en "
                        "cantidad igual por célula. Necesario cuando cambia el ARN total "
                        "por célula.", fuente="LOV12 JIA11 RIS14"),
}
ORDEN_ENTRADAS = list(ENTRADAS)

PRUEBAS = {
    "deseq2": dict(nombre="DESeq2 (Wald)", fuente="LOV14",
                   texto="Binomial negativa con dispersión compartida entre genes "
                         "(shrinkage) y prueba de Wald por coeficiente."),
    "edger": dict(nombre="edgeR (QL F)", fuente="ROB10",
                  texto="Binomial negativa con dispersión moderada empíricamente; prueba "
                        "cuasi-verosimilitud."),
    "limma": dict(nombre="limma-voom", fuente="LAW14",
                  texto="Transforma a log-CPM con pesos de precisión y usa modelos "
                        "lineales con varianza moderada. Rápido y robusto con n ≥ 3."),
    "lrt": dict(nombre="DESeq2 LRT (modelo completo vs reducido)", fuente="DESV LOV14",
                texto="Compara el modelo completo con uno sin el factor de interés: "
                      "detecta cambios en CUALQUIER nivel (series de tiempo, >2 grupos)."),
    "ttest": dict(nombre="t de Student por gen", fuente="CON16",
                  texto="Una prueba t sin compartir información entre genes. Con 3 "
                        "réplicas la varianza de cada gen es muy inestable."),
    "fc": dict(nombre="solo fold change > 2", fuente="CON16",
               texto="Llamar diferencial a todo lo que cambia más de 2 veces, sin "
                     "estadística. Ignora la variación entre réplicas."),
}
ORDEN_PRUEBAS = list(PRUEBAS)

CORRECCIONES = {
    "bh": dict(nombre="Benjamini-Hochberg (FDR 5 %)", fuente="BH95",
               texto="Controla la proporción esperada de falsos positivos entre los "
                     "genes que llamas significativos. Estándar en ómicas."),
    "bonf": dict(nombre="Bonferroni", fuente="BH95",
                 texto="Controla la probabilidad de UN solo falso positivo: con 20 000 "
                       "pruebas es muy conservadora y pierde potencia."),
    "nada": dict(nombre="ninguna (p < 0.05)", fuente="BH95",
                 texto="Con 20 000 genes y p < 0.05 esperas ~1 000 falsos positivos "
                       "aunque no cambie nada."),
}
ORDEN_CORRECCIONES = list(CORRECCIONES)

# extras: se activan o desactivan. costo por muestra (USD).
EXTRAS = {
    "hebra": dict(nombre="Biblioteca con hebra (dUTP)", costo=15, fuente="LEV10 PAR09",
                  texto="Conserva de qué hebra viene cada ARN. Imprescindible para "
                        "antisentido y genes que se solapan; casi gratis en kits "
                        "modernos."),
    "umi": dict(nombre="UMIs", costo=15, fuente="KIV12 FU18 SMI17",
                texto="Etiqueta cada molécula antes del PCR: los duplicados de PCR se "
                      "quitan sin borrar duplicados biológicos. Útil con poco material, "
                      "FFPE, small RNA y célula única."),
    "ercc": dict(nombre="Spike-ins ERCC", costo=6, fuente="JIA11 LOV12",
                 texto="92 ARN sintéticos en concentraciones conocidas: control de "
                       "calidad (linealidad, límite de detección) y normalización "
                       "cuando cambia el ARN total."),
    "filtro": dict(nombre="Filtrar genes poco expresados", costo=0, fuente="BOU10 CON16",
                   texto="Quitar genes con muy pocas cuentas antes de corregir por "
                         "pruebas múltiples: menos pruebas inútiles, más potencia."),
    "shrink": dict(nombre="Encoger log2FC (apeglm)", costo=0, fuente="ZHU19 DESV",
                   texto="Los fold changes de genes con pocas cuentas son ruidosos; "
                         "encogerlos da rankings y gráficas MA más fiables."),
    "splicing": dict(nombre="Splicing / uso de exones (rMATS, DEXSeq)", costo=0,
                     fuente="SHE14 AND12",
                     texto="Prueba si cambia la inclusión de exones o eventos de "
                           "splicing, no solo el total del gen."),
    "gsea": dict(nombre="Enriquecimiento (GSEA / ORA con goseq)", costo=0,
                 fuente="SUB05 YOU10",
                 texto="Lleva la lista de genes a vías y procesos (GO, KEGG, Hallmark). "
                       "goseq corrige el sesgo por longitud del gen."),
    "decon": dict(nombre="Deconvolución de tipos celulares", costo=0, fuente="NEW19",
                  texto="Estima la proporción de tipos celulares en muestras de bulk "
                        "con una referencia de célula única."),
}
ORDEN_EXTRAS = list(EXTRAS)

# --------------------------------------------------------------- costos
EXTRACCION = 25          # USD por muestra (extracción + QC de ARN)
SC_CELULAS = 5000        # células por muestra en gotas


def lecturas_por_celula(prof_m):
    return round(prof_m * 1e6 / SC_CELULAS)


# multiplica el costo por millón de lecturas según la plataforma
FACTOR_PLATAFORMA = {"miseq": 8.0, "nextseq": 1.6, "novaseq": 1.0, "iontorrent": 3.0,
                     "pacbio": 1.5, "nanopore": 1.0}


def costo_secuenciacion(dis):
    """USD por muestra en secuenciación."""
    f = FACTOR_PLATAFORMA.get(dis.get("plataforma"), 1.0)
    return LECTURAS[dis["lectura"]]["costo"] * dis["profundidad"] * f


def costo_muestra(dis):
    b = BIBLIOTECAS[dis["biblioteca"]]
    extra = sum(EXTRAS[e]["costo"] for e in dis["extras"])
    return EXTRACCION + b["costo"] + extra + costo_secuenciacion(dis)


def n_muestras(dis, caso):
    """Bibliotecas que se secuencian (incluye réplicas técnicas)."""
    return len(caso["grupos"]) * dis["replicas"] * dis["tecnicas"]


def costo_total(dis, caso):
    return round(costo_muestra(dis) * n_muestras(dis, caso))
