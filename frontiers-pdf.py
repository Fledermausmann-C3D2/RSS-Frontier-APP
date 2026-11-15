import feedparser
import subprocess
import sys
from datetime import datetime

FEED = "https://www.frontiersin.org/journals/plant-science/rss"

feed = feedparser.parse(FEED)

# Dateinamen mit heutigem Datum
datum = datetime.now().strftime('%Y-%m-%d')
dateiname = f"frontiers_papers_{datum}.md"
pdfname = f"frontiers_papers_{datum}.pdf"

# 1) Ausgabe in der Konsole (erste 10 Artikel)
for i, entry in enumerate(feed.entries[:10], start=1):
    print(f"[{i}] {entry.title}")
    print(f"    Link: {entry.link}")
    print(f"    Datum: {entry.published}")
    text = entry.summary.replace("<p>", "").replace("</p>", "")
    text = " ".join(text.split())
    print(f"    {text}")
    print()

# 2) Export als Markdown-Datei (alle 30 Artikel, komplette Abstracts)
with open(dateiname, "w", encoding="utf-8") as f:
    for i, entry in enumerate(feed.entries[:30], start=1):
        f.write(f"## {i}. {entry.title}\n")
        f.write(f"**Link:** {entry.link}\n\n")
        f.write(f"**Datum:** {entry.published}\n\n")
        f.write(" ".join(entry.summary.split()) + "\n\n")

print(f"Fertig! Gespeichert unter {dateiname}")

# 3) Markdown → PDF im Typora-Stil
CSS = """
body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
       font-size: 11pt; line-height: 1.6; color: #333; max-width: 800px;
       margin: 40px auto; padding: 0 20px; }
h2 { font-size: 16pt; color: #1a1a1a; border-bottom: 1px solid #ddd;
     padding-bottom: 4px; margin-top: 28px; }
a { color: #428bca; text-decoration: none; }
@page { size: A4; margin: 2cm; }
"""

import markdown
from weasyprint import HTML

with open(dateiname, "r", encoding="utf-8") as f:
    md_text = f.read()

html_body = markdown.markdown(md_text, extensions=["extra"])
html_doc = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"

HTML(string=html_doc).write_pdf(pdfname)
print(f"PDF gespeichert unter {pdfname}")

# 4) PDF bzw. MD in Typora öffnen
try:
    if sys.platform == "win32":
        try:
            subprocess.run(["typora", dateiname], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            import os
            os.startfile(dateiname)
    elif sys.platform == "darwin":
        subprocess.run(["open", "-a", "Typora", dateiname], check=True)
    else:
        subprocess.run(["typora", dateiname], check=True)
    print("In Typora geöffnet.")
except Exception as e:
    print(f"Typora konnte nicht geöffnet werden ({e}). Bitte Datei manuell öffnen.")