# -*- coding: utf-8 -*-
"""Hero kare dizisini üretir (scroll ile sürülen canvas için).

  python3 herokare.py <video.mp4> [sürüm] [mobil_merkez_x]

Çıktı: assets/img/hero/<sürüm>/
  d001… : masaüstü, 1920x1080, videonun her karesi
  m001… : dikey telefon, 720x1280, mobil_merkez_x'e (0–1) göre dikey kırpım, her 2. kare
  poster.webp : ilk kare (poster ve og:image)
main.js komşu kareleri kesirli olarak üst üste bindirdiği için bu sayılar yeterli.
Sürüm klasörü build.py'deki HERO_VER ile aynı olmalı."""
import os, sys, glob, shutil, subprocess, tempfile
from PIL import Image

SRC = sys.argv[1]
VER = sys.argv[2] if len(sys.argv) > 2 else "v3"
CX = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img", "hero", VER)
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)

tmp = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vsync", "0", os.path.join(tmp, "%05d.png")], check=True)
fs = sorted(glob.glob(os.path.join(tmp, "*.png")))
nd = nm = 0
for i, f in enumerate(fs):
    im = Image.open(f).convert("RGB")
    w, h = im.size
    if i == 0:
        im.resize((2400, round(h * 2400 / w)), Image.LANCZOS).save(os.path.join(OUT, "poster.webp"), "WEBP", quality=80, method=6)
    nd += 1
    im.resize((1920, round(h * 1920 / w)), Image.LANCZOS).save(os.path.join(OUT, f"d{nd:03d}.webp"), "WEBP", quality=72, method=5)
    if i % 2 == 0:
        nm += 1
        cw = int(h * 9 / 16); cx = min(max(int(w * CX), cw // 2), w - cw // 2)
        im.crop((cx - cw // 2, 0, cx + cw // 2, h)).resize((720, 1280), Image.LANCZOS) \
          .save(os.path.join(OUT, f"m{nm:03d}.webp"), "WEBP", quality=70, method=5)
shutil.rmtree(tmp)
print(f"{VER}: masaüstü {nd} kare, mobil {nm} kare, kaynak {w}x{h}")
