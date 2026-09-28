#!/usr/bin/env python3
"""Controleert de gebouwde site. Moet eindigen op '0 fouten'.

  python3 tools/check.py            -> productiebestanden in de repo-root
  python3 tools/check.py --preview DIR
  python3 tools/check.py --strict   -> ook ontbrekende bedrijfsgegevens zijn fouten (vóór livegang)
"""
import html.parser, json, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "content"))
import siteconf as C  # noqa: E402


class P(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0; self.title = ""; self._t = False; self.desc = None; self.canon = None
        self.hreflang = set(); self.links = []; self.ld = []; self._ld = False; self._buf = ""; self.robots = ""
        self.ids = set(); self.imgs = []

    def handle_starttag(self, tag, a):
        a = dict(a)
        if "id" in a: self.ids.add(a["id"])
        if tag == "h1": self.h1 += 1
        if tag == "title": self._t = True
        if tag == "meta" and a.get("name") == "description": self.desc = a.get("content", "")
        if tag == "meta" and a.get("name") == "robots": self.robots = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical": self.canon = a.get("href")
        if tag == "link" and a.get("rel") == "alternate" and a.get("hreflang"): self.hreflang.add(a["hreflang"])
        if tag in ("a", "link") and a.get("href"): self.links.append(a["href"])
        if tag == "script" and a.get("src"): self.links.append(a["src"])
        if tag == "script" and a.get("type") == "application/ld+json": self._ld = True; self._buf = ""

    def handle_endtag(self, tag):
        if tag == "title": self._t = False
        if tag == "script" and self._ld: self._ld = False; self.ld.append(self._buf)

    def handle_data(self, d):
        if self._t: self.title += d
        if self._ld: self._buf += d


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    preview = args[args.index("--preview") + 1] if "--preview" in args else None
    base = os.path.abspath(preview) if preview else ROOT
    if preview:
        files = [os.path.relpath(os.path.join(d, f), base) for d, _, fs in os.walk(base) for f in fs if f.endswith(".html")]
    else:
        files = [f for f in json.load(open(os.path.join(ROOT, "tools", ".generated.json"))) if f.endswith(".html")]
    errors, warns = [], []
    titles, descs = defaultdict(list), defaultdict(list)
    for rel in sorted(files):
        src = open(os.path.join(base, rel), encoding="utf-8").read()
        p = P(); p.feed(src)
        noindex = "noindex" in p.robots or rel == "404.html"
        is_frag = preview and rel == "index.html"
        if p.h1 != 1: errors.append(f"{rel}: {p.h1} × h1")
        if "[[" in src: errors.append(f"{rel}: niet-ingevulde [[sleutel]]")
        if not is_frag:  # wettelijke vermeldingen (WER boek XII) in de footer van elke pagina
            for k in ("legal_name", "street", "kbo"):
                if C.BIZ[k] and C.BIZ[k] not in src:
                    errors.append(f"{rel}: {k} ontbreekt op de pagina")
            if not (10 <= len(p.title) <= 60): errors.append(f"{rel}: title {len(p.title)} tekens: {p.title}")
            if not noindex:
                if p.desc is None or not (110 <= len(p.desc) <= 160): errors.append(f"{rel}: description {len(p.desc or '')} tekens")
                if not p.canon: errors.append(f"{rel}: geen canonical")
                if p.hreflang != {"nl-BE", "fr-BE", "en", "x-default"}: errors.append(f"{rel}: hreflang {sorted(p.hreflang)}")
                titles[p.title].append(rel); descs[p.desc].append(rel)
        for block in p.ld:
            try: json.loads(block)
            except Exception as e: errors.append(f"{rel}: JSON-LD ongeldig ({e})")
        here = os.path.dirname(rel)
        for h in p.links:
            if h.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                continue
            path, _, frag = h.partition("#")
            path = path.split("?")[0]
            if preview or not path.startswith("/"):
                target = os.path.normpath(os.path.join(base, here, path))
            else:
                target = os.path.join(base, path.lstrip("/"))
            if path.endswith("/") or os.path.isdir(target):
                target = os.path.join(target, "index.html")
            if path.endswith(".php"):
                continue
            if not os.path.exists(target):
                errors.append(f"{rel}: kapotte link {h}")
    for t, where in titles.items():
        if len(where) > 1: errors.append(f"dubbele title '{t}': {where}")
    for d, where in descs.items():
        if d and len(where) > 1: errors.append(f"dubbele description: {where}")
    missing = [k for k in ("legal_name", "kbo", "street", "whatsapp") if not C.BIZ[k]]
    if missing:
        (errors if strict else warns).append("bedrijfsgegevens ontbreken in siteconf.BIZ: " + ", ".join(missing))
    for w in warns: print("waarschuwing:", w)
    for e in errors: print("FOUT:", e)
    print(f"{len(files)} pagina's gecontroleerd — {len(errors)} fouten, {len(warns)} waarschuwingen")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
