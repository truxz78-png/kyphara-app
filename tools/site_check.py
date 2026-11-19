#!/usr/bin/env python3
"""Daily check of the Kyphara site: index, privacy and terms open and keep their links and translator."""
import os, sys, urllib.request

SITE = os.environ.get("SITE", "https://truxz78-png.github.io/kyphara-app/").rstrip("/") + "/"
CHECKS = {
    "index.html":   ["privacy.html", "terms.html", "tr.js", "links.json", "Opens partner site", "Cuidado de la piel", "Ship packages to your country", "Beauty courses"],
    "privacy.html": ["terms.html", "index.html", "tr.js", "legal-tr.js", "hpind77@gmail.com"],
    "terms.html":   ["privacy.html", "index.html", "tr.js", "legal-tr.js", "hpind77@gmail.com", "Dominican Republic"],
    "legal-tr.js":  ["KyTr", "Volver a"],
    "tr.js":        ["translate.googleapis.com", "tr/"],
    "links.json":   ["primary", "official", "planetexpress.com/?ref=378266", "id_affiliate=24923"],
}
fails = []
for page, needles in CHECKS.items():
    url = SITE + page
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "kyphara-site-check"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            status = r.status
    except Exception as e:
        fails.append(f"{page}: does not open ({e})")
        continue
    if status != 200:
        fails.append(f"{page}: HTTP {status}")
    for n in needles:
        if n not in body:
            fails.append(f"{page}: missing '{n}'")
    print(f"OK  {page}" if not any(f.startswith(page) for f in fails) else f"ERR {page}")

summary = os.environ.get("GITHUB_STEP_SUMMARY")
text = "## Kyphara site check\n\n" + ("All pages OK ✅\n" if not fails else "\n".join("- ❌ " + f for f in fails) + "\n")
if summary:
    open(summary, "a").write(text)
print(text)
sys.exit(1 if fails else 0)
