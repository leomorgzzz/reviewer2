# REVIEWER 2

*English · [Español](README.es.md)*

A terminal game for learning to design RNA-seq experiments. Each case is a
researcher with a question, a budget and a hidden problem. You run the whole
experiment in a lab you walk around, from the design on paper to the analysis,
and at the end Reviewer 2 grades the manuscript and the lab notebook.

Mistakes carry over: degraded RNA you let through QC shows up as noise in the
results.

> **Work in progress.** The game keeps getting updated: when you open it, it
> tells you if there's a new version and updates from the title screen, no
> reinstall needed. Your save is kept. Bugs, ideas, or science that's wrong:
> [Issues](https://github.com/leomorgzzz/reviewer2/issues).

**Download:** [Windows](https://github.com/leomorgzzz/reviewer2/releases/latest/download/Reviewer2-Windows-Setup.exe) · [macOS](https://github.com/leomorgzzz/reviewer2/releases/latest/download/Reviewer2-macOS.zip) · install and play.

## Screenshots

![Title screen](capturas/pantalla-de-inicio.png)

![Lab map](capturas/mapa.png)

![Design sheet](capturas/papel-diseno.png)

## Installation

### Linux, or from source

```bash
git clone https://github.com/leomorgzzz/reviewer2.git
cd reviewer2
./instalar.sh        # creates the `reviewer2` command in ~/.local/bin
reviewer2
```

Without installing: `python3 reviewer2.py`. Update: `reviewer2 --update` (runs
`git pull`). Remove the command: `./instalar.sh --quitar`.

From source it needs Python 3 (standard library only; on Windows it installs
`windows-curses` the first time). Works from 80×24.

### Windows

1. Download **[Reviewer2-Windows-Setup.exe](https://github.com/leomorgzzz/reviewer2/releases/latest/download/Reviewer2-Windows-Setup.exe)** and open it.
2. Follow the installer (no admin rights needed). When it's done, the game is
   in the Start menu and, if you want, on the desktop. It opens full screen.

The installer isn't signed (signing costs a yearly license), so the first time
Windows may warn "Windows protected your PC": **More info → Run anyway**. It
only happens when installing. To uninstall: **Settings → Apps**.

### macOS

1. Download **[Reviewer2-macOS.zip](https://github.com/leomorgzzz/reviewer2/releases/latest/download/Reviewer2-macOS.zip)** and open it.
2. Double-click `Reviewer2`. If macOS won't open it: **System Settings →
   Privacy & Security → Open Anyway**.

For Macs with Apple silicon (M1 or later).

### Files it creates

- `~/.reviewer2.json`: your save (on Windows, `~` is `C:\Users\<your user>`);
- `~/.reviewer2_idioma`: the language (the first time it follows your system);
- `~/Documents/reviewer2-protocols/`: exported protocols.

On startup the game asks GitHub whether there's a new version; it sends
nothing else. To turn it off: `reviewer2 --no-update`.

## Leaving full screen

| System | Key |
|---|---|
| Windows | Alt+Enter (or F11 in Windows Terminal) |
| macOS | Ctrl+Cmd+F |
| Linux | F11 in most terminals |

## Controls

| Key | Action |
|---|---|
| Arrows / WASD | move |
| E / Enter | use a station or talk |
| N | lab notebook and protocol export |
| M / H | manual / help |
| Q | quit (it saves) |

## Menu

- **Play**: cases, free lab and training.
- **Study**: manual, methods catalog and glossary.
- **Practice**: review and exam.
- **Options**: difficulty, speed and language.
- **Update to vX** (title screen): shows up when there's a new version.

## Sources

Every fact carries its citation in `datos.FUENTES`: Conesa 2016, Schurch 2016,
Liu 2014, Love 2014, Auer & Doerge 2010, Leek 2010, Lovén 2012, Squair 2021,
among others.

## Tests

```bash
python3 pruebas/correr.py
```

They check that everything imports in both languages, that every text has a
translation (`python3 traduccion/extraer.py --faltan` lists what's missing),
that only symbols the Windows console can draw are used, that every citation
exists, and that the code in the exported protocol is the same in English.
They run on GitHub on every push and before building a release.

## License

MIT · [LICENSE](LICENSE)
