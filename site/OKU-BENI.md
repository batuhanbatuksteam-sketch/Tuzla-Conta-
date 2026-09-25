# Tuzla Conta & Sızdırmazlık — web sitesi

Statik site. Sunucu, veritabanı veya build aracı gerektirmez; `site/` klasörünü
herhangi bir hosting'e (Netlify, Vercel, cPanel, Nginx) olduğu gibi yükleyin.

## Klasörler

```
site/
├── index.html            ana sayfa
├── urunler.html          tüm katalog (14 grup, 60 kalem)
├── kaucuk-silikon.html   kauçuk & silikon özel üretim sayfası
├── hakkimizda.html
├── iletisim.html
├── urun/<slug>.html      60 ürün sayfası — elle düzenlenmez, üretilir
├── sitemap.xml, robots.txt
├── api/
│   ├── teklif-gonder.php teklif formunu e-postaya gönderir (SMTP, PHP)
│   ├── _config.php       SMTP kimlik bilgileri — ASLA tarayıcıya servis edilmez
│   └── .htaccess         "_" ile başlayan dosyalara doğrudan erişimi keser
├── assets/
│   ├── css/main.css      tüm tasarım sistemi + açık/koyu tema tek dosyada
│   ├── js/main.js        açılış, hero scroll, katalog sahnesi, tema, imleç
│   ├── img/logo.svg      dikey logo (orijinal kilit)
│   ├── img/logo-mark.svg TC monogramı
│   ├── img/urun/         60 ürün çekimi (webp)
│   ├── img/sahne/        kategori, kullanım alanı ve kurumsal görseller (webp)
│   ├── img/hero/<sürüm>/ hero kare dizisi (sürüm başına ayrı klasör, bkz. build.py HERO_VER)
│   └── video/            isin-ozu-bg.mp4 ("İşin özü" arka planı)
│                         hero*.mp4 artık kullanılmıyor — silinebilir
└── data/                 KAYNAK — siteyle birlikte yayına ÇIKMAZ
    ├── catalog.py        ürün metinlerinin tek kaynağı
    ├── build.py          sayfaları üretir
    ├── genimg.py         ürün görseli üretimi (Replicate)
    ├── genscene.py       ortam görseli üretimi (Replicate)
    ├── genurun2.py       Eylül 2026 yeni/yenilenen ürün görselleri (referanslı)
    ├── genscene2.py      Eylül 2026 temiz fabrika sahneleri
    ├── genhero2.py       hero v2: başlangıç karesi + LTX-2.3 video
    ├── herokare.py       4K120 asıldan web kare dizisini çıkarır
    ├── olcu-din2576.jpg  müşterinin verdiği PN16 ölçü tablosu (build.py'de DIN2576)
    └── master/           2K ve 4K asıllar, ham ürün/sahne jpg'leri (arşiv, git'e girmez)
```

## İçerik nasıl değiştirilir

Ürün adı, açıklama veya teknik tablo değişecekse **HTML'e dokunmayın**.
`data/catalog.py` içindeki ilgili ürünü düzenleyin, sonra:

```bash
cd site/data && python3 build.py
```

65 sayfa yeniden yazılır; katalogdan çıkarılan ürünün sayfası ve görseli de silinir. Yeni ürün eklemek için aynı dosyada `add(...)` bloğu
kopyalayıp doldurun; kategori, ürün sayfası, katalog listesi ve sitemap kendiliğinden oluşur.

## Tasarım sistemi

| | |
|---|---|
| Lacivert | `#162D63` — logodan birebir alındı |
| Gümüş | `#A6A6A6` — logodan birebir alındı |
| Zemin | `#0A1322` mavi-siyah (nötr siyah değil) |
| Açık zemin | `#EDEFF2` soğuk gri |
| Aksan | `#4E9C7F` — klingrit conta levhasının kendi yeşili, az kullanılır |
| Yazı tipi | Archivo (variable). Başlıklar `wdth 122`, metin `wdth 100` |

Tek yazı ailesi, iki genişlik kullanıldı: başlıkların geniş kesimi logodaki
kare kesimli **T** harfinin geometrisini sürdürür. Aksan rengi süs değil;
gerçek klingrit levhanın rengi olduğu için seçildi ve yalnızca aktif durum,
buton ve vurgu sayısında görünür.

Kontrast: tüm metin/zemin çiftleri WCAG AA (4.5:1) üzerinde ölçüldü.
Klavye odağı görünür, `prefers-reduced-motion` destekleniyor.

## Animasyonlar

