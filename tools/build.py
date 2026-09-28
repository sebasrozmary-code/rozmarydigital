#!/usr/bin/env python3
"""Bouwt rozmarydigital.be (NL/FR/EN) uit tools/content/.

  python3 tools/build.py                 -> productie: pagina's in de repo-root (Hostinger deployt de root)
  python3 tools/build.py --preview DIR   -> preview met relatieve links (voor de Claude-artifact)
"""
import hashlib, html, importlib, json, os, re, shutil, sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "content"))
import siteconf as C  # noqa: E402

CONTENT = {lang: importlib.import_module(lang) for lang in C.LANGS
           if os.path.exists(os.path.join(ROOT, "tools", "content", lang + ".py"))}
LANGS = [l for l in C.LANGS if l in CONTENT]
MANIFEST = os.path.join(ROOT, "tools", ".generated.json")


# ---------- helpers ----------
def esc(s):
    return html.escape(str(s), quote=True)


def money(lang, n):
    if n == 0:
        return CONTENT[lang].UI["free"]
    if lang == "fr":
        return f"{n:,}".replace(",", " ") + " €"
    if lang == "en":
        return f"€{n:,}"
    return "€" + f"{n:,}".replace(",", ".")


def fill(lang, s):
    """[[sleutel]] -> prijs of bedrijfsgegeven."""
    def rep(m):
        k = m.group(1)
        if k == "legal":
            return C.BIZ["legal_name"] or C.BIZ["name"]
        if k == "email":
            return C.BIZ["email"]
        if k in C.PRICES:
            return money(lang, C.PRICES[k])
        raise KeyError(f"onbekende sleutel [[{k}]]")
    s = re.sub(r"\[\[(\w+)\]\]", rep, s)
    if lang == "fr":  # typographie française : espace insécable avant ? ! : ;
        s = re.sub(r" ([?!:;])", "\u00a0\\1", s)
    return s


def T(lang, s):
    return esc(fill(lang, s))


