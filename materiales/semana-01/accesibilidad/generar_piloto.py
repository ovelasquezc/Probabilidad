#!/usr/bin/env python3
"""Genera pistas de voz y páginas HTML semánticas para el piloto accesible."""

from __future__ import annotations

import html
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VOICE = "Paulina"
# La notación y las demostraciones requieren una velocidad algo menor que la
# conversación ordinaria. El reproductor permite acelerar si el estudiante lo desea.
RATE = "128"

JOBS = [
    ("guiones/01_sesion_01_guion_sonoro.txt", "sesion-01", "Sesión 1: modelos y probabilidad"),
    ("guiones/02_sesion_02_guion_sonoro.txt", "sesion-02", "Sesión 2: variables y leyes"),
    ("guiones/03_practica_guion_sonoro.txt", "practica", "Práctica dirigida"),
    ("guiones/04_prueba_entrada_guion_sonoro.txt", "prueba-entrada", "Prueba de entrada accesible"),
]

FORMULAS = {
    "sesion-01": [
        ("Axioma de aditividad numerable", "probabilidad de la unión disjunta de A sub n es igual a la suma de las probabilidades de A sub n", "<math><mrow><mi mathvariant='double-struck'>P</mi><mo>(</mo><msubsup><mo>⋃</mo><mrow><mi>n</mi><mo>=</mo><mn>1</mn></mrow><mi>∞</mi></msubsup><msub><mi>A</mi><mi>n</mi></msub><mo>)</mo><mo>=</mo><msubsup><mo>∑</mo><mrow><mi>n</mi><mo>=</mo><mn>1</mn></mrow><mi>∞</mi></msubsup><mi mathvariant='double-struck'>P</mi><mo>(</mo><msub><mi>A</mi><mi>n</mi></msub><mo>)</mo></mrow></math>"),
        ("Borelianos generados por semirrectas", "la sigma álgebra de Borel es la sigma álgebra generada por las semirrectas menos infinito hasta x", "<math><mrow><mi>ℬ</mi><mo>(</mo><mi>ℝ</mi><mo>)</mo><mo>=</mo><mi>σ</mi><mo>(</mo><mo>{</mo><mo>(</mo><mo>−∞</mo><mo>,</mo><mi>x</mi><mo>]</mo><mo>:</mo><mi>x</mi><mo>∈</mo><mi>ℝ</mi><mo>}</mo><mo>)</mo></mrow></math>"),
        ("Integral de una función simple", "integral de s respecto de mu es la suma de a sub k por mu de A sub k", "<math><mrow><mo>∫</mo><mi>s</mi><mi>d</mi><mi>μ</mi><mo>=</mo><munderover><mo>∑</mo><mrow><mi>k</mi><mo>=</mo><mn>1</mn></mrow><mi>m</mi></munderover><msub><mi>a</mi><mi>k</mi></msub><mi>μ</mi><mo>(</mo><msub><mi>A</mi><mi>k</mi></msub><mo>)</mo></mrow></math>"),
        ("Continuidad desde abajo", "si A sub n crece hacia A, P de A sub n converge a P de A", "<math><mrow><msub><mi>A</mi><mi>n</mi></msub><mo>↑</mo><mi>A</mi><mo>⇒</mo><mi mathvariant='double-struck'>P</mi><mo>(</mo><msub><mi>A</mi><mi>n</mi></msub><mo>)</mo><mo>↑</mo><mi mathvariant='double-struck'>P</mi><mo>(</mo><mi>A</mi><mo>)</mo></mrow></math>"),
        ("Probabilidad condicional", "probabilidad de A condicionada a B es probabilidad de A intersección B dividida entre probabilidad de B", "<math><mrow><mi mathvariant='double-struck'>P</mi><mo>(</mo><mi>A</mi><mo>|</mo><mi>B</mi><mo>)</mo><mo>=</mo><mfrac><mrow><mi mathvariant='double-struck'>P</mi><mo>(</mo><mi>A</mi><mo>∩</mo><mi>B</mi><mo>)</mo></mrow><mrow><mi mathvariant='double-struck'>P</mi><mo>(</mo><mi>B</mi><mo>)</mo></mrow></mfrac></mrow></math>"),
        ("Probabilidad total", "P de A es la suma de P de A condicionada a B sub i por P de B sub i", "<math><mrow><mi mathvariant='double-struck'>P</mi><mo>(</mo><mi>A</mi><mo>)</mo><mo>=</mo><munder><mo>∑</mo><mi>i</mi></munder><mi mathvariant='double-struck'>P</mi><mo>(</mo><mi>A</mi><mo>|</mo><msub><mi>B</mi><mi>i</mi></msub><mo>)</mo><mi mathvariant='double-struck'>P</mi><mo>(</mo><msub><mi>B</mi><mi>i</mi></msub><mo>)</mo></mrow></math>"),
    ],
    "sesion-02": [
        ("Teorema pi lambda", "lambda de P es igual a sigma de P cuando P es un sistema pi", "<math><mrow><mi>λ</mi><mo>(</mo><mi>𝒫</mi><mo>)</mo><mo>=</mo><mi>σ</mi><mo>(</mo><mi>𝒫</mi><mo>)</mo></mrow></math>"),
        ("Medibilidad", "la preimagen por X de todo boreliano C pertenece a efe", "<math><mrow><msup><mi>X</mi><mrow><mo>−</mo><mn>1</mn></mrow></msup><mo>(</mo><mi>C</mi><mo>)</mo><mo>∈</mo><mi>ℱ</mi><mspace width='.5em'/><mtext>para todo</mtext><mspace width='.5em'/><mi>C</mi><mo>∈</mo><mi>ℬ</mi><mo>(</mo><mi>ℝ</mi><mo>)</mo></mrow></math>"),
        ("Ley de X", "mu sub X de C es P de X perteneciente a C", "<math><mrow><msub><mi>μ</mi><mi>X</mi></msub><mo>(</mo><mi>C</mi><mo>)</mo><mo>=</mo><mi mathvariant='double-struck'>P</mi><mo>(</mo><mi>X</mi><mo>∈</mo><mi>C</mi><mo>)</mo></mrow></math>"),
        ("Función de distribución", "F sub X de x es P de X menor o igual que x", "<math><mrow><msub><mi>F</mi><mi>X</mi></msub><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><mi mathvariant='double-struck'>P</mi><mo>(</mo><mi>X</mi><mo>≤</mo><mi>x</mi><mo>)</mo></mrow></math>"),
        ("Masa como salto", "P de X igual a x es F de x menos F de x por la izquierda", "<math><mrow><mi mathvariant='double-struck'>P</mi><mo>(</mo><mi>X</mi><mo>=</mo><mi>x</mi><mo>)</mo><mo>=</mo><msub><mi>F</mi><mi>X</mi></msub><mo>(</mo><mi>x</mi><mo>)</mo><mo>−</mo><msub><mi>F</mi><mi>X</mi></msub><mo>(</mo><mi>x</mi><mo>−</mo><mo>)</mo></mrow></math>"),
        ("Intervalo semiabierto", "P de a menor que X menor o igual que b es F de b menos F de a", "<math><mrow><mi mathvariant='double-struck'>P</mi><mo>(</mo><mi>a</mi><mo>&lt;</mo><mi>X</mi><mo>≤</mo><mi>b</mi><mo>)</mo><mo>=</mo><msub><mi>F</mi><mi>X</mi></msub><mo>(</mo><mi>b</mi><mo>)</mo><mo>−</mo><msub><mi>F</mi><mi>X</mi></msub><mo>(</mo><mi>a</mi><mo>)</mo></mrow></math>"),
        ("Distribución desde una densidad", "F de x es la integral desde menos infinito hasta x de f de t respecto de t", "<math><mrow><mi>F</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><msubsup><mo>∫</mo><mrow><mo>−∞</mo></mrow><mi>x</mi></msubsup><mi>f</mi><mo>(</mo><mi>t</mi><mo>)</mo><mi>d</mi><mi>t</mi></mrow></math>"),
    ],
    "practica": [],
    "prueba-entrada": [],
}

