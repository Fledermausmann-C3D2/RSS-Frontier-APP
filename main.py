import flet as ft
import feedparser
from datetime import datetime
from pathlib import Path
from fpdf import FPDF

FEED = "https://www.frontiersin.org/journals/plant-science/rss"

def sauber(text):
    return text.encode("latin-1", "replace").decode("latin-1")

def erzeuge_dateien(feed):
    """MD + PDF im App-Datenordner erzeugen, gibt (md, pdf) zurück."""
   
    ordner = Path.cwd()

    datum = datetime.now().strftime("%Y-%m-%d")
    md = ordner / f"frontiers_papers_{datum}.md"
    pdf_datei = ordner / f"frontiers_papers_{datum}.pdf"

    with open(md, "w", encoding="utf-8") as f:
        for i, e in enumerate(feed.entries[:30], 1):
            f.write(f"## {i}. {e.title}\n\n{e.link}\n\n")
            f.write(" ".join(e.summary.split()) + "\n\n")

    pdf = FPDF(format=(105, 200))
    pdf.set_margins(10, 12, 10)
    pdf.set_auto_page_break(auto=True, margin=14)
    for i, e in enumerate(feed.entries[:30], 1):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 15)
        pdf.multi_cell(pdf.epw, 8, sauber(f"{i}. {e.title}"))
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(pdf.epw, 6, sauber(e.link))
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 13)
        pdf.multi_cell(pdf.epw, 7, sauber(" ".join(e.summary.split())))
    pdf.output(str(pdf_datei))
    return md, pdf_datei

def main(page: ft.Page):
    page.title = "Frontiers Papers"
    liste = ft.ListView(spacing=10, padding=10, expand=True)
    status = ft.Text("Noch keine Daten - NOW drücken")
    pdf_link = None

    def aktualisieren(e):
        status.value = "Lade Feed..."
        liste.controls.clear()
        liste.controls.append(ft.ProgressBar())
        page.update()

        feed = feedparser.parse(FEED)
        liste.controls.clear()
        for i, entry in enumerate(feed.entries[:30], 1):
            text = " ".join(entry.summary.split()).replace("<p>", "").replace("</p>", "")
            liste.controls.append(ft.Card(
                content=ft.Container(
                    padding=12,
                    content=ft.Column([
                        ft.Text(f"{i}. {entry.title}", weight=ft.FontWeight.BOLD, size=16),
                        ft.Text(entry.published, size=11, color=ft.Colors.GREY),
                        ft.Text(text, size=13),
                        ft.TextButton(entry.link, on_click=lambda ev, u=entry.link: page.launch_url(u)),
                    ], tight=True),
                )))

        md, pdf_datei = erzeuge_dateien(feed)
        status.value = f"{len(feed.entries[:30])} Artikel - MD und PDF gespeichert"
        liste.controls.append(ft.Row([
            ft.FilledButton("PDF teilen",
                on_click=lambda ev: page.share_file(str(pdf_datei))),
            ft.FilledButton("MD teilen",
                on_click=lambda ev: page.share_file(str(md))),
        ]))
        page.update()

    page.add(
        ft.Row([
            ft.FilledTonalButton("NOW aktualisieren", icon=ft.Icons.REFRESH,
                                 on_click=aktualisieren),
            status,
        ]),
        liste,
    )

ft.run(main)
