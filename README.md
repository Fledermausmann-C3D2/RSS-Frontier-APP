# RSS-Frontiers

Eine Flet-App (Android-APK + Desktop), die die 30 neuesten Forschungsartikel aus dem [Frontiers in Plant Science](https://www.frontiersin.org/journals/plant-science) RSS-Feed lädt, übersichtlich als Karten anzeigt und daraus automatisch ein Markdown-Dokument und ein PDF im handyfreundlichen Schmalformat erzeugt. Die erzeugten Dateien lassen sich direkt aus der App teilen.

## Features

- **NOW-Button**: Feed aktualisieren und Artikelkarten (Titel, Datum, Abstract, Link) anzeigen
- **PDF-Export**: schmale 105-mm-Seiten mit großer Schrift - optimal fürs Handy-Reading ohne Zoomen
- **Markdown-Export**: dieselben Artikel als `.md`
- **Teilen-Buttons**: PDF/MD über das Android-Share-Menü weitergeben (Drive, Mail etc.)
- Jeder Artikel auf einer eigenen Seite

## Screenshot / Struktur

```
RSS-Frontiers/
├── pyproject.toml
├── requirements.txt
├── science.ico / science.png      # Icon-Quelle
└── src/
    ├── assets/
    │   └── icon.svg                # App-Icon (Vektor)
    └── main.py                    # Flet-App
```

## Voraussetzungen

- Python 3.10+
- Für den APK-Bau unter Linux: Android SDK (commandline-tools), OpenJDK 17
- Abhängigkeiten: `flet`, `feedparser`, `fpdf2` (siehe `requirements.txt`)

## Nutzung

**Am PC starten (Desktop-Fenster):**

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
flet run
```

**APK bauen (Linux):**

```bash
flet build apk
adb install -r build/apk/RSS-Frontiers.apk
```

Die fertige APK liegt unter `build/apk/RSS-Frontiers.apk`.

## Technische Hinweise

- Die App speichert die erzeugten Dateien im app-privaten Datenverzeichnis (`Path.cwd()`); der Export ans Zielgerät erfolgt über die Teilen-Buttons - so sind keine Storage-Berechtigungen nötig.
- Das Launcher-Icon wird beim Build aus `src/assets/icon.svg` automatisch in alle Android-Größen (inkl. Adaptive Icon) generiert.
- PDF-Erzeugung mit [fpdf2](https://github.com/py-pdf/fpdf2), Feed-Parsing mit [feedparser](https://github.com/kurtmckee/feedparser), UI mit [Flet](https://flet.dev).

## Ideen / Roadmap

- Filter nach Stichworten oder Autor
- Mehrere Frontiers-Journals als Feed-Auswahl
- Merkliste für Artikel