CSS = """
:root{color-scheme:light dark}body{font-family:system-ui,-apple-system,sans-serif;line-height:1.65;max-width:78ch;margin:auto;padding:1rem 1.4rem}a{color:#7b001c}a:focus,button:focus,audio:focus{outline:3px solid #d39b00;outline-offset:3px}.skip{position:absolute;left:-10000px}.skip:focus{position:static}header{border-bottom:4px solid #7b001c;margin-bottom:1.5rem}section{margin:2.2rem 0}h1,h2,h3{line-height:1.25}audio{width:100%;margin:.5rem 0 1rem}.formula{border-left:5px solid #7b001c;padding:.75rem 1rem;margin:1rem 0;overflow-x:auto}.spoken{font-style:italic}.note{background:#f2e9eb;color:#231f20;padding:1rem;border-radius:.3rem}@media(prefers-color-scheme:dark){a{color:#ff9db2}.note{background:#3a242a;color:#fff}}math{font-size:1.25em}
"""


def split_tracks(text: str):
    parts = re.split(r"^=== PISTA (\d+): (.+?) ===\s*$", text, flags=re.M)
    tracks = []
    for i in range(1, len(parts), 3):
        number, title, body = parts[i], parts[i + 1].strip(), parts[i + 2].strip()
        tracks.append((int(number), title, body))
    return tracks


def paragraphs(body: str) -> str:
    return "\n".join(f"<p>{html.escape(p.strip())}</p>" for p in body.split("\n\n") if p.strip())


def slugify(title: str) -> str:
    plain = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", plain.lower()).strip("_")


