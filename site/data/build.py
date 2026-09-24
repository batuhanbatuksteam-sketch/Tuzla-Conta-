# -*- coding: utf-8 -*-
"""Statik site üreticisi. `python3 build.py` tüm sayfaları yeniden yazar."""
import os, sys, html, shutil, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog import BRAND, CATEGORIES, P

try:
    from PIL import Image
    _PIL = True
except ImportError:
    _PIL = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BG_CACHE = {}


def product_bg(slug):
    """Ürün görselinin kenar şeridinden medyan renk örnekler — kart zemini
    bu renk olunca görsel, kartın kendi arka planından kopuk durmuyor,
    stüdyo fonunun devamı gibi görünüyor."""
    if slug in _BG_CACHE:
        return _BG_CACHE[slug]
    default = "#141922"
    if not _PIL:
        return default
    path = os.path.join(ROOT, "assets", "img", "urun", f"{slug}.webp")
    try:
        im = Image.open(path).convert("RGB")
        w, h = im.size
        mx, my = max(1, int(w * 0.03)), max(1, int(h * 0.03))
        px = im.load()
        samples = []
        step = max(1, min(w, h) // 60)
        for x in range(0, w, step):
            samples.append(px[x, my]); samples.append(px[x, h - 1 - my])
        for y in range(0, h, step):
            samples.append(px[mx, y]); samples.append(px[w - 1 - mx, y])
        r = int(statistics.median(s[0] for s in samples))
        g = int(statistics.median(s[1] for s in samples))
        b = int(statistics.median(s[2] for s in samples))
        color = f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        color = default
    _BG_CACHE[slug] = color
    return color
CATS = {s: (n, d, sc) for s, n, d, sc in CATEGORIES}
BY_CAT = {s: [p for p in P if p["kat"] == s] for s in CATS}
BY_SLUG = {p["slug"]: p for p in P}
E = lambda t: html.escape(str(t), quote=True)
NK, NP = len(CATS), len(P)   # grup ve kalem sayısı — metinlerde elle yazılmaz

LOGO = open(os.path.join(ROOT, "assets", "img", "logo.svg"), encoding="utf-8").read()
MARK = open(os.path.join(ROOT, "assets", "img", "logo-mark.svg"), encoding="utf-8").read()
BRANDLOCK = (f'<span class="brand">{MARK}'
             '<span class="brand__t"><span class="brand__n">TUZLA CONTA</span>'
             '<span class="brand__s">SIZDIRMAZLIK</span></span></span>')

# Müşterinin gönderdiği "PN 16 DÜZ FLANŞ DIN:2576" tablosu. Contalar grubunda
# eşanjör ve özel ölçü hariç tüm ürünlerde gösterilir (catalog.py -> olcu="din2576").
# Sütunlar: DN, iç çap, dış çap, delik merkezi, delik çapı, delik adedi (mm).
DIN2576 = [
 (15,"22","95","65","14",4),(20,"27,5","105","75","14",4),(25,"34,5","115","85","14",4),
 (32,"43,5","140","100","18",4),(40,"49,5","150","110","18",4),(50,"61,5","165","125","18",4),
 (65,"77,5","185","145","18",4),(80,"90,5","200","160","18",8),(100,"116","220","180","18",8),
 (125,"141,5","250","210","18",8),(150,"170,5","285","240","22",8),(200,"221,5","340","295","22",12),
 (250,"276,5","405","355","26",12),(300,"327,5","460","410","26",12),(350,"359","520","470","26",16),
 (400,"411","580","525","30",16),(450,"462","640","585","30",20),(500,"513,5","715","650","33",20),
 (550,"564","745","680","33",20),(600,"616,5","840","770","36",20),(650,"665","875","805","36",24),
 (700,"718","910","840","36",24),(750,"766","967","895","39",24),(800,"819","1025","950","39",24),
 (900,"920","1125","1050","39",28),(1000,"1022","1255","1170","42",28),(1100,"1123","1355","1270","42",32),
 (1200,"1225","1485","1390","48",32),(1300,"1326","1585","1490","48",32),(1400,"1426","1685","1590","48",36),
 (1500,"1530","1820","1710","56",36),(1600,"1626","1930","1820","56",40),(1800,"1826","2130","2020","56",44),
 (2000,"2026","2345","2230","62",48),
]


def olcu_table(p):
    if p.get("olcu") != "din2576":
        return ""
    rows = "".join(f'<tr><th scope="row">DN {dn}</th><td>{ic}</td><td>{dis}</td><td>{dm}</td><td>{dc}</td><td>{n}</td></tr>'
                   for dn, ic, dis, dm, dc, n in DIN2576)
    return f"""<section class="band band--tight" id="olculer">
  <div class="wrap">
    <div class="seam"><span class="tag">Standart ölçüler</span></div>
    <div class="olcu">
      <div class="olcu__head">
        <h2 class="d3">PN 16 düz flanş ölçüleri<br>DIN 2576</h2>
        <p>{E(p['ad'])} bu tablodaki flanş ölçülerinde standart olarak kesilir. Ölçüler milimetredir.
          Tabloda olmayan ölçüler ve farklı basınç sınıfları için numune veya çizim gönderin.</p>
        <a class="btn btn--ghost" href="../iletisim.html?urun={p['slug']}#teklif">Ölçü ile teklif iste</a>
      </div>
      <div class="olcu__scroll" tabindex="0" role="region" aria-label="DIN 2576 PN16 ölçü tablosu">
        <table class="olcu__t">
          <thead><tr><th scope="col">Anma çapı</th><th scope="col">İç çap</th><th scope="col">Dış çap</th>
            <th scope="col">Delik merkezi</th><th scope="col">Delik çapı</th><th scope="col">Delik adedi</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>
  </div>
</section>"""


# ---------------------------------------------------------------- iskelet
THEME_INIT = ("<script>(function(){try{"
              "var t=localStorage.getItem('tc-theme')||'harmony';"
              "document.documentElement.setAttribute('data-theme',t);"
              "}catch(e){}})();</script>")


def head(title, desc, rel="", cls="", canon=""):
    return f"""<!doctype html>
<html lang="tr" class="{cls}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#0A1322">
{THEME_INIT}
<link rel="canonical" href="https://tuzlaconta.com/{canon}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="tr_TR">
<meta property="og:image" content="https://tuzlaconta.com/{rel}assets/img/sahne/hero-frame.webp">
<link rel="icon" href="{rel}assets/img/logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&display=swap">
<link rel="stylesheet" href="{rel}assets/css/main.css">
</head>
<body>
<a class="skip" href="#main">İçeriğe geç</a>
<div class="cursor is-hidden" id="cursor" aria-hidden="true"><span class="cursor__ring"></span><span class="cursor__dot"></span></div>"""


def nav(rel="", here=""):
    def a(href, label, key):
        cur = ' aria-current="page"' if key == here else ""
        return f'<a class="nav__link" href="{rel}{href}"{cur}>{label}</a>'
    return f"""<header class="nav"{' data-boot="1"' if here == "home" else ''}>
  <a class="nav__logo" id="navLogo" href="{rel}index.html" aria-label="Tuzla Conta ana sayfa">{BRANDLOCK}</a>
  <button class="nav__burger" type="button" aria-label="Menüyü aç" aria-expanded="false" aria-controls="navMenu"><span></span></button>
  <nav class="nav__menu" id="navMenu" aria-label="Ana menü">
    {a('urunler.html','Ürünler','urunler')}
    {a('kaucuk-silikon.html','Kauçuk &amp; Silikon','kaucuk')}
    {a('hakkimizda.html','Hakkımızda','hakkimizda')}
    {a('iletisim.html','İletişim','iletisim')}
    <a class="nav__tel" href="tel:{BRAND['phone']}">{BRAND['phone_display']}</a>
    <button class="nav__theme" id="themeBtn" type="button" aria-label="Görünüm: harmoni / gece / gündüz" aria-pressed="false">
      <svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.6M12 18.9v2.6M4.6 4.6l1.85 1.85M17.55 17.55l1.85 1.85M2.5 12h2.6M18.9 12h2.6M4.6 19.4l1.85-1.85M17.55 6.45l1.85-1.85"/></svg>
      <svg class="i-moon" viewBox="0 0 24 24" fill="currentColor"><path d="M20.6 15.1A8.7 8.7 0 1 1 8.9 3.4a7 7 0 0 0 11.7 11.7z"/></svg>
      <svg class="i-harmony" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="8.6"/><path d="M6 18 18 6" stroke-linecap="round"/><circle cx="15.6" cy="8.4" r="1.5" fill="currentColor" stroke="none"/><path d="M15.6 5.3v1M18.7 8.4h-1M17.5 6.5l-.7.7" stroke-linecap="round"/><path d="M6.3 16.9a2.1 2.1 0 1 0 2.5-3.3 2.1 2.1 0 0 1-2.5 3.3z" fill="currentColor" stroke="none"/></svg>
    </button>
    <a class="nav__cta" href="{rel}iletisim.html#teklif">Teklif iste</a>
  </nav>
</header>"""


def foot(rel=""):
    cols = "".join(
        f'<li><a href="{rel}urunler.html#{s}">{E(CATS[s][0])}</a></li>' for s in list(CATS)[:7])
    cols2 = "".join(
        f'<li><a href="{rel}urunler.html#{s}">{E(CATS[s][0])}</a></li>' for s in list(CATS)[7:])
    return f"""<footer class="foot">
<div class="wrap">
  <div class="foot__top">
    <div>
      <div class="foot__logo">{BRANDLOCK}</div>
      <p class="foot__blurb">Fabrikalara, üretim tesislerine ve gemilere conta, salmastra,
        kauçuk ve silikon sızdırmazlık ürünleri. Standart ölçü stoktan, özel ölçü üretimden.</p>
    </div>
    <div><h4>Sızdırmazlık</h4><ul>{cols}</ul></div>
    <div><h4>Malzeme ve özel üretim</h4><ul>{cols2}</ul></div>
    <div><h4>İletişim</h4><ul>
      <li><a href="tel:{BRAND['phone']}">{BRAND['phone_display']}</a></li>
      <li><a href="mailto:{BRAND['mail']}">{BRAND['mail']}</a></li>
      <li><a href="{BRAND['maps']}" target="_blank" rel="noopener">{E(BRAND['adres'])}</a></li>
    </ul></div>
  </div>
  <div class="foot__bot">
    <span>© 2026 {E(BRAND['name'])}</span>
    <span>Hafta içi 08:30 – 18:30, cumartesi 09:00 – 15:00</span>
  </div>
</div>
</footer>
<script src="{rel}assets/js/main.js" defer></script>
</body>
</html>"""


def loader():
    return f"""<div id="loader" aria-hidden="true">
  <div class="ld__mark" id="ldMark"><i class="ld__line"></i>{BRANDLOCK}</div>
</div>"""


# ---------------------------------------------------------------- parçalar
def card(p, rel=""):
    bg = product_bg(p["slug"])
    return f"""<a class="card" href="{rel}urun/{p['slug']}.html" style="--card-bg:{bg}">
  <span class="card__shot"><img src="{rel}assets/img/urun/{p['slug']}.webp" alt="{E(p['ad'])}" loading="lazy" width="800" height="600"></span>
  <span class="card__b"><span class="card__t">{E(p['ad'])}</span><span class="card__d">{E(p['ozet'])}</span></span>
</a>"""


DIAGRAM = """<svg class="joint" viewBox="0 0 660 440" role="img"
  aria-label="Flanş bağlantısının kesiti: üstte ve altta çelik flanş, aralarında sıkışan conta ve
  bağlantıyı çeken cıvata. Contanın yüzeyleri, çeliğin mikron ölçeğindeki pürüzüne oturur.">
 <defs>
  <pattern id="hatch" width="10" height="10" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
    <rect width="10" height="10" fill="#2A3A57"/>
    <line x1="0" y1="0" x2="0" y2="10" stroke="#8592AC" stroke-width="1.15" opacity=".55"/>
  </pattern>
  <clipPath id="clipTop"><path d="M60 62h410v140H60z"/></clipPath>
  <clipPath id="clipBot"><path d="M60 236h410v140H60z"/></clipPath>
 </defs>

 <!-- çelik gövdeler, cıvata deliği boşluklu -->
 <g fill="url(#hatch)" stroke="#A6B2C6" stroke-width="1.7">
   <path d="M60 62h64v140H60zM192 62h278v140H192z"/>
   <path d="M60 236h64v140H60zM192 236h278v140H192z"/>
 </g>

 <!-- conta: üstte ve altta çeliğin pürüzüne oturan testere dişi -->
 <path d="M60 202h64v32H60zM192 202h278v32H192z" fill="#4E9C7F"/>
 <g stroke="#2F6B55" stroke-width="1.4" fill="none">
   <path d="M60 202h64M192 202h278M60 234h64M192 234h278"/>
 </g>
 <g stroke="#EDEFF2" stroke-width="1.1" fill="none" opacity=".75">
   <path d="M62 205l6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4M194 205l6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4
            6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4
            6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4"/>
 </g>

 <!-- cıvata -->
 <g fill="#EDEFF2" stroke="#8592AC" stroke-width="1.7">
   <path d="M124 30h68v380h-68z"/>
   <path d="M108 30h100v34H108zM108 376h100v34H108z"/>
 </g>
 <g stroke="#162D63" stroke-width="1" opacity=".4">
   <path d="M136 64v312M180 64v312"/>
 </g>

 <!-- kuvvet oku: cıvatanın çektiği yön -->
 <g stroke="#7FD4AC" stroke-width="1.6" fill="none">
   <path d="M158 92v58M158 348v-58"/>
   <path d="M152 100l6-8 6 8M152 340l6 8 6-8" stroke-linecap="round"/>
 </g>

 <!-- ölçü çizgileri -->
 <g stroke="#C7CFDE" stroke-width="1.2" fill="none" opacity=".85">
   <path d="M510 62v140M504 62h12M504 202h12"/>
   <path d="M510 236v140M504 236h12M504 376h12"/>
 </g>
 <g stroke="#7FD4AC" stroke-width="1.2" fill="none">
   <path d="M510 202v32M504 202h12M504 234h12M522 218h34"/>
 </g>

 <g fill="#EDEFF2" font-family="Archivo,system-ui,sans-serif" font-size="13.5" font-weight="600">
  <text x="528" y="138">çelik flanş</text>
  <text x="528" y="312">çelik flanş</text>
  <text x="562" y="222" fill="#7FD4AC">conta</text>
  <text x="222" y="22" font-size="12.5" opacity=".75">cıvata kuvveti</text>
 </g>
</svg>"""


# ---------------------------------------------------------------- ana sayfa
def seq_count(prefix):
    d = os.path.join(ROOT, "assets", "img", "hero-seq")
    return len([f for f in os.listdir(d) if f.startswith(prefix) and f.endswith(".webp")]) if os.path.isdir(d) else 0


# Müşterinin ana sayfada görmek istediği üretim kabiliyeti (ChatGPT önerisi üzerinden
# birlikte netleştirdiği liste). "Her türlü kauçuk ürünü üretiriz" gibi sınırsız bir
# iddia yerine, neyin yapıldığını tek tek sayan teknik bir dil.
KABILIYET = ["Kauçuk contalar", "Silikon contalar", "Kalıplı kauçuk parçalar",
             "Özel ölçü ve formda ürünler", "Kauçuk-metal birleşimli parçalar", "Özel profil ve şeritler",
             "Müşteri çizimine göre üretim", "Numune üzerinden üretim", "Prototip ve seri üretim"]
MALZEME = ["EPDM", "NBR", "Viton (FKM)", "Silikon", "Neopren", "Doğal kauçuk"]
KAUCUK_LEDE = ("Standart ürünlerin yanı sıra, ihtiyaca özel ölçü, formülasyon ve teknik gereksinimlere göre "
               "kauçuk ve silikon bazlı contalar, profiller, kalıplı parçalar ve özel sızdırmazlık ürünleri üretiyoruz.")


def page_index():
    stage_items, stage_shots = [], []
    for i, s in enumerate(CATS):
        name, desc, _ = CATS[s]
        n = len(BY_CAT[s])
        stage_items.append(f"""<li class="stage__item{' on' if i == 0 else ''}">
  <button class="stage__btn" type="button">
    <span class="stage__n num">{i+1:02d}</span>
    <span class="stage__name">{E(name)}</span>
  </button>
  <div class="stage__desc">
    <img class="stage__shot" src="assets/img/sahne/kat-{s}.webp"
         alt="{E(name)} kullanım ortamı" loading="lazy" width="1200" height="900">
    <p>{E(desc)}</p>
    <a class="stage__more" href="urunler.html#{s}">{n} ürünü gör</a></div>
</li>""")
        stage_shots.append(
            f'<img class="stage__img{" on" if i == 0 else ""}" src="assets/img/sahne/kat-{s}.webp" '
            f'alt="{E(name)} kullanım ortamı" loading="lazy" width="1200" height="900">')

    scenes = [
        ("uyg-fabrika", "Fabrikalar ve üretim hatları",
         "Makine, hat ve ekipman sızdırmazlığı; kalıplı kauçuk parçalar, profiller ve bakım stoğu."),
        ("uyg-gida", "Gıda, içecek ve kimya",
         "Silikon ve EPDM contalar, PTFE ve Viton çözümleri; hijyen ve kimyasal dayanımı gereken hatlar."),
        ("uyg-pompa", "Pompa ve vana hatları",
         "Mekanik salmastra, yumuşak salmastra ve flanş contalarıyla duran pompayı tekrar çalıştırmak."),
        ("uyg-esanjor", "Enerji ve proses tesisleri",
         "Plaka eşanjör contaları, yüksek sıcaklık contaları ve kimyasala dayanıklı malzemeler."),
    ]
    scene_html = "".join(f"""<a class="scene" href="urunler.html">
  <img src="assets/img/sahne/{k}.webp" alt="{E(t)}" loading="lazy" width="1200" height="900">
  <span class="scene__v"><span class="scene__t">{E(t)}</span><span class="scene__d">{E(d)}</span></span>
</a>""" for k, t, d in scenes)

    facts = [
        ("Aynı gün", "Stoktaki ürünlerde aynı gün sevkiyat; olmayan ölçü aynı gün kesilir."),
        ("1 adet", "Minimum sipariş yok. Tek parça conta da kesiyoruz."),
        (str(NP), f"kalem ürün, {NK} grup. Hepsi tek tedarikçiden."),
        ("Özel", "Kauçuk ve silikon parçalar numuneden, çizimden veya ölçüden üretilir."),
    ]
    fact_html = "".join(
        f'<div class="fact"><div class="fact__n num">{E(n)}</div><p class="fact__l">{E(l)}</p></div>'
        for n, l in facts)

    gap_items = [
        ("Hiçbir yüzey tam düz değildir",
         "Taşlanmış bir flanş bile mikron ölçeğinde dalgalıdır. Conta, o dalgayı doldurarak kapatır."),
        ("Sızdırmazlığı kuran şey kuvvet değil",
         "Cıvatayı daha çok sıkmak çözüm değildir. Önemli olan kuvvetin conta yüzeyine eşit dağılması."),
        ("Malzemeyi akışkan belirler",
         "Aynı ölçüdeki iki conta, yanlış malzemeyle bir haftada biter. Önce ne aktığını konuşuyoruz."),
        ("Contanın fiyatı en küçük kalemdir",
         "Duran bir makinenin saatlik maliyeti yanında conta parası görünmez. Doğru seçim burada kazandırır."),
    ]
    gap_html = "".join(f"<li><b>{E(t)}</b><span>{E(d)}</span></li>" for t, d in gap_items)

    kab_html = "".join(f"<li>{E(k)}</li>" for k in KABILIYET)
    mal_html = "".join(f"<span>{E(m)}</span>" for m in MALZEME)
    nd, nm = seq_count("d"), seq_count("m")
    return f"""{head(BRAND['name'] + " — Conta, salmastra, kauçuk ve silikon sızdırmazlık ürünleri",
       "Conta, mekanik salmastra, o-ring, keçe, ambar kapak lastiği; numuneden ve çizimden kauçuk ve silikon "
       f"özel üretim. Aynı gün sevkiyat. {NK} ürün grubunda {NP} kalem.", cls="is-locked", canon="")}
{loader()}
{nav(here="home")}
<main id="main">

<section class="hero" id="hero">
  <div class="hero__stage">
    <div class="hero__media">
      <img src="assets/img/sahne/hero-frame.webp" alt="" aria-hidden="true">
      <canvas id="heroCanvas" aria-hidden="true"
              data-seq-d="assets/img/hero-seq/d%.webp" data-n-d="{nd}"
              data-seq-m="assets/img/hero-seq/m%.webp" data-n-m="{nm}"></canvas>
    </div>
    <div class="hero__scrim"></div>
    <div class="hero__inner">
      <div id="heroH">
        <h1 class="d1 hero__h"><span class="hero__l1">Kaçak</span><span class="hero__l2" id="heroL2">burada durur.</span></h1>
        <p class="hero__sub">Fabrikalara, üretim tesislerine ve gemilere conta, salmastra,
          kauçuk ve silikon sızdırmazlık ürünleri. Ölçüyü siz verin, malzemeyi birlikte seçelim.</p>
        <div class="hero__acts">
          <a class="btn btn--solid" href="iletisim.html#teklif"><span class="btn__dot"></span>Teklif iste</a>
          <a class="btn btn--ghost" href="urunler.html">Ürünlere bak</a>
        </div>
        <div class="hero__meta">
          <span><b>{NK}</b> ürün grubu</span>
          <span><b>{NP}</b> kalem</span>
          <span><b>Kauçuk &amp; silikon</b> özel üretim</span>
        </div>
      </div>
    </div>
    <div class="hero__cue" aria-hidden="true"><span>Kaydır</span><i></i></div>
  </div>
</section>

<section class="band kauc" id="kaucuk-silikon">
  <div class="wrap">
    <div class="seam"><span class="tag">Kauçuk &amp; silikon özel üretim</span></div>
    <div class="kauc__grid">
      <div>
        <h2 class="d2" data-rise>Kauçuk ve silikon bazlı özel ürünlerde üretim çözümü.</h2>
        <p class="lede kauc__lede" data-rise="60">{E(KAUCUK_LEDE)}</p>
        <ul class="kauc__list" data-rise="100">{kab_html}</ul>
        <div class="kauc__mat" data-rise="120"><span class="kauc__k">Malzeme</span>{mal_html}</div>
        <div class="hero__acts" data-rise="140">
          <a class="btn btn--solid" href="kaucuk-silikon.html"><span class="btn__dot"></span>Kauçuk &amp; silikon ürünler</a>
          <a class="btn btn--ghost" href="iletisim.html#teklif">Numune veya çizim gönder</a>
        </div>
      </div>
      <div class="kauc__shot" data-rise="80">
        <img src="assets/img/sahne/kaucuk-silikon.webp" alt="Kalıplı kauçuk parçalar, ekstrüde profiller ve silikon ürünler"
             loading="lazy" width="1800" height="1344">
      </div>
    </div>
  </div>
</section>

<section class="band" id="stage">
  <div class="wrap">
    <div class="seam"><span class="tag">Ürünler</span></div>
    <h2 class="d2" data-rise>Sızdırmazlık hattının tamamı,<br>tek yerden.</h2>
    <p class="lede" style="margin-top:18px" data-rise="80">Conta ve salmastradan flanşa, kaplin
      lastiğinden ambar kapak profiline kadar. Listede gezinin, ne olduğunu ve nerede çalıştığını görün.</p>
    <div class="stage__grid" style="margin-top:clamp(34px,4.4vw,64px)">
      <ul class="stage__list">{"".join(stage_items)}</ul>
      <div class="stage__viewport">{"".join(stage_shots)}</div>
    </div>
    <p style="margin-top:34px"><a class="btn btn--ghost" href="urunler.html">Tüm ürünleri gör</a></p>
  </div>
</section>

<section class="band band--video">
  <div class="band__media">
    <img src="assets/img/sahne/isin-ozu-bg.webp" alt="" aria-hidden="true">
    <video src="assets/video/isin-ozu-bg.mp4" poster="assets/img/sahne/isin-ozu-bg.webp"
           autoplay muted loop playsinline preload="auto" aria-hidden="true" tabindex="-1"></video>
  </div>
  <div class="band__scrim"></div>
  <div class="wrap">
    <div class="seam"><span class="tag">İşin özü</span></div>
    <h2 class="d2" data-rise>Bütün iş, iki yüzey arasında kalan<br>o birkaç milimetrede biter.</h2>
    <div class="gap-demo" style="margin-top:clamp(30px,4vw,58px)">
      <div data-rise>{DIAGRAM}</div>
      <ul class="gap-demo__list" data-rise="90">{gap_html}</ul>
    </div>
  </div>
</section>

<section class="band band--tight">
  <div class="wrap">
    <div class="seam"><span class="tag">Çalıştığı yerler</span></div>
    <h2 class="d2" data-rise>Aynı sızdırmazlık ailesi, dört ayrı<br>sektörde aynı işi yapar.</h2>
  </div>
  <div class="scenes" style="margin-top:clamp(28px,3.4vw,48px)">{scene_html}</div>
</section>

<section class="band band--light">
  <div class="wrap">
    <div class="seam"><span class="tag">Nasıl çalışıyoruz</span></div>
    <div class="gap-demo">
      <div data-rise>
        <h2 class="d2">Stokta varsa bugün,<br>yoksa ölçüsünde üretilir.</h2>
        <p class="lede" style="margin-top:20px">Duran bir hatta conta aramak pahalıdır. Standart ölçüler
          depomuzda hazır bekler ve aynı gün yola çıkar; katalogda olmayan ölçü numuneden kesilir,
          kalıp gerektiren parça çizimden üretilir.</p>
        <p style="margin-top:26px"><a class="btn btn--ghost" href="hakkimizda.html">Firmayı tanıyın</a></p>
      </div>
      <div data-rise="90" style="aspect-ratio:4/3;overflow:hidden">
        <img src="assets/img/sahne/kurumsal-depo.webp" alt="Düzenli raflarda levha ruloları, profil makaraları ve ürün kutuları"
             loading="lazy" width="1200" height="900" style="width:100%;height:100%;object-fit:cover">
      </div>
    </div>
    <div class="facts" style="margin-top:clamp(34px,4vw,58px)" data-rise>{fact_html}</div>
  </div>
</section>

{quote_block()}
</main>
{foot()}"""


def quote_block(rel=""):
    # değer ürünün slug'ı: mail tarafı görseli, teknik tabloyu ve ölçüyü buradan bulur
    opts = "".join(
        f'<optgroup label="{E(CATS[s][0])}">' + "".join(
            f'<option value="{p["slug"]}"{" data-olcu=1" if p.get("olcu") else ""}>{E(p["ad"])}</option>'
            for p in BY_CAT[s]) + "</optgroup>" for s in CATS)
    dn_opts = "".join(f'<option value="{dn}">DN {dn} — iç {ic} / dış {dis} mm</option>' for dn, ic, dis, *_ in DIN2576)
    return f"""<section class="band" id="teklif">
  <div class="wrap">
    <div class="seam"><span class="tag">Teklif</span></div>
    <div class="quote">
      <div>
        <h2 class="d2">Ölçüyü söyleyin,<br>malzemeyi birlikte seçelim.</h2>
        <p class="lede" style="margin-top:20px">Elinizde eski bir conta, bir flanş ölçüsü veya
          sadece pompanın markası olsun yeter. Doğru malzemeyi biz bulalım.</p>
        <ul class="contact-list" style="margin-top:clamp(28px,3vw,44px)">
          <li><span class="k">Telefon</span><a class="v" href="tel:{BRAND['phone']}">{BRAND['phone_display']}</a></li>
          <li><span class="k">E-posta</span><a class="v" href="mailto:{BRAND['mail']}">{BRAND['mail']}</a></li>
          <li><span class="k">Adres</span><a class="v" href="{BRAND['maps']}" target="_blank" rel="noopener">{E(BRAND['adres'])}</a></li>
        </ul>
      </div>
      <form class="form" id="quoteForm" novalidate>
        <div class="form__row">
          <div class="field"><label for="f-ad">Ad soyad</label>
            <input id="f-ad" name="ad" type="text" autocomplete="name" required></div>
          <div class="field"><label for="f-firma">Firma adı</label>
            <input id="f-firma" name="firma" type="text" autocomplete="organization"></div>
        </div>
        <div class="form__row">
          <div class="field"><label for="f-tel">Telefon</label>
            <input id="f-tel" name="tel" type="tel" inputmode="tel" autocomplete="tel" required></div>
          <div class="field"><label for="f-urun">Aradığınız ürün</label>
            <select id="f-urun" name="urun"><option value="">Seçin</option>{opts}
              <option value="emin-degilim">Emin değilim, yardım gerekiyor</option></select></div>
        </div>
        <div class="form__row">
          <div class="field" id="f-dn-wrap" hidden><label for="f-dn">Standart ölçü <span class="hint">DIN 2576 PN16</span></label>
            <select id="f-dn" name="dn"><option value="">Ölçü seçin</option>{dn_opts}</select></div>
          <div class="field"><label for="f-adet">Adet <span class="hint">İsteğe bağlı</span></label>
            <input id="f-adet" name="adet" type="text" inputmode="numeric" placeholder="Örn: 12"></div>
        </div>
        <div class="field">
          <label for="f-olcu">Ölçü ve açıklama <span class="hint">Bilmiyorsanız pompanın veya makinenin markasını yazın.</span></label>
          <textarea id="f-olcu" name="olcu" placeholder="Örn: 2 mm kalınlık, iç çap 116, dış çap 220"></textarea>
        </div>
        <div class="form__row">
          <div class="field"><label for="f-acil">Aciliyet</label>
            <select id="f-acil" name="aciliyet">
              <option>Bugün lazım</option><option>Bu hafta</option><option>Planlı iş</option></select></div>
          <div class="field"><label for="f-not">Not <span class="hint">İsteğe bağlı</span></label>
            <input id="f-not" name="not" type="text"></div>
        </div>
        <div class="hp" aria-hidden="true">
          <label for="f-website">Bu alanı boş bırakın</label>
          <input id="f-website" name="website" type="text" tabindex="-1" autocomplete="off"></div>
        <div class="form__foot">
          <button class="btn btn--solid" id="quoteSend" type="submit"><span class="btn__dot"></span>Teklif iste</button>
          <button class="btn btn--ghost btn--wa" id="quoteWa" type="button">
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2c-5.46 0-9.9 4.44-9.9 9.9 0 1.75.46 3.45 1.32 4.95L2 22l5.3-1.38a9.87 9.87 0 0 0 4.74 1.21h.01c5.46 0 9.9-4.44 9.9-9.9 0-2.64-1.03-5.13-2.9-7A9.82 9.82 0 0 0 12.04 2zm0 18.13h-.01a8.2 8.2 0 0 1-4.18-1.15l-.3-.18-3.11.82.83-3.04-.2-.31a8.19 8.19 0 0 1-1.26-4.37c0-4.54 3.7-8.23 8.23-8.23 2.2 0 4.26.86 5.82 2.41a8.18 8.18 0 0 1 2.41 5.82c0 4.54-3.7 8.23-8.23 8.23zm4.51-6.16c-.25-.12-1.46-.72-1.69-.8-.23-.09-.39-.12-.56.12-.16.25-.64.8-.79.97-.14.16-.29.18-.54.06-.25-.12-1.04-.38-1.98-1.22-.73-.65-1.23-1.46-1.37-1.7-.14-.25-.02-.38.11-.5.11-.11.25-.29.37-.43.12-.14.16-.25.25-.41.08-.16.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.16 0-.43.06-.64.31-.22.25-.85.83-.85 2.03s.87 2.35.99 2.51c.12.16 1.71 2.61 4.14 3.66.58.25 1.03.4 1.38.51.58.19 1.11.16 1.53.1.47-.07 1.46-.6 1.66-1.18.21-.58.21-1.07.14-1.18-.06-.11-.22-.18-.47-.3z"/></svg>
            WhatsApp'tan gönder
          </button>
          <p class="form__note">Talebiniz doğrudan <b>info@tuzlaconta.com</b> adresine iletilir.
            Dilerseniz WhatsApp üzerinden de gönderebilirsiniz.</p>
        </div>
        <p class="form__ok" id="quoteOk" hidden tabindex="-1">Teklif talebiniz iletildi.
          En kısa sürede size dönüş yapacağız.</p>
        <p class="form__err" id="quoteErr" hidden tabindex="-1">Talep gönderilemedi.
          Lütfen WhatsApp butonunu kullanın ya da <a href="tel:{BRAND['phone']}">{BRAND['phone_display']}</a>'ü arayın.</p>
      </form>
    </div>
  </div>
</section>"""


# ---------------------------------------------------------------- ürün listesi
def page_urunler():
    blocks = []
    for s in CATS:
        name, desc, _ = CATS[s]
        items = "".join(card(p, "") for p in BY_CAT[s])
        blocks.append(f"""<section class="cat-block" id="{s}">
  <div class="cat-head"><h2 class="d3">{E(name)}</h2><p class="cat-head__d">{E(desc)}</p></div>
  <div class="grid">{items}</div>
</section>""")
    idx = "".join(f'<a class="btn btn--ghost" href="#{s}" style="padding:9px 16px;font-size:.86rem">{E(CATS[s][0])}</a>'
                  for s in CATS)
    return f"""{head("Ürünler — " + BRAND['short'],
       f"{NK} grupta {NP} kalem: ambar kapak lastiği, mekanik salmastra, conta, levha, salmastra, o-ring, keçe, "
       "kaplin, takoz, flanş, set, servis ekipmanları ve kauçuk-silikon özel üretim.", canon="urunler.html")}
{nav(here="urunler")}
<main id="main">
<section class="ph">
  <div class="wrap">
    <div class="crumb"><a href="index.html">Ana sayfa</a><span aria-hidden="true">/</span><span>Ürünler</span></div>
    <h1 class="d1" style="max-width:14ch">Ürünler</h1>
    <p class="lede" style="margin-top:20px;max-width:52ch">{NK} ürün grubunda {NP} kalem. Ölçü katalogda
      yoksa numuneden kesiyoruz; malzemeyi akışkana, sıcaklığa ve basınca göre birlikte seçiyoruz.</p>
    <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:clamp(26px,3vw,40px)">{idx}</div>
  </div>
</section>
<section class="band band--tight" style="padding-top:0">
  <div class="wrap">{"".join(blocks)}</div>
</section>
{quote_block()}
</main>
{foot()}"""


# ---------------------------------------------------------------- ürün sayfası
def page_urun(p):
    kat, kdesc, _ = CATS[p["kat"]]
    ticks = "".join(f"<li>{E(x)}</li>" for x in p["ne_yarar"])
    where = "".join(f"<li>{E(x)}</li>" for x in p["nerede"])
    rows = "".join(f"<tr><th scope=\"row\">{E(k)}</th><td>{E(v)}</td></tr>" for k, v in p["teknik"])
    note = f'<p class="note">{E(p["teknik_not"])}</p>' if p.get("teknik_not") else ""
    sibs = [q for q in BY_CAT[p["kat"]] if q["slug"] != p["slug"]][:4]
    rel_html = ""
    if sibs:
        rel_html = f"""<section class="band band--tight">
  <div class="wrap">
    <div class="seam"><span class="tag">Aynı gruptan</span></div>
    <div class="grid">{"".join(card(q, "../") for q in sibs)}</div>
  </div>
</section>"""
    ld = {
        "@context": "https://schema.org", "@type": "Product", "name": p["ad"],
        "description": p["ozet"], "category": kat,
        "image": f"https://tuzlaconta.com/assets/img/urun/{p['slug']}.webp",
        "brand": {"@type": "Brand", "name": BRAND["short"]},
    }
    import json as _j
    return f"""{head(p['ad'] + " — " + BRAND['short'], p['ozet'], rel="../", canon="urun/" + p['slug'] + ".html")}
{nav("../", here="urunler")}
<main id="main">
<section class="ph">
  <div class="wrap">
    <div class="crumb">
      <a href="../index.html">Ana sayfa</a><span aria-hidden="true">/</span>
      <a href="../urunler.html">Ürünler</a><span aria-hidden="true">/</span>
      <a href="../urunler.html#{p['kat']}">{E(kat)}</a><span aria-hidden="true">/</span>
      <span>{E(p['ad'])}</span>
    </div>
    <div class="ph__grid">
      <div class="ph__shot" data-rise>
        <img src="../assets/img/urun/{p['slug']}.webp" alt="{E(p['ad'])} stüdyo çekimi" width="1200" height="900">
      </div>
      <div>
        <h1 class="d2">{E(p['ad'])}</h1>
        <p class="ph__lede">{E(p['ozet'])}</p>
        <div class="ph__acts">
          <a class="btn btn--solid" href="../iletisim.html?urun={p['slug']}#teklif"><span class="btn__dot"></span>Bu ürün için teklif iste</a>
          <a class="btn btn--ghost" href="tel:{BRAND['phone']}">{BRAND['phone_display']}</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="band band--light">
  <div class="wrap">
    <div class="pd">
      <div>
        <div class="pd__blk"><h2>{E(p['ad'])} nedir?</h2><p>{E(p['nedir'])}</p></div>
        <div class="pd__blk"><h2>Ne işe yarar?</h2><ul class="ticks">{ticks}</ul></div>
        <div class="pd__blk"><h2>Nerede kullanılır?</h2><ul class="ticks">{where}</ul></div>
      </div>
      <div>
        <table class="spec"><caption>Teknik bilgiler</caption><tbody>{rows}</tbody></table>
        {note}
        <div class="aside-card" style="margin-top:28px">
          <h3>Ölçü katalogda yok mu?</h3>
          <p>Elinizdeki numuneden veya flanş ölçüsünden kesiyoruz. Tek adet de üretiyoruz.</p>
          <a class="btn btn--solid" href="../iletisim.html?urun={p['slug']}#teklif"><span class="btn__dot"></span>Ölçü gönder</a>
        </div>
      </div>
    </div>
  </div>
</section>
{olcu_table(p)}
{rel_html}
</main>
<script type="application/ld+json">{_j.dumps(ld, ensure_ascii=False)}</script>
{foot("../")}"""


# ---------------------------------------------------------------- kurumsal
def page_hakkimizda():
    return f"""{head("Hakkımızda — " + BRAND['short'],
       "Conta, salmastra, kauçuk ve silikon sızdırmazlık ürünlerinde stoklu tedarik ve ölçüye özel üretim.",
       canon="hakkimizda.html")}
{nav(here="hakkimizda")}
<main id="main">
<section class="ph">
  <div class="wrap">
    <div class="crumb"><a href="index.html">Ana sayfa</a><span aria-hidden="true">/</span><span>Hakkımızda</span></div>
    <h1 class="d1" style="max-width:16ch">Sızdırmazlık, bizim tek işimiz.</h1>
    <p class="lede" style="margin-top:22px;max-width:56ch">Fabrikaların, üretim tesislerinin ve gemilerin
      sızdırmazlık ihtiyacını tek elden karşılıyoruz. Yaptığımız iş tek cümleyle şu: bir yerden bir şey
      kaçıyorsa, onu durduracak parçayı doğru malzemeden, doğru ölçüde ve zamanında getirmek; katalogda
      yoksa üretmek.</p>
  </div>
</section>

<section class="band band--tight" style="padding-top:0">
  <div class="wrap">
    <div class="about-shot" data-rise>
      <img src="assets/img/sahne/kurumsal-hakkimizda.webp"
        alt="Aydınlık, sade bir yüzey üzerinde mekanik salmastra, conta, kauçuk profil, o-ring ve silikon profil"
        width="2400" height="1018">
    </div>
  </div>
</section>

<section class="band band--light">
  <div class="wrap">
    <div class="pd">
      <div>
        <div class="pd__blk">
          <h2>Ne yapıyoruz?</h2>
          <p>Conta, mekanik salmastra, salmastra, o-ring, keçe, kaplin lastiği, flanş, levha, takoz ve
            ambar kapak lastiği gruplarında {NP} kalemi stokta tutuyor, standart ölçüleri aynı gün
            gönderiyoruz. Katalog ölçüsü yetmediğinde levhadan ve numuneden kesim yapıyoruz.</p>
          <p>Standart ürünlerin yanı sıra, ihtiyaca özel ölçü, formülasyon ve teknik gereksinimlere göre
            kauçuk ve silikon bazlı contalar, profiller, kalıplı parçalar ve kauçuk-metal birleşimli parçalar
            üretiyoruz. Numuneden, müşteri çiziminden veya yalnızca bir ölçüden yola çıkıp önce prototip,
            ardından seri üretim yapıyoruz.</p>
          <p>Mekanik salmastralarda EMU, Flygt, ABS, Alfa Laval, Fristam ve Frick gibi markaların
            pompalarına birebir uyan muadil çözümler sunuyoruz.</p>
        </div>
        <div class="pd__blk">
          <h2>Nasıl çalışıyoruz?</h2>
          <ul class="ticks">
            <li>Önce ne aktığını, kaç derece ve kaç bar olduğunu soruyoruz. Malzeme ondan sonra seçiliyor.</li>
            <li>Ölçü katalogda yoksa numuneden birebir kesiyoruz; tek adet için de üretim yapıyoruz.</li>
            <li>Kalıp gerektiren parçada önce prototip çıkarıyor, onaydan sonra seriye geçiyoruz.</li>
            <li>Stoktaki ürünler aynı gün yola çıkıyor.</li>
            <li>Yanlış malzemeden dolayı tekrarlayan arızalarda ürünü değil, çözümü değiştiriyoruz.</li>
          </ul>
        </div>
        <div class="pd__blk">
          <h2>Kimlerle çalışıyoruz?</h2>
          <p>Üretim fabrikaları ve makine imalatçıları, gıda, içecek, kimya ve ilaç tesisleri, enerji
            santralleri, pompa ve vana servisleri, bakım atölyeleri, gemi işletmeleri ve gemi tedarik firmaları.</p>
        </div>
      </div>
      <div>
        <table class="spec"><caption>Künye</caption><tbody>
          <tr><th scope="row">Firma</th><td>{E(BRAND['name'])}</td></tr>
          <tr><th scope="row">Adres</th><td>{E(BRAND['adres'])}</td></tr>
          <tr><th scope="row">Telefon</th><td>{BRAND['phone_display']}</td></tr>
          <tr><th scope="row">E-posta</th><td>{BRAND['mail']}</td></tr>
          <tr><th scope="row">Ürün grubu</th><td>{NK} grup, {NP} kalem</td></tr>
          <tr><th scope="row">Özel üretim</th><td>Kauçuk, silikon, kauçuk-metal</td></tr>
          <tr><th scope="row">Çalışma saatleri</th><td>Hafta içi 08:30 – 18:30<br>Cumartesi 09:00 – 15:00</td></tr>
        </tbody></table>
        <div class="aside-card" style="margin-top:28px">
          <h3>Katalog mu lazım?</h3>
          <p>Genel katalog ve uluslararası mekanik salmastra kataloğunu e-posta ile gönderelim.</p>
          <a class="btn btn--solid" href="mailto:{BRAND['mail']}?subject=Katalog%20talebi"><span class="btn__dot"></span>Katalog iste</a>
        </div>
      </div>
    </div>
  </div>
</section>
{quote_block()}
</main>
{foot()}"""


# ---------------------------------------------------------------- kauçuk & silikon
def page_kaucuk():
    steps = [("Numune, çizim veya ölçü", "Elinizdeki eski parça, 2D/3D çizim ya da yalnızca birkaç ölçü yeterli."),
             ("Malzeme ve sertlik", "Akışkana, sıcaklığa, basınca ve aşınmaya göre hamur ve Shore sertliği birlikte seçilir."),
             ("Kalıp ve prototip", "Kalıp veya ekstrüzyon düzesi hazırlanır, ilk parçalar ölçü ve montaj için onaya sunulur."),
             ("Seri üretim", "Onaylanan parça aynı kalıpla tekrarlanabilir kalitede, istenen adette üretilir.")]
    step_html = "".join(f'<li><span class="num">{i+1:02d}</span><b>{E(t)}</b><p>{E(d)}</p></li>'
                        for i, (t, d) in enumerate(steps))
    mats = [("EPDM", "Sıcak su, buhar kondensi, ozon ve dış ortam"), ("NBR", "Yağ, yakıt ve hidrolik akışkan"),
            ("Viton (FKM)", "Yüksek sıcaklıkta yağ, yakıt ve kimyasal"), ("Silikon (VMQ)", "-60 °C … +230 °C, gıda ve ilaç teması"),
            ("Neopren (CR)", "Hava koşulları, deniz suyu, alev geciktirme"), ("Doğal kauçuk (NR)", "Aşınma, darbe ve yüksek esneklik")]
    mat_rows = "".join(f'<tr><th scope="row">{E(k)}</th><td>{E(v)}</td></tr>' for k, v in mats)
    kab = "".join(f"<li>{E(k)}</li>" for k in KABILIYET)
    ozel = [p for p in P if p["kat"] in ("ozel-kaucuk", "ozel-conta")] + \
           [BY_SLUG[s] for s in ("kaucuk-conta", "viton-conta", "epdm-sunger-profil") if s in BY_SLUG]
    cards = "".join(card(p, "") for p in ozel)
    return f"""{head("Kauçuk & Silikon Ürünler — " + BRAND['short'],
       "Kauçuk ve silikon bazlı contalar, profiller, kalıplı parçalar ve kauçuk-metal parçalar. "
       "Numuneden, çizimden veya ölçüden prototip ve seri üretim.", canon="kaucuk-silikon.html")}
{nav(here="kaucuk")}
<main id="main">
<section class="ph">
  <div class="wrap">
    <div class="crumb"><a href="index.html">Ana sayfa</a><span aria-hidden="true">/</span><span>Kauçuk &amp; Silikon Ürünler</span></div>
    <div class="ph__grid">
      <div>
        <h1 class="d2">Kauçuk ve silikon bazlı özel ürünlerde üretim çözümü.</h1>
        <p class="ph__lede" style="max-width:52ch">{E(KAUCUK_LEDE)}</p>
        <div class="ph__acts">
          <a class="btn btn--solid" href="iletisim.html#teklif"><span class="btn__dot"></span>Numune veya çizim gönder</a>
          <a class="btn btn--ghost" href="tel:{BRAND['phone']}">{BRAND['phone_display']}</a>
        </div>
      </div>
      <div class="ph__shot" data-rise>
        <img src="assets/img/sahne/kaucuk-silikon.webp" alt="Kalıplı kauçuk parçalar, profiller ve silikon ürünler" width="1800" height="1344">
      </div>
    </div>
  </div>
</section>

<section class="band band--light">
  <div class="wrap">
    <div class="pd">
      <div>
        <div class="pd__blk"><h2>Neler üretiyoruz?</h2><ul class="ticks ticks--2">{kab}</ul></div>
        <div class="pd__blk"><h2>Nasıl üretiyoruz?</h2><ol class="steps">{step_html}</ol></div>
      </div>
      <div>
        <table class="spec"><caption>Malzeme ve kullanım yeri</caption><tbody>{mat_rows}</tbody></table>
        <p class="note">Sertlik 30 – 90 Shore A aralığında; renkli, gıda uygun ve alev geciktirici hamurlar talebe göre hazırlanır.</p>
      </div>
    </div>
  </div>
</section>

<section class="band band--tight">
  <div class="wrap">
    <div class="seam"><span class="tag">Kauçuk ve silikon ürünler</span></div>
    <div class="grid">{cards}</div>
  </div>
</section>
{quote_block()}
</main>
{foot()}"""


def page_iletisim():
    return f"""{head("İletişim — " + BRAND['short'],
       "Telefon, WhatsApp ve teklif formu. Ölçü, numune fotoğrafı veya çizim gönderin, aynı gün dönelim.",
       canon="iletisim.html")}
{nav(here="iletisim")}
<main id="main">
<section class="ph">
  <div class="wrap">
    <div class="crumb"><a href="index.html">Ana sayfa</a><span aria-hidden="true">/</span><span>İletişim</span></div>
    <h1 class="d1" style="max-width:14ch">Arayın, çözelim.</h1>
    <p class="lede" style="margin-top:22px">Acil bir işse telefon en hızlısı. Ölçü ve fotoğraf
      göndereceksiniz WhatsApp daha pratik.</p>
  </div>
</section>
<section class="band band--tight" style="padding-top:0">
  <div class="wrap">
    <div class="scenes" style="margin-bottom:clamp(22px,2.6vw,38px)">
      <a class="scene" href="urunler.html" style="min-height:clamp(230px,26vw,330px)">
        <img src="assets/img/sahne/kurumsal-depo.webp" alt="Düzenli raflarda levha ruloları ve ürün kutuları"
             loading="lazy" width="1200" height="900">
        <span class="scene__v"><span class="scene__t">Stoktan aynı gün</span>
          <span class="scene__d">Standart ölçüler depoda hazır; sipariş aynı gün yola çıkar.</span></span>
      </a>
      <a class="scene" href="kaucuk-silikon.html" style="min-height:clamp(230px,26vw,330px)">
        <img src="assets/img/sahne/kat-ozel-conta.webp" alt="CNC kesim tezgâhı yanında özel ölçü contalar"
             loading="lazy" width="1200" height="900">
        <span class="scene__v"><span class="scene__t">Ölçü yoksa üretiriz</span>
          <span class="scene__d">Numuneyi getirin ya da fotoğrafını, çizimini gönderin; birebir çıkaralım.</span></span>
      </a>
    </div>
    <div style="aspect-ratio:21/9;overflow:hidden;border:1px solid var(--line-dark)">
      <iframe title="Tuzla Conta konumu" loading="lazy" style="width:100%;height:100%;border:0;filter:grayscale(1) invert(.92) hue-rotate(180deg) contrast(.92)"
        referrerpolicy="no-referrer-when-downgrade"
        src="https://www.google.com/maps?q=%C4%B0stasyon%20Mahallesi%20Su%20Yolu%20Sokak%20No%3A3%2C%2034940%20Tuzla%2F%C4%B0stanbul&z=16&output=embed"></iframe>
    </div>
  </div>
</section>
{quote_block()}
</main>
{foot()}"""


# ---------------------------------------------------------------- teklif maili
def mail_katalog():
    """api/teklif-gonder.js'in okuduğu katalog özeti ve e-posta görselleri.
    E-posta istemcilerinin çoğu (Outlook masaüstü dahil) webp göstermez; mail
    görselleri ayrıca küçük jpg olarak üretilir ve maile gömülü (CID) eklenir."""
    import json
    api = os.path.join(os.path.dirname(ROOT), "api")
    out = os.path.join(api, "_mail")
    os.makedirs(out, exist_ok=True)
    data = {"din2576": [list(r) for r in DIN2576], "urunler": {}}
    for p in P:
        data["urunler"][p["slug"]] = {"ad": p["ad"], "kat": CATS[p["kat"]][0], "ozet": p["ozet"],
                                      "teknik": p["teknik"], "olcu": p.get("olcu") or ""}
        src = os.path.join(ROOT, "assets", "img", "urun", p["slug"] + ".webp")
        dst = os.path.join(out, p["slug"] + ".jpg")
        if _PIL and (not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src)):
            im = Image.open(src).convert("RGB")
            im.resize((1120, round(im.height * 1120 / im.width)), Image.LANCZOS).save(
                dst, "JPEG", quality=76, optimize=True, progressive=True)
    live = set(data["urunler"])
    for f in os.listdir(out):
        if f.endswith(".jpg") and f[:-4] not in live and not f.startswith("_"):
            os.remove(os.path.join(out, f))
    with open(os.path.join(api, "_katalog.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------- yaz
def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(content)
    return len(content)


if __name__ == "__main__":
    total = 0
    total += write("index.html", page_index())
    total += write("urunler.html", page_urunler())
    total += write("hakkimizda.html", page_hakkimizda())
    total += write("iletisim.html", page_iletisim())
    total += write("kaucuk-silikon.html", page_kaucuk())
    for p in P:
        total += write(f"urun/{p['slug']}.html", page_urun(p))
    # robots + sitemap
    urls = ["", "urunler.html", "kaucuk-silikon.html", "hakkimizda.html", "iletisim.html"] + [f"urun/{p['slug']}.html" for p in P]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          + "".join(f"<url><loc>https://tuzlaconta.com/{u}</loc></url>" for u in urls) + "</urlset>")
    write("sitemap.xml", sm)
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: https://tuzlaconta.com/sitemap.xml\n")
    mail_katalog()
    # katalogdan çıkarılan ürünlerin sayfaları ve görselleri kalmasın
    live = {p["slug"] for p in P}
    for f in os.listdir(os.path.join(ROOT, "urun")):
        if f.endswith(".html") and f[:-5] not in live:
            os.remove(os.path.join(ROOT, "urun", f)); print("silindi: urun/" + f)
    for f in os.listdir(os.path.join(ROOT, "assets", "img", "urun")):
        if f.endswith(".webp") and f[:-5] not in live:
            os.remove(os.path.join(ROOT, "assets", "img", "urun", f)); print("silindi: img/urun/" + f)
    print(f"{5 + len(P)} sayfa yazıldı, {total//1024} KB")