def sha(path):
    with open(os.path.join(ROOT, path), "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:10]


def page_path(lang, key):
    slug = C.PAGE_SLUGS[key][lang]
    return C.LANG_META[lang]["prefix"] + (slug + "/" if slug else "")


def service_path(lang, key):
    return C.LANG_META[lang]["prefix"] + C.SERVICE_SLUGS[key][lang] + "/"


class Ctx:
    def __init__(self, mode, lang, cur):
        self.mode, self.lang, self.cur = mode, lang, cur
        self.ui = CONTENT[lang].UI

    def up(self):
        return "../" * self.cur.count("/")

    def href(self, to):
        if self.mode == "prod":
            return "/" + to
        return self.up() + to + "index.html"

    def asset(self, p):
        if self.mode == "prod":
            return "/" + p + "?v=" + sha(p)
        return self.up() + p


def wa_number():
    return C.BIZ["whatsapp"] or C.WA_PLACEHOLDER


def wa_url(text):
    return f"https://wa.me/{wa_number()}?text={quote(text)}"


# ---------- iconen (24x24, lijn) ----------
ICONS = {
    "website": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/><circle cx="6.5" cy="6.5" r=".6" fill="currentColor"/><circle cx="9" cy="6.5" r=".6" fill="currentColor"/>',
    "starter": '<path d="M12 3l2.3 5.4 5.7.6-4.3 3.8 1.3 5.7L12 15.6 7 18.5l1.3-5.7L4 9l5.7-.6z"/>',
    "brand": '<path d="M4 20l4.2-1.1L19 8.1 15.9 5 5.1 15.8z"/><path d="M13.8 7.1l3.1 3.1"/>',
    "cards": '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M7 10.5h7M7 13.5h4"/>',
    "google": '<path d="M12 21s-6.5-5.6-6.5-10.5a6.5 6.5 0 0 1 13 0C18.5 15.4 12 21 12 21z"/><circle cx="12" cy="10.5" r="2.4"/>',
    "shop": '<path d="M5 8h14l-1.2 12H6.2z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/>',
    "ads": '<path d="M4 10v4h3l7 4V6l-7 4z"/><path d="M17 9.5a3.5 3.5 0 0 1 0 5M19.3 7a7 7 0 0 1 0 10"/>',
    "social": '<path d="M4 5h16v11H9.5L5 19.5V16H4z"/><path d="M8 9.5h8M8 12.5h5"/>',
    "chatbot": '<rect x="5" y="8" width="14" height="11" rx="3"/><path d="M12 4.5V8"/><circle cx="12" cy="3.6" r="1"/><circle cx="9.5" cy="13.2" r="1" fill="currentColor"/><circle cx="14.5" cy="13.2" r="1" fill="currentColor"/>',
    "photo": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8.5 7l1.4-2.6h4.2L15.5 7"/><circle cx="12" cy="13.4" r="3.4"/>',
    "pos": '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 11.5h6M9 15h3.5"/>',
    "software": '<path d="M8.5 8L4.5 12l4 4M15.5 8l4 4-4 4M13.5 5l-3 14"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "chevron": '<path d="M6 9l6 6 6-6"/>',
    "loop": '<path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20 4v4h-4"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5L12 13l8.5-6.5"/>',
    "pin": '<path d="M12 21s-6.5-5.6-6.5-10.5a6.5 6.5 0 0 1 13 0C18.5 15.4 12 21 12 21z"/><circle cx="12" cy="10.5" r="2.4"/>',
}
WA_ICON = ('<svg class="wa-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2.6a9.3 9.3 0 0 0-8 14.1L2.7 21.4l4.8-1.3A9.3 9.3 0 1 0 12 2.6zm0 17a7.7 7.7 0 0 1-3.9-1.1l-.3-.2-2.8.8.8-2.7-.2-.3A7.7 7.7 0 1 1 12 19.6z"/>'
           '<path fill="currentColor" d="M16.4 14.3c-.2-.1-1.4-.7-1.6-.8-.2-.1-.4-.1-.5.1l-.7.9c-.1.2-.3.2-.5.1a6.3 6.3 0 0 1-3.1-2.7c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.7-1.7c-.2-.4-.4-.4-.5-.4h-.5a.9.9 0 0 0-.6.3 2.7 2.7 0 0 0-.9 2c0 1.2.9 2.4 1 2.5.1.2 1.7 2.6 4.2 3.6 1.6.7 2.2.7 3 .6.5-.1 1.4-.6 1.6-1.1.2-.6.2-1 .1-1.1l-.6-.2z"/></svg>')
IG_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".9" fill="currentColor" stroke="none"/></svg>'


def icon(name, cls=""):
    return (f'<svg{" class=" + chr(34) + cls + chr(34) if cls else ""} viewBox="0 0 24 24" aria-hidden="true" fill="none" '
            f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


LOGO = json.load(open(os.path.join(ROOT, "tools", "logo_paths.json")))
_x0, _y0, _x1, _y1 = LOGO["bbox"]
LOGO_VB = f"{_x0 - 2:.1f} {_y0 - 2:.1f} {_x1 - _x0 + 4:.1f} {_y1 - _y0 + 4:.1f}"


def logo_mark(cls="brand-mark"):
    return (f'<svg class="{cls}" viewBox="{LOGO_VB}" role="img" aria-label="Rozmary Digital">'
            f'<path fill="#11B4FF" fill-rule="evenodd" d="{LOGO["blue"]}"/>'
            f'<path fill="currentColor" fill-rule="evenodd" d="{LOGO["white"]}"/></svg>')


# ---------- bouwstenen ----------
def alternates_for(kind, key):
    fn = service_path if kind == "service" else page_path
    return {l: fn(l, key) for l in LANGS}


def lang_switch(ctx, alts):
    out = []
    for l in LANGS:
        m = C.LANG_META[l]
        cur = ' aria-current="true"' if l == ctx.lang else ""
        out.append(f'<a href="{ctx.href(alts[l])}" hreflang="{m["hreflang"]}" lang="{m["html"]}"{cur} title="{esc(m["name"])}">{m["short"]}</a>')
    return f'<div class="lang" aria-label="{esc(ctx.ui["lang_label"])}">' + "".join(out) + "</div>"


def header(ctx, alts, active):
    ui, L = ctx.ui, ctx.lang
    S = CONTENT[L].SERVICES
    subs = "".join(
        f'<li><a href="{ctx.href(service_path(L, k))}"{" aria-current=" + chr(34) + "page" + chr(34) if active == k else ""}>'
        f'{esc(S[k]["nav"])}<small>{T(L, S[k]["card"])}</small></a></li>' for k in C.SERVICE_ORDER)
    items = [("pricing", ui["nav_pricing"]), ("method", ui["nav_method"]), ("work", ui["nav_work"]),
             ("about", ui["nav_about"]), ("contact", ui["nav_contact"])]
    links = "".join(
        f'<li><a href="{ctx.href(page_path(L, k))}"{" aria-current=" + chr(34) + "page" + chr(34) if active == k else ""}>{esc(t)}</a></li>'
        for k, t in items)
    return f'''<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{ctx.href(page_path(L, "home"))}">{logo_mark()}<span class="brand-word">Rozmary<span>Digital</span></span></a>
    <nav class="main-nav" id="main-nav" aria-label="{esc(ui["menu"])}">
      <ul>
        <li class="has-sub"><button class="sub-toggle" type="button" aria-expanded="false">{esc(ui["nav_services"])}{icon("chevron")}</button>
          <div class="sub"><ul>{subs}</ul></div></li>
        {links}
      </ul>
      <div class="nav-extra">{lang_switch(ctx, alts)}
        <a class="btn btn-ghost btn-sm btn-wa" data-evt="whatsapp_click" href="{esc(wa_url(ui["wa_general"]))}" target="_blank" rel="noopener">{WA_ICON}{esc(ui["whatsapp"])}</a></div>
    </nav>
    <a class="btn btn-primary btn-sm header-cta" data-evt="scan_click" href="{ctx.href(page_path(L, "scan"))}">{esc(ui["cta_scan"])}</a>
    <button class="menu-toggle" type="button" aria-controls="main-nav" aria-expanded="false"><span aria-hidden="true"></span>{esc(ui["menu"])}</button>
  </div>
</header>'''


def footer(ctx, alts):
    ui, L = ctx.ui, ctx.lang
    S = CONTENT[L].SERVICES
    svc = "".join(f'<li><a href="{ctx.href(service_path(L, k))}">{esc(S[k]["nav"])}</a></li>' for k in C.SERVICE_ORDER)
    comp = "".join(f'<li><a href="{ctx.href(page_path(L, k))}">{esc(t)}</a></li>' for k, t in [
        ("pricing", ui["nav_pricing"]), ("method", ui["nav_method"]), ("work", ui["nav_work"]),
        ("about", ui["nav_about"]), ("scan", ui["cta_scan"]), ("contact", ui["nav_contact"])])
    areas = ", ".join(C.AREAS)
    kbo = f'{esc(ui["kbo"])} {esc(C.BIZ["kbo"])}' if C.BIZ["kbo"] else esc(ui["kbo_missing"])
    legal = esc(C.BIZ["legal_name"]) + " · " if C.BIZ["legal_name"] else ""
    phone = f'<li><a href="tel:{esc(C.BIZ["phone"].replace(" ", ""))}">{esc(C.BIZ["phone"])}</a></li>' if C.BIZ["phone"] else ""
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="{ctx.href(page_path(L, "home"))}">{logo_mark()}<span class="brand-word">Rozmary<span>Digital</span></span></a>
        <p>{esc(ui["footer_tagline"])}</p>
        <div class="social"><a href="{esc(C.BIZ["instagram"])}" target="_blank" rel="noopener" aria-label="Instagram">{IG_ICON}</a>
          <a href="{esc(wa_url(ui["wa_general"]))}" target="_blank" rel="noopener" aria-label="WhatsApp" data-evt="whatsapp_click">{WA_ICON}</a></div>
      </div>
      <div><h2>{esc(ui["footer_services"])}</h2><ul>{svc}</ul></div>
      <div><h2>{esc(ui["footer_company"])}</h2><ul>{comp}</ul></div>
      <div><h2>{esc(ui["footer_contact"])}</h2><ul>
        <li><a href="{esc(wa_url(ui["wa_general"]))}" target="_blank" rel="noopener" data-evt="whatsapp_click">WhatsApp</a></li>
        <li><a href="mailto:{esc(C.BIZ["email"])}" data-evt="email_click">{esc(C.BIZ["email"])}</a></li>{phone}
        <li>{esc(C.BIZ["city"])}, {esc(ui["region"])}</li></ul>
        <h2 style="margin-top:22px">{esc(ui["footer_area"])}</h2><p>{esc(areas)}</p></div>
    </div>
    <div class="footer-bottom">
      <span>© <span data-year>2026</span> {esc(C.BIZ["name"])} · {legal}{kbo} · {esc(ui["rights"])} · <a href="{ctx.href(page_path(L, "privacy"))}">{esc(ui["privacy"])}</a></span>
      {lang_switch(ctx, alts)}
    </div>
  </div>
</footer>
<div class="mobile-bar">
  <a class="btn btn-ghost btn-wa" data-evt="whatsapp_click" href="{esc(wa_url(ui["wa_general"]))}" target="_blank" rel="noopener">{WA_ICON}{esc(ui["whatsapp"])}</a>
  <a class="btn btn-primary" data-evt="scan_click" href="{ctx.href(page_path(L, "scan"))}">{esc(ui["cta_scan"])}</a>
</div>'''


def crumbs(ctx, trail):
    """trail: [(naam, pad of None)]"""
    items = []
    for name, path in trail:
        if path is None:
            items.append(f'<li aria-current="page">{esc(name)}</li>')
        else:
            items.append(f'<li><a href="{ctx.href(path)}">{esc(name)}</a></li>')
    return f'<nav aria-label="{esc(ctx.ui["breadcrumb"])}"><ol class="crumbs">{"".join(items)}</ol></nav>'


def page_hero(ctx, trail, h1, lead, chips=None, ctas=""):
    ch = ""
    if chips:
        ch = '<ul class="chips">' + "".join(f"<li>{T(ctx.lang, c)}</li>" for c in chips) + "</ul>"
    return f'''<section class="page-hero"><div class="wrap">
  {crumbs(ctx, trail)}
  <h1>{T(ctx.lang, h1)}</h1>
  <p class="lead">{T(ctx.lang, lead)}</p>
  {ch}{ctas}
</div></section>'''


def cta_band(ctx, h=None, p=None):
    ui = ctx.ui
    return f'''<section class="cta-band"><div class="wrap cta-inner">
  <div><h2>{T(ctx.lang, h or ui["cta_band_h"])}</h2><p>{T(ctx.lang, p or ui["cta_band_p"])}</p></div>
  <div class="btn-row">
    <a class="btn btn-primary" data-evt="scan_click" href="{ctx.href(page_path(ctx.lang, "scan"))}">{esc(ui["cta_scan"])}</a>
    <a class="btn btn-ghost btn-wa" data-evt="whatsapp_click" href="{esc(wa_url(ui["wa_general"]))}" target="_blank" rel="noopener">{WA_ICON}{esc(ui["whatsapp_long"])}</a>
  </div>
</div></section>'''


def service_card(ctx, key):
    L, S = ctx.lang, CONTENT[ctx.lang].SERVICES[key]
    per = f' <small>{esc(ctx.ui["per_month"])}</small>' if S.get("price_card_per") else ""
    price = fill(L, S["price_card"])
    frm = "" if price == ctx.ui["free"] else esc(ctx.ui["from"])
    return f'''<a class="card" href="{ctx.href(service_path(L, key))}">
  <span class="card-icon">{icon(key)}</span>
  <h3>{esc(S["nav"])}</h3>
  <p>{T(L, S["card"])}</p>
  <span class="card-price"><span>{frm} <strong>{esc(price)}</strong>{per}</span><span class="arrow" aria-hidden="true">→</span></span>
</a>'''


def faq_block(ctx, faq, h=None):
    items = "".join(f'<details><summary>{T(ctx.lang, q)}</summary><div class="answer"><p>{T(ctx.lang, a)}</p></div></details>' for q, a in faq)
    return f'<div class="section-head"><h2>{esc(h or ctx.ui["faq_h"])}</h2></div><div class="faq">{items}</div>'


def plan_card(ctx, name, price_key=None, price_text=None, per=False, frm=False, note=None, items=(), cta=None, href=None, featured=False):
    ui, L = ctx.ui, ctx.lang
    if price_key is not None or price_text:
        pt = price_text if price_text else money(L, C.PRICES[price_key])
        price = f'<div class="price">{"<span class=" + chr(34) + "from" + chr(34) + ">" + esc(ui["from"]) + "</span>" if frm else ""}<strong>{esc(fill(L, pt))}</strong>{"<span class=" + chr(34) + "per" + chr(34) + ">" + esc(ui["per_month"]) + "</span>" if per else ""}</div>'
    else:
        price = f'<div class="price"><strong>{esc(ui["on_quote"])}</strong></div>'
    tag = f'<span class="tag">{esc(ui["recommended"])}</span>' if featured else ""
    lis = "".join(f"<li>{icon('check')}<span>{T(L, i)}</span></li>" for i in items)
    nt = f'<p class="pnote">{T(L, note)}</p>' if note else ""
    btn = f'<a class="btn btn-primary" href="{href}">{T(L, cta)}</a>' if cta and href else ""
    return f'<div class="plan{" featured" if featured else ""}">{tag}<h3>{T(L, name)}</h3>{price}{nt}<ul>{lis}</ul>{btn}</div>'


def contact_link(ctx, service_key, pkg_name=None):
    base = ctx.href(page_path(ctx.lang, "contact"))
    q = f"?dienst={quote(service_key)}"
    if pkg_name:
        q += "&pakket=" + quote(fill(ctx.lang, pkg_name))
    return base + q + "#formulier"


def lead_form(ctx, form_id, preset=None, scan=False):
    ui, L = ctx.ui, ctx.lang
    F = ui["form"]
    S = CONTENT[L].SERVICES
    opts = [("scan", ui["cta_scan"])] + [(k, S[k]["nav"]) for k in C.SERVICE_ORDER] + [("other", F["other"])]
    options = "".join(f'<option value="{k}"{" selected" if k == preset else ""}>{esc(t)}</option>' for k, t in opts)
    endpoint = "/api/aanvraag.php" if ctx.mode == "prod" else ctx.up() + "api/aanvraag.php"
    thanks = ctx.href(page_path(L, "thanks"))
    wa_base = f"https://wa.me/{wa_number()}"
    site_req = "" if not scan else ""
    return f'''<form class="lead-form" id="{form_id}" method="post" action="{endpoint}" data-endpoint="{endpoint}" data-thanks="{thanks}"
  data-ok="{esc(F["ok"])}" data-fail="{esc(F["fail"])}" data-sending="{esc(F["sending"])}" data-wa-intro="{esc(F["wa_intro"])}">
  <input type="hidden" name="lang" value="{L}"><input type="hidden" name="page" value="{esc(ctx.cur)}"><input type="hidden" name="ts" value="">
  <input type="hidden" name="thanks" value="{esc(page_path(L, "thanks"))}">
  <div class="hp" aria-hidden="true"><label for="{form_id}-url">URL</label><input id="{form_id}-url" name="company_url" tabindex="-1" autocomplete="off"></div>
  <div class="field-row">
    <div class="field"><label for="{form_id}-name">{esc(F["name"])}</label><input id="{form_id}-name" name="name" autocomplete="name" required></div>
    <div class="field"><label for="{form_id}-company">{esc(F["company"])}</label><input id="{form_id}-company" name="company" autocomplete="organization"></div>
  </div>
  <div class="field-row">
    <div class="field"><label for="{form_id}-email">{esc(F["email"])}</label><input id="{form_id}-email" name="email" type="email" autocomplete="email" required></div>
    <div class="field"><label for="{form_id}-phone">{esc(F["phone"])}</label><input id="{form_id}-phone" name="phone" type="tel" autocomplete="tel"></div>
  </div>
  <div class="field-row">
    <div class="field"><label for="{form_id}-website">{esc(F["website"])}</label><input id="{form_id}-website" name="website" inputmode="url" placeholder="www."{site_req}></div>
    <div class="field"><label for="{form_id}-city">{esc(F["city"])}</label><input id="{form_id}-city" name="city" autocomplete="address-level2"></div>
  </div>
  <div class="field"><label for="{form_id}-interest">{esc(F["interest"])}</label><select id="{form_id}-interest" name="interest">{options}</select></div>
  <div class="field"><label for="{form_id}-message">{esc(F["message"])}</label><textarea id="{form_id}-message" name="message" rows="5"></textarea></div>
  <label class="consent"><input type="checkbox" name="consent" value="1" required><span>{esc(F["consent"])} <a href="{ctx.href(page_path(L, "privacy"))}">{esc(F["consent_link"])}</a></span></label>
  <div class="btn-row"><button class="btn btn-primary" type="submit">{esc(F["submit"])}</button></div>
  <p class="form-status" role="status" aria-live="polite"></p>
  <div class="form-fallback" hidden>
    <a class="btn btn-dark btn-wa" data-wa-fallback data-base="{wa_base}" href="{wa_base}" target="_blank" rel="noopener">{WA_ICON}{esc(F["wa_fallback"])}</a>
    <a class="btn btn-ghost" href="mailto:{esc(C.BIZ["email"])}">{esc(C.BIZ["email"])}</a>
  </div>
</form>'''


# ---------- structured data ----------
def org_ld(lang):
    ui = CONTENT[lang].UI
    d = {
        "@type": "ProfessionalService", "@id": C.DOMAIN + "/#org", "name": C.BIZ["name"],
        "url": C.DOMAIN + "/", "logo": C.DOMAIN + "/assets/img/logo-512.png", "image": C.DOMAIN + "/assets/img/og-nl.png",
        "email": C.BIZ["email"], "description": fill(lang, CONTENT[lang].PAGES["home"]["desc"]),
        "sameAs": [C.BIZ["instagram"]], "priceRange": "€€",
        "address": {"@type": "PostalAddress", "addressLocality": C.BIZ["city"], "addressRegion": "Antwerpen", "addressCountry": "BE"},
        "areaServed": [{"@type": "City", "name": a} for a in C.AREAS] + [{"@type": "Country", "name": "België"}],
        "knowsLanguage": ["nl", "fr", "en"],
    }
    if C.BIZ["street"]:
        d["address"]["streetAddress"] = C.BIZ["street"]
        d["address"]["postalCode"] = C.BIZ["postal"]
    if C.BIZ["phone"]:
        d["telephone"] = C.BIZ["phone"]
    if C.BIZ["kbo"]:
        d["vatID"] = C.BIZ["kbo"]
    return d


def crumbs_ld(lang, trail):
    items = []
    for i, (name, path) in enumerate(trail, 1):
        items.append({"@type": "ListItem", "position": i, "name": name, "item": C.DOMAIN + "/" + (path or "")})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def faq_ld(lang, faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": fill(lang, q),
            "acceptedAnswer": {"@type": "Answer", "text": fill(lang, a)}} for q, a in faq]}


def service_ld(lang, key, path):
    S = CONTENT[lang].SERVICES[key]
    offers = []
    for p in S["packages"]:
        m = re.fullmatch(r"\[\[(\w+)\]\]", p.get("price") or "")
        if not m:
            continue
        val = C.PRICES[m.group(1)]
        spec = {"@type": "UnitPriceSpecification", "price": val, "priceCurrency": "EUR", "valueAddedTaxIncluded": False}
        if p.get("per"):
            spec["unitText"] = "MON"
        offers.append({"@type": "Offer", "name": fill(lang, p["name"]), "price": val, "priceCurrency": "EUR", "priceSpecification": spec})
    return {"@type": "Service", "name": fill(lang, S["h1"]), "serviceType": S["nav"], "url": C.DOMAIN + "/" + path,
            "provider": {"@id": C.DOMAIN + "/#org"}, "areaServed": {"@type": "Country", "name": "België"},
            "description": fill(lang, S["desc"]), "offers": offers}


# ---------- documenten ----------
def document(ctx, title, desc, main, alts, active, ld=(), noindex=False, fragment=False):
    L = ctx.lang
    m = C.LANG_META[L]
    head_links = []
    if alts and not noindex:
        for l in LANGS:
            head_links.append(f'<link rel="alternate" hreflang="{C.LANG_META[l]["hreflang"]}" href="{C.DOMAIN}/{alts[l]}">')
        head_links.append(f'<link rel="alternate" hreflang="x-default" href="{C.DOMAIN}/{alts["nl"]}">')
    graph = [x for x in ld if x]
    ld_json = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) if graph else ""
    body = f'''<a class="skip" href="#main">{esc(ctx.ui["skip"])}</a>
{header(ctx, alts, active)}
<main id="main">
{main}
</main>
{footer(ctx, alts)}
<script src="{ctx.asset("assets/js/site.js")}" defer></script>'''
    if fragment:
        return (f'<title>Rozmary Digital Website</title>\n<link rel="stylesheet" href="{ctx.asset("assets/css/site.css")}">\n'
                f'<script>document.documentElement.lang="{m["html"]}";</script>\n' + body + "\n")
    canonical = C.DOMAIN + "/" + ctx.cur
    og = C.DOMAIN + f"/assets/img/og-{L}.png"
    robots = '<meta name="robots" content="noindex, follow">\n' if noindex else ""
    ldtag = f'<script type="application/ld+json">{ld_json}</script>\n' if ld_json else ""
    return f'''<!doctype html>
<html lang="{m["html"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<link rel="canonical" href="{canonical}">
{chr(10).join(head_links)}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(C.BIZ["name"])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="{m["og"]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0A0D06">
<link rel="icon" href="{ctx.asset("assets/img/favicon.svg")}" type="image/svg+xml">
<link rel="icon" href="{ctx.asset("assets/img/favicon-32.png")}" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{ctx.asset("assets/img/apple-touch-icon.png")}">
<link rel="preload" href="{ctx.asset("assets/fonts/archivo-var.woff2").split("?")[0]}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{ctx.asset("assets/css/site.css")}">
{ldtag}</head>
<body>
{body}
</body>
</html>
'''


# ---------- pagina's ----------
def build_home(ctx):
    L, ui, P = ctx.lang, ctx.ui, CONTENT[ctx.lang].PAGES["home"]
    def tprice(p):
        main, _, per = fill(L, p).partition("/")
        return esc(main) + (f"<small>/{esc(per)}</small>" if per else "")
    tickets = "".join(f'<div class="ticket"><span class="ticket-name">{T(L, n)}</span><span class="ticket-price">{tprice(p)}</span><span class="ticket-note">{T(L, d)}</span></div>' for n, p, d in P["tickets"])
    trust = "".join(f'<li><span class="dash" aria-hidden="true"></span>{T(L, t)}</li>' for t in P["trust"])
    cards = "".join(service_card(ctx, k) for k in C.SERVICE_ORDER)
    model = "".join(f'<li><span class="num">{i}</span><h3>{esc(n)}</h3><p class="q">{T(L, q)}</p><p>{T(L, d)}</p></li>'
                    for i, (n, q, d, _s) in enumerate(CONTENT[L].MODEL, 1))
    W = CONTENT[L].PAGES["work"]
    cases = ""
    for ck in ("shiny", "thunder"):
        c, cc = W["cases"][ck], C.CASES[ck]
        sw = "".join(f'<span style="background:{col}"></span>' for col in cc["colors"])
        facts = "".join(f"<div><strong>{esc(a)}</strong><span>{T(L, b)}</span></div>" for a, b in c["facts"])
        cases += f'''<article class="case"><div class="swatch" aria-hidden="true">{sw}</div><span class="sector">{T(L, c["sector"])} · {esc(cc["city"])}</span>
  <h3>{esc(cc["name"])}</h3><p class="case-q">{T(L, c["question"])}</p><div class="facts">{facts}</div></article>'''
    why = "".join(f'<li><h3><span class="dash" aria-hidden="true"></span>{T(L, a)}</h3><p>{T(L, b)}</p></li>' for a, b in P["why"])
    plans = "".join(plan_card(ctx, n, price_key=k, per=True, items=items, featured=(i == 1), cta=ui["more"],
                              href=ctx.href(page_path(L, "pricing")) + "#maandplannen")
                    for i, (n, k, items) in enumerate(P["plans"]))
    st = CONTENT[L].SERVICES["starter"]
    starter_items = "".join(f'<li><span class="dash" aria-hidden="true"></span>{T(L, x)}</li>' for x in P["starter_items"])
    main = f'''<section class="hero"><div class="wrap hero-grid">
  <div>
    <span class="eyebrow"><span class="dash" aria-hidden="true"></span>{T(L, P["eyebrow"])}</span>
    <h1>{T(L, P["h1a"])} <span class="line2">{T(L, P["h1b"])}</span></h1>
    <p class="lead">{T(L, P["lead"])}</p>
    <div class="btn-row">
      <a class="btn btn-primary" data-evt="scan_click" href="{ctx.href(page_path(L, "scan"))}">{esc(ui["cta_scan"])}</a>
      <a class="btn btn-ghost" href="{ctx.href(page_path(L, "pricing"))}">{T(L, P["cta2"])}</a>
    </div>
    <ul class="trust">{trust}</ul>
  </div>
  <div class="tickets" aria-label="{esc(ui["nav_pricing"])}">{tickets}</div>
</div></section>
<section class="section" id="diensten"><div class="wrap">
  <div class="section-head"><h2>{T(L, P["services_h"])}</h2><p>{T(L, P["services_p"])}</p></div>
  <div class="cards">{cards}</div>
</div></section>
<section class="band-blue"><div class="wrap band-grid">
  <div><h2>{T(L, P["starter_h"])}</h2><p>{T(L, P["starter_p"])}</p><ul class="check-list">{starter_items}</ul></div>
  <div class="price-box"><span class="small">{esc(st["nav"])}</span><span class="big">{esc(money(L, C.PRICES["starter"]))}</span>
    <span class="small">{T(L, P["starter_price_note"])} · {esc(ui["excl"])}</span>
    <a class="btn btn-primary" href="{ctx.href(service_path(L, "starter"))}">{T(L, P["starter_cta"])}</a></div>
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head"><h2>{T(L, P["method_h"])}</h2><p>{T(L, P["method_p"])}</p></div>
  <ol class="model">{model}</ol>
  <p class="loop">{icon("loop")}{T(L, P["method_loop"])} <a href="{ctx.href(page_path(L, "method"))}">{T(L, P["method_cta"])}</a></p>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head"><h2>{T(L, P["work_h"])}</h2></div>
  <div class="cases">{cases}</div>
  <p class="note"><a href="{ctx.href(page_path(L, "work"))}">{T(L, P["work_cta"])} →</a></p>
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head"><h2>{T(L, P["why_h"])}</h2></div>
  <ul class="why">{why}</ul>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head"><h2>{T(L, P["plans_h"])}</h2><p>{T(L, P["plans_p"])}</p></div>
  <div class="plans">{plans}</div>
  <p class="note">{esc(ui["rights"])} <a href="{ctx.href(page_path(L, "pricing"))}">{T(L, P["plans_cta"])} →</a></p>
</div></section>
<section class="section alt"><div class="wrap">{faq_block(ctx, P["faq"])}</div></section>
{cta_band(ctx)}'''
    ld = [org_ld(L), {"@type": "WebSite", "@id": C.DOMAIN + "/#website", "url": C.DOMAIN + "/", "name": C.BIZ["name"],
                      "inLanguage": C.LANG_META[L]["html"], "publisher": {"@id": C.DOMAIN + "/#org"}}, faq_ld(L, P["faq"])]
    return fill(L, P["title"]), fill(L, P["desc"]), main, ld


def build_service(ctx, key):
    L, ui = ctx.lang, ctx.ui
    S = CONTENT[L].SERVICES[key]
    path = service_path(L, key)
    trail = [(ui["home"], page_path(L, "home")), (S["nav"], None)]
    feat = next((p for p in S["packages"] if p.get("featured")), S["packages"][0])
    ctas = f'''<div class="btn-row"><a class="btn btn-primary" href="{contact_link(ctx, key, feat["name"])}">{T(L, feat["cta"])}</a>
  <a class="btn btn-ghost btn-wa" data-evt="whatsapp_click" href="{esc(wa_url(fill(L, ui["wa_service"]).format(s=S["nav"])))}" target="_blank" rel="noopener">{WA_ICON}{esc(ui["whatsapp"])}</a></div>'''
    bullets = "".join(f'<li><span class="dash" aria-hidden="true"></span><span>{T(L, b)}</span></li>' for b in S["bullets"])
    pk = ""
    for p in S["packages"]:
        m = re.fullmatch(r"\[\[(\w+)\]\]", p.get("price") or "")
        link = p.get("link")
        if link in C.SERVICE_SLUGS:
            href = ctx.href(service_path(L, link))
        elif link in C.PAGE_SLUGS:
            href = ctx.href(page_path(L, link))
        else:
            href = contact_link(ctx, key, p["name"])
        pk += plan_card(ctx, p["name"], price_key=m.group(1) if m else None, per=p.get("per", False), frm=p.get("from", False),
                        note=p.get("note"), items=p["items"], cta=p["cta"], href=href, featured=p.get("featured", False))
    steps = S.get("steps") or CONTENT[L].STEPS
    st = "".join(f"<li><h3>{T(L, a)}</h3><p>{T(L, b)}</p></li>" for a, b in steps)
    rel = "".join(service_card(ctx, k) for k in S["related"])
    main = f'''{page_hero(ctx, trail, S["h1"], S["lead"], S["chips"], ctas)}
<section class="section"><div class="wrap split">
  <div class="text"><h2>{T(L, S["intro_h"])}</h2><p>{T(L, S["intro"])}</p></div>
  <ul class="bullets">{bullets}</ul>
</div></section>
<section class="section alt" id="prijzen"><div class="wrap">
  <div class="section-head"><h2>{esc(ui["packages_h"])}</h2></div>
  <div class="packages">{pk}</div>
  <p class="note">{T(L, S["packages_note"])}</p>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head"><h2>{esc(ui["steps_h"])}</h2></div>
  <ol class="steps">{st}</ol>
</div></section>
<section class="section alt"><div class="wrap">{faq_block(ctx, S["faq"])}</div></section>
<section class="section"><div class="wrap">
  <div class="section-head"><h2>{esc(ui["related_h"])}</h2></div>
  <div class="cards">{rel}</div>
</div></section>
{cta_band(ctx)}'''
    ld = [service_ld(L, key, path), crumbs_ld(L, [(ui["home"], page_path(L, "home")), (S["nav"], path)]), faq_ld(L, S["faq"])]
    return fill(L, S["title"]), fill(L, S["desc"]), main, ld


def simple_trail(ctx, name):
    return [(ctx.ui["home"], page_path(ctx.lang, "home")), (name, None)]


def build_pricing(ctx):
    L, ui, P = ctx.lang, ctx.ui, CONTENT[ctx.lang].PAGES["pricing"]
    groups = ""
    for gname, gid, rows in CONTENT[L].PRICE_GROUPS:
        lis = ""
        for name, desc, pkey, per, frm, target in rows:
            href = ctx.href(page_path(L, target)) if target in C.PAGE_SLUGS else ctx.href(service_path(L, target))
            pr = money(L, C.PRICES[pkey])
            pre = f'<small>{esc(ui["from"])}</small> ' if frm else ""
            suf = f' <small>{esc(ui["per_month"])}</small>' if per else ""
            lis += f'<li><span class="pname"><a href="{href}">{T(L, name)}</a></span><span class="pdesc">{T(L, desc)}</span><span class="pprice">{pre}{esc(pr)}{suf}</span></li>'
        idattr = f' id="{gid}"' if gid else ""
        groups += f'<section class="price-group"{idattr}><h2><span class="dash" aria-hidden="true"></span>{T(L, gname)}</h2><ul class="price-rows">{lis}</ul></section>'
    rules = "".join(f'<li><span class="dash" aria-hidden="true"></span><span>{T(L, r)}</span></li>' for r in P["rules"])
    main = f'''{page_hero(ctx, simple_trail(ctx, ui["nav_pricing"]), P["h1"], P["lead"])}
<section class="section"><div class="wrap">{groups}</div></section>
<section class="section alt"><div class="wrap"><div class="section-head"><h2>{T(L, P["rules_h"])}</h2></div><ul class="rules">{rules}</ul></div></section>
<section class="section"><div class="wrap">{faq_block(ctx, P["faq"])}</div></section>
{cta_band(ctx)}'''
    ld = [crumbs_ld(L, [(ui["home"], page_path(L, "home")), (ui["nav_pricing"], page_path(L, "pricing"))]), faq_ld(L, P["faq"])]
    return fill(L, P["title"]), fill(L, P["desc"]), main, ld


def build_method(ctx):
    L, ui, P = ctx.lang, ctx.ui, CONTENT[ctx.lang].PAGES["method"]
    S = CONTENT[L].SERVICES
    items = ""
    for i, (n, q, d, svcs) in enumerate(CONTENT[L].MODEL, 1):
        links = " · ".join(f'<a href="{ctx.href(service_path(L, k))}">{esc(S[k]["nav"])}</a>' for k in svcs)
        items += f'<li><span class="num">{i}</span><h3>{esc(n)}</h3><p class="q">{T(L, q)}</p><p>{T(L, d)}</p><p>{links}</p></li>'
    st = "".join(f"<li><h3>{T(L, a)}</h3><p>{T(L, b)}</p></li>" for a, b in CONTENT[L].STEPS)
    main = f'''{page_hero(ctx, simple_trail(ctx, ui["nav_method"]), P["h1"], P["lead"])}
<section class="section"><div class="wrap"><ol class="model">{items}</ol></div></section>
<section class="section alt"><div class="wrap split">
  <div class="text"><h2>{T(L, P["loop_h"])}</h2><p>{T(L, P["loop_p"])}</p></div>
  <p class="loop">{icon("loop")}{T(L, CONTENT[L].PAGES["home"]["method_loop"])}</p>
</div></section>
<section class="section"><div class="wrap"><div class="section-head"><h2>{T(L, P["project_h"])}</h2></div><ol class="steps">{st}</ol></div></section>
{cta_band(ctx)}'''
    return fill(L, P["title"]), fill(L, P["desc"]), main, [crumbs_ld(L, [(ui["home"], page_path(L, "home")), (ui["nav_method"], page_path(L, "method"))])]


def build_work(ctx):
    L, ui, P = ctx.lang, ctx.ui, CONTENT[ctx.lang].PAGES["work"]
    cases = ""
    for ck in ("shiny", "thunder"):
        c, cc = P["cases"][ck], C.CASES[ck]
        sw = "".join(f'<span style="background:{col}"></span>' for col in cc["colors"])
        did = "".join(f'<li><span class="dash" aria-hidden="true"></span><span>{T(L, x)}</span></li>' for x in c["did"])
        facts = "".join(f"<div><strong>{esc(a)}</strong><span>{T(L, b)}</span></div>" for a, b in c["facts"])
        cases += f'''<article class="case"><div class="swatch" aria-hidden="true">{sw}</div>
  <span class="sector">{T(L, c["sector"])} · {esc(cc["city"])}</span><h3>{esc(cc["name"])}</h3>
  <p class="case-q">{T(L, c["question"])}</p><ul class="did">{did}</ul><div class="facts">{facts}</div>
  <p><a href="{esc(cc["url"])}" target="_blank" rel="noopener">{T(L, P["visit"])} →</a></p></article>'''
    main = f'''{page_hero(ctx, simple_trail(ctx, ui["nav_work"]), P["h1"], P["lead"])}
<section class="section"><div class="wrap"><div class="cases">{cases}</div></div></section>
{cta_band(ctx)}'''
    return fill(L, P["title"]), fill(L, P["desc"]), main, [crumbs_ld(L, [(ui["home"], page_path(L, "home")), (ui["nav_work"], page_path(L, "work"))])]


def build_about(ctx):
    L, ui, P = ctx.lang, ctx.ui, CONTENT[ctx.lang].PAGES["about"]
    secs = "".join(f"<div><h2>{T(L, h)}</h2><p>{T(L, p)}</p></div>" for h, p in P["sections"])
    vals = "".join(f'<li><span class="dash" aria-hidden="true"></span><span>{T(L, v)}</span></li>' for v in P["values"])
    areas = "".join(f"<li>{esc(a)}</li>" for a in C.AREAS)
    main = f'''{page_hero(ctx, simple_trail(ctx, ui["nav_about"]), P["h1"], P["lead"])}
<section class="section"><div class="wrap split">
  <div class="prose">{secs}</div>
  <div class="prose"><div><h2>{T(L, P["values_h"])}</h2><ul class="values" style="margin-top:14px">{vals}</ul></div>
    <div><h2>{T(L, P["area_h"])}</h2><p>{T(L, P["area_p"])}</p><ul class="area-list">{areas}</ul></div></div>
</div></section>
{cta_band(ctx)}'''
    return fill(L, P["title"]), fill(L, P["desc"]), main, [org_ld(L), crumbs_ld(L, [(ui["home"], page_path(L, "home")), (ui["nav_about"], page_path(L, "about"))])]


def build_contact(ctx):
    L, ui, P = ctx.lang, ctx.ui, CONTENT[ctx.lang].PAGES["contact"]
    wa_disp = C.BIZ["phone"] or "WhatsApp"
    main = f'''{page_hero(ctx, simple_trail(ctx, ui["nav_contact"]), P["h1"], P["lead"])}
<section class="section"><div class="wrap form-wrap">
  <ul class="contact-list">
    <li><h3>{WA_ICON.replace('class="wa-icon"', 'class="wa-icon" width="24" height="24"')}{T(L, P["wa_h"])}</h3><p>{T(L, P["wa_p"])}</p>
      <p><a class="btn btn-dark btn-wa" data-evt="whatsapp_click" href="{esc(wa_url(ui["wa_general"]))}" target="_blank" rel="noopener">{WA_ICON}{esc(ui["whatsapp_long"])}</a></p>
      <p class="contact-value">{esc(wa_disp)}</p></li>
    <li><h3>{icon("mail")}{T(L, P["mail_h"])}</h3><p>{T(L, P["mail_p"])}</p><p class="contact-value">{esc(C.BIZ["email"])}</p></li>
    <li><h3>{icon("pin")}{T(L, P["visit_h"])}</h3><p>{T(L, P["visit_p"])}</p></li>
  </ul>
  <div id="formulier"><h2 style="margin-bottom:16px">{T(L, P["form_h"])}</h2>{lead_form(ctx, "contactformulier")}</div>
</div></section>'''
    return fill(L, P["title"]), fill(L, P["desc"]), main, [org_ld(L), crumbs_ld(L, [(ui["home"], page_path(L, "home")), (ui["nav_contact"], page_path(L, "contact"))])]


def build_scan(ctx):
    L, ui, P = ctx.lang, ctx.ui, CONTENT[ctx.lang].PAGES["scan"]
    checks = "".join(f'<li><span class="dash" aria-hidden="true"></span><span>{T(L, c)}</span></li>' for c in P["checks"])
    main = f'''{page_hero(ctx, simple_trail(ctx, ui["cta_scan"]), P["h1"], P["lead"])}
<section class="section"><div class="wrap form-wrap">
  <div class="text" style="display:grid;gap:18px"><h2>{T(L, P["check_h"])}</h2><ul class="bullets">{checks}</ul><p class="note">{T(L, P["no_site"])}</p></div>
  <div id="formulier"><h2 style="margin-bottom:16px">{T(L, P["form_h"])}</h2>{lead_form(ctx, "groeiscan", preset="scan", scan=True)}</div>
</div></section>'''
    return fill(L, P["title"]), fill(L, P["desc"]), main, [crumbs_ld(L, [(ui["home"], page_path(L, "home")), (ui["cta_scan"], page_path(L, "scan"))])]


def build_privacy(ctx):
    L, ui, P = ctx.lang, ctx.ui, CONTENT[ctx.lang].PAGES["privacy"]
    secs = "".join(f"<div><h2>{T(L, h)}</h2><p>{T(L, p)}</p></div>" for h, p in P["sections"])
    main = f'''{page_hero(ctx, simple_trail(ctx, ui["privacy"]), P["h1"], P["lead"])}
<section class="section"><div class="wrap"><div class="prose">{secs}</div></div></section>'''
    return fill(L, P["title"]), fill(L, P["desc"]), main, []


def build_thanks(ctx):
    L, ui, P = ctx.lang, ctx.ui, CONTENT[ctx.lang].PAGES["thanks"]
    ctas = f'''<div class="btn-row"><a class="btn btn-primary" href="{ctx.href(page_path(L, "home"))}">{T(L, P["back"])}</a>
  <a class="btn btn-ghost btn-wa" href="{esc(wa_url(ui["wa_general"]))}" target="_blank" rel="noopener">{WA_ICON}{esc(ui["whatsapp"])}</a></div>'''
    main = page_hero(ctx, simple_trail(ctx, P["h1"]), P["h1"], P["lead"], None, ctas)
    return fill(L, P["title"]), fill(L, P["desc"]), main, []


PAGE_BUILDERS = {"home": build_home, "pricing": build_pricing, "method": build_method, "work": build_work,
                 "about": build_about, "contact": build_contact, "scan": build_scan, "privacy": build_privacy,
                 "thanks": build_thanks}


def build_404(mode):
    ctx = Ctx(mode, "nl", "")
    P = CONTENT["nl"].PAGES["404"]
    links = "".join(f'<li><a href="{ctx.href(page_path(l, "home"))}">{C.LANG_META[l]["name"]}</a></li>' for l in LANGS)
    links += f'<li><a href="{ctx.href(page_path("nl", "pricing"))}">{esc(ctx.ui["nav_pricing"])}</a></li>'
    links += f'<li><a href="{ctx.href(page_path("nl", "contact"))}">{esc(ctx.ui["nav_contact"])}</a></li>'
    main = f'''<section class="page-hero"><div class="wrap"><h1>{esc(P["h1"])}</h1><p class="lead">{esc(P["lead"])}</p>
<ul class="chips">{links}</ul></div></section>'''
    alts = {l: page_path(l, "home") for l in LANGS}
    return document(ctx, P["title"], P["title"], main, alts, None, noindex=True)


# ---------- uitvoer ----------
def all_pages():
    for L in LANGS:
        for key in PAGE_BUILDERS:
            yield L, "page", key, page_path(L, key)
        for key in C.SERVICE_ORDER:
            yield L, "service", key, service_path(L, key)


def render(mode, L, kind, key, path, fragment=False):
    ctx = Ctx(mode, L, path)
    if kind == "service":
        title, desc, main, ld = build_service(ctx, key)
    else:
        title, desc, main, ld = PAGE_BUILDERS[key](ctx)
    alts = alternates_for(kind, key)
    return document(ctx, title, desc, main, alts, key, ld, noindex=(kind == "page" and key in C.NOINDEX), fragment=fragment), title, desc


def sitemap():
    urls = []
    for L, kind, key, path in all_pages():
        if kind == "page" and key in C.NOINDEX:
            continue
        alts = alternates_for(kind, key)
        links = "".join(f'<xhtml:link rel="alternate" hreflang="{C.LANG_META[l]["hreflang"]}" href="{C.DOMAIN}/{alts[l]}"/>' for l in LANGS)
        links += f'<xhtml:link rel="alternate" hreflang="x-default" href="{C.DOMAIN}/{alts["nl"]}"/>'
        urls.append(f"<url><loc>{C.DOMAIN}/{path}</loc>{links}</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")


def write(out, rel, text, written):
    p = os.path.join(out, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    written.append(rel)


def build_prod():
    old = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else []
    for rel in old:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            os.remove(p)
    written = []
    for L, kind, key, path in all_pages():
        doc, _, _ = render("prod", L, kind, key, path)
        write(ROOT, path + "index.html", doc, written)
    write(ROOT, "404.html", build_404("prod"), written)
    write(ROOT, "sitemap.xml", sitemap(), written)
    write(ROOT, "robots.txt", f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /tools/\n\nSitemap: {C.DOMAIN}/sitemap.xml\n", written)
    json.dump(sorted(written), open(MANIFEST, "w"), indent=0)
    # lege mappen opruimen
    for rel in old:
        d = os.path.dirname(os.path.join(ROOT, rel))
        while d != ROOT and os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
            d = os.path.dirname(d)
    print(f"productie: {len(written)} bestanden in {ROOT}")


def build_preview(out):
    if os.path.exists(out):
        shutil.rmtree(out)
    written = []
    for L, kind, key, path in all_pages():
        frag = (L == "nl" and kind == "page" and key == "home")
        doc, _, _ = render("preview", L, kind, key, path, fragment=frag)
        write(out, path + "index.html", doc, written)
    for sub in ("assets/css", "assets/js", "assets/fonts", "assets/img"):
        src = os.path.join(ROOT, sub)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(out, sub))
    print(f"preview: {len(written)} pagina's in {out}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--preview":
        build_preview(os.path.abspath(sys.argv[2]))
    else:
        build_prod()
