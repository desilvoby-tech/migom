#!/usr/bin/env python3
"""SEO-тексты для страниц /uslugi/ (desilvo.by).

Отдельный шаг после tools/gen_masters.py в .github/workflows/masters.yml. Код генератора не меняет:
вставляет блок текста между метками <!--seo-text-->…<!--/seo-text--> перед «Как это работает».
meta robots не трогает — noindex для «услуга + город» без мастеров ставит gen_masters.py.
Смысловые тексты по группам услуг — в tools/seo_texts_uslugi.json, типовые задачи — из cats.js.
Данные — одобренные анкеты мастеров из Supabase по публичному ключу из config.js.
Нулевые значения (рейтинг, отзывы, заказы) не выводятся. Только стандартная библиотека Python.
"""
import hashlib, html, json, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UDIR = os.path.join(ROOT, "uslugi")
E = lambda s: html.escape(str(s), quote=True)
MARK_RE = re.compile(r'data-svc="([^"]*)" data-city="([^"]*)"')
BLOCK_RE = re.compile(r"<!--seo-text-->.*?<!--/seo-text--> ?", re.S)
ANCHOR = "<h2>Как это работает</h2>"
CITY_IN = {"Минск": "Минске", "Гомель": "Гомеле", "Брест": "Бресте", "Гродно": "Гродно", "Витебск": "Витебске",
           "Могилёв": "Могилёве", "Могилев": "Могилёве", "Бобруйск": "Бобруйске", "Барановичи": "Барановичах",
           "Борисов": "Борисове", "Пинск": "Пинске", "Орша": "Орше", "Мозырь": "Мозыре", "Солигорск": "Солигорске",
           "Новополоцк": "Новополоцке", "Лида": "Лиде", "Молодечно": "Молодечно", "Полоцк": "Полоцке",
           "Жлобин": "Жлобине", "Светлогорск": "Светлогорске", "Речица": "Речице", "Слуцк": "Слуцке",
           "Жодино": "Жодино", "Кобрин": "Кобрине", "Слоним": "Слониме", "Волковыск": "Волковыске"}


def city_in(c, first=True):
    w = CITY_IN.get(c)
    if not w:
        if c.endswith(("ь", "й", "а", "я")):
            w = c[:-1] + "е"
        elif c.endswith(("о", "е", "и", "ы", "у")):
            return ("в г. " if first else "г. ") + c
        else:
            w = c + "е"
    return ("в " if first else "") + w


