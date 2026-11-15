import feedparser
from datetime import datetime

FEED = "https://www.frontiersin.org/journals/plant-science/rss"

feed = feedparser.parse(FEED)

# Dateiname mit heutigem Datum, z. B. frontiers_papers_2026-11-15.md
dateiname = f"frontiers_papers_{datetime.now().strftime('%Y-%m-%d')}.md"

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