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

LOGO = open(os.path.join(ROOT, "assets", "img", "logo.svg"), encoding="utf-8").read()
MARK = open(os.path.join(ROOT, "assets", "img", "logo-mark.svg"), encoding="utf-8").read()
BRANDLOCK = (f'<span class="brand">{MARK}'
             '<span class="brand__t"><span class="brand__n">TUZLA CONTA</span>'
             '<span class="brand__s">SIZDIRMAZLIK</span></span></span>')

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
        f'<li><a href="{rel}urunler.html#{s}">{E(CATS[s][0])}</a></li>' for s in list(CATS)[:6])
    cols2 = "".join(
        f'<li><a href="{rel}urunler.html#{s}">{E(CATS[s][0])}</a></li>' for s in list(CATS)[6:])
    return f"""<footer class="foot">
<div class="wrap">
  <div class="foot__top">
    <div>
      <div class="foot__logo">{BRANDLOCK}</div>
      <p class="foot__blurb">Tuzla'da, tersane hattının içinde. Gemilere ve sanayi tesislerine
        conta, salmastra ve sızdırmazlık elemanları.</p>
    </div>
    <div><h4>Sızdırmazlık</h4><ul>{cols}</ul></div>
    <div><h4>Malzeme ve ekipman</h4><ul>{cols2}</ul></div>
    <div><h4>İletişim</h4><ul>
      <li><a href="tel:{BRAND['phone']}">{BRAND['phone_display']}</a></li>
      <li><a href="tel:{BRAND['phone2']}">{BRAND['phone2_display']}</a></li>
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
        ("uyg-tersane", "Tersaneler ve gemiler",
         "Ambar kapak profilleri, köşe parçaları, güverte ekipmanları ve klas gerektiren sızdırmazlık hatları."),
        ("uyg-makine-dairesi", "Makine daireleri",
         "Ana makine, yardımcı makine, yakıt ve yağlama hatlarının conta ve salmastraları."),
        ("uyg-pompa", "Pompa ve vana hatları",
         "Mekanik salmastra, yumuşak salmastra ve flanş contalarıyla duran pompayı tekrar çalıştırmak."),
        ("uyg-esanjor", "Eşanjör ve proses",
         "Plaka eşanjör contaları, yüksek sıcaklık contaları ve kimyasala dayanıklı malzemeler."),
    ]
    scene_html = "".join(f"""<a class="scene" href="urunler.html">
  <img src="assets/img/sahne/{k}.webp" alt="{E(t)}" loading="lazy" width="1200" height="900">
  <span class="scene__v"><span class="scene__t">{E(t)}</span><span class="scene__d">{E(d)}</span></span>
</a>""" for k, t, d in scenes)

    facts = [
        ("Aynı gün", "Stoktaki ürünler için Tuzla ve tersane bölgesine aynı gün sevkiyat."),
        ("1 adet", "Minimum sipariş yok. Tek parça conta da kesiyoruz."),
        ("51", "kalem ürün, 12 grup. Hepsi tek tedarikçiden."),
        ("IACS", "Ambar kapak ürünleri klas kuruluşu standartlarına göre üretilir."),
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

    return f"""{head(BRAND['name'] + " — Gemi ve sanayi sızdırmazlık ürünleri | Tuzla, İstanbul",
       "Tuzla'da conta, mekanik salmastra, o-ring, keçe, kaplin lastiği, flanş ve ambar kapak lastiği. "
       "Numuneden kesim, aynı gün sevkiyat. 12 ürün grubunda 51 kalem.", cls="is-locked", canon="")}
{loader()}
{nav(here="home")}
<main id="main">

<section class="hero" id="hero">
  <div class="hero__stage">
    <div class="hero__media">
      <img src="assets/img/sahne/hero-frame.webp" alt="" aria-hidden="true">
      <canvas id="heroCanvas" aria-hidden="true"
              data-seq-d="assets/img/hero-seq/d%.webp" data-n-d="154"
              data-seq-m="assets/img/hero-seq/m%.webp" data-n-m="77"></canvas>
    </div>
    <div class="hero__scrim"></div>
    <div class="hero__inner">
      <div id="heroH">
        <h1 class="d1 hero__h"><span class="hero__l1">Kaçak</span><span class="hero__l2" id="heroL2">burada durur.</span></h1>
        <p class="hero__sub">Gemilere, tersanelere ve sanayi tesislerine conta, salmastra ve
          sızdırmazlık elemanları. Ölçüyü siz verin, malzemeyi birlikte seçelim.</p>
        <div class="hero__acts">
          <a class="btn btn--solid" href="iletisim.html#teklif"><span class="btn__dot"></span>Teklif iste</a>
          <a class="btn btn--ghost" href="urunler.html">Ürünlere bak</a>
        </div>
        <div class="hero__meta">
          <span><b>12</b> ürün grubu</span>
          <span><b>51</b> kalem</span>
          <span><b>Tuzla</b> İstasyon Mahallesi</span>
        </div>
      </div>
    </div>
    <div class="hero__cue" aria-hidden="true"><span>Kaydır</span><i></i></div>
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

