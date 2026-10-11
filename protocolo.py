"""Genera el protocolo completo de un experimento en Markdown, más la hoja de
muestras en CSV, a partir del diseño de la mesa.

Se guarda en ~/Documents/reviewer2-protocols/ (o ~/Documentos/ si existe). Cada sección se adapta a la
biblioteca, la lectura, la ruta de análisis, la fórmula y los extras
elegidos, y lleva las fuentes al final.
"""

import datetime
import os
import random
import re

import datos
import simulacion as sim
from idioma import tr

_DOCS = os.path.expanduser("~/Documentos")
if not os.path.isdir(_DOCS):
    _DOCS = os.path.expanduser("~/Documents")
CARPETA = os.path.join(_DOCS, "reviewer2-protocols")
if os.path.isdir(os.path.expanduser("~/Documentos/revisor2-protocolos")):   # nombre anterior
    CARPETA = os.path.expanduser("~/Documentos/revisor2-protocolos")

FORMULA_R = {
    "cond": "~ condicion", "lote": "~ lote + condicion", "par": "~ donante + condicion",
    "par_lote": "~ donante + lote + condicion",
    "inter": "~ genotipo + tratamiento + genotipo:tratamiento",
    "aditivo": "~ genotipo + tratamiento", "tiempo": "~ tiempo",
    "tiempo_lote": "~ lote + tiempo",
}
REDUCIDA_R = {"tiempo": "~ 1", "tiempo_lote": "~ lote", "cond": "~ 1", "lote": "~ lote",
              "par": "~ donante", "par_lote": "~ donante + lote",
              "inter": "~ genotipo + tratamiento", "aditivo": "~ genotipo"}


def _slug(texto):
    t = texto.lower()
    for a, b in zip("áéíóúñü", "aeiounu"):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:40] or "experimento"


def hoja_muestras(dis, caso, semilla=1):
    """Filas de la hoja de muestras con orden de procesamiento aleatorio
    dentro de cada lote."""
    rng = random.Random(semilla)
    filas = []
    for m in sim.muestras(dis, caso):
        f = dict(id=m["nombre"], grupo=caso["grupos"][m["grupo"]],
                 replica_biologica=m["rep"] + 1, replica_tecnica=m["tec"] + 1,
                 lote=m["lote"] + 1)
        if caso.get("pareado"):
            f["donante"] = f"D{m['donante'] + 1}"
        if caso.get("factores"):
            f["genotipo"] = ["WT", "KO"][caso["factores"]["genotipo"][m["grupo"]]]
            f["tratamiento"] = ["control", "tratado"][caso["factores"]["tratamiento"][m["grupo"]]]
        filas.append(f)
    for lote in {f["lote"] for f in filas}:
        del_lote = [f for f in filas if f["lote"] == lote]
        orden = list(range(1, len(del_lote) + 1))
        rng.shuffle(orden)
        for f, o in zip(del_lote, orden):
            f["orden_en_lote"] = o
    for i, f in enumerate(filas):
        f["indice_UDI"] = f"UDI{i + 1:03d}"
    return filas


def _tabla(filas):
    cols = list(filas[0])
    lineas = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for f in filas:
        lineas.append("| " + " | ".join(tr(str(f[c])) for c in cols) + " |")
    return "\n".join(lineas)


def _csv(filas):
    cols = list(filas[0])
    return "\n".join([",".join(cols)] + [",".join(str(f[c]) for c in cols) for f in filas]) + "\n"


# ------------------------------------------------------------- secciones
def _muestreo(dis, caso):
    lib = dis["biblioteca"]
    p = ["- Registrar para cada muestra: ID, grupo, fecha y hora, operador, tiempo de "
         "isquemia, sexo, edad y cualquier covariable (será el `colData`).",
         "- Tomar todas las muestras a la misma hora del día y con el mismo protocolo.",
         "- Procesar en el orden aleatorio de la hoja de muestras, nunca grupo por grupo."]
    if caso.get("rin", 9) < 4:
        p += ["- **FFPE:** cortar 4-5 secciones de 5-10 µm del bloque (desechar la "
              "primera); macrodisección si el contenido tumoral es < 50 %.",
              "- Desparafinar (xileno o aceite mineral) y digerir con proteinasa K; el "
              "calor revierte parte de los entrecruzamientos de formalina."]
    elif lib in ("sc10x", "smartseq"):
        p += ["- **Célula única:** disociación enzimática corta y en frío (≤ 30 min); "
              "filtrar a 40 µm; viabilidad ≥ 80 % (azul de tripano o AO/PI).",
              "- Contar células y cargar ~10 000 por canal para recuperar ~5 000.",
              "- Procesar todas las condiciones el mismo día o en lotes balanceados; "
              "considerar hashing (CellPlex/HTO) para multiplexar donantes."]
    elif lib == "snrna":
        p += ["- **Núcleos:** tejido congelado a −80 °C; homogeneizar en buffer de lisis "
              "con inhibidor de RNasas, filtrar y lavar; teñir con DAPI y contar.",
              "- Opcional: FANS para quitar restos."]
    elif lib == "small" and caso.get("poco_material"):
        p += ["- **Plasma:** tubos EDTA, centrifugar en < 2 h (doble centrifugación para "
              "quitar plaquetas). Registrar hemólisis (A414 o miR-451a/miR-23a).",
              "- Alícuotas a −80 °C; evitar ciclos de congelación."]
    elif lib == "espacial":
        p += ["- **Espacial:** tejido fresco incluido en OCT y congelado en isopentano; "
              "cortes de 10 µm sobre la lámina; optimizar el tiempo de permeabilización."]
    else:
        p += ["- Congelar en nitrógeno líquido (o RNAlater, o directo en TRIzol) y guardar "
              "a −80 °C."]
    if "ercc" in dis["extras"] and caso["objetivo"] == "global":
        p.append("- **Contar las células** de cada muestra: los spike-ins se agregarán "
                 "por número de células (p. ej. 1 µL de dilución 1:100 de ERCC por cada "
                 "10^6 células), no por masa de ARN.")
    return p


