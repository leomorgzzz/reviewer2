"""Las estaciones del laboratorio: cada una es una etapa del experimento o un
lugar donde investigar.

  papel → unidades → campana → QC (NanoDrop, gel, Bioanalyzer) → kits →
  secuenciador → computadora → buzón del Revisor 2

Cada función recibe la Partida del laboratorio (laboratorio.Lab) y regresa
cuando el jugador se aleja de la estación.
"""

from est_investigacion import calendario, congelador, cuaderno, investigador, librero, replica, tecnico  # noqa: F401
from est_diseno import papel, unidades  # noqa: F401
from est_humedo import campana, kits  # noqa: F401
from est_qc import qc  # noqa: F401
from est_analisis import buzon, computadora, secuenciador  # noqa: F401
