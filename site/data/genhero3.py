# -*- coding: utf-8 -*-
"""Hero v3 (Eylül 2026): renksiz (siyah kauçuk, grafit, çelik), her üründen bir tane,
büyük ürünler, patlayıp saçılan hareket.
1) Her ürün için 4 açılı referans sayfası (nano-banana-2, 2K)       ~7 x $0.10
2) Başlangıç karesi: referanslardan toplu kompozisyon (nano-banana-2)   $0.10
3) Video: kwaivgi/kling-v3-omni-video, mode 4k, 5 sn, start_image + 7 referans  $2.10
Kullanım: python3 genhero3.py ref | kare | video"""
import os, sys, time, urllib.request, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genimg as G

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(HERE, "master", "hero3")
os.makedirs(M, exist_ok=True)
URUN = os.path.join(HERE, "master", "urun")

# (anahtar, kaynak ürün görseli, nesne tarifi)
PARCA = [
 ("kedi", "kedi-yuzu-ambar-kapak-lastigi", "a short section of black EPDM cat face hatch cover rubber profile with its pentagonal cross-section and three hollow chambers"),
 ("kose", "kose-lastigi", "one moulded black EPDM 90-degree L-shaped hatch cover corner packing piece with a hollow D-shaped cross-section"),
 ("3s", "3s-ambar-kapak-lastigi", "a short section of black EPDM triple-ridge hatch cover packing profile with a wide flat base and three rounded sealing ridges"),
 ("mekanik", "mekanik-salmastra", "one mechanical shaft seal: a polished stainless steel rotating unit with a coil spring and a black carbon face ring"),
 ("grafit", "saf-grafit-salmastra", "one coil of black braided graphite gland packing rope with a square cross-section and a fine diagonal braid"),
 ("conta", "kaucuk-conta", "one black NBR rubber full-face flange gasket ring with a circle of bolt holes"),
 ("flex", "flex-seal", "a short section of black EPDM flex seal profile: a rounded rectangular body with an oval hollow core"),
]
SHEET = ("Product reference sheet for a 3D artist. Show {obj} four times, left to right, from four different "
 "angles: straight-on view of the front face / cross-section, three-quarter view from the front left, pure side view, "
 "and three-quarter view from behind and above. Exactly the same single object in every view, same scale, evenly "
 "spaced, not touching, all fully inside the frame. Seamless pure black background, no floor, soft cool studio key "
 "light from the upper left and a crisp cool-white rim light, true materials: matte satin black rubber with fine "
 "texture, polished steel, dark graphite. Monochrome neutral grade, no colour accents. Match the attached photo "
 "exactly for shape and material. No text, no labels, no numbers, no arrows, no grid, no watermark.")

FRAME = (
 "Cinematic 16:9 hero still for an industrial rubber and sealing manufacturer, photographic realism, monochrome "
 "palette only: matte black rubber, dark graphite and polished steel on a pure absolute black background. "
 "Exactly seven large objects float weightlessly in mid-air in a loose, dynamic, asymmetric cluster centred slightly "
 "right of the frame centre, each one a different product and each appearing only once: "
 "{items}. The objects are big and fill most of the frame height, at clearly different depths and tilted at varied "
 "angles, slightly overlapping in depth; one is close to the camera and partly cut by the right frame edge; the "
 "left third of the frame is darker with only the edge of one object entering it. The moment just before the "
 "cluster bursts apart. Lighting: crisp cool-white rim lights tracing every edge, a soft key from the upper left, "
 "specular highlights on steel; rubber reads matte black with fine texture. Use the attached reference sheets for "
 "the exact shape of every object from every angle. No colour accents, no red, no green, no gold, no floor, no "
 "horizon, no smoke, no particles, no text, no logos, no watermark.")

