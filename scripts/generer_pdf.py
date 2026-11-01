#!/usr/bin/env python3
"""Génère le rapport de session en PDF imprimable (A4) depuis sessions/session-NN.md.

Usage : python3 scripts/generer_pdf.py NN [sortie.pdf]
Dépendances : pip install markdown weasyprint
"""
import sys
from pathlib import Path

import markdown
from weasyprint import HTML

RACINE = Path(__file__).resolve().parent.parent

CSS = """
@page { size: A4; margin: 2cm 2cm 2.2cm;
  @bottom-center { content: "Barrevoudla · page " counter(page) " / " counter(pages);
                   font: 9pt sans-serif; color: #666; } }
body { font: 11pt/1.5 "DejaVu Serif", Georgia, serif; color: #111; }
h1 { font: bold 22pt "DejaVu Sans", sans-serif; border-bottom: 2px solid #8b1a1a;
     padding-bottom: .2em; margin-top: 0; }
h2 { font: bold 14pt "DejaVu Sans", sans-serif; color: #8b1a1a; margin-top: 1.4em;
     break-after: avoid; }
li { margin-bottom: .35em; break-inside: avoid; }
table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 1em 0; }
th, td { border: 1px solid #999; padding: .3em .5em; text-align: left; vertical-align: top; }
th { background: #eee; }
tr { break-inside: avoid; }
blockquote { border-left: 3px solid #ccc; margin-left: 0; padding-left: 1em; color: #444; }
"""

def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        sys.exit(__doc__)
    n = int(sys.argv[1])
    source = RACINE / "sessions" / f"session-{n:02d}.md"
    if not source.exists():
        sys.exit(f"{source} introuvable")
    sortie = Path(sys.argv[2]) if len(sys.argv) > 2 else RACINE / "dist" / f"session-{n:02d}.pdf"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    corps = markdown.markdown(source.read_text(encoding="utf-8"), extensions=["tables", "sane_lists", "nl2br"])
    titre = source.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
    html = f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{titre}</title></head><body>{corps}</body></html>'
    HTML(string=html).write_pdf(sortie, stylesheets=[__import__("weasyprint").CSS(string=CSS)])
    print(f"{sortie} généré")

if __name__ == "__main__":
    main()