**Açılış (yalnızca ana sayfa).** T ile C birbirinden ayrı başlar ve kapanır —
sattığınız işin kendisi. Ardından "TUZLA CONTA" yazısı soldan açılır, tüm kilit
üst bardaki yuvasına uçar (FLIP), açık perde yukarı sıyrılıp hero'yu açar.
Aynı oturumda ikinci kez girildiğinde bekleme süresi kısalır (`sessionStorage`).

**Hero.** Scroll bir videoyu değil, bir **kare dizisini** sürer. İçerik: en çok satan
ürünlerden (köşe lastikleri, kedi yüzü / 3S / lip seal profilleri, mekanik salmastralar,
spiral ve klingrit contalar, o-ringler, silikon profiller) kurulu, siyah boşlukta süzülen
bir spiral; kamera spiralin içine doğru ilerler.

Üretim zinciri (`data/genhero2.py`, `~/tools/video-ai/pipeline_hero2.sh`, `data/herokare.py`):
1. `nano-banana-2` ile başlangıç karesi — güncel ürün görselleri referans verilerek ($0.10)
2. `lightricks/ltx-2.3-pro`, image_to_video, **2K (2560×1440), 6 sn, 50 fps**, dolly_in ($0.96)
3. RIFE v4.6 ile 50 → **120 fps** (732 kare), Real-ESRGAN (realesr-animevideov3 ×2) ile
   5120×2880, Lanczos ile **3840×2160** → `data/master/hero2-4k120-master.mp4`
4. Web kareleri: masaüstü `d001…d183` (1920px, her 4. kare, ~6.9 MB), dikey telefon
   `m001…m122` (720×1280, spiral merkezine göre kırpılmış, her 6. kare, ~2.7 MB)

`main.js` → `hero()` scroll oranını doğrudan kareye çevirmez: gösterilen oran hedefe
kare hızından bağımsız bir yayla yaklaşır ve kare konumu kesirlidir — 12.4. konumda
12. kare tam, 13. kare %40 opaklıkla üstüne çizilir. Böylece 120 Hz ekranda saniyede
120 ara görüntü çizilir; kare sayısı düşük tutulup hareket basamaksız kalır.
Kare sayıları `build.py` tarafından klasörden okunur, HTML'e elle yazılmaz.

Neden video değil: `video.currentTime` ile kare sürmek sunucunun HTTP **Range**
(206 Partial Content) desteğine, codec'e ve tarayıcının seek/autoplay
politikasına bağlıdır. Bunlardan biri eksik olduğunda tarayıcı `seekable`
aralığını `[0,0]` verir, atanan `currentTime` sessizce 0'a döner ve **kare hiç
değişmez**. Kare dizisi bunların hiçbirine bağlı değil. Kaydırma mesafesi 190vh (mobilde 165vh).

Eski `assets/video/hero*.mp4` dosyaları artık kullanılmıyor, silinebilir.

**İşin özü bandı.** "Bütün iş, iki yüzey arasında kalan..." başlığı, çizim ve
dört maddelik liste `isin-ozu-bg.mp4` arka plan videosunun üstünde
(`band--video` sınıfı). Okunabilirlik scrim gradyanına ve çizim/listenin kendi
yarı saydam paneline dayanıyor; scrim bilinçli olarak hafif tutuldu ki videonun
kendi görüntüsü kaybolmasın. Video `autoplay` özniteliğine bırakılmadı —
tarayıcılar ekran dışındaki veya etkileşim görmemiş videoları sessizce
duraklatabildiği için `main.js` → `bgVideos()` görünür alana girince `play()`
çağırır, çıkınca duraklatır.

**Katalog sahnesi (sekmeler).** Scroll ilerledikçe kategori kendiliğinden değişir;
kullanıcı bir başlığa tıkladığı/dokunduğu anda kontrol ona geçer ve otomatik
ilerleme durur — mobilde de aynı tıklama/dokunma davranışı çalışır.

**Tema (açık/koyu).** Üst bardaki düğme `data-theme` özniteliğini `dark`/`light`
arasında değiştirir, `localStorage['tc-theme']`'de saklar, sistem tercihini
(`prefers-color-scheme`) ilk ziyarette esas alır. Açık modda `--ink` neredeyse
siyah lacivertten (`#0A1322`) marka lacivertinden bir tık daha açık dolgun bir
maviye (`#1E3D78`) döner; beyaza yıkanmaz. Yanıp sönmeyi önlemek için tema,
`<head>`'in en başında satır içi bir betikle CSS yüklenmeden önce uygulanır.