def _extraccion(dis, caso):
    lib = dis["biblioteca"]
    if lib == "small":
        return ["- Kit que conserve ARN < 200 nt (miRNeasy Serum/Plasma, o TRIzol LS con "
                "glucógeno como acarreador).",
                "- Agregar un spike-in sintético (cel-miR-39) para controlar la "
                "eficiencia de extracción.",
                "- Eluir en volumen pequeño (14 µL)."]
    if lib in ("sc10x", "smartseq", "snrna"):
        return ["- No hay extracción de ARN: las células o núcleos entran directo al "
                "chip / placa; la retrotranscripción ocurre dentro de la gota o el pozo."]
    if caso.get("rin", 9) < 4:
        return ["- Kit específico para FFPE (p. ej. RNeasy FFPE o equivalente) con "
                "digestión de proteinasa K y DNasa en columna.",
                "- Esperar rendimientos bajos y fragmentos cortos: medir DV200."]
    return ["- TRIzol / fenol-cloroformo o columna de sílice, igual para todas las "
            "muestras.",
            "- DNasa I (en columna o en solución) para quitar ADN genómico.",
            "- Trabajar libre de RNasas; eluir en agua sin nucleasas; −80 °C."]


def _qc_arn(dis, caso):
    p = ["- Cantidad: Qubit RNA HS/BR.",
         "- Pureza: NanoDrop A260/280 ≈ 2.0 y A260/230 > 1.8."]
    if caso.get("rin", 9) < 4:
        p.append("- Integridad: **DV200** en Bioanalyzer/TapeStation. Aceptar ≥ 30 %; "
                 "con 30-50 % aumentar la entrada de ARN. (El RIN no es informativo en FFPE.)")
    elif dis["biblioteca"] == "small":
        p.append("- Perfil de ARN pequeño (Bioanalyzer Small RNA chip). En plasma la "
                 "concentración suele estar por debajo del límite: usar volumen fijo.")
    elif dis["biblioteca"] in ("sc10x", "snrna", "smartseq"):
        p.append("- En lugar de RIN: viabilidad celular ≥ 80 %, sin agregados; después, "
                 "perfil del cDNA amplificado (Bioanalyzer).")
    else:
        minimo = 7 if dis["biblioteca"] != "polyA" else 8
        p.append(f"- Integridad: RIN ≥ {minimo} (Bioanalyzer/TapeStation). Si el RIN "
                 "varía entre grupos, incluirlo como covariable.")
    return p


def _biblioteca(dis, caso):
    lib = dis["biblioteca"]
    b = datos.BIBLIOTECAS[lib]
    hebra = "hebra" in dis["extras"]
    p = [f"**{tr(b['nombre'])}.** {tr(b['resumen'])}", ""]
    if lib in ("polyA", "ribo"):
        p += [tr("1. Entrada: 100 ng - 1 µg de ARN total (según el kit).")
              + (tr(" Agregar spike-ins ERCC (Mezcla 1) antes de empezar.") if "ercc" in dis["extras"] else ""),
              "2. " + tr("Captura de ARN poli(A) con perlas oligo-dT (dos rondas)."
                          if lib == "polyA" else
                          "Ribodepleción con sondas + RNasa H (incluye ARNr mitocondrial)."),
              tr("3. Fragmentación (calor + Mg²+) a ~200-300 nt")
              + (tr(" (acortar o saltar si el ARN ya está degradado).") if caso.get("rin", 9) < 4 else "."),
              "4. Primera hebra con hexámeros al azar.",
              tr("5. Segunda hebra ") + tr("con dUTP (biblioteca con hebra)." if hebra else "(sin hebra)."),
              tr("6. Reparación de extremos, cola A y ligación de adaptadores con índices "
                 "dobles únicos") + (tr(" y UMIs.") if "umi" in dis["extras"] else "."),
              "7. " + (tr("Digestión de la hebra con U (UDG). ") if hebra else "")
              + tr("PCR de enriquecimiento con el menor número de ciclos posible."),
              "8. Limpieza con perlas (0.8-1×)."]
    elif lib == "tag3":
        p += ["1. Retrotranscripción con oligo-dT que lleva código de barras de muestra "
              "(y UMI); todas las muestras se juntan después de este paso.",
              "2. Segunda hebra / tagmentación; PCR con índice de placa.",
              "3. Limpieza con perlas. Una biblioteca contiene hasta 96-384 muestras."]
    elif lib == "small":
        p += [tr("1. Ligación del adaptador 3′ (pre-adenilado, sin ATP) y del 5′")
              + (tr(" con UMIs.") if "umi" in dis["extras"] else "."),
              "2. Retrotranscripción y PCR con índices.",
              "3. Selección de tamaño en gel o perlas: insertos de 18-34 nt (banda de "
              "~140-150 pb con adaptadores).",
              "4. Biblioteca de baja diversidad: usar ≥ 10-20 % de PhiX."]
    elif lib in ("sc10x", "snrna"):
        p += ["1. Cargar células/núcleos en el chip (Chromium) con perlas de gel; cada "
              "gota: célula + perla con código celular + UMI + oligo-dT.",
              "2. Retrotranscripción en la gota, romper la emulsión, amplificar cDNA.",
              "3. Fragmentación, ligación de adaptadores e índice de muestra.",
              f"4. Profundidad: {datos.lecturas_por_celula(dis['profundidad']):,} lecturas "
              "por célula aproximadas (meta ≥ 20 000)."]
    elif lib == "smartseq":
        p += ["1. Clasificar células individuales por FACS en placas con buffer de lisis.",
              "2. Oligo-dT + template switching oligo → cDNA de longitud completa; "
              "preamplificación.",
              "3. Tagmentación (Nextera) e índices por pozo."]
    elif lib == "largo":
        p += ["1. cDNA de longitud completa (template switching) o ARN directo (ONT).",
              "2. PacBio: bibliotecas SMRTbell, Kinnex/MAS-Seq para más lecturas; ONT: "
              "kit de cDNA con códigos de barras o kit de ARN directo.",
              "3. QC de longitud (Femto Pulse / Bioanalyzer)."]
    elif lib == "espacial":
        p += ["1. Tinción H&E e imagen de alta resolución del corte.",
              "2. Permeabilización (tiempo optimizado), captura del ARN en los puntos, "
              "retrotranscripción en la lámina.",
              "3. Liberar el cDNA, amplificar y construir la biblioteca con índices."]
    return p


