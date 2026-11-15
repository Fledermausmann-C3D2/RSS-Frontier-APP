import feedparser
from datetime import datetime
from fpdf import FPDF

FEED = "https://www.frontiersin.org/journals/plant-science/rss"
feed = feedparser.parse(FEED)

datum = datetime.now().strftime('%Y-%m-%d')
pdfname = f"/data/data/com.termux/files/home/storage/shared/Frontiers/frontiers_papers_{datum}.pdf"

# Schmale Seite statt A4: 105 mm breit (etwa Handy-Display-Proportionen)
SEITE_BREITE = 105
SEITE_HOEHE = 200

pdf = FPDF(format=(SEITE_BREITE, SEITE_HOEHE))
pdf.set_margins(10, 12, 10)
pdf.set_auto_page_break(auto=True, margin=14)

def sauber(text):
    return text.encode("latin-1", "replace").decode("latin-1")

for i, entry in enumerate(feed.entries[:30], start=1):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)          # Titel: groß
    pdf.multi_cell(pdf.epw, 8, sauber(f"{i}. {entry.title}"))
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 11)          # Datum: mittel
    pdf.multi_cell(pdf.epw, 6, sauber(f"Datum: {entry.published}"))
    pdf.set_font("Helvetica", "", 11)           # Link: mittel
    pdf.multi_cell(pdf.epw, 6, sauber(entry.link))
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 13)           # Abstract: groß
    text = " ".join(entry.summary.split()).replace("<p>", "").replace("</p>", "")
    pdf.multi_cell(pdf.epw, 7, sauber(text))

pdf.output(pdfname)
print(f"PDF gespeichert: {pdfname}")