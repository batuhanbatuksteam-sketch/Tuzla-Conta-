# -*- coding: utf-8 -*-
"""Hero kare dizisini üretir (scroll ile sürülen canvas için).
Kaynak: pipeline_hero2.sh çıktısı — RIFE ile 120 fps'e çıkarılıp Real-ESRGAN ile
5120x2880'e büyütülmüş PNG kareler (732 adet).
  d001… : masaüstü, 1920x1080, her 4. kare
  m001… : dikey telefon, 720x1280, spiral merkezine (x=%62) göre dikey kırpım, her 6. kare
main.js komşu kareleri kesirli olarak üst üste bindirdiği için bu sayılar yeterli."""
import os, sys, glob
from PIL import Image
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/tools/video-ai/work/hero2/up")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "img", "hero-seq")
CX = 0.62
fs = sorted(glob.glob(os.path.join(SRC, "*.png")))
for f in glob.glob(os.path.join(OUT, "*.webp")):
    os.remove(f)
os.makedirs(OUT, exist_ok=True)
nd = nm = 0
for i, f in enumerate(fs):
    if i % 4 and i % 6 and i != len(fs) - 1:
        continue
    im = Image.open(f).convert("RGB")
    w, h = im.size
    if i % 4 == 0:
        nd += 1
        im.resize((1920, 1080), Image.LANCZOS).save(os.path.join(OUT, f"d{nd:03d}.webp"), "WEBP", quality=70, method=5)
    if i % 6 == 0:
        nm += 1
        cw = int(h * 9 / 16); cx = int(w * CX)
        im.crop((cx - cw // 2, 0, cx + cw // 2, h)).resize((720, 1280), Image.LANCZOS) \
          .save(os.path.join(OUT, f"m{nm:03d}.webp"), "WEBP", quality=68, method=5)
print(f"masaüstü {nd} kare, mobil {nm} kare")