def _secuenciacion(dis, caso, n):
    lect = datos.LECTURAS[dis["lectura"]]
    total = n * dis["profundidad"]
    p = ["- QC de bibliotecas: tamaño (Bioanalyzer/TapeStation) y concentración molar "
         "(qPCR KAPA). Sin dímeros de adaptador.",
         "- Pooling equimolar de todas las bibliotecas; índices dobles únicos (UDI).",
         f"- Lectura: **{lect['nombre']}**. Profundidad: **{dis['profundidad']} M** "
         f"{'pares de ' if dis['lectura'].startswith('PE') else ''}lecturas por muestra "
         f"→ {total:,} M en total (+10-20 % de margen).",
         "- Todas las muestras en todos los carriles (o carriles balanceados por grupo).",
         "- PhiX 1-5 % (más si la biblioteca es de baja diversidad).",
         tr("- Demultiplexar con bcl-convert → `muestra_R1.fastq.gz`")
         + (tr(", `muestra_R2.fastq.gz`.") if dis["lectura"].startswith("PE") else ".")]
    if dis["lectura"] == "LARGA":
        p[2] = (f"- Plataforma de lectura larga (PacBio Revio/Sequel IIe u ONT). "
                f"{dis['profundidad']} M lecturas por muestra.")
    return p


