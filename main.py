import flet as ft
import feedparser
import json
import re
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fpdf import FPDF

FEED = "https://www.frontiersin.org/journals/plant-science/rss"
JOURNAL = "Frontiers in Plant Science"
IMPACT = "IF 5.9 (JCR 2024)"
MERKER_DATEI = Path.cwd() / "gemerkt.json"

def sauber(text):
    return text.encode("latin-1", "replace").decode("latin-1")

def doi_aus_link(link):
    """Extrahiert die DOI (10.3389/...) aus dem Frontiers-Link."""
    m = re.search(r"(10\.\d{4,9}/[^\s?#]+)", link)
    return m.group(1).rstrip("/") if m else None

def hole_zitation(doi):
    """Fragt Crossref nach der Zitationszahl eines Artikels."""
    if not doi:
        return None
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Frontiers-Papers/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())["message"]["is-referenced-by-count"]
    except Exception:
        return None

def lade_gemerkt():
    try:
        daten = json.loads(MERKER_DATEI.read_text(encoding="utf-8"))
        return daten if isinstance(daten, dict) else {
            link: {"titel": link, "published": "", "text": "", "zit": None} for link in daten
        }
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def speichere_gemerkt(gemerkt):
    MERKER_DATEI.write_text(json.dumps(gemerkt, ensure_ascii=False), encoding="utf-8")


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

    gemerkt = lade_gemerkt()
    ansicht = "feed"

    url_launcher = ft.UrlLauncher()
    share = ft.Share()

    def mache_link_button(url):
        async def handler(ev):
            await url_launcher.launch_url(url)
        return ft.TextButton(url, on_click=handler)

    def mache_herz(url, titel="", published="", text="", zit=None):
        def toggle(ev):
            if url in gemerkt:
                del gemerkt[url]
            else:
                gemerkt[url] = {
                    "titel": titel,
                    "published": published,
                    "text": text[:500],
                    "zit": zit,
                }
            speichere_gemerkt(gemerkt)
            ev.control.selected = url in gemerkt
            aktualisiere_zaehler()
        return ft.IconButton(
            icon=ft.Icons.FAVORITE_BORDER,
            selected_icon=ft.Icons.FAVORITE,
            selected=url in gemerkt,
            on_click=toggle,
            icon_color=ft.Colors.RED,
            tooltip="Artikel merken",
        )

    def aktualisiere_zaehler():
        zaehler.value = f"♥ {len(gemerkt)} gemerkt"
        page.update()

    async def pdf_teilen(ev):
        await share.share_files([str(pdf_teilen.pfad)])

    async def md_teilen(ev):
        await share.share_files([str(md_teilen.pfad)])

    def zeige_gemerkt(e):
        nonlocal ansicht
        ansicht = "gemerkt" if ansicht != "gemerkt" else "feed"
        liste.controls.clear()

        if ansicht == "gemerkt":
            if not gemerkt:
                liste.controls.append(ft.Text("Noch nichts gemerkt - Herz in der Feed-Ansicht tippen"))
            for url, d in gemerkt.items():
                liste.controls.append(ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(d["titel"], weight=ft.FontWeight.BOLD,
                                        size=16, expand=True),
                                mache_entfernen(url),
                            ]),
                            ft.Text(d.get("published", ""), size=11, color=ft.Colors.GREY),
                            ft.Text(d.get("text", ""), size=13),
                            mache_link_button(url),
                        ], tight=True),
                    )))
        else:
            aktualisieren(e)   # Feed-Ansicht neu aufbauen

        page.update()


    def mache_entfernen(url):
        def entfernen(ev):
            del gemerkt[url]
            speichere_gemerkt(gemerkt)
            zeige_gemerkt(ev)
        return ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, on_click=entfernen,
                             tooltip="Aus Merkliste entfernen", icon_color=ft.Colors.GREY)



    def aktualisieren(e):
        status.value = "Lade Feed..."
        liste.controls.clear()
        liste.controls.append(ft.ProgressBar())
        page.update()

        feed = feedparser.parse(FEED)
        eintraege = feed.entries[:30]

        # Zitationszahlen parallel von Crossref holen
        status.value = f"Lade Zitationen für {len(eintraege)} Artikel..."
        page.update()
        with ThreadPoolExecutor(max_workers=8) as ex:
            zitationen = list(ex.map(
                lambda en: hole_zitation(doi_aus_link(en.link)), eintraege))

        liste.controls.clear()
        for i, entry in enumerate(eintraege, 1):
            text = " ".join(entry.summary.split()).replace("<p>", "").replace("</p>", "")
            zit = zitationen[i - 1]
            zit_text = ft.Text(
                f"🔬 {zit}× zitiert" if zit is not None else "Zitationen n/a",
                size=11,
                color=ft.Colors.BLUE_700 if (zit or 0) >= 10 else ft.Colors.GREY,
            )
            liste.controls.append(ft.Card(
                content=ft.Container(
                    padding=12,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"{i}. {entry.title}", weight=ft.FontWeight.BOLD,
                                    size=16, expand=True),
                            mache_herz(entry.link, entry.title, entry.published, text, zit)
                        ]),
                        ft.Row([
                            ft.Text(entry.published, size=11, color=ft.Colors.GREY),
                            zit_text,
                        ]),
                        ft.Text(text, size=13),
                        mache_link_button(entry.link),
                    ], tight=True),
                )))

        md, pdf_datei = erzeuge_dateien(feed)
        status.value = f"{len(eintraege)} Artikel - MD und PDF gespeichert"

        pdf_teilen.pfad = pdf_datei
        md_teilen.pfad = md

        liste.controls.append(ft.Row([
            ft.FilledButton("PDF teilen", on_click=pdf_teilen),
            ft.FilledButton("MD teilen", on_click=md_teilen),
        ]))
        aktualisiere_zaehler()
        page.update()

    badge = ft.Container(
        padding=ft.Padding(left=8, top=4, right=8, bottom=4),
        bgcolor=ft.Colors.GREEN_50,
        border_radius=8,
        content=ft.Row([
            ft.Icon(ft.Icons.SCIENCE, size=14, color=ft.Colors.GREEN_700),
            ft.Text(f"{JOURNAL} · {IMPACT}", size=11, color=ft.Colors.GREEN_900),
        ]),
    )

    zaehler = ft.Text(f"♥ {len(gemerkt)} gemerkt", size=11, color=ft.Colors.GREY)

    page.add(
        ft.Row([
            ft.FilledTonalButton("NOW aktualisieren", icon=ft.Icons.REFRESH,
                                 on_click=aktualisieren),
            ft.OutlinedButton("Gemerkt", icon=ft.Icons.FAVORITE,
                              on_click=zeige_gemerkt),
            status,
        ]),
        ft.Row([badge, zaehler]),
        liste,
    )

ft.run(main)