# Tuzla Conta & Sızdırmazlık — web sitesi

Statik site. Sunucu, veritabanı veya build aracı gerektirmez; `site/` klasörünü
herhangi bir hosting'e (Netlify, Vercel, cPanel, Nginx) olduğu gibi yükleyin.

## Klasörler

```
site/
├── index.html            ana sayfa
├── urunler.html          tüm katalog (12 grup, 51 kalem)
├── hakkimizda.html
├── iletisim.html
├── urun/<slug>.html      51 ürün sayfası — elle düzenlenmez, üretilir
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
│   ├── img/urun/         51 ürün çekimi (webp)
│   ├── img/sahne/        19 ortam/kategori görseli + 2 video posteri (webp)
│   ├── img/hero-seq/     hero kare dizisi: d001–d154 (masaüstü), m001–m077 (mobil)
│   └── video/            isin-ozu-bg.mp4 ("İşin özü" arka planı)
│                         hero*.mp4 artık kullanılmıyor — silinebilir
└── data/                 KAYNAK — siteyle birlikte yayına ÇIKMAZ
    ├── catalog.py        ürün metinlerinin tek kaynağı
    ├── build.py          sayfaları üretir
    ├── genimg.py         ürün görseli üretimi (Replicate)
    ├── genscene.py       ortam görseli üretimi (Replicate)
    ├── genhero.py        hero videosu üretimi (Replicate)
    └── master/           2K ve 4K asıllar (arşiv)
```

## İçerik nasıl değiştirilir

Ürün adı, açıklama veya teknik tablo değişecekse **HTML'e dokunmayın**.
`data/catalog.py` içindeki ilgili ürünü düzenleyin, sonra:

```bash
cd site/data && python3 build.py
```

55 sayfa yeniden yazılır. Yeni ürün eklemek için aynı dosyada `add(...)` bloğu
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

**Hero.** Scroll bir videoyu değil, bir **kare dizisini** sürer. Kaynak,
precision-turntable çekimidir (Real-ESRGAN ile büyütülüp RIFE ile 24fps'ten
120fps'e ara-kare üretildi, 616 kare). Yayına giden hâli `assets/img/hero-seq/`
içindeki webp kareleridir: masaüstü için `d001…d154` (1600px, ~3.6 MB toplam),
mobil/veri tasarrufu için `m001…m077` (900px, ~0.9 MB). `main.js` → `hero()`
kareleri sırayla arkadan indirir ve scroll oranına düşen kareyi canvas'a çizer.

Neden video değil: `video.currentTime` ile kare sürmek sunucunun HTTP **Range**
(206 Partial Content) desteğine, codec'e ve tarayıcının seek/autoplay
politikasına bağlıdır. Bunlardan biri eksik olduğunda — örneğin `python3 -m
http.server` gibi Range desteklemeyen bir sunucuda — tarayıcı `seekable`
aralığını `[0,0]` verir, atanan `currentTime` sessizce 0'a döner ve **kare hiç
değişmez**. Kare dizisi bunların hiçbirine bağlı değil; her karе sıradan bir
görseldir, her ortamda aynı çalışır. Kaydırma mesafesi 190vh (mobilde 165vh).

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

İki kanal birden çalışır:

1. **WhatsApp (garantili).** Girilen bilgilerle hazırlanmış mesaj WhatsApp'ta
   açılır (`0543 618 38 93`). Müşteri göndermeden önce düzenleyebilir. Bu yol
   hiçbir sunucuya bağlı değildir, her zaman çalışır.
2. **E-posta (en iyi çaba).** Aynı anda `api/teklif-gonder.php`'ye sessizce bir
   istek gider; bu betik `ahmet.kurtoglu@tuzlaconta.com` üzerinden ham SMTP ile
   (Composer/PHPMailer gerekmez) `info@tuzlaconta.com`'a mail atar. Başarısız
   olursa WhatsApp akışını hiçbir şekilde etkilemez — sessizce loglanır
   (`error_log`), kullanıcı fark etmez.

**Neden Office 365?** `dig MX tuzlaconta.com` şu anda
`tuzlaconta-com.mail.protection.outlook.com`'u gösteriyor; alan adı tamamen
Microsoft 365 tarafından yönetiliyor (`NameSpaceType: Managed`, cPanel maili
değil). Bu yüzden `api/_config.php` içinde SMTP sunucusu `smtp.office365.com:587`
olarak ayarlandı, STARTTLS + AUTH LOGIN ile bağlanıyor.

**Test edilmedi — canlıya almadan önce mutlaka deneyin.** Bu betiği yazan ortam,
gerçek şifre içeren bir komutu güvenlik sınıflandırıcısı gereği çalıştıramadı;
yani SMTP girişinin gerçekten kabul edildiği doğrulanmadı. En olası engel:
Microsoft 365 kiracılarında "SMTP AUTH" (temel kimlik doğrulama) artık varsayılan
kapalı geliyor. Test ettiğinizde `535 5.7.139 ... basic authentication is
disabled` gibi bir hata görürseniz:

- M365 admin panelinden (admin.microsoft.com) → Kullanıcılar → Etkin kullanıcılar →
  `ahmet.kurtoglu@tuzlaconta.com` → Posta → "İzinleri yönet" → **SMTP AUTH'u aç**.
- Kiracı genelinde kapalıysa Exchange Admin Center → Posta akışı → Kimlik
  doğrulama ilkeleri üzerinden bu kutuya özel bir istisna eklenmesi gerekir.
- Uzun vadede SMTP AUTH yerine Microsoft Graph API (OAuth2, `Mail.Send` izni)
  kullanmak daha sağlam bir çözümdür; SMTP AUTH herhangi bir noktada kiracı
  genelinde tamamen kapatılabilir.

Test etmek için: siteyi hosting'e yükleyin, formu bir kez gerçek bilgiyle
gönderin, `info@tuzlaconta.com` kutusuna (ve spam klasörüne) bakın. `api/`
klasörüne PHP hata logu erişiminiz varsa `mail_gonderilemedi` dönerse log'daki
`[teklif-gonder] SMTP hata:` satırı tam nedeni söyler.

**Güvenlik — şifreyi değiştirin.** `ahmet.kurtoglu@tuzlaconta.com` şifresi bu
görüşmede WhatsApp ekran görüntüsüyle paylaşıldı ve artık `api/_config.php`
içinde düz metin olarak duruyor (PHP dosyaları sunucu tarafında çalıştığı için
bu normal/yaygın bir pratiktir — dosya tarayıcıya asla gönderilmez, `.htaccess`
da `_` ile başlayan dosyalara erişimi ayrıca reddeder). Yine de bu şifre bir
mesajlaşma uygulamasından geçtiği için M365 admin panelinden **değiştirilmesi**
ve `_config.php`'nin yeni şifreyle güncellenmesi önerilir. Barındırma sağlayıcı
değişirse veya PHP desteklenmiyorsa, aynı `quote()` fonksiyonunu (`assets/js/main.js`)
Formspree/Netlify Forms gibi bir servise bağlamak da bir alternatiftir.

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
| Hero videosu | `kwaivgi/kling-v3-video` (mode `4k`, 16:9, 5 sn) | 1 | $2.10 |

Video 3856×2148 olarak üretildi; asıl dosya `data/master/hero-4k-master.mp4`
içinde duruyor. Yayına giden sürümler bundan küçültüldü.

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
