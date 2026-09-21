# -*- coding: utf-8 -*-
"""Replicate ile ürün görseli üretir. Tekrar çalıştırılabilir: var olan dosyayı atlar."""
import json, os, sys, time, random, threading, urllib.request, urllib.error, concurrent.futures as cf

TOKEN = os.environ["REPLICATE_API_TOKEN"]
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


def gen(slug, obj, ratio="4:3", res="2K", tries=6):
    dest = os.path.join(OUT, slug + ".jpg")
    if os.path.exists(dest) and os.path.getsize(dest) > 40000:
        return slug, "atlandi", 0
    prompt = f"{obj}. {RECIPE}"
    for t in range(tries):
        try:
            _throttle()
            p = post(f"https://api.replicate.com/v1/models/{MODEL}/predictions",
                     {"input": {"prompt": prompt, "resolution": res,
                                "aspect_ratio": ratio, "output_format": "jpg"}},
                     {"Prefer": "wait=60"})
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
