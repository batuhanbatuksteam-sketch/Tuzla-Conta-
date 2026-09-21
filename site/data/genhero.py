# -*- coding: utf-8 -*-
"""Hero videosu: Kling v3 (mode=4k, 16:9, 5 sn). Başlangıç karesi hero-frame.jpg.
Maliyet: 5 sn x $0.42 = $2.10."""
import json, os, sys, time, mimetypes, uuid, urllib.request

TOKEN = os.environ["REPLICATE_API_TOKEN"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "img", "sahne", "hero-frame.jpg")
OUT = os.path.join(ROOT, "assets", "video")
os.makedirs(OUT, exist_ok=True)

PROMPT = (
 "One single continuous locked cinematic shot, no cuts. Extremely slow camera push-in along the "
 "seam between two heavy machined steel flange faces. The two steel faces drift almost "
 "imperceptibly closer and compress the dark green gasket ring held between them. A cold "
 "blue-white specular highlight travels slowly along the polished steel edge as the camera moves. "
 "Fine metal dust and a faint haze drift through the light. Shallow depth of field, deep black "
 "background, cold industrial colour grade, heavy material realism with oil film and machining marks."
)
NEG = ("text, letters, numbers, watermark, logo, subtitles, people, hands, fast motion, camera shake, "
       "cuts, scene change, zoom flicker, warping, morphing, cartoon, oversaturated colours")


def api(path, payload=None, method=None, hdrs=None):
    h = {"Authorization": f"Bearer {TOKEN}"}
    data = None
    if payload is not None:
        h["Content-Type"] = "application/json"; data = json.dumps(payload).encode()
    h.update(hdrs or {})
    req = urllib.request.Request("https://api.replicate.com/v1/" + path, data, h, method=method)
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def upload(path):
    """Replicate files API'ye multipart yükleme."""
    b = str(uuid.uuid4())
    name = os.path.basename(path)
    ct = mimetypes.guess_type(name)[0] or "application/octet-stream"
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"content\"; filename=\"{name}\"\r\n"
            f"Content-Type: {ct}\r\n\r\n").encode() + open(path, "rb").read() + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request("https://api.replicate.com/v1/files", body,
        {"Authorization": f"Bearer {TOKEN}", "Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["urls"]["get"]


if __name__ == "__main__":
    dest = os.path.join(OUT, "hero-4k.mp4")
    if os.path.exists(dest) and os.path.getsize(dest) > 200000:
        print("video zaten var, atlandı"); sys.exit(0)
    url = upload(SRC)
    print("başlangıç karesi yüklendi:", url)
    p = api("models/kwaivgi/kling-v3-video/predictions", {"input": {
        "prompt": PROMPT, "negative_prompt": NEG, "mode": "4k",
        "duration": 5, "aspect_ratio": "16:9",
        "start_image": url, "generate_audio": False}})
    print("tahmin:", p["id"], p["status"])
    t0 = time.time()
    while p["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(10)
        p = api("predictions/" + p["id"])
        print(f"  {int(time.time()-t0):>4}s {p['status']}", flush=True)
    if p["status"] != "succeeded":
        print("HATA:", p.get("error")); sys.exit(1)
    out = p["output"]; vurl = out[0] if isinstance(out, list) else out
    with urllib.request.urlopen(vurl, timeout=600) as r, open(dest, "wb") as f:
        f.write(r.read())
    print("indirildi:", dest, os.path.getsize(dest) // 1024, "KB")
