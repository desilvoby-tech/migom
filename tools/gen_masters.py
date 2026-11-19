#!/usr/bin/env python3
"""Генератор статических страниц мастеров desilvo: /master/<id>.

Запускается GitHub Actions (.github/workflows/masters.yml) раз в час.
Берёт одобренные анкеты (не демо, не заблокированные) из Supabase по публичному ключу из config.js,
пишет master/*.html, sitemap-masters.xml и вставляет список мастеров прямо в HTML страниц /uslugi/
(живой список по-прежнему подгружает uslugi/p.js). Только стандартная библиотека Python.
"""
import json, os, re, html, urllib.request, urllib.parse, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://desilvo.by"
OUT = os.path.join(ROOT, "master")
E = lambda s: html.escape(str(s if s is not None else ""), quote=True)
COLS = ("id,name,services,cities,about,experience,prices,districts,rating,reviews_count,done_count,price_from,"
        "photo_url,legal_status,verified_phone,verified_passport,ext_source,ext_rating,ext_reviews_count,created_at")


def cfg():
    s = open(os.path.join(ROOT, "config.js"), encoding="utf-8").read()
    url = re.search(r'url:\s*"([^"]+)"', s).group(1)
    key = re.search(r'key:\s*"([^"]+)"', s).group(1)
    return url, key