<section class="band band--tight">
  <div class="wrap">
    <div class="seam"><span class="tag">Çalıştığı yerler</span></div>
    <h2 class="d2" data-rise>Aynı conta ailesi, dört ayrı dünyada<br>aynı işi yapar.</h2>
  </div>
  <div class="scenes" style="margin-top:clamp(28px,3.4vw,48px)">{scene_html}</div>
</section>

<section class="band band--light">
  <div class="wrap">
    <div class="seam"><span class="tag">Nasıl çalışıyoruz</span></div>
    <div class="gap-demo">
      <div data-rise>
        <h2 class="d2">Tuzla'dayız. Yani zaten<br>tersanenin içindeyiz.</h2>
        <p class="lede" style="margin-top:20px">Bir gemi rıhtımda beklerken conta aramak pahalıdır.
          İstasyon Mahallesi'ndeki depomuz tersane hattının tam ortasında; stoktaki ürün aynı gün yola çıkar,
          olmayan ölçü aynı gün kesilir.</p>
        <p style="margin-top:26px"><a class="btn btn--ghost" href="hakkimizda.html">Firmayı tanıyın</a></p>
      </div>
      <div data-rise="90" style="aspect-ratio:4/3;overflow:hidden">
        <img src="assets/img/sahne/kurumsal-depo.webp" alt="Tuzla Conta deposunda raflarda duran levha ruloları ve conta kutuları"
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
    opts = "".join(f'<option value="{E(CATS[s][0])}">{E(CATS[s][0])}</option>' for s in CATS)
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
          <li><span class="k">İkinci hat</span><a class="v" href="tel:{BRAND['phone2']}">{BRAND['phone2_display']}</a></li>
          <li><span class="k">E-posta</span><a class="v" href="mailto:{BRAND['mail']}">{BRAND['mail']}</a></li>
          <li><span class="k">Adres</span><a class="v" href="{BRAND['maps']}" target="_blank" rel="noopener">{E(BRAND['adres'])}</a></li>
        </ul>
      </div>
      <form class="form" id="quoteForm" novalidate>
        <div class="form__row">
          <div class="field"><label for="f-ad">Ad soyad</label>
            <input id="f-ad" name="ad" type="text" autocomplete="name" required></div>
          <div class="field"><label for="f-firma">Firma veya gemi adı</label>
            <input id="f-firma" name="firma" type="text" autocomplete="organization"></div>
        </div>
        <div class="form__row">
          <div class="field"><label for="f-tel">Telefon</label>
            <input id="f-tel" name="tel" type="tel" inputmode="tel" autocomplete="tel" required></div>
          <div class="field"><label for="f-urun">Aradığınız ürün</label>
            <select id="f-urun" name="urun"><option value="">Seçin</option>{opts}
              <option value="Emin değilim">Emin değilim, yardım gerekiyor</option></select></div>
        </div>
        <div class="field">
          <label for="f-olcu">Ölçü ve adet <span class="hint">Bilmiyorsanız pompanın veya makinenin markasını yazın.</span></label>
          <textarea id="f-olcu" name="olcu" placeholder="Örn: DN80 PN16 klingrit conta, 2 mm, 12 adet"></textarea>
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
          Lütfen WhatsApp butonunu kullanın ya da <a href="tel:+905436183893">0543 618 38 93</a>'ü arayın.</p>
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
       "12 grupta 51 kalem: conta, mekanik salmastra, yumuşak salmastra, o-ring, keçe, ambar kapak lastiği, "
       "levha, kaplin, flanş, takoz, set ve servis ekipmanları.", canon="urunler.html")}
{nav(here="urunler")}
<main id="main">
<section class="ph">
  <div class="wrap">
    <div class="crumb"><a href="index.html">Ana sayfa</a><span aria-hidden="true">/</span><span>Ürünler</span></div>
    <h1 class="d1" style="max-width:14ch">Ürünler</h1>
    <p class="lede" style="margin-top:20px;max-width:52ch">12 ürün grubunda 51 kalem. Ölçü katalogda
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
          <a class="btn btn--solid" href="../iletisim.html#teklif"><span class="btn__dot"></span>Bu ürün için teklif iste</a>
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
          <a class="btn btn--solid" href="../iletisim.html#teklif"><span class="btn__dot"></span>Ölçü gönder</a>
        </div>
      </div>
    </div>
  </div>
</section>
{rel_html}
</main>
<script type="application/ld+json">{_j.dumps(ld, ensure_ascii=False)}</script>
{foot("../")}"""


# ---------------------------------------------------------------- kurumsal
def page_hakkimizda():
    return f"""{head("Hakkımızda — " + BRAND['short'],
       "Tuzla İstasyon Mahallesi'nde, tersane hattının içinde conta ve sızdırmazlık tedarikçisi.",
       canon="hakkimizda.html")}
{nav(here="hakkimizda")}
<main id="main">
<section class="ph">
  <div class="wrap">
    <div class="crumb"><a href="index.html">Ana sayfa</a><span aria-hidden="true">/</span><span>Hakkımızda</span></div>
    <h1 class="d1" style="max-width:16ch">Sızdırmazlık, bizim tek işimiz.</h1>
    <p class="lede" style="margin-top:22px;max-width:54ch">Tuzla İstasyon Mahallesi'nde, tersanelerin
      ve gemi tedarik hattının tam ortasındayız. Yaptığımız iş tek cümleyle şu: bir yerden bir şey
      kaçıyorsa, onu durduracak parçayı doğru malzemeden, doğru ölçüde ve zamanında getirmek.</p>
  </div>
