# rozmarydigital.be

Website van Rozmary Digital in NL (root), FR (`/fr/`) en EN (`/en/`): homepage, 12 dienstpagina's met prijzen en funnel, prijzen, werkwijze, realisaties, over ons, contact, Groeiscan, privacy en bedankpagina — 63 pagina's.

## Werken aan de site
- **Inhoud** staat in `tools/content/`: `siteconf.py` (bedrijfsgegevens, **alle prijzen**, slugs), `nl.py`, `fr.py`, `en.py`.
  Prijzen schrijf je in teksten als `[[web_start]]`; de build zet ze per taal om (NL €1.495 · FR 1 495 € · EN €1,495).
- **Bouwen:** `python3 tools/build.py` → schrijft alle pagina's, `sitemap.xml`, `robots.txt` en `404.html` in de root.
- **Controleren:** `python3 tools/check.py` → titels, descriptions, één H1, canonicals, hreflang, JSON-LD, kapotte links. Moet eindigen op **0 fouten**.
  Vóór livegang: `python3 tools/check.py --strict` (weigert zolang bedrijfsgegevens ontbreken).
- **Afbeeldingen opnieuw maken** (favicon, app-icoon, OG-beelden per taal): `python3 tools/make_images.py` (Playwright/Chromium nodig).
- **Preview met relatieve links:** `python3 tools/build.py --preview /pad/naar/map`.
- Huisstijl: `assets/css/site.css` (zwart #0A0D06, blauw #11B4FF, wit; Archivo + Figtree, zelf gehost). Logo als vector in `tools/logo_paths.json` en `assets/img/logo-mark*.svg`.

## Vóór livegang invullen (`tools/content/siteconf.py` → `BIZ`)
- `legal_name` (naam eenmanszaak), `kbo` (ondernemingsnummer), `street` (adres) — wettelijk verplicht op de site
- `whatsapp` (bv. `32470123456`) en `phone`
- Toestemming van Shiny Cleaning en Thunder Racing voor de cases (`/realisaties/`)
- In `api/aanvraag.php`: `$TO` en `$FROM` (bestaand mailadres op het domein)

## Deploy (zelfde werkwijze als Shiny Cleaning)
1. Repo publiceren: GitHub Desktop → Add local repository → deze map → Publish (private mag).
2. Hostinger hPanel → Websites → rozmarydigital.be → Geavanceerd → Git → repository koppelen, branch `main`, map `public_html`, **auto-deploy aan**.
3. Na elke wijziging: `python3 tools/build.py` → `python3 tools/check.py` → commit → push (VS Code: Sync Changes).
4. Hostinger CDN legen: hPanel → Performance → CDN → Flush cache.
5. Eenmalig: Google Search Console (domein verifiëren, `sitemap.xml` indienen) en het Google-bedrijfsprofiel van Rozmary Digital aanmaken met link naar de site.

`.htaccess` forceert https + www, blokkeert `/tools/` en `/data/`, zet cache- en beveiligingsheaders. Het formulier (`api/aanvraag.php`) mailt elke aanvraag en bewaart een kopie in `/data/aanvragen.jsonl`.
