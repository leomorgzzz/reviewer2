# REVIEWER 2 · Revisor 2

*[English](README.md) · Español*

Juego de terminal para aprender a diseñar experimentos de RNA-seq. Cada caso es
un investigador con una pregunta, un presupuesto y un problema escondido. Haces
el experimento completo en un laboratorio que recorres, del diseño en papel al
análisis, y al final el Revisor 2 califica el manuscrito y el cuaderno.

Los errores se arrastran: un ARN degradado aprobado en el QC sale como ruido en
los resultados.

> **En desarrollo.** El juego se sigue actualizando: al abrirlo te avisa si hay
> una versión nueva y se actualiza desde la pantalla de inicio, sin reinstalar.
> Tu partida se conserva. Errores, ideas o datos que corregir:
> [Issues](https://github.com/leomorgzzz/reviewer2/issues).

**Descargar:** [Windows](https://github.com/leomorgzzz/reviewer2/releases/latest/download/Reviewer2-Windows-Setup.exe) · [macOS](https://github.com/leomorgzzz/reviewer2/releases/latest/download/Reviewer2-macOS.zip) · instala y a jugar.

## Capturas

![Pantalla de inicio](capturas/pantalla-de-inicio.png)

![Plano del laboratorio](capturas/mapa.png)

![Papel de diseño](capturas/papel-diseno.png)

## Instalación

### Windows

1. Descarga **[Reviewer2-Windows-Setup.exe](https://github.com/leomorgzzz/reviewer2/releases/latest/download/Reviewer2-Windows-Setup.exe)** y ábrelo.
2. Sigue el instalador (no pide permisos de administrador). Al terminar, el
   juego queda en el menú Inicio y, si quieres, en el escritorio. Se abre en
   pantalla completa.

El instalador no está firmado (firmarlo cuesta una licencia anual), así que la
primera vez Windows puede avisar «Windows protegió su PC»: **Más información →
Ejecutar de todas formas**. Solo pasa al instalar. Para desinstalar:
**Configuración → Aplicaciones**.

### macOS

1. Descarga **[Reviewer2-macOS.zip](https://github.com/leomorgzzz/reviewer2/releases/latest/download/Reviewer2-macOS.zip)** y ábrelo.
2. Doble clic en `Reviewer2`. Si macOS no lo deja abrir: **Ajustes del Sistema →
   Privacidad y seguridad → Abrir de todos modos**.

Es para Mac con chip Apple (M1 o posterior).

### Linux o desde el código

```bash
git clone https://github.com/leomorgzzz/reviewer2.git
cd reviewer2
./instalar.sh        # crea el comando `reviewer2` en ~/.local/bin
reviewer2
```

Sin instalar: `python3 reviewer2.py`. Actualizar: `reviewer2 --update` (hace
`git pull`). Quitar el comando: `./instalar.sh --quitar`.

Desde el código requiere Python 3 (solo biblioteca estándar; en Windows instala
`windows-curses` la primera vez). Funciona desde 80×24.

Archivos que crea:

- `~/.reviewer2.json`: la partida (en Windows, `~` es `C:\Users\<tu usuario>`);
- `~/.reviewer2_idioma`: el idioma (la primera vez se usa el del sistema);
- `~/Documentos/reviewer2-protocols/` (o `~/Documents/`): los protocolos
  exportados.

Si tenías el juego con su nombre anterior (Revisor 2), la partida y el idioma
se pasan solos al nombre nuevo.

Al abrir, el juego consulta en GitHub si hay una versión nueva; no envía nada
más. Para desactivarlo: `reviewer2 --sin-actualizar`.

## Salir de pantalla completa

| Sistema | Tecla |
|---|---|
| Windows | Alt+Enter (o F11 en Windows Terminal) |
| macOS | Ctrl+Cmd+F |
| Linux | F11 en la mayoría de las terminales |

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
- **Actualizar a vX** (pantalla de inicio): aparece cuando hay una versión nueva.

## Fuentes

Cada dato lleva su cita en `datos.FUENTES`: Conesa 2016, Schurch 2016, Liu
2014, Love 2014, Auer & Doerge 2010, Leek 2010, Lovén 2012, Squair 2021, entre
otras.

## Pruebas

```bash
python3 pruebas/correr.py
```

Revisan que todo importe en los dos idiomas, que cada texto tenga traducción
(`python3 traduccion/extraer.py --faltan` lista lo que falta), que solo haya
símbolos que la consola de Windows sabe dibujar, que toda cita exista y que el
código del protocolo exportado sea el mismo en inglés. Corren solas en GitHub
en cada push y antes de compilar una versión.