</section>

<section class="band band--tight" style="padding-top:0">
  <div class="wrap">
    <div style="aspect-ratio:21/9;overflow:hidden" data-rise>
      <img src="assets/img/sahne/kurumsal-tezgah.webp" alt="Atölyede levhadan conta kesimi"
        loading="lazy" width="1600" height="686" style="width:100%;height:100%;object-fit:cover">
    </div>
  </div>
</section>

<section class="band band--light">
  <div class="wrap">
    <div class="pd">
      <div>
        <div class="pd__blk">
          <h2>Ne yapıyoruz?</h2>
          <p>Conta, mekanik salmastra, yumuşak salmastra, o-ring, keçe, kaplin lastiği, flanş, levha,
            takoz ve gemi ambar kapak grubu ürünlerini stoklayıp tedarik ediyoruz. Katalog ölçüsü
            yetmediğinde levhadan ve numuneden kesim yapıyoruz.</p>
          <p>Mekanik salmastralarda EMU, Flygt, ABS, Alfa Laval, Fristam ve Frick gibi markaların
            pompalarına birebir uyan muadil çözümler sunuyoruz. Ambar kapak ürünlerimiz IACS
            standartlarında üretiliyor.</p>
        </div>
        <div class="pd__blk">
          <h2>Nasıl çalışıyoruz?</h2>
          <ul class="ticks">
            <li>Önce ne aktığını, kaç derece ve kaç bar olduğunu soruyoruz. Malzeme ondan sonra seçiliyor.</li>
            <li>Ölçü katalogda yoksa numuneden birebir kesiyoruz; tek adet için de üretim yapıyoruz.</li>
            <li>Stoktaki ürünler Tuzla ve tersane bölgesine aynı gün çıkıyor.</li>
            <li>Yanlış malzemeden dolayı tekrarlayan arızalarda ürünü değil, çözümü değiştiriyoruz.</li>
          </ul>
        </div>
        <div class="pd__blk">
          <h2>Kimlerle çalışıyoruz?</h2>
          <p>Tersaneler, gemi tedarik (ship supply) firmaları, armatörler, liman işletmeleri, pompa ve
            vana servisleri, enerji santralleri, gıda ve kimya tesisleri ile bakım atölyeleri.</p>
        </div>
      </div>
      <div>
        <table class="spec"><caption>Künye</caption><tbody>
          <tr><th scope="row">Firma</th><td>{E(BRAND['name'])}</td></tr>
          <tr><th scope="row">Adres</th><td>{E(BRAND['adres'])}</td></tr>
          <tr><th scope="row">Telefon</th><td>{BRAND['phone_display']}</td></tr>
          <tr><th scope="row">İkinci hat</th><td>{BRAND['phone2_display']}</td></tr>
          <tr><th scope="row">E-posta</th><td>{BRAND['mail']}</td></tr>
          <tr><th scope="row">Ürün grubu</th><td>12 grup, 51 kalem</td></tr>
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


def page_iletisim():
    return f"""{head("İletişim — " + BRAND['short'],
       "Tuzla İstasyon Mahallesi Suyolu Sokak No 3/A. Telefon, WhatsApp ve teklif formu.",
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
        <img src="assets/img/sahne/uyg-tersane.webp" alt="Tuzla tersane bölgesinde havuzdaki gemi"
             loading="lazy" width="1200" height="900">
        <span class="scene__v"><span class="scene__t">Tersanenin içindeyiz</span>
          <span class="scene__d">İstasyon Mahallesi, Tuzla. Stoktaki ürün aynı gün yola çıkar.</span></span>
      </a>
      <a class="scene" href="hakkimizda.html" style="min-height:clamp(230px,26vw,330px)">
        <img src="assets/img/sahne/kurumsal-tezgah.webp" alt="Atölyede levhadan conta kesimi"
             loading="lazy" width="1200" height="900">
        <span class="scene__v"><span class="scene__t">Ölçü yoksa keseriz</span>
          <span class="scene__d">Numuneyi getirin ya da fotoğrafını gönderin, birebir çıkaralım.</span></span>
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
    for p in P:
        total += write(f"urun/{p['slug']}.html", page_urun(p))
    # robots + sitemap
    urls = ["", "urunler.html", "hakkimizda.html", "iletisim.html"] + [f"urun/{p['slug']}.html" for p in P]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          + "".join(f"<url><loc>https://tuzlaconta.com/{u}</loc></url>" for u in urls) + "</urlset>")
    write("sitemap.xml", sm)
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: https://tuzlaconta.com/sitemap.xml\n")
    print(f"{4 + len(P)} sayfa yazıldı, {total//1024} KB")
