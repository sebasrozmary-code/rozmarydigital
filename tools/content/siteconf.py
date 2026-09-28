"""Rozmary Digital — gedeelde gegevens: bedrijf, prijzen, talen, slugs.

Prijzen staan hier ÉÉN keer. In de teksten verwijs je ernaar met [[sleutel]],
bv. [[web_start]] of [[starter_m]]. build.py zet ze om naar het juiste formaat
per taal (NL €1.495 · FR 1 495 € · EN €1,495).
"""

DOMAIN = "https://www.rozmarydigital.be"

# Vul de ontbrekende gegevens in vóór livegang (check.py waarschuwt zolang iets op None staat).
BIZ = {
    "name": "Rozmary Digital",
    "owner": "Sebastiaan",
    "legal_name": None,          # bv. "Sebastiaan Achternaam" (eenmanszaak) — verplicht op de site
    "kbo": None,                 # bv. "BE 0123.456.789" — verplicht op de site
    "street": None,              # geografisch adres — verplicht op de site (WER boek XII)
    "postal": "2440",
    "city": "Geel",
    "email": "info@rozmarydigital.be",
    "phone": None,               # bv. "+32 470 12 34 56"
    "whatsapp": None,            # internationaal zonder +, bv. "32470123456"
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
    "social_m": 349, "photo": 395, "crm": 395, "pos": 295, "software": 1500,
    "late_discount": 100,
}
PRICES["starter_loose"] = PRICES["brand"] + PRICES["web_start"] + PRICES["gbp"] + PRICES["cards"]

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