def _comandos(dis, caso):
    pe = dis["lectura"].startswith("PE")
    r2 = " -I fastq/{m}_R2.fastq.gz -O trim/{m}_R2.fq.gz" if pe else ""
    s = 2 if "hebra" in dis["extras"] else 0
    ruta = dis["ruta"]
    b = ["```bash",
         "# 1. Control de calidad",
         "mkdir -p qc trim",
         "fastqc -t 8 -o qc/ fastq/*.fastq.gz",
         "",
         "# 2. Recorte de adaptadores y calidad"]
    if ruta == "mirdeep":
        b += ["for m in $(cat muestras.txt); do",
              "  cutadapt -a TGGAATTCTCGGGTGCCAAGG -m 18 -M 30 -q 20 \\",
              "    -o trim/$m.fq.gz fastq/${m}_R1.fastq.gz",
              "done"]
        if "umi" in dis["extras"]:
            b += ["# UMIs: extraer antes de alinear y deduplicar después",
                  "umi_tools extract --bc-pattern=NNNNNNNNNNNN -I trim/$m.fq.gz -S trim/$m.umi.fq.gz"]
        b += ["", "# 3. Cuantificación de miRNA",
              "mapper.pl todas.fa -c -j -l 18 -m -p genoma_idx -s collapsed.fa -t reads.arf",
              "miRDeep2.pl collapsed.fa genoma.fa reads.arf mature_hsa.fa none hairpin_hsa.fa",
              "quantifier.pl -p hairpin_hsa.fa -m mature_hsa.fa -r collapsed.fa"]
    elif ruta in ("cr_pb", "cr_cel"):
        b += ["# (no hace falta recortar: Cell Ranger lo maneja)", "",
              "# 3. Cuentas por célula",
              "cellranger count --id=$m --transcriptome=refdata-gex-GRCh38 \\",
              "  --fastqs=fastq/ --sample=$m --create-bam=true"
              + (" --include-introns=true" if dis["biblioteca"] == "snrna" else ""),
              "# alternativa abierta: STAR --soloType CB_UMI_Simple (STARsolo)"]
    elif ruta == "trinity":
        b += ["for m in $(cat muestras.txt); do",
              f"  fastp -i fastq/${{m}}_R1.fastq.gz -o trim/${{m}}_R1.fq.gz{r2.format(m='${m}')} \\",
              "    --detect_adapter_for_pe -q 20 -l 25",
              "done", "",
              "# 3. Ensamblaje de novo con TODAS las muestras",
              "Trinity --seqType fq --max_memory 100G --CPU 16 \\",
              "  --samples_file muestras_trinity.txt"
              + (" --SS_lib_type RF" if "hebra" in dis["extras"] else "")
              + " --output trinity_out",
              "BUSCO -i trinity_out.Trinity.fasta -l metazoa_odb10 -m transcriptome -o busco",
              "TransDecoder.LongOrfs -t trinity_out.Trinity.fasta",
              "# anotación: DIAMOND blastx contra UniProt + Trinotate", "",
              "# 4. Cuantificación por muestra contra el ensamblaje",
              "salmon index -t trinity_out.Trinity.fasta -i trinity_idx",
              "salmon quant -i trinity_idx -l A -1 trim/${m}_R1.fq.gz -2 trim/${m}_R2.fq.gz -o salmon/${m}"]
    elif ruta == "isoseq":
        b += ["# PacBio", "isoseq refine $m.fl.bam primers.fasta $m.flnc.bam --require-polya",
              "isoseq cluster2 todas.flnc.fofn agrupadas.bam",
              "pbmm2 align genoma.fa agrupadas.bam alineadas.bam --preset ISOSEQ --sort",
              "isoseq collapse alineadas.bam colapsadas.gff",
              "sqanti3_qc.py colapsadas.gff anotacion.gtf genoma.fa",
              "# ONT: minimap2 -ax splice -uf genoma.fa lecturas.fq | samtools sort > $m.bam",
              "# cuantificación por isoforma: bambu / IsoQuant"]
    elif ruta == "spaceranger":
        b += ["spaceranger count --id=$m --transcriptome=refdata-gex-GRCh38 \\",
              "  --fastqs=fastq/ --image=$m.tif --slide=SLIDE --area=A1"]
    else:
        # índices una sola vez; luego, por muestra: recorte → alineamiento
        if ruta == "star":
            b[-1:] = ["# 2. Índice del genoma (una vez)",
                      "STAR --runMode genomeGenerate --genomeDir star_idx --runThreadN 16 \\",
                      "  --genomeFastaFiles genoma.fa --sjdbGTFfile anotacion.gtf --sjdbOverhang 100"]
        elif ruta == "hisat":
            b[-1:] = ["# 2. Índice del genoma (una vez)",
                      "hisat2-build -p 16 genoma.fa hisat_idx"]
        else:
            b[-1:] = ["# 2. Índice del transcriptoma con señuelos del genoma (una vez)",
                      "salmon index -t gentrome.fa -d decoys.txt -i salmon_idx -k 31"]
        b += ["", "# 3. Por muestra: recorte de adaptadores y alineamiento / cuantificación",
              "mkdir -p bam salmon",
              "for m in $(cat muestras.txt); do",
              f"  fastp -i fastq/${{m}}_R1.fastq.gz -o trim/${{m}}_R1.fq.gz{r2.format(m='${m}')} \\",
              "    --detect_adapter_for_pe -q 20 -l 25 -h qc/${m}.fastp.html"]
        if ruta == "star":
            b += ["  STAR --runThreadN 16 --genomeDir star_idx --readFilesCommand zcat \\",
                  "    --readFilesIn trim/${m}_R1.fq.gz" + (" trim/${m}_R2.fq.gz" if pe else "") + " \\",
                  "    --outSAMtype BAM SortedByCoordinate --outFileNamePrefix bam/${m}_",
                  "  mv bam/${m}_Aligned.sortedByCoord.out.bam bam/${m}.bam"]
        elif ruta == "hisat":
            b += ["  hisat2 -p 16 -x hisat_idx " + ("-1 trim/${m}_R1.fq.gz -2 trim/${m}_R2.fq.gz"
                                                    if pe else "-U trim/${m}_R1.fq.gz")
                  + (" --rna-strandness RF" if "hebra" in dis["extras"] and pe else "")
                  + " | samtools sort -o bam/${m}.bam"]
        else:
            b += ["  salmon quant -i salmon_idx -l A " + ("-1 trim/${m}_R1.fq.gz -2 trim/${m}_R2.fq.gz"
                                                          if pe else "-r trim/${m}_R1.fq.gz")
                  + " --validateMappings --gcBias --seqBias -p 8 -o salmon/${m}"]
        if ruta in ("star", "hisat"):
            b += ["  samtools index bam/${m}.bam"]
            if "umi" in dis["extras"]:
                b += ["  umi_tools dedup -I bam/${m}.bam -S bam/${m}.dedup.bam"
                      + (" --paired" if pe else "")]
        b += ["done"]
        if ruta in ("star", "hisat"):
            b += ["", "# 4. Cuentas por gen",
                  f"featureCounts -T 8 {'-p --countReadPairs ' if pe else ''}-s {s} "
                  "-a anotacion.gtf -o cuentas.txt bam/*.bam"]
            if "splicing" in dis["extras"]:
                b += ["", "# 5. Splicing",
                      "rmats.py --b1 grupo1.txt --b2 grupo2.txt --gtf anotacion.gtf \\",
                      f"  -t {'paired' if pe else 'single'} --readLength "
                      f"{dis['lectura'][2:] or 100} --libType "
                      f"{'fr-firststrand' if 'hebra' in dis['extras'] else 'fr-unstranded'} "
                      "--od rmats_out --tmp rmats_tmp",
                      "# DEXSeq: dexseq_prepare_annotation.py + dexseq_count.py por muestra"]
    b += ["", "# QC de todo junto",
          "multiqc .",
          "```",
          "",
          "Alternativa reproducible de todo el preprocesamiento: "
          "`nextflow run nf-core/rnaseq -profile docker --input samplesheet.csv "
          "--genome GRCh38 --aligner star_salmon` (para bulk)."]
    return b


