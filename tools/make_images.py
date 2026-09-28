#!/usr/bin/env python3
"""Maakt favicon, app-iconen en social-afbeeldingen (OG) uit het logo. Vereist Playwright (Chromium).

  python3 tools/make_images.py
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
os.makedirs(IMG, exist_ok=True)
L = json.load(open(os.path.join(ROOT, "tools", "logo_paths.json")))
x0, y0, x1, y1 = L["bbox"]
w, h = x1 - x0, y1 - y0


def mark(d_fill="#FFFFFF", pad=0.0):
    p = max(w, h) * pad
    vb = f"{x0 - p:.1f} {y0 - p - (w - h) / 2 if w > h else y0 - p:.1f} {max(w, h) + 2 * p:.1f} {max(w, h) + 2 * p:.1f}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'
            f'<path fill="#11B4FF" fill-rule="evenodd" d="{L["blue"]}"/>'
            f'<path fill="{d_fill}" fill-rule="evenodd" d="{L["white"]}"/></svg>')


# favicon.svg: zwart vierkant met afgeronde hoeken + monogram
s = max(w, h) * 1.36
cx, cy = x0 + w / 2, y0 + h / 2
fav = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx - s / 2:.1f} {cy - s / 2:.1f} {s:.1f} {s:.1f}">'
       f'<rect x="{cx - s / 2:.1f}" y="{cy - s / 2:.1f}" width="{s:.1f}" height="{s:.1f}" rx="{s * 0.22:.1f}" fill="#0A0D06"/>'
       f'<path fill="#11B4FF" fill-rule="evenodd" d="{L["blue"]}"/><path fill="#FFFFFF" fill-rule="evenodd" d="{L["white"]}"/></svg>')
open(os.path.join(IMG, "favicon.svg"), "w").write(fav)
open(os.path.join(IMG, "logo-mark.svg"), "w").write(mark())
open(os.path.join(IMG, "logo-mark-light.svg"), "w").write(mark("#0A0D06"))

FONT = "file://" + os.path.join(ROOT, "assets", "fonts", "archivo-var.woff2")
OG = {
    "nl": ("Meer klanten uit je eigen regio.", "Eén partner die alles regelt.", "Website · Huisstijl · Google-profiel · Adverteren · Kassa & facturatie"),
    "fr": ("Plus de clients dans votre région.", "Un seul partenaire pour tout.", "Site web · Identité visuelle · Fiche Google · Publicité · Caisse & facturation"),
    "en": ("More customers from your own area.", "One partner for everything.", "Website · Branding · Google profile · Advertising · POS & invoicing"),
}
jobs = [("favicon-32.png", 32, 32, f'<body style="margin:0">{fav.replace("<svg ", "<svg width=32 height=32 ")}</body>'),
        ("apple-touch-icon.png", 180, 180, f'<body style="margin:0;background:#0A0D06;display:grid;place-items:center;width:180px;height:180px"><div style="width:132px">{mark()}</div></body>'),
        ("logo-512.png", 512, 512, f'<body style="margin:0;background:#0A0D06;display:grid;place-items:center;width:512px;height:512px"><div style="width:380px">{mark()}</div></body>')]
for lang, (a, b, c) in OG.items():
    html = f'''<html><head><style>@font-face{{font-family:A;src:url("{FONT}") format("woff2");font-weight:100 900;font-stretch:62% 125%}}
body{{margin:0;width:1200px;height:630px;background:#0A0D06;color:#fff;font-family:A,Arial Black,sans-serif;position:relative;overflow:hidden}}
.s{{position:absolute;top:-80px;right:-160px;width:520px;height:820px;background:rgba(17,180,255,.16);transform:skewX(-28deg)}}
.m{{position:absolute;left:84px;top:84px;width:150px}} .t{{position:absolute;left:84px;top:250px;right:84px}}
h1{{margin:0;font-weight:820;font-stretch:112%;font-size:64px;line-height:1.04;letter-spacing:-.01em}} h1 span{{display:block;color:#11B4FF}}
p{{margin:28px 0 0;font-family:A;font-weight:500;font-stretch:100%;font-size:26px;color:#A9B5BD}}
.w{{position:absolute;left:260px;top:118px;font-weight:820;font-stretch:114%;font-size:40px}} .w span{{color:#11B4FF;font-weight:600;margin-left:10px}}</style></head>
<body><div class="s"></div><div class="m">{mark()}</div><div class="w">Rozmary<span>Digital</span></div>
<div class="t"><h1>{a}<span>{b}</span></h1><p>{c}</p></div></body></html>'''
    jobs.append((f"og-{lang}.png", 1200, 630, html))

tmp = tempfile.mkdtemp()
script = os.path.join(tmp, "shot.js")
spec = []
for name, W, H, html in jobs:
    hp = os.path.join(tmp, name + ".html")
    open(hp, "w").write(html)
    spec.append({"in": hp, "out": os.path.join(IMG, name), "w": W, "h": H})
open(os.path.join(tmp, "spec.json"), "w").write(json.dumps(spec))
open(script, "w").write('''const { chromium } = require('playwright'); const spec = require(process.argv[2]);
(async () => { const b = await chromium.launch(); for (const j of spec) { const p = await b.newPage({ viewport: { width: j.w, height: j.h } });
await p.goto('file://' + j.in); await p.waitForTimeout(250); await p.screenshot({ path: j.out, omitBackground: j.w === 32 }); await p.close(); } await b.close(); })();''')
env = dict(os.environ, NODE_PATH=os.path.expanduser("~/.npm-global/lib/node_modules") + ":/home/claude/.npm-global/lib/node_modules")
subprocess.run(["node", script, os.path.join(tmp, "spec.json")], check=True, env=env)
print("afbeeldingen:", ", ".join(sorted(os.listdir(IMG))))
