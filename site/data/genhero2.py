# -*- coding: utf-8 -*-
"""Hero v2 (Eylül 2026): en çok satan ürünlerden kurulu hipnotik spiral.
1) nano-banana-2 ile başlangıç karesi — güncel ürün görselleri referans verilir
2) LTX-2.3-pro image_to_video, 2K, 6 sn, 50 fps, dolly_in  ($0.16/sn -> $0.96)
Kullanım: python3 genhero2.py kare | python3 genhero2.py video"""
import os, sys, time, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genimg as G

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, "master")
URUN = os.path.join(G.ROOT, "assets", "img", "urun")
REFS = ["kedi-yuzu-ambar-kapak-lastigi", "kose-lastigi", "3s-ambar-kapak-lastigi", "lip-seal",
        "mekanik-salmastra", "spiral-sarimli-conta", "klingrit-conta", "nitril-oring",
        "flex-seal", "kaucuk-conta", "viton-conta", "silikon-parcalar"]

FRAME = (
 "Cinematic 16:9 hero still for an industrial sealing and rubber products manufacturer. "
 "A hypnotic spiral vortex of floating sealing products suspended weightlessly in a pure absolute black void. "
 "Use the attached product photos only for the exact real shapes, cross-sections and materials of the parts: "
 "moulded black EPDM hatch cover corner pieces, short sections of cat face, triple-ridge and lip seal hatch cover "
 "rubber profiles, flex seal profile sections, polished stainless mechanical shaft seals, spiral wound gaskets with "
 "gold outer rings, pale green fibre flange gaskets, black and brown rubber flange gaskets with bolt holes, "
 "black and brown O-rings and a few red silicone profile pieces. "
 "About thirty parts are arranged along one smooth logarithmic spiral that curls inward and recedes into depth toward "
 "a vanishing point located slightly right of the frame centre: the largest parts are close to the camera near the frame "
 "edges, progressively smaller parts spiral inward toward the centre, each tilted at a different angle, evenly spaced "
 "with clear black gaps, nothing touching, nothing cut in half by another part. The left third of the frame is darker "
 "and sparser so a headline can sit there. "
 "Lighting: crisp cool blue-white rim lights outlining every edge against the black, a soft key light from the upper "
 "left, gentle specular highlights on steel and glossy rubber; rubber reads as matte satin black with fine texture. "
 "Subtle depth of field: foreground and mid parts tack sharp, the deepest parts at the vortex centre softly defocused. "
 "Photographic realism like a high-end commercial studio composite, factory-new clean parts. "
 "Pure black background everywhere, no floor, no horizon, no smoke, no particles, no lens flare, no text, no logos, "
 "no watermark, no people, no hands.")

MOTION = (
 "One continuous slow cinematic shot, no cuts. The camera glides forward smoothly at a constant speed into the spiral "
 "vortex of floating sealing parts, travelling toward the vanishing point. As it advances, the whole spiral turns "
 "slowly and steadily clockwise around its centre, and every part rotates gently around its own axis, catching "
 "travelling cool rim highlights on its edges. Parts drift past the camera at the frame edges with natural parallax. "
 "Hypnotic, calm, weightless, perfectly smooth motion. Every part keeps exactly the same shape, size and material in "
 "every frame; nothing morphs, melts, bends, merges or multiplies, and no new objects appear. Pure black background, "
 "no text, no logos, no particles, no smoke, no flicker.")


def frame():
    G.OUT = MASTER
    refs = [os.path.join(HERE, "master", "urun", s + ".jpg") if os.path.exists(os.path.join(HERE, "master", "urun", s + ".jpg"))
            else os.path.join(URUN, s + ".webp") for s in REFS]
    print(G.gen("hero2-frame", FRAME, ratio="16:9", res="2K", refs=refs, raw=True))


def video():
    src = os.path.join(MASTER, "hero2-frame.jpg")
    url = G.upload(src)
    p = G.post("https://api.replicate.com/v1/models/lightricks/ltx-2.3-pro/predictions", {"input": {
        "task": "image_to_video", "image": url, "prompt": MOTION, "resolution": "2k",
        "duration": 6, "fps": 50, "aspect_ratio": "16:9", "camera_motion": "dolly_in",
        "generate_audio": False}})
    print("tahmin:", p["id"], p["status"], flush=True)
    t0 = time.time()
    while p["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(8); p = G.get(p["urls"]["get"])
        print(f"  {int(time.time()-t0):>4}s {p['status']}", flush=True)
    if p["status"] != "succeeded":
        print("HATA:", p.get("error")); sys.exit(1)
    out = p["output"]; vurl = out[0] if isinstance(out, list) else out
    dest = os.path.join(MASTER, "hero2-2k.mp4")
    with urllib.request.urlopen(vurl, timeout=600) as r, open(dest, "wb") as f:
        f.write(r.read())
    print("indirildi:", dest, os.path.getsize(dest) // 1024, "KB")


if __name__ == "__main__":
    {"kare": frame, "video": video}[sys.argv[1]]()