def build_job(script_rel: str, out_name: str, page_title: str):
    script = ROOT / script_rel
    out = ROOT / out_name
    out.mkdir(parents=True, exist_ok=True)
    tracks = split_tracks(script.read_text(encoding="utf-8"))
    playlist = []
    sections = []
    for pattern in ("*.m4a", "*.mp3", "*.txt", ".*.aiff"):
        for obsolete in out.glob(pattern):
            obsolete.unlink()
    for number, title, body in tracks:
        stem = f"{number:02d}_{slugify(title)}"
        txt_path = out / f"{stem}.txt"
        aiff_path = out / f".{stem}.aiff"
        audio_path = out / f"{stem}.mp3"
        txt_path.write_text(body + "\n", encoding="utf-8")
        subprocess.run(["say", "-v", VOICE, "-r", RATE, "-f", str(txt_path), "-o", str(aiff_path)], check=True)
        subprocess.run([
            "lame", "--silent", "-b", "64", "-m", "m",
            "--tt", f"Pista {number}. {title.title()}",
            "--ta", "Oswaldo Velásquez Castañón",
            "--tl", "CM4H1 · Semana 1 · 2026-2",
            "--tn", str(number), str(aiff_path), str(audio_path),
        ], check=True)
        aiff_path.unlink()
        playlist.append(audio_path.name)
        sections.append(
            f"<section id='pista-{number}'><h2>Pista {number}. {html.escape(title.title())}</h2>"
            f"<audio controls preload='metadata' aria-label='Pista {number}: {html.escape(title)}'>"
            f"<source src='../{out_name}/{html.escape(audio_path.name)}' type='audio/mpeg'>"
            "Su navegador no puede reproducir el audio. Use el enlace de descarga siguiente.</audio>"
            f"<p><a download href='../{out_name}/{html.escape(audio_path.name)}'>Descargar pista {number}</a></p>"
            f"<details><summary>Leer la transcripción de la pista {number}</summary>{paragraphs(body)}</details></section>"
        )
    (out / "00_escuchar_en_orden.m3u").write_text("#EXTM3U\n" + "\n".join(playlist) + "\n", encoding="utf-8")

    formula_html = []
    for label, spoken, mathml in FORMULAS[out_name]:
        formula_html.append(
            f"<div class='formula'><h3>{html.escape(label)}</h3>"
            f"<div role='math' aria-label='{html.escape(spoken)}'>{mathml}</div>"
            f"<p class='spoken'><strong>Lectura sugerida:</strong> {html.escape(spoken)}.</p></div>"
        )
    formulas = ""
    if formula_html:
        formulas = "<section id='formulas'><h2>Fórmulas explorables</h2><p>Las fórmulas siguientes usan MathML y llevan una lectura verbal alternativa.</p>" + "".join(formula_html) + "</section>"

    page = f"""<!doctype html>
<html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{html.escape(page_title)} · CM4H1</title><style>{CSS}</style></head>
<body><a class='skip' href='#contenido'>Saltar al contenido</a><header><p>Universidad Nacional de Ingeniería · CM4H1 · 2026-2</p>
<h1>{html.escape(page_title)}</h1><p>Docente: Oswaldo Velásquez Castañón</p></header>
<nav aria-label='Navegación del material'><a href='index.html'>Inicio del piloto</a> · <a href='#formulas'>Fórmulas</a></nav>
<main id='contenido'><p class='note'>Las pistas pueden escucharse por separado. La transcripción exacta está inmediatamente después de cada reproductor.</p>
{formulas}{''.join(sections)}</main></body></html>"""
    return page, tracks


def main():
    html_dir = ROOT / "html"
    html_dir.mkdir(exist_ok=True)
    links = []
    for script, out_name, title in JOBS:
        page, tracks = build_job(script, out_name, title)
        filename = f"{out_name}.html"
        (html_dir / filename).write_text(page, encoding="utf-8")
        links.append((title, filename, out_name, len(tracks)))

    cards = "".join(
        f"<section><h2><a href='{filename}'>{html.escape(title)}</a></h2>"
        f"<p>{count} pistas con transcripción. <a href='../{out_name}/00_escuchar_en_orden.m3u'>Descargar lista de reproducción</a>.</p></section>"
        for title, filename, out_name, count in links
    )
    index = f"""<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Piloto accesible · Semana 1 · CM4H1</title><style>{CSS}</style></head><body>
<a class='skip' href='#contenido'>Saltar al contenido</a><header><p>Universidad Nacional de Ingeniería · CM4H1 · 2026-2</p>
<h1>Piloto accesible de la semana 1</h1><p>Audio comentado, transcripciones y matemáticas explorables.</p></header>
<main id='contenido'><p class='note'>Este piloto complementa las separatas. La voz es sintética y se ajustará después de recoger las preferencias del estudiante.</p>{cards}
<section><h2>Convenciones</h2><p><a href='../README.md'>Leer las convenciones de pronunciación y el modo de uso recomendado</a>.</p></section></main></body></html>"""
    (html_dir / "index.html").write_text(index, encoding="utf-8")


if __name__ == "__main__":
    main()