def _codigo_r(dis, caso):
    ruta = dis["ruta"]
    formula = dis["formula"]
    fr = FORMULA_R[formula]
    k = len(caso["grupos"])
    ref, trat = caso["grupos"][0], caso["grupos"][-1]
    var = "tiempo" if formula.startswith("tiempo") else "condicion"
    r = ["```r", "library(DESeq2)", ""]
    r.append('coldata <- read.csv("muestras.csv")')
    r.append(f'coldata${var} <- factor(coldata$grupo, levels = c('
             + ", ".join(f'"{g}"' for g in caso["grupos"]) + "))")
    if formula in ("lote", "par_lote", "tiempo_lote"):
        r.append("coldata$lote <- factor(coldata$lote)")
    if formula in ("par", "par_lote"):
        r.append("coldata$donante <- factor(coldata$donante)")
    if formula in ("inter", "aditivo"):
        r += ['coldata$genotipo <- factor(coldata$genotipo, levels = c("WT", "KO"))',
              'coldata$tratamiento <- factor(coldata$tratamiento, levels = c("control", "tratado"))']
    r.append("")
    if ruta == "salmon" or ruta == "trinity":
        r += ["library(tximport)",
              'archivos <- file.path("salmon", coldata$id, "quant.sf")',
              "names(archivos) <- coldata$id",
              ("txi <- tximport(archivos, type = \"salmon\", tx2gene = tx2gene)"
               if ruta == "salmon" else
               "txi <- tximport(archivos, type = \"salmon\", tx2gene = trinity_gene_map)"),
              f"dds <- DESeqDataSetFromTximport(txi, coldata, design = {fr})"]
    elif ruta in ("cr_pb", "cr_cel"):
        r += ["# pseudobulk: sumar las células de un tipo celular por muestra",
              "library(SingleCellExperiment); library(muscat)",
              "sce <- prepSCE(sce, kid = \"tipo_celular\", gid = \"grupo\", sid = \"id\")",
              "pb <- aggregateData(sce, assay = \"counts\", fun = \"sum\", by = c(\"cluster_id\", \"sample_id\"))",
              "cuentas <- assay(pb, \"transicional\")   # el tipo celular de interés",
              f"dds <- DESeqDataSetFromMatrix(cuentas, coldata, design = {fr})"]
    elif ruta == "mirdeep":
        r += ['cuentas <- read.delim("miRNAs_expressed_all_samples.csv", row.names = 1)',
              f"dds <- DESeqDataSetFromMatrix(round(cuentas), coldata, design = {fr})"]
    else:
        r += ['fc <- read.delim("cuentas.txt", comment.char = "#", row.names = 1)',
              "cuentas <- as.matrix(fc[, -(1:5)])",
              "colnames(cuentas) <- coldata$id",
              f"dds <- DESeqDataSetFromMatrix(cuentas, coldata, design = {fr})"]
    if dis["entrada"] == "tpm":
        r.append("# ¡OJO! DESeq2 necesita cuentas, no TPM/FPKM (ver dictamen del Revisor 2).")
    if "filtro" in dis["extras"]:
        n_min = max(3, dis["replicas"])
        r += ["", "# filtrar genes con muy pocas cuentas",
              f"dds <- dds[rowSums(counts(dds) >= 10) >= {n_min}, ]"]
    if dis["entrada"] == "spike":
        r += ["", "# normalización con spike-ins (cambia el ARN total por célula)",
              'ercc <- grepl("^ERCC-", rownames(dds))',
              "dds <- estimateSizeFactors(dds, controlGenes = ercc)",
              "dds <- dds[!ercc, ]"]
    if dis["tecnicas"] > 1:
        r += ["", "# sumar réplicas técnicas (no son muestras independientes)",
              "dds <- collapseReplicates(dds, groupby = paste(dds$grupo, dds$replica_biologica))"]
    r += ["", "# exploración",
          "vsd <- vst(dds, blind = TRUE)",
          'plotPCA(vsd, intgroup = c("' + var + '"'
          + (', "lote"' if formula in ("lote", "par_lote", "tiempo_lote") else "") + "))", ""]
    padj = {"bh": "BH", "bonf": "bonferroni", "nada": "none"}[dis["correccion"]]
    if dis["prueba"] == "lrt":
        r += [f"dds <- DESeq(dds, test = \"LRT\", reduced = {REDUCIDA_R.get(formula, '~ 1')})",
              "res <- results(dds, alpha = 0.05)"]
    elif dis["prueba"] == "edger":
        r = r[:-1] + ["library(edgeR)",
                      "y <- DGEList(counts(dds), group = coldata$grupo)",
                      "y <- calcNormFactors(y)    # TMM",
                      f"diseno <- model.matrix({fr}, data = coldata)",
                      "y <- estimateDisp(y, diseno)",
                      "ajuste <- glmQLFit(y, diseno)",
                      "prueba <- glmQLFTest(ajuste, coef = ncol(diseno))",
                      f"res <- topTags(prueba, n = Inf, adjust.method = \"{padj}\")"]
    elif dis["prueba"] == "limma":
        r = r[:-1] + ["library(limma); library(edgeR)",
                      "y <- calcNormFactors(DGEList(counts(dds)))",
                      f"diseno <- model.matrix({fr}, data = coldata)",
                      "v <- voom(y, diseno, plot = TRUE)",
                      "ajuste <- eBayes(lmFit(v, diseno))",
                      f"res <- topTable(ajuste, coef = ncol(diseno), number = Inf, adjust.method = \"{padj}\")"]
    else:
        r.append("dds <- DESeq(dds)")
        if formula == "inter":
            r += ["resultsNames(dds)",
                  'res <- results(dds, name = "genotipoKO.tratamientotratado", alpha = 0.05)']
        elif formula.startswith("tiempo") or k > 2:
            r += [f'res <- results(dds, contrast = c("{var}", "{trat}", "{ref}"), alpha = 0.05)',
                  "# para cada grupo frente a la referencia, repetir el contraste"]
        else:
            r += [f'res <- results(dds, contrast = c("{var}", "{trat}", "{ref}"), alpha = 0.05)']
        if dis["correccion"] != "bh":
            r.append(f'res$padj <- p.adjust(res$pvalue, method = "{padj}")')
    if "shrink" in dis["extras"] and dis["prueba"] in ("deseq2",):
        coef = ("genotipoKO.tratamientotratado" if formula == "inter"
                else f"{var}_{_r(trat)}_vs_{_r(ref)}")
        r += ["library(apeglm)",
              f'res_shr <- lfcShrink(dds, coef = "{coef}", type = "apeglm")',
              "plotMA(res_shr, ylim = c(-4, 4))"]
    r += ["summary(res)",
          'write.csv(as.data.frame(res[order(res$padj), ]), "resultados_DE.csv")']
    if "gsea" in dis["extras"]:
        r += ["", "# enriquecimiento: GSEA con todos los genes ordenados",
              "library(fgsea); library(msigdbr)",
              'hallmark <- split(msigdbr(species = "Homo sapiens", category = "H")$gene_symbol,',
              '                  msigdbr(species = "Homo sapiens", category = "H")$gs_name)',
              "rangos <- sort(setNames(res$stat, rownames(res)), decreasing = TRUE)",
              "gsea <- fgsea(hallmark, rangos, minSize = 15, maxSize = 500)",
              "# ORA con corrección por longitud: goseq(nullp(de_vector, \"hg38\", \"ensGene\"))",
              "# universo = genes PROBADOS, no todo el genoma"]
    if "decon" in dis["extras"]:
        r += ["", "# deconvolución: CIBERSORTx / MuSiC con una referencia de célula única"]
    r.append("```")
    return r