def join_ru(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " и " + xs[-1]


def cities_text(cs):
    return join_ru([city_in(c, i == 0) for i, c in enumerate(cs)])


def plural(n, one, few, many):
    n = abs(n) % 100
    if 11 <= n <= 19:
        return many
    n %= 10
    return one if n == 1 else few if 2 <= n <= 4 else many


def pick(key, variants):
    return variants[int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % len(variants)]


def cfg():
    s = open(os.path.join(ROOT, "config.js"), encoding="utf-8").read()
    return re.search(r'url:\s*"([^"]+)"', s).group(1), re.search(r'key:\s*"([^"]+)"', s).group(1)


def fetch_masters():
    url, key = cfg()
    q = ("%s/rest/v1/masters?select=id,services,cities,rating,reviews_count,done_count,price_from,experience"
         "&approved=eq.true&blocked=eq.false&is_demo=eq.false" % url)
    req = urllib.request.Request(q, headers={"apikey": key, "Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def load_cats():
    t = open(os.path.join(ROOT, "cats.js"), encoding="utf-8").read()
    i = t.index("window.DCAT=")
    j = t.index("];", i)
    svc = {}
    for g in json.loads(t[i + len("window.DCAT="):j + 1]):
        for c in g["c"]:
            for s in c.get("s", []):
                svc.setdefault(s["t"], (g["t"], s.get("v", [])))
    return svc


def real_cities(m):
    return [c for c in (m.get("cities") or []) if c and c != "Другой город"]


def data_paragraph(key, svc, city, ms):
    n = len(ms)
    if not n:
        if city:
            return "<p>" + E(f"{city_in(city)[0].upper() + city_in(city)[1:]} мастеров по услуге «{svc}» в каталоге пока нет. "
                             "Создайте задание — его увидят исполнители, а с появлением мастеров в вашем городе они смогут откликнуться.") + "</p>"
        return "<p>" + E(f"Мастеров по услуге «{svc}» в каталоге пока нет. Создайте задание бесплатно — исполнители смогут откликнуться на него.") + "</p>"
    noun = plural(n, "мастер", "мастера", "мастеров")
    if city:
        s = pick(key + "|c", [f"{city_in(city)[0].upper() + city_in(city)[1:]} услугу «{svc}» на Десилво предлагают {n} {noun}.",
                              f"Сейчас {city_in(city)} по услуге «{svc}» в каталоге {n} {noun}."])
    else:
        cs = {}
        for m in ms:
            for c in real_cities(m):
                cs[c] = cs.get(c, 0) + 1
        top = sorted(cs, key=lambda c: (-cs[c], c))
        where = (": " + (cities_text(top) if len(top) <= 4 else cities_text(top[:4] + ["__"]).rsplit(" и ", 1)[0] + " и в других городах")) if top else ""
        s = pick(key + "|b", [f"На Десилво услугу «{svc}» предлагают {n} {noun}{where}.",
                              f"Сейчас в каталоге {n} {noun} по услуге «{svc}»{where}."])
    parts = [s]
    pf = sorted(float(m["price_from"]) for m in ms if m.get("price_from") and float(m["price_from"]) > 0)
    if pf:
        p = int(pf[0]) if pf[0].is_integer() else pf[0]
        parts.append(f"Цены в анкетах — от {p} BYN, точную стоимость мастера называют в откликах на задание.")
    exp10 = sum(1 for m in ms if (m.get("experience") or "").strip().lower() == "больше 10 лет")
    if exp10:
        parts.append(("У одного из мастеров" if exp10 == 1 else f"У {exp10} мастеров") + " опыт больше 10 лет.")
    rv = [(float(m["rating"]), int(m["reviews_count"])) for m in ms if m.get("reviews_count") and int(m["reviews_count"]) > 0 and m.get("rating")]
    if rv:
        cnt = sum(c for _, c in rv)
        avg = sum(r * c for r, c in rv) / cnt
        parts.append(f"Средняя оценка — {avg:.1f} по {cnt} {plural(cnt, 'отзыву', 'отзывам', 'отзывам')}.".replace(".", ",", 1))
    done = sum(int(m.get("done_count") or 0) for m in ms)
    if done > 0:
        parts.append(f"Через Десилво выполнено {done} {plural(done, 'заказ', 'заказа', 'заказов')}.")
    return "<p>" + E(" ".join(parts)) + "</p>"


def block(texts, svc, city, group, tasks, ms, key):
    g = texts.get("groups", {}).get(group, {})
    st = texts.get("services", {}).get(svc, {})
    out = []
    h2 = st.get("h2") or (g.get("h2_tpl", "{svc}: как выбрать исполнителя").format(svc=svc))
    if city:
        h2 = f"{svc} {city_in(city)}: что важно знать"
    out.append(f"<h2>{E(h2)}</h2>")
    out.append(data_paragraph(key, svc, city, ms))
    if st.get("about") and not city:
        out.append(f"<p>{E(st['about'])}</p>")
    if tasks:
        tl = join_ru(tasks)
        out.append("<p>" + E(pick(key + "|t", [f"С чем чаще всего обращаются: {tl}.", f"Частые запросы: {tl}."])) + "</p>")
    if city:
        # на городских страницах — только короткий совет, чтобы не повторять основную страницу услуги
        ask = st.get("ask") or g.get("ask")
        if ask:
            out.append(f"<p><b>{E(g.get('ask_title', 'Что спросить у мастера.'))}</b> {E(ask)}</p>")
    else:
        for k, d in (("brief", "Как описать задачу."), ("ask", "Что спросить у мастера."), ("safety", "Как обезопасить себя.")):
            v = st.get(k) or g.get(k)   # услуга может переопределить совет группы
            if v:
                out.append(f"<p><b>{E(g.get(k + '_title', d))}</b> {E(v)}</p>")
    return '<section class="seo-text">' + "".join(out) + "</section>"


def shingles(block_html):
    w = html.unescape(re.sub(r"<[^>]+>", " ", block_html)).lower().split()
    return {tuple(w[i:i + 5]) for i in range(len(w) - 4)}


def similarity_warnings(blocks):
    """blocks: [(file, html)] индексируемых страниц по порядку. Предупреждение, если у соседей > 60% общих шинглов."""
    sh = [(f, shingles(b)) for f, b in blocks]
    for (fa, a), (fb, b) in zip(sh, sh[1:]):
        j = len(a & b) / max(1, len(a | b))
        if j > 0.6:
            print(f"::warning::seo_text_uslugi: похожие тексты {fa} и {fb}: {j:.0%}")


def main():
    texts = json.load(open(os.path.join(ROOT, "tools", "seo_texts_uslugi.json"), encoding="utf-8"))
    enabled = set(texts.get("enabled", []))
    cats = load_cats()
    ms_all = fetch_masters()
    st = {"pages": 0, "text": 0, "changed": 0}
    indexed = []
    for f in sorted(os.listdir(UDIR)):
        if not f.endswith(".html"):
            continue
        p = os.path.join(UDIR, f)
        t = open(p, encoding="utf-8").read()
        m = MARK_RE.search(t)
        if not m:
            continue
        st["pages"] += 1
        svc, city = html.unescape(m.group(1)), html.unescape(m.group(2))
        group, tasks = cats.get(svc, (None, []))
        t2 = BLOCK_RE.sub("", t)
        if group in enabled and ANCHOR in t2:
            ms = [x for x in ms_all if svc in (x.get("services") or []) and (not city or city in (x.get("cities") or []))]
            blk = block(texts, svc, city, group, tasks, ms, f)
            t2 = t2.replace(ANCHOR, "<!--seo-text-->" + blk + "<!--/seo-text--> " + ANCHOR, 1)
            st["text"] += 1
            if "noindex" not in "".join(re.findall(r'<meta name="robots" content="([^"]*)"', t2)):
                indexed.append((f, blk))
        if t2 != t:
            open(p, "w", encoding="utf-8").write(t2)
            st["changed"] += 1
    similarity_warnings(indexed)
    print("seo_text_uslugi:", st, "masters:", len(ms_all))


if __name__ == "__main__":
    main()
