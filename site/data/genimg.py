# -*- coding: utf-8 -*-
"""Replicate ile ürün görseli üretir. Tekrar çalıştırılabilir: var olan dosyayı atlar."""
import json, os, sys, time, random, threading, mimetypes, uuid, urllib.request, urllib.error, concurrent.futures as cf

TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
MODEL = "google/nano-banana-2"
_gate = threading.Semaphore(3)
_lock = threading.Lock()
_last = [0.0]
MIN_GAP = 1.6   # istekler arası en az bu kadar saniye
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img", "urun")
os.makedirs(OUT, exist_ok=True)

# Tüm katalogda tek bir çekim kimliği kuran ortak ışık/zemin reçetesi
RECIPE = (
 "Professional studio product photograph for an industrial sealing catalogue. "
 "Seamless dark graphite backdrop (#181c22) falling off to near-black at the edges. "
 "One large softbox key light from the upper left, a cool blue-white rim light from the right rear, "
 "soft bounce fill from below. The object rests on a dark matte surface with a faint short reflection. "
 "85mm lens look, three-quarter view, tack-sharp macro detail, true material texture and honest wear, "
 "moderate depth of field, neutral cool colour grade, high dynamic range. "
 "The background is a perfectly clean seamless gradient with no visible wall-to-floor corner line. "
 "Absolutely no text, no lettering, no numbers, no logos, no watermarks, no hands, no people, "
 "no props and no background objects. Every corner of the frame is dark and empty background: "
 "no softbox, no light panel, no reflector, no bright shape and no white area may appear anywhere in the frame "
 "except on the product itself. The lighting comes from outside the frame."
)

def post(url, payload, hdrs=None):
    h = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    h.update(hdrs or {})
    req = urllib.request.Request(url, json.dumps(payload).encode(), h)
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)

def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

def _throttle():
    with _lock:
        w = MIN_GAP - (time.time() - _last[0])
        if w > 0: time.sleep(w)
        _last[0] = time.time()


def upload(path):
    """Referans görseli Replicate files API'ye yükler, kalıcı URL döndürür."""
    b = str(uuid.uuid4())
    name = os.path.basename(path)
    ct = mimetypes.guess_type(name)[0] or "application/octet-stream"
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"content\"; filename=\"{name}\"\r\n"
            f"Content-Type: {ct}\r\n\r\n").encode() + open(path, "rb").read() + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request("https://api.replicate.com/v1/files", body,
        {"Authorization": f"Bearer {TOKEN}", "Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["urls"]["get"]


def gen(slug, obj, ratio="4:3", res="2K", tries=6, refs=(), raw=False):
    """refs: yerel referans görsel yolları (ürünün gerçek formu için).
    raw=True: istem ortak reçeteye eklenmeden olduğu gibi gider (düzenleme işleri)."""
    dest = os.path.join(OUT, slug + ".jpg")
    if os.path.exists(dest) and os.path.getsize(dest) > 40000:
        return slug, "atlandi", 0
    prompt = obj if raw else f"{obj}. {RECIPE}"
    inp = {"prompt": prompt, "resolution": res, "aspect_ratio": ratio, "output_format": "jpg"}
    if refs:
        inp["image_input"] = [upload(r) for r in refs]
    for t in range(tries):
        try:
            _throttle()
            p = post(f"https://api.replicate.com/v1/models/{MODEL}/predictions",
                     {"input": inp}, {"Prefer": "wait=60"})
            for _ in range(90):
                if p["status"] in ("succeeded", "failed", "canceled"):
                    break
                time.sleep(3); p = get(p["urls"]["get"])
            if p["status"] != "succeeded":
                raise RuntimeError(p.get("error") or p["status"])
            out = p["output"]
            url = out[0] if isinstance(out, list) else out
            with urllib.request.urlopen(url, timeout=180) as r, open(dest, "wb") as f:
                f.write(r.read())
            return slug, "ok", os.path.getsize(dest)
        except Exception as e:
            if t == tries - 1:
                return slug, f"HATA {e}", 0
            # 429'da giderek artan bekleme
            time.sleep(min(90, (5 * (2 ** t)) + random.uniform(0, 3)))


RETOUCH = ("Retouch this studio product photograph. In the upper-left corner there is a visible studio softbox / "
   "light panel and its bright edge. Remove it completely and continue the seamless dark graphite backdrop there with "
   "the same smooth falloff as the rest of the background, so that corner is dark and empty. Change nothing else: keep "
   "the products, their position, shape, materials, reflections, lighting, colours, framing and resolution exactly identical.")


def leaks(jpg):
    """Sol üst köşede zeminden belirgin parlak bir alan (softbox sızıntısı) var mı?"""
    from PIL import Image, ImageStat
    g = Image.open(jpg).convert("L")
    w, h = g.size
    corner = g.crop((0, 0, int(w * .3), int(h * .3)))
    return ImageStat.Stat(corner).extrema[0][1] > ImageStat.Stat(g).median[0] + 90


def retouch(slug, jpg):
    """Sızıntıyı modelin kendisine sildirir. Piksel maskesiyle harmanlama denendi:
    softbox'ın ince kenar çizgisi kalıyor, ürün köşeye taşıyorsa ürünü de yiyor."""
    return gen(slug, RETOUCH, refs=[jpg], raw=True)


def finish(jpg, webp, width=1400):
    """Üretilen jpg'yi yayın webp'sine çevirir."""
    from PIL import Image
    im = Image.open(jpg).convert("RGB")
    if width and im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(webp, "WEBP", quality=84, method=6)
    return webp


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import catalog
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    jobs = [(p["slug"], p["gorsel"]) for p in catalog.P if not only or p["slug"] in only]
    print(f"{len(jobs)} görsel kuyrukta")
    done = 0
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for slug, st, sz in ex.map(lambda a: gen(*a), jobs):
            done += 1
            print(f"[{done}/{len(jobs)}] {slug:32} {st} {sz//1024 if sz else ''}", flush=True)
