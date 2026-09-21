# Hero videosu — üretim talimatı

Amaç: saf siyah zeminde, tertemiz, tek hareketli, kusursuz bir stüdyo çekimi.
Video **oynatılmayacak**, scroll ile kare kare sürülecek. Bu yüzden hareket ne kadar
yavaş, tekdüze ve kesintisiz olursa o kadar iyi olur. Karmaşık hareket = bozulma.

---

## 1. Referans kare seç

Dördü de hazır: `site/data/hero-adayi/` — hepsi **2560×1440 (16:9), zemin mutlak siyah**,
ürün sağ üçte birde, sol yarı başlık için boş.

| Dosya | Ürün | Not |
|---|---|---|
| `aday-1-spiral.jpg` | Spiral sarımlı conta | **Önerilen.** Katalogdaki en çarpıcı parça; altın halka + çelik sarım siyahta mücevher gibi duruyor. Dönerken ışığı en iyi bu tutar. |
| `aday-2-mekanik.jpg` | Mekanik salmastra | İki parça ayrı duruyor; "kapanma" hareketi için tek uygun aday. |
| `aday-3-klingrit.jpg` | Klingrit conta | Marka aksan yeşiliyle birebir aynı renk. En "conta" duran kare. |
| `aday-4-teflon.jpg` | PTFE conta | Beyaz üzeri siyah, en yüksek kontrast. En grafik, en sade. |

---

## 2. Model ve ayarlar

Replicate → **`kwaivgi/kling-v3-video`**

| Alan | Değer |
|---|---|
| `mode` | `4k` |
| `aspect_ratio` | `16:9` |
| `duration` | `5` |
| `start_image` | Seçtiğiniz aday dosyası |
| `generate_audio` | kapalı (`false`) |
| `prompt` | Aşağıdaki A veya B |
| `negative_prompt` | Aşağıdaki ortak liste |

Maliyet: 4k modunda saniyesi **$0.42** → 5 sn = **$2.10**.
Scroll için 5 saniye fazlasıyla yeter; hareket 300vh'lik alana yayılıyor.

> Hesapta şu an kredi yok (`402 Insufficient credit`).
> replicate.com/account/billing üzerinden yükledikten birkaç dakika sonra çalışır.

---

## PROMPT A — dönüş (önerilen)

`aday-1`, `aday-3` veya `aday-4` ile kullanın. Scroll aşağı indikçe parça kendi
ekseninde dönüyormuş gibi olur. En sağlam, en az bozulma üreten hareket budur.

```
A single continuous locked-off studio shot on a pure absolute black background, no cuts.
The object rotates slowly and smoothly around its own vertical axis, one steady constant-speed
turn from the first frame to the last, like a part on a precision turntable. The camera itself
stays completely still: no pan, no tilt, no zoom, no handheld shake.
A narrow cold blue-white specular highlight travels cleanly across the machined surfaces as the
object turns, revealing one contour after another.
The object stays in the right third of the frame for the entire shot and never drifts left.
The left half of the frame stays empty pure black from start to finish.
The object is factory-new and flawless throughout: no rust, no dirt, no oil, no scratches, no wear,
no patina. Its shape, proportions and material stay exactly the same in every frame.
Nothing else ever enters the frame: no smoke, no dust, no particles, no sparks, no lens flare,
no floor, no horizon, no background element.
Cinematic macro product film, cool neutral colour grade, true deep black, high dynamic range.
```

---

## PROMPT B — kapanış

Yalnızca **`aday-2-mekanik.jpg`** ile kullanın. Öndeki siyah karşı halka yavaşça
arkadaki parlak gövdenin üzerine kapanır — sızdırmazlığın kurulduğu anın kendisi.
Daha anlamlı ama modelin bozma ihtimali A'ya göre biraz yüksek.

```
A single continuous locked-off studio shot on a pure absolute black background, no cuts.
The black seal ring in front drifts slowly and evenly towards the polished steel seal body behind
it and closes onto it, until the two parts meet face to face as one assembled unit in the final
frame. The movement is smooth, linear and unhurried along a single axis from the first frame to
the last. The camera itself stays completely still: no pan, no tilt, no zoom, no handheld shake.
A narrow cold blue-white specular highlight tightens along the closing seam as the two faces meet.
The parts stay in the right third of the frame for the entire shot and never drift left.
The left half of the frame stays empty pure black from start to finish.
Both parts are factory-new and flawless: no rust, no dirt, no oil, no scratches, no wear.
Shapes and proportions stay exactly the same in every frame; nothing bends, melts or deforms.
Nothing else ever enters the frame: no smoke, no dust, no particles, no sparks, no lens flare,
no floor, no horizon, no background element.
Cinematic macro product film, cool neutral colour grade, true deep black, high dynamic range.
```

---

## NEGATIVE PROMPT (ikisinde de aynı)

```
text, letters, numbers, watermark, logo, subtitles, people, hands, fingers,
rust, dirt, oil, grime, scratches, scuffs, wear, patina, corrosion, weathering,
dust, smoke, steam, particles, sparks, embers, lens flare, glare, bokeh balls,
floor, table, horizon line, wall, grey background, gradient background, vignette edges,
camera shake, handheld, fast motion, speed ramp, cuts, scene change, jump cut,
morphing, warping, melting, bending, deforming, duplicated parts, extra objects,
appearing objects, disappearing objects, distortion, cartoon, illustration, 3d render look,
oversaturated colours, warm orange grade
```

---

## 3. Bana getirin

`.mp4` dosyasını olduğu gibi gönderin, gerisini ben yaparım:

- 4K asıl `data/master/` içine arşivlenir
- Scroll için her karesi anahtar kare olacak şekilde yeniden kodlanır (`-g 1`)
- Masaüstü 2K, mobil 1280 sürümleri çıkarılır
- İlk kare hero poster görseli olur, hero'nun scrim'i saf siyah zemine göre ayarlanır

Beğenmezseniz prompt'un tek satırını değiştirip tekrar üretmek yeterli;
sitede elle hiçbir şey değiştirmeye gerek yok.