def _r(nombre):
    return re.sub(r"[^A-Za-z0-9.]", ".", nombre)


def _criterios(dis, caso):
    filas = [
        ("ARN", "RIN ≥ 7 (DV200 ≥ 30 % en FFPE); A260/280 ≈ 2.0", "repetir extracción"),
        ("Biblioteca", "pico 300-400 pb, sin dímeros de adaptador", "limpieza extra"),
        ("Lecturas", f"≥ {int(dis['profundidad'] * 0.8)} M por muestra, Q30 ≥ 80 %", "resecuenciar"),
        ("Alineamiento", "70-90 % alineado (humano); hebra coherente con el kit", "revisar especie/kit"),
        ("Cobertura", "sin sesgo 3′ fuerte; ARNr < 5 % (poli(A))", "anotar como covariable"),
        ("Réplicas", "Spearman > 0.9 (isogénicas) / > 0.8 (entre donantes)", "investigar la muestra"),
        ("PCA", "PC1/PC2 no explicados por lote, fecha o RIN", "covariable o SVA/RUV"),
    ]
    out = ["| Paso | Criterio | Si falla |", "|---|---|---|"]
    out += [f"| {a} | {b} | {c} |" for a, b, c in filas]
    return out


# ------------------------------------------------------------------ todo
def _lab_hipotesis(exp, caso):
    import expediente as X
    info = X.info(caso)
    out = []
    if exp.get("hipotesis") is not None:
        original = exp.get("hipotesis_original")
        original = exp["hipotesis"] if original is None else original
        out.append(f"- **Hipótesis (registrada antes del experimento):** "
                   f"{info['hipotesis'][original]}")
        if exp.get("harking"):
            out.append(f"- **Hipótesis posterior a los datos ({'exploratoria' if exp.get('exploratorio') else 'NO declarada'}):** "
                       f"{info['hipotesis'][exp['hipotesis']]}")
    if exp.get("unidad") is not None:
        import lab_datos as L
        out.append(f"- **Unidad experimental elegida:** {L.UNIDADES[info['lugar']][exp['unidad']]}")
    if exp.get("asignacion"):
        out.append(tr("- **Asignación de tratamientos:** ")
                   + tr({"azar": "sorteo aleatorio", "orden": "por orden (no aleatoria)",
                         "ojo": "a criterio del investigador (no aleatoria)"}[exp["asignacion"]]))
    if exp.get("registros"):
        out.append(tr("- **Se registra por muestra:** ") + ", ".join(tr(r) for r in exp["registros"]))
    return out


def _lab_extraccion(exp):
    import lab_datos as L
    met = exp.get("extraccion")
    if not met:
        return []
    e = L.EXTRACCIONES[met]
    p = exp.get("pasos", {})
    out = [f"- **Método usado:** {e['nombre']}. {e['texto']}"]
    if "limpieza" in p:
        out.append(tr("- Área libre de RNasas: ") + tr("sí (RNaseZap, puntas con filtro)." if p["limpieza"]
                                                       else "**no** (riesgo de degradación)."))
    if "fase" in p and met in ("trizol", "ctab"):
        out.append(f"- Fase recuperada: {p['fase']}; precipitación con {p.get('alcohol')}; "
                   f"secado: {'correcto' if p.get('secado') != 'seco' else 'excesivo'}.")
    if "dnasa" in p:
        out.append(tr("- DNasa I: ") + tr("sí." if p["dnasa"] else "**no**."))
    return out


