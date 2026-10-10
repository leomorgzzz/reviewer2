# REVISOR 2

*English: `revisor2 --en` or Options → Language.*

Juego de terminal para aprender a diseñar experimentos de RNA-seq. Cada caso es
un investigador con una pregunta, un presupuesto y un problema escondido. Haces
el experimento completo en un laboratorio que recorres, del diseño en papel al
análisis, y al final el Revisor 2 califica el manuscrito y el cuaderno.

Los errores se arrastran: un ARN degradado aprobado en el QC sale como ruido en
los resultados.

## Capturas

![Pantalla de inicio](capturas/pantalla-de-inicio.png)

![Plano del laboratorio](capturas/mapa.png)

![Papel de diseño](capturas/papel-diseno.png)

## Instalación

```bash
git clone https://github.com/leomorgzzz/revisor2.git
cd revisor2
./instalar.sh        # crea el comando `revisor2` en ~/.local/bin
revisor2
```

Sin instalar: `python3 revisor2.py`. Quitar el comando: `./instalar.sh --quitar`.

Requiere Python 3 (solo biblioteca estándar). Funciona desde 80×24; se ve mejor
en pantalla completa.

Archivos que crea:

- `~/.revisor2.json`: la partida;
- `~/.revisor2_idioma`: el idioma;
- `~/Documentos/revisor2-protocolos/`: los protocolos exportados.

## Controles

| Tecla | Acción |
|---|---|
| Flechas / WASD | moverse |
| E / Enter | usar la estación o hablar |
| N | cuaderno de laboratorio y exportar protocolo |
| M / H | manual / ayuda |
| Q | salir (se guarda) |

## Menú

- **Jugar**: casos, laboratorio libre y capacitación.
- **Estudiar**: manual, catálogo de métodos y glosario.
- **Practicar**: repaso y examen.
- **Opciones**: dificultad, velocidad e idioma.

## Fuentes

Cada dato lleva su cita en `datos.FUENTES`: Conesa 2016, Schurch 2016, Liu
2014, Love 2014, Auer & Doerge 2010, Leek 2010, Lovén 2012, Squair 2021, entre
otras.
