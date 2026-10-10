# Traducción al inglés: plantillas que solo «abren» textos compuestos para
# traducir lo de adentro (T, por hash) y palabras sueltas que vienen de datos
# internos (L, texto en español -> inglés, sin hash).
T = {
    "998e1b466b": "{0}\n\n<tenue>{1}</>",
    "b916ce64e1": "<tenue>{0}</>",
    "2c91c6327a": "<titulo!>{0}</>",
    "4ea0c9cfd6": "<titulo!>{0}</>  {1}",
    "f6c7324a06": "<{0}!>{1}</>  <titulo!>{2}</>",
    "8a56fb950c": "<titulo!>{0}</>{1}",
    "ed9b30bc67": "<titulo!>{0}</>   <tenue>{1}</>",
    "09f3dc5015": "  design = ~ patient + condition",
    "d7715f1929": "  design = ~ genotype + treatment + genotype:treatment",
    "e1c2413edf": "@read_1  ACGTTGCAGGATCCATTGCA  +  IIIIIHHHGGFFF",
    "b658ec24d6": "  miRNA                          →  <agua>small RNA-seq</>",
    "872b72da17": "  • 3′ tag-seq: 3-10 M · small RNA: 2-10 M",
    "de3634ef7b": "**no**.",
}
L = {
    # textos armados con «·» y citas con página
    "{0} · {1}": "{0} · {1}",
    "{0} [{1}]": "{0} [{1}]",
    "- **{0}:** {1} {2}": "- **{0}:** {1} {2}",
    "({0})": "({0})",
    "**{0}.** {1}": "**{0}.** {1}",
    "| {0} | {1} | {2} |": "| {0} | {1} | {2} |",
    "{0}, {1}": "{0}, {1}",
    # secciones del Manual
    "FUNDAMENTOS": "FUNDAMENTALS", "DISEÑO": "DESIGN", "LABORATORIO": "LAB",
    "ANÁLISIS": "ANALYSIS",
    # nombres de lote y decisiones guardadas
    "banca": "bench", "lote": "batch", "azar": "random", "orden": "in order",
    "ojo": "by eye", "acuosa": "aqueous", "interfase": "interphase", "organica": "organic",
    "etanol100": "100 % ethanol", "ninguno": "none", "correcto": "correct",
    "excesivo": "excessive", "fuerte": "strong", "leve": "mild", "rin": "RIN",
    "donante": "donor", "sexo": "sex", "operador": "operator",
    "aprobada": "approved", "excluida": "excluded", "pendiente": "pending",
    # etiquetas del plano y cuartos en minúsculas
    "unidades": "units", "calendario": "calendar", "librero": "bookshelf",
    "computadora": "computer", "cuaderno": "notebook", "investigador": "researcher",
    "nuevo": "new", "oficina": "office", "secuenciador": "sequencer", "laboratorio húmedo": "wet lab",
    "cuarto de qc": "QC room", "secuenciación": "sequencing",
    "bioinformática": "bioinformatics", "buzón": "mailbox",
    "cuarto de cultivo": "cell culture room", "bioterio": "animal facility",
    "biobanco clínico": "clinical biobank", "invernadero": "greenhouse",
    "menor": "minor", "bien": "good", "gel": "gel", "resecuenciar": "resequence",
    "colega": "colleague",
    # velocidades
    "lenta": "slow", "normal": "normal", "rápida": "fast",
    # gel
    "pozo": "well",
    # menú de opciones
    "Idioma / Language: Español": "Idioma / Language: Spanish",
}