**İmleç.** Yalnızca hassas işaretçili cihazlarda (`hover:hover` + `pointer:fine`):
nokta imlecin tam üstünde, halka gevşek bir yayla arkadan takip eder; bağlantı,
buton, kart gibi etkileşimli öğelerin üstünde halka büyür. Dokunmatik cihazlarda
ve `prefers-reduced-motion`'da tamamen devre dışı, native imleç geri döner.

Bunların dışında hareket bilinçli olarak yok.

## Teklif formu

Site Vercel'de; form `/api/teklif-gonder`'e (kökteki `api/teklif-gonder.js`) istek atar,
o da `info@tuzlaconta.com`'a mail gönderir. WhatsApp butonu sunucudan bağımsız, her zaman çalışır.

Canlıda (Eylül 2026) uç nokta ayakta ve origin kontrolünü geçiyor; mailin gitmemesi
gönderim adımında: parolalı SMTP (SMTP AUTH) Microsoft 365 kiracılarında çoğunlukla
kapalıdır ve Microsoft **Aralık 2026 sonunda** varsayılan olarak kapatıyor. Bu yüzden
uç noktaya **Microsoft Graph** yolu eklendi; SMTP yalnızca yedek.

Vercel → Project → Settings → Environment Variables:

| Değişken | Değer |
|---|---|
| `GRAPH_TENANT_ID` | Entra ID → Genel bakış → Kiracı (tenant) kimliği |
| `GRAPH_CLIENT_ID` | Uygulama kaydı → Uygulama (client) kimliği |
| `GRAPH_CLIENT_SECRET` | Uygulama kaydı → Sertifikalar ve gizli anahtarlar → yeni gizli anahtar (değer) |
| `MAIL_FROM` | gönderen kutu — gerçek bir posta kutusu olmalı (grup adresi olmaz): `ahmet.kurtoglu@tuzlaconta.com` |
| `MAIL_TO` | teklifin düşeceği kutu (boşsa `info@tuzlaconta.com`) |
| `KONTROL_ANAHTARI` | rastgele uzun bir metin — sağlık kontrolü için |

Uygulama kaydı: entra.microsoft.com → Uygulama kayıtları → Yeni kayıt → API izinleri →
Microsoft Graph → **Uygulama izinleri** → `Mail.Send` → "Yönetici onayı ver".
(İsteğe bağlı sıkılaştırma: Exchange'de uygulamanın yalnızca `MAIL_FROM` kutusundan
gönderebilmesi için RBAC for Applications / Application Access Policy.)

Değişkenler girilip yeniden deploy edildikten sonra, **mail göndermeden** test:

```
https://www.tuzlaconta.com/api/teklif-gonder?kontrol=<KONTROL_ANAHTARI>
```

`{"ok":true,"yol":"graph","token":"alındı"}` dönerse yapılandırma tamam; hata varsa
`hata` alanı hangi adımda takıldığını söyler. Ardından formdan bir gerçek deneme yapın.

**Mail tasarımı** (`api/_eposta.js`): lacivert başlık, aciliyet etiketi (Bugün lazım
= kırmızı ve "yüksek önem"), istenen ürünün fotoğrafı, DIN 2576 ölçüsü seçildiyse o
satırın beş ölçüsü, müşterinin notu, tek dokunuşla "Hemen ara / WhatsApp'tan yaz"
butonları ve ürünün teknik tablosu. Tablo + satır içi stil ile yazıldı (Outlook masaüstü
dahil aynı görünür); görseller webp değil jpg ve maile gömülü (CID), bu yüzden
"görselleri indir" uyarısına takılmaz. Gönderen ve alıcı aynı kiracıda olduğu için
mail spam filtresine girmez. Mail görselleri ve `api/_katalog.json` her `build.py`
çalıştırmasında katalogdan yeniden üretilir.

Form artık ürün bazında: ürün sayfasındaki "Bu ürün için teklif iste" formu o ürün
seçili açar (`?urun=<slug>`); ölçü tablosu olan contalarda "Standart ölçü (DN)" alanı çıkar.

Gönderen kutu `ahmet.kurtoglu@tuzlaconta.com` (`MAIL_FROM`). `info@tuzlaconta.com`
bir posta kutusu değil, "Tuzla Conta Bilgilendirme" grubunun adresi; Graph grup adına
gönderemez ama gruba teslim eder. Teklifler grubun gelen kutusunda toplanır.

`site/api/teklif-gonder.php` eski PHP hosting sürümüdür; Vercel'de kullanılmaz.

## Alan adı ve barındırma (DNS)