def _lab_qc(exp, caso):
    qc = exp.get("qc") or {}
    if not qc:
        return []
    filas = []
    for k, q in qc.items():
        g, r = k.split("-")
        nombre = f"{caso['abrev'][int(g)]}{int(r) + 1}"
        if "viabilidad" in q:
            filas.append(f"| {nombre} | viabilidad {q['viabilidad']} % | | | | {tr(q['estado'])} |")
        else:
            filas.append(f"| {nombre} | {q['ng']} | {q['r280']} | {q['r230']} | "
                         f"{q['rin']} | {tr(q['estado'])}{tr(' (ADNg)') if q['gdna'] else ''} |")
    return ["", "### QC registrado", "",
            "| muestra | ng/µL | A260/280 | A260/230 | RIN | decisión |",
            "|---|---|---|---|---|---|"] + filas


def _traducir_md(md):
    """Traduce el protocolo menos el código: dentro de ``` solo los comentarios
    de línea completa. El código usa las columnas y niveles de la hoja de
    muestras (condicion, Vehículo…), que se exporta en español; traducirlo
    dejaba un script que no corría."""
    salida, en_codigo = [], False
    for l in md:
        if l.startswith("```"):
            en_codigo = not en_codigo
            salida.append(l)
        elif en_codigo and not l.lstrip().startswith("#"):
            salida.append(l)
        elif l.startswith("| id |"):
            # la hoja de muestras: _tabla ya tradujo las celdas y las columnas
            # son las del CSV
            salida.append(l)
        else:
            salida.append(tr(l))
    return salida


