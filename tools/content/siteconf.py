"""Rozmary Digital — gedeelde gegevens: bedrijf, prijzen, talen, slugs.

Prijzen staan hier ÉÉN keer. In de teksten verwijs je ernaar met [[sleutel]],
bv. [[web_start]] of [[starter_m]]. build.py zet ze om naar het juiste formaat
per taal (NL €1.495 · FR 1 495 € · EN €1,495).
"""

DOMAIN = "https://www.rozmarydigital.be"

# Wettelijk verplicht op de site (WER boek XII): naam, geografisch adres, ondernemings- en btw-nummer.
# Bron: KBO Public Search (28-09-2026) — natuurlijk persoon, actief sinds 27-01-2025, btw-plichtig sinds
# 01-02-2025; vestigingseenheid 2.369.448.395 op Pas 151, 2440 Geel sinds 27-03-2026.
BIZ = {
    "name": "Rozmary Digital",
    "owner": "Sebastiaan",
    "legal_name": "Sebastiaan Ganbaatar",   # eenmanszaak; Rozmary Digital is de handelsnaam
    "kbo": "BE 1019.580.163",               # ondernemingsnummer = btw-nummer
    "street": "Pas 151",
    "postal": "2440",
    "city": "Geel",
    "region": "Antwerpen",                  # provincie (structured data)
    "email": "info@rozmarydigital.be",
    "phone": "+32 456 92 02 61",
    "whatsapp": "32456920261",   # internationaal zonder +
    "instagram": "https://www.instagram.com/rozmarydigital/",
}
WA_PLACEHOLDER = "32000000000"   # enkel voor de preview; check.py weigert dit in productie

LANGS = ["nl", "fr", "en"]
LANG_META = {
    "nl": {"html": "nl-BE", "hreflang": "nl-BE", "og": "nl_BE", "name": "Nederlands", "short": "NL", "prefix": ""},
    "fr": {"html": "fr-BE", "hreflang": "fr-BE", "og": "fr_BE", "name": "Français", "short": "FR", "prefix": "fr/"},
    "en": {"html": "en", "hreflang": "en", "og": "en_GB", "name": "English", "short": "EN", "prefix": "en/"},
}

# Alle prijzen excl. btw (euro).
PRICES = {
    "scan": 0, "cards": 119, "vcard": 79, "vcard_m": 5, "gbp": 149, "shopcheck": 149,
    "peppol": 149, "logo": 249, "brand": 595, "web_start": 995, "starter": 1495,
    "starter_m": 99, "web_grow": 2495, "shop": 2995, "care": 29, "plan_local": 249,
    "plan_plus": 595, "ads_m": 199, "ads_setup": 249, "bot": 495, "bot_m": 39,
    "social_m": 349, "photo": 395, "crm": 395, "software": 1500,
    "late_discount": 100,
    # RozmaryPOS (SaaS, zie RozmaryPOS-document): per maand, 36 maanden via domiciliëring
    "pos_m": 175, "pos_web_m": 125, "pos_setup_min": 250, "pos_setup_max": 500,
}
PRICES["starter_loose"] = PRICES["brand"] + PRICES["web_start"] + PRICES["gbp"] + PRICES["cards"]
PRICES["pos_shop_m"] = PRICES["pos_m"] + PRICES["pos_web_m"]   # kassa + webshopmodule = 300

# Diensten in vaste volgorde (menu, homepage, footer).
SERVICE_ORDER = ["website", "starter", "brand", "cards", "google", "shop",
                 "ads", "social", "chatbot", "photo", "pos", "software"]

SERVICE_SLUGS = {
    "website":  {"nl": "website-laten-maken",   "fr": "creation-site-internet",  "en": "website-design"},
    "starter":  {"nl": "starterspakket",        "fr": "pack-demarrage",          "en": "starter-package"},
    "brand":    {"nl": "huisstijl-logo",        "fr": "logo-identite-visuelle",  "en": "logo-branding"},
    "cards":    {"nl": "visitekaartjes",        "fr": "cartes-de-visite",        "en": "business-cards"},
    "google":   {"nl": "google-bedrijfsprofiel", "fr": "fiche-google",           "en": "google-business-profile"},
    "shop":     {"nl": "webshop-laten-maken",   "fr": "boutique-en-ligne",       "en": "webshop"},
    "ads":      {"nl": "online-adverteren",     "fr": "publicite-en-ligne",      "en": "online-advertising"},
    "social":   {"nl": "social-media",          "fr": "reseaux-sociaux",         "en": "social-media"},
    "chatbot":  {"nl": "ai-chatbot",            "fr": "chatbot-ia",              "en": "ai-chatbot"},
    "photo":    {"nl": "foto-video",            "fr": "photo-video",             "en": "photo-video"},
    "pos":      {"nl": "kassa-crm-facturatie",  "fr": "caisse-crm-facturation",  "en": "pos-crm-invoicing"},
    "software": {"nl": "software-koppelingen",  "fr": "logiciels-integrations",  "en": "software-integrations"},
}

PAGE_SLUGS = {
    "home":    {"nl": "",           "fr": "",                "en": ""},
    "pricing": {"nl": "prijzen",    "fr": "tarifs",          "en": "pricing"},
    "method":  {"nl": "werkwijze",  "fr": "methode",         "en": "how-we-work"},
    "work":    {"nl": "realisaties", "fr": "realisations",   "en": "work"},
    "about":   {"nl": "over-ons",   "fr": "a-propos",        "en": "about"},
    "contact": {"nl": "contact",    "fr": "contact",         "en": "contact"},
    "scan":    {"nl": "groeiscan",  "fr": "scan-croissance", "en": "growth-scan"},
    "privacy": {"nl": "privacy",    "fr": "confidentialite", "en": "privacy"},
    "thanks":  {"nl": "bedankt",    "fr": "merci",           "en": "thank-you"},
}
NOINDEX = {"privacy", "thanks"}

# Werkgebied (Kempen eerst), voor footer en structured data.
AREAS = ["Geel", "Mol", "Herentals", "Turnhout", "Westerlo", "Olen", "Kasterlee",
         "Balen", "Laakdal", "Meerhout", "Dessel", "Retie", "Heist-op-den-Berg", "Lier"]

# Kleuren van klantcases (voor de kleurstrook op de casekaarten).
CASES = {
    "shiny": {"name": "Shiny Cleaning", "city": "Geel", "url": "https://www.shinycleaning-kempen.be",
              "colors": ["#17A2A2", "#0A4D4D", "#F6BF45"]},
    "thunder": {"name": "Thunder Racing", "city": "Geel", "url": "https://www.thunderracing.be",
                "colors": ["#FF7101", "#0B0B0B", "#FFFFFF"]},
}