`dig` ile doğrulanan mevcut durum: NS kayıtları `*.bdm.microsoftonline.com`,
yani DNS'in tamamı Microsoft 365 tarafından yönetiliyor; A kaydı `185.124.84.51`'e
gidiyor. WhatsApp'ta paylaşılan Cloudrome talimatı ("isim sunucularını
`cd1/cd2.cloudrome.net`'e çevirin") **olduğu gibi uygulanırsa mevcut çalışan
e-postayı (MX, SPF) kırma riski taşır** — Cloudrome'un DNS panelinde bu kayıtlar
birebir yeniden oluşturulmadan NS değişmemeli.

Daha güvenli yol: NS'i Microsoft'ta bırakıp yalnızca site trafiğini Cloudrome
hosting'e yönlendirmek. admin.microsoft.com → Ayarlar → Etki alanları →
`tuzlaconta.com` → DNS kayıtları üzerinden kök (`@`) A kaydını Cloudrome'un
vereceği hosting IP'sine güncellemek yeterli; MX/SPF hiç dokunulmadığı için
posta kesintisiz çalışmaya devam eder. Cloudrome'dan hosting IP'sini isteyin,
o kayıtla bu adım tamamlanabilir.

## Görseller ve video

Ürün görselleri gerçek ürünlerin araştırılmış tanımlarından yola çıkılarak
tek bir stüdyo reçetesiyle üretildi: dikişsiz koyu grafit fon, sol üstten büyük
softbox, sağ arkadan soğuk kenar ışığı. 51 ürünün tamamı aynı çekimden çıkmış
gibi görünür. Referans olarak jetrubbersolutions.com ve mertin.com.tr ürün
fotoğraflarındaki form ve kadrajlar kullanıldı.

Kaynak modeller ve maliyet:

| İş | Model | Adet | Tutar |
|---|---|---|---|
| Ürün + ortam görselleri | `google/nano-banana-2` (2K) | 87 üretim | ≈ $8.79 |
| Hero videosu (v1, artık kullanılmıyor) | `kwaivgi/kling-v3-video` (mode `4k`, 16:9, 5 sn) | 1 | $2.10 |
| **Eylül 2026 revizyonu** | | | |
| Yeni/yenilenen ürün görselleri + rötuş | `google/nano-banana-2` (2K) | ~21 | ≈ $2.1 |
| Temiz fabrika sahneleri (14 kategori, 4 sektör, kurumsal) | `google/nano-banana-2` (2K) | ~23 | ≈ $2.3 |
| Hero v2 başlangıç karesi + video | `nano-banana-2` + `lightricks/ltx-2.3-pro` (2K, 6 sn) | 2 | ≈ $1.06 |

Softbox sızıntısı: model bazen sol üst köşeye ışık paneli koyuyor. Piksel maskesiyle
harmanlama ince kenar çizgisini bırakıyor ve ürün köşeye taşıyorsa ürünü de yiyor;
bunun yerine `genimg.retouch()` görseli modele "paneli sil, başka hiçbir şeyi değiştirme"
talimatıyla geri veriyor ($0.10). `genimg.leaks()` sızıntılı kareleri bulur.

Görselleri yeniden üretmek için:

```bash
export REPLICATE_API_TOKEN=...
cd site/data
python3 genimg.py                 # eksik ürün görsellerini tamamlar
python3 genimg.py klingrit-conta  # tek ürünü yeniler (önce .webp dosyasını silin)
python3 genscene.py
```

## Bilinmesi gerekenler

- Görseller **yapay zekâ ile üretildi**; gerçek ürün fotoğrafı değildir. Teknik
  olarak doğru olacak şekilde yönlendirildi ve tek tek kontrol edildi, ancak
  elinizde kendi çekimleriniz varsa `assets/img/urun/<slug>.webp` dosyalarını
  aynı isimle değiştirmeniz yeterli (4:3, koyu fon).
- Ürün açıklamaları sektör standartlarına (EN 1092-1, ASME B16.20, DIN 3760,
  IACS) göre yazıldı. Yayına almadan önce firmanın gerçekten stokladığı
  ölçü ve malzeme aralıklarıyla bir kez karşılaştırın.
- `data/` klasörü yayına çıkmamalı. Hosting'e `site/` içindeki html dosyalarını,
  `assets/`, `api/` (teklif formu e-postayı buradan gönderir — atlanmamalı),
  `sitemap.xml` ve `robots.txt` dosyalarını yükleyin. Hosting PHP desteklemiyorsa
  (ör. Netlify/Vercel gibi statik-only servisler) `api/` çalışmaz — bkz. "Teklif formu".
- Canlıya alırken `build.py` içindeki `https://tuzlaconta.com/` adresini
  gerçek alan adıyla doğrulayın (canonical ve sitemap bu adresi kullanıyor).