def fetch_masters(url, key):
    q = "%s/rest/v1/masters?select=%s&approved=eq.true&blocked=eq.false&is_demo=eq.false&order=created_at.asc" % (url, COLS)
    req = urllib.request.Request(q, headers={"apikey": key, "Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def lst(x):
    return [str(v) for v in (x or []) if v and str(v) != "Другой город"]


def price_rows(m):
    rows = []
    for p in m.get("prices") or []:
        if not isinstance(p, dict) or not p.get("s"):
            continue
        f, t, u = p.get("f"), p.get("t"), p.get("u") or "услугу"
        if f is not None and t is not None:
            v = "%s–%s BYN за %s" % (f, t, u)
        elif f is not None:
            v = "от %s BYN за %s" % (f, u)
        else:
            v = "по договорённости"
        rows.append((p["s"], v))
    return rows


def rating_html(m):
    if (m.get("reviews_count") or 0) > 0:
        return "Рейтинг %.1f из 5 · отзывов: %d" % (float(m.get("rating") or 0), m["reviews_count"])
    if m.get("ext_rating") and m.get("ext_reviews_count"):
        return "Рейтинг %.1f из 5 на %s · отзывов: %d (перенесён с другой площадки)" % (
            float(m["ext_rating"]), E(m.get("ext_source") or "другой площадке"), int(m["ext_reviews_count"]))
    return ""


def is_thin(m):
    return len((m.get("about") or "").strip()) < 80 and not price_rows(m)


def page(m):
    url = "%s/master/%s" % (SITE, m["id"])
    svcs, cities = lst(m.get("services")), lst(m.get("cities"))
    svc_txt = ", ".join(svcs[:3]).lower() if svcs else "услуги"
    city_txt = ", ".join(cities) if cities else "Беларусь"
    title = "%s — %s, %s | desilvo" % (m.get("name") or "Мастер", svc_txt, city_txt)
    if len(title) > 70:
        title = "%s — %s | desilvo" % (m.get("name") or "Мастер", city_txt)
    about = (m.get("about") or "").strip()
    desc = ("%s: %s в %s. %s" % (m.get("name") or "Мастер", svc_txt, city_txt, re.sub(r"\s+", " ", about)))[:157].rstrip()
    if len(desc) == 157:
        desc += "…"
    robots = "noindex,follow" if is_thin(m) else "index,follow"
    facts = []
    if m.get("experience"): facts.append(("Опыт", m["experience"]))
    if m.get("legal_status"): facts.append(("Статус", m["legal_status"]))
    if cities: facts.append(("Города", city_txt))
    if m.get("districts"): facts.append(("Районы", ", ".join(lst(m["districts"]))))
    if m.get("price_from"): facts.append(("Цены", "от %s BYN" % m["price_from"]))
    rt = rating_html(m)
    if rt: facts.append(("Рейтинг", rt))
    if (m.get("done_count") or 0) > 0: facts.append(("Выполнено заказов", str(m["done_count"])))
    pr = price_rows(m)
    svc_links = "".join('<li><a href="/uslugi/">%s</a></li>' % E(s) for s in svcs) if False else "".join("<li>%s</li>" % E(s) for s in svcs)
    ld = {"@context": "https://schema.org", "@type": "ProfilePage", "url": url, "name": title,
          "mainEntity": {"@type": "Person", "name": m.get("name") or "Мастер", "jobTitle": ", ".join(svcs[:3]) or None,
                         "address": {"@type": "PostalAddress", "addressLocality": cities[0], "addressCountry": "BY"} if cities else None,
                         "description": about[:300] or None}}
    ld["mainEntity"] = {k: v for k, v in ld["mainEntity"].items() if v}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "desilvo", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Мастера", "item": SITE + "/mastera"},
        {"@type": "ListItem", "position": 3, "name": m.get("name") or "Мастер", "item": url}]}
    about_html = "<br>".join(E(l) for l in about.splitlines()) if about else ""
    photo = '<img src="%s" alt="%s" width="160" height="160" style="border-radius:12px;object-fit:cover">' % (E(m["photo_url"]), E(m.get("name"))) if m.get("photo_url") else ""
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}"><meta name="robots" content="{robots}">
<meta property="og:type" content="profile"><meta property="og:site_name" content="desilvo"><meta property="og:locale" content="ru_BY">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}">
<link rel="stylesheet" href="/uslugi/s.css">
<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head><body>
<header><div class="w"><a class="logo" href="/">desilvo</a> <a href="/mastera">Все мастера</a></div></header>
<main class="w">
<p class="crumbs"><a href="/">Главная</a> → <a href="/mastera">Мастера</a> → {E(m.get("name"))}</p>
{photo}<h1>{E(m.get("name") or "Мастер")}</h1>
<p>{E(", ".join(svcs))}{(" — " + E(city_txt)) if cities else ""}</p>
{"<dl>" + "".join("<dt>%s</dt><dd>%s</dd>" % (E(k), v if k == "Рейтинг" else E(v)) for k, v in facts) + "</dl>" if facts else ""}
{"<h2>О себе</h2><p>" + about_html + "</p>" if about_html else ""}
{"<h2>Услуги</h2><ul>" + svc_links + "</ul>" if svcs else ""}
{"<h2>Цены</h2><table>" + "".join("<tr><td>%s</td><td>%s</td></tr>" % (E(a), E(b)) for a, b in pr) + "</table>" if pr else ""}
<p><a class="btn" href="/app.html#m-{E(m["id"])}">Открыть анкету и связаться</a></p>
<p class="muted">Создайте задание бесплатно — мастера откликнутся с ценами: <a href="/app.html#new">разместить задание</a>.</p>
</main></body></html>
"""


def index_page(ms):
    rows = "".join('<li><a href="/master/%s">%s</a> — %s%s</li>' % (
        E(m["id"]), E(m.get("name")), E(", ".join(lst(m.get("services"))[:3])),
        (", " + E(", ".join(lst(m.get("cities"))))) if lst(m.get("cities")) else "") for m in ms)
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Мастера в Беларуси — анкеты исполнителей | desilvo</title>
<meta name="description" content="Анкеты мастеров desilvo по всей Беларуси: услуги, города, цены и рейтинги. Выберите исполнителя или создайте задание бесплатно.">
<link rel="canonical" href="{SITE}/mastera"><meta name="robots" content="index,follow">
<link rel="stylesheet" href="/uslugi/s.css"></head><body>
<header><div class="w"><a class="logo" href="/">desilvo</a></div></header>
<main class="w"><h1>Мастера desilvo</h1><p>Проверенные анкеты исполнителей. Чтобы получить предложения с ценами, <a href="/app.html#new">создайте задание</a>.</p>
<ul>{rows}</ul></main></body></html>
"""