def generar(dis, caso, comentarios=None, resultado=None, dificultad="normal", exp=None,
            autor=None):
    """Escribe el .md y el .csv; devuelve la ruta del .md."""
    exp = exp or {}
    dis = datos.provisional(dis)
    os.makedirs(CARPETA, exist_ok=True)
    hoy = datetime.date.today().isoformat()
    base = f"{hoy}-{_slug(caso['titulo'] if not caso.get('libre') else caso['organismo'])}"
    ruta_md = os.path.join(CARPETA, base + ".md")
    i = 2
    while os.path.exists(ruta_md):
        ruta_md = os.path.join(CARPETA, f"{base}-{i}.md")
        i += 1
    ruta_csv = ruta_md[:-3] + "-muestras.csv"
    filas = hoja_muestras(dis, caso)
    n = len(filas)
    b = datos.BIBLIOTECAS[dis["biblioteca"]]
    costo = datos.costo_total(dis, caso)
    pot = sim.potencia_aprox(dis, caso)
    refs = set()

    def cit(*ks):
        refs.update(k.partition(":")[0] for k in ks)
        return "(" + datos.cita(*ks) + ")" if ks else ""

    md = [f"# Protocolo de transcriptómica: {caso['pregunta'] if not caso.get('libre') else caso['organismo']}",
          "",
          (tr(f"*Responsable: {autor}.* ") if autor else "") +
          tr(f"*Generado por REVISOR 2 el {hoy}.* Organismo: **{caso['organismo']}**. "
             f"Muestra: {caso['muestra']}."),
          "",
          "## 1. Pregunta y unidad experimental",
          "",
          f"- **Pregunta:** {caso['pregunta']}",
          f"- **Grupos:** {', '.join(caso['grupos'])} (referencia: {caso['grupos'][0]}).",
          tr("- **Unidad experimental / réplica biológica:** ")
          + tr("cada donante (aporta una muestra de cada condición)." if caso.get("pareado") else
               "cada individuo o cultivo tratado de forma independiente."),
          f"- **Qué se mide:** {b['nombre']} → {datos.RUTAS[dis['ruta']]['nombre']}.",
          "",
          "## 2. Diseño experimental",
          "",
          f"- **Réplicas biológicas:** {dis['replicas']} por grupo "
          f"{cit('SCH16', 'CON16')}. Réplicas técnicas: {dis['tecnicas']}.",
          f"- **Total de bibliotecas:** {n}.",
          f"- **Potencia aproximada** (gen típico, cambio de ~"
          f"{2 ** (caso['sim']['lfc_min'] + 0.6 * caso['sim']['lfc_sd']):.1f}×, FDR 5 %): "
          f"{pot:.0%} {cit('HAR13', 'CHI14')}. Para un cálculo formal usar RNASeqPower o "
          "PROPER con la dispersión de un piloto.",
          f"- **Fórmula del modelo:** `{FORMULA_R[dis['formula']]}` {cit('DESV')}.",
          tr(f"- **Lotes:** {len(sim.tabla_lotes(dis, caso))} ")
          + (tr(f"(máximo {caso['capacidad']} muestras por lote). ") if caso.get("capacidad") else "· ")
          + tr("Cada lote lleva muestras de todos los grupos y el orden dentro del lote es "
               f"aleatorio {cit('AUE10', 'LEE10')}."),
          f"- **Presupuesto estimado:** ${costo:,} (${datos.costo_muestra(dis):,.0f} por "
          "biblioteca: extracción, biblioteca, extras y secuenciación). Precios de "
          "referencia del juego; cotizar con el proveedor.",
          "",
          "### Hoja de muestras",
          "",
          f"También en `{os.path.basename(ruta_csv)}`.",
          "",
          _tabla(filas),
          "",
          ] + (["### Registro del laboratorio", ""] + _lab_hipotesis(exp, caso) + [""]
               if exp else []) + [
          "## 3. Toma y conservación de muestras",
          ""] + _muestreo(dis, caso) + [
          "", "## 4. Extracción de ARN", ""] + _extraccion(dis, caso) + _lab_extraccion(exp) + [
          "", f"## 5. Control de calidad del ARN {cit('SCR06', 'ILL14')}", ""] + _qc_arn(dis, caso) + _lab_qc(exp, caso) + [
          "", f"## 6. Preparación de bibliotecas {cit(*b['fuente'].split())}", ""] + _biblioteca(dis, caso) + [
          "", "## 7. Control de bibliotecas y secuenciación", ""] + _secuenciacion(dis, caso, n)
    if exp.get("plataforma"):
        import lab_datos as L
        md.append(tr(f"- Plataforma: **{L.PLATAFORMAS[exp['plataforma']]['nombre']}**; carriles: ")
                  + tr("todas las muestras en todos." if exp.get("carriles") != "grupo"
                       else "**un grupo por carril** (confundido)."))
        md.append(tr(f"- Biblioteca: {exp.get('pcr', 12)} ciclos de PCR; limpieza de dímeros: ")
                  + tr("sí." if exp.get("limpieza", True) else "**no**."))
    refs.update(datos.claves_fuente(b["fuente"]))
    extras_txt = [f"- **{tr(datos.EXTRAS[e]['nombre'])}:** {tr(datos.EXTRAS[e]['texto'])} "
                  f"{tr(cit(*datos.EXTRAS[e]['fuente'].split()))}" for e in dis["extras"]]
    if extras_txt:
        md += ["", "### Controles y extras", ""] + extras_txt
    md += ["", "## 8. Análisis bioinformático", "",
           f"Ruta: **{tr(datos.RUTAS[dis['ruta']]['nombre'])}** — {tr(datos.RUTAS[dis['ruta']]['texto'])} "
           f"{tr(cit(*datos.RUTAS[dis['ruta']]['fuente'].split()))}", "",
           f"### 8.1 Preprocesamiento {cit('AND10', 'EWE16', 'CHE18')}", ""] + _comandos(dis, caso) + [
           "", f"### 8.2 Control de calidad después de cuantificar {cit('WAN12', 'OKO16')}", "",
           "- RSeQC `infer_experiment.py` (hebra), `geneBody_coverage.py` (sesgo 3′), "
           "`read_distribution.py` (exones/intrones).",
           "- Qualimap rnaseq / Picard CollectRnaSeqMetrics; % ARNr y % mitocondrial.",
           "- Todo junto en MultiQC.", "",
           f"### 8.3 Normalización y prueba estadística {cit('LOV14', 'BH95')}", "",
           f"- Entrada: {tr(datos.ENTRADAS[dis['entrada']]['nombre'])}. "
           f"{tr(datos.ENTRADAS[dis['entrada']]['texto'])}",
           f"- Prueba: {tr(datos.PRUEBAS[dis['prueba']]['nombre'])}. {tr(datos.PRUEBAS[dis['prueba']]['texto'])}",
           f"- Corrección: {tr(datos.CORRECCIONES[dis['correccion']]['nombre'])}. "
           f"{tr(datos.CORRECCIONES[dis['correccion']]['texto'])}",
           "- Umbral: padj < 0.05; reportar log2FC encogido y el número de genes probados.",
           ""] + _codigo_r(dis, caso) + [
           "", "## 9. Criterios de aceptación", ""] + _criterios(dis, caso) + [
           "", f"## 10. Validación {cit('BUS09')}", "",
           "- RT-qPCR de 5-10 genes DE (subidos y bajados) en réplicas biológicas "
           "independientes, con ≥ 2 genes de referencia validados (MIQE).",
           "- Confirmación a nivel de proteína o funcional según la hipótesis.", "",
           f"## 11. Reproducibilidad y depósito de datos {cit('EWE20', 'FGED')}", "",
           "- Pipeline versionado (nf-core/rnaseq o Snakemake) con contenedores; registrar "
           "versión del genoma y de la anotación (p. ej. GRCh38 + GENCODE v46).",
           "- Código de R en un repositorio; guardar `sessionInfo()`.",
           "- FASTQ crudos en SRA/ENA; matriz de cuentas y hoja de muestras en GEO "
           "(MINSEQE). Datos humanos: acceso controlado si el consentimiento lo exige.",
           ]
    refs.update(datos.claves_fuente(datos.RUTAS[dis["ruta"]]["fuente"]))
    if comentarios:
        md += ["", "## 12. Dictamen del Revisor 2", ""]
        # cuadro de color (HTML en línea; GitHub lo muestra sin color) + gravedad
        etiquetas = {"fatal": ("#af8787", "FATAL"), "mayor": ("#d78787", "MAYOR"),
                     "menor": ("#afaf87", "menor"), "bien": ("#87af87", "bien")}
        for x in comentarios:
            color, grav = etiquetas[x["grav"]]
            md.append(f'- <span style="color:{color}">■</span> **{tr(grav)}** — {tr(x["texto"])} '
                      f"{tr(cit(*x['fuente'].split()))}")
        if resultado and resultado.get("estado") == "ok" and not caso.get("libre"):
            md += ["", f"Resultado simulado: {resultado['sig']} genes significativos, "
                       f"{resultado['tp']} verdaderos, {resultado['fp']} falsos; sensibilidad "
                       f"{resultado['sens']:.0%}, FDR observado {resultado['fdr']:.0%}."]
    md += ["", "## Referencias", ""]
    for k in sorted(refs):
        md.append(f"- {tr(datos.FUENTES[k])}")
    md.append("")
    md = _traducir_md(md)
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(ruta_csv, "w", encoding="utf-8") as f:
        f.write(_csv(filas))
    return ruta_md
