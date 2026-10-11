#!/usr/bin/env python3
"""Nombre anterior del juego: los lanzadores viejos de instalar.sh abren este
archivo. Abre reviewer2.py; `./instalar.sh` crea el comando nuevo."""

import os
import runpy

if __name__ == "__main__":
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviewer2.py"),
                   run_name="__main__")