ML_RE = re.compile(r'(<div id="ml"[^>]*data-svc="([^"]*)" data-city="([^"]*)">)(?:<div class="empty">Загрузка мастеров…</div>|<!--ssr-->.*?<!--/ssr-->)(</div>)', re.S)


ROBOTS_RE = re.compile(r'<meta name="robots" content="[^"]*"\s*/?>')
NOINDEX = []


def inject_uslugi(ms):
    d = os.path.join(ROOT, "uslugi")
    if not os.path.isdir(d):
        return 0
    n = 0
    for f in sorted(os.listdir(d)):
        if not f.endswith(".html"):
            continue
        p = os.path.join(d, f)
        t = open(p, encoding="utf-8").read()
        mm = ML_RE.search(t)
        if not mm:
            continue
        svc, city = html.unescape(mm.group(2)), html.unescape(mm.group(3))
        hits = [m for m in ms if svc in (m.get("services") or []) and (not city or city in (m.get("cities") or []))][:12]
        if hits:
            cards = "".join('<a class="card" href="/master/%s"><b>%s</b> <span class="muted">%s</span></a>' % (
                E(m["id"]), E(m.get("name")), E(", ".join(lst(m.get("cities"))))) for m in hits)
            block = mm.group(1) + "<!--ssr-->" + cards + "<!--/ssr-->" + mm.group(4)
        else:
            block = mm.group(1) + '<div class="empty">Загрузка мастеров…</div>' + mm.group(4)
        t2 = t[:mm.start()] + block + t[mm.end():]
        if city:
            # страница «услуга + город»: без мастеров в этом городе — noindex,follow до появления первого
            # (у этих страниц изначально нет своего meta robots — индексируются по умолчанию)
            t2 = ROBOTS_RE.sub("", t2)
            if not hits:
                t2 = t2.replace('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="robots" content="noindex,follow">', 1)
                NOINDEX.append(f)
        if t2 != t:
            open(p, "w", encoding="utf-8").write(t2)
            n += 1
    return n


def write(p, s):
    if not os.path.exists(p) or open(p, encoding="utf-8").read() != s:
        open(p, "w", encoding="utf-8").write(s)


def main():
    url, key = cfg()
    ms = [m for m in fetch_masters(url, key) if m.get("name")]
    os.makedirs(OUT, exist_ok=True)
    keep = set()
    for m in ms:
        name = m["id"] + ".html"
        keep.add(name)
        write(os.path.join(OUT, name), page(m))
    for f in os.listdir(OUT):
        if f.endswith(".html") and f not in keep:
            os.remove(os.path.join(OUT, f))
    write(os.path.join(ROOT, "mastera.html"), index_page(ms))
    today = datetime.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
          "  <url><loc>%s/mastera</loc><changefreq>daily</changefreq></url>" % SITE]
    for m in ms:
        if not is_thin(m):
            sm.append("  <url><loc>%s/master/%s</loc><lastmod>%s</lastmod></url>" % (SITE, m["id"], (m.get("created_at") or today)[:10]))
    sm.append("</urlset>")
    write(os.path.join(ROOT, "sitemap-masters.xml"), "\n".join(sm) + "\n")
    rp = os.path.join(ROOT, "robots.txt")
    r = open(rp, encoding="utf-8").read()
    if "sitemap-masters.xml" not in r:
        open(rp, "w", encoding="utf-8").write(r.rstrip("\n") + "\nSitemap: %s/sitemap-masters.xml\n" % SITE)
    print("masters:", len(ms), "indexable:", sum(1 for m in ms if not is_thin(m)), "uslugi updated:", inject_uslugi(ms),
          "city pages without masters (noindex):", len(NOINDEX))


if __name__ == "__main__":
    main()