MOTION = (
 "One continuous cinematic slow-motion shot, no cuts, pure black background. The floating cluster of sealing "
 "products bursts apart in a powerful, graceful explosion of motion: {refs} fly outward in different directions, "
 "each tumbling and spinning on its own axis so every side of it is revealed, crossing and passing each other at "
 "different depths with strong parallax; the large pieces sweep close past the camera while the camera pushes "
 "forward through the scattering objects. Motion is energetic but smooth and continuous from the first frame to the "
 "last, like a high-speed product commercial. Every object keeps exactly its shape, size and material from the "
 "references; nothing morphs, melts, bends, breaks or multiplies, and no new objects appear. Monochrome: black "
 "rubber, graphite and polished steel only, crisp cool-white rim light. No text, no logos, no smoke, no sparks, "
 "no particles, no floor.")
NEG = ("colour accents, red, green, gold, yellow, text, letters, watermark, logo, smoke, dust, sparks, particles, "
       "floor, horizon, morphing, melting, deforming, duplicated objects, extra objects, flicker, cuts, scene change")


def src(slug):
    j = os.path.join(URUN, slug + ".jpg")
    return j if os.path.exists(j) else os.path.join(G.ROOT, "assets", "img", "urun", slug + ".webp")


def ref():
    G.OUT = M
    jobs = [(f"ref-{k}", SHEET.format(obj=o), src(s)) for k, s, o in PARCA]
    with cf.ThreadPoolExecutor(3) as ex:
        for r in ex.map(lambda j: G.gen(j[0], j[1], ratio="16:9", res="2K", refs=[j[2]], raw=True), jobs):
            print(r, flush=True)


def kare():
    G.OUT = M
    items = "; ".join(o for _, _, o in PARCA)
    refs = [os.path.join(M, f"ref-{k}.jpg") for k, _, _ in PARCA]
    print(G.gen("hero3-kare", FRAME.format(items=items), ratio="16:9", res="2K", refs=refs, raw=True))


def tekrar(f, *a, n=6):
    """Ağ kesintisinde (DNS/zaman aşımı) aynı adımı birkaç kez dener."""
    for t in range(n):
        try:
            return f(*a)
        except Exception as e:
            if t == n - 1:
                raise
            print("  ağ hatası, tekrar:", e, flush=True); time.sleep(8 * (t + 1))


def video():
    # Kling: başlangıç karesi + referanslar toplam en fazla 7 görsel. Flex seal
    # başlangıç karesinde zaten var; referansı ayrıca gönderilmez.
    secili = [k for k, _, _ in PARCA if k != "flex"]
    refs = [tekrar(G.upload, os.path.join(M, f"ref-{k}.jpg")) for k in secili]
    tags = ", ".join(f"<<<image_{i+1}>>>" for i in range(len(secili)))
    p = G.post("https://api.replicate.com/v1/models/kwaivgi/kling-v3-omni-video/predictions", {"input": {
        "prompt": MOTION.format(refs=tags), "negative_prompt": NEG, "mode": "4k", "duration": 5,
        "aspect_ratio": "16:9", "start_image": tekrar(G.upload, os.path.join(M, "hero3-kare.jpg")),
        "reference_images": refs, "generate_audio": False}})
    print("tahmin:", p["id"], p["status"], flush=True)
    open(os.path.join(M, "son-tahmin.txt"), "w").write(p["id"])   # kopunca kaldığı yerden izlemek için
    izle(p)


def izle(p):
    t0 = time.time()
    while p["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(10)
        try:
            p = G.get(p["urls"]["get"])
        except Exception as e:   # ağ kesintisi: tahmin Replicate'te sürüyor, beklemeye devam
            print("  ağ yok, bekleniyor:", e, flush=True); continue
        print(f"  {int(time.time()-t0):>4}s {p['status']}", flush=True)
    if p["status"] != "succeeded":
        print("HATA:", p.get("error")); sys.exit(1)
    out = p["output"]; url = out[0] if isinstance(out, list) else out
    dest = os.path.join(M, "hero3-4k.mp4")
    def indir():
        with urllib.request.urlopen(url, timeout=600) as r, open(dest, "wb") as f:
            f.write(r.read())
    tekrar(indir)
    print("indirildi:", dest, os.path.getsize(dest) // 1024, "KB")


if __name__ == "__main__":
    {"ref": ref, "kare": kare, "video": video}[sys.argv[1]]()
