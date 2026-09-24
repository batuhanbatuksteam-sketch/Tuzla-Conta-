# -*- coding: utf-8 -*-
"""Eylül 2026 revizyonu: yeni/yenilenen ürün görselleri.
Referanslı olanlarda referans yalnızca form içindir; çekim ortak stüdyo reçetesiyle yapılır.
Kullanım: REF=<referans klasörü> python3 genurun2.py [slug ...]"""
import os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genimg as G, catalog

REF = os.environ.get("REF", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref"))
R = lambda *n: [os.path.join(REF, x) for x in n]
FORM = ("Use the attached reference photos only to copy the exact real-world shape, proportions and "
        "cross-section of the product. Ignore their white background, framing, logos and watermarks; "
        "re-photograph the product from scratch in the studio set-up described below")

REFS = {
 "kedi-yuzu-ambar-kapak-lastigi": R("2fd55cat-face-rubber-2.jpg", "36346cat-face-rubber-3.jpg"),
 "lip-seal": R("06536lip-seal-2.jpg"),
 "flex-seal": R("6467fflex-seal.jpg"),
 "epdm-sunger-profil": R("49a28epdm-sponge-profile-1.jpg", "6816depdm-sponge-profile-2.jpg"),
 "kose-lastigi": R("clean_gefa_0bda7gemi_ambar_kapak_kose_lastikleri_2-gefa-akl-kl-04-.jpg",
                   "clean_gefa_f571dgemi_ambar_kapak_kose_lastikleri_1-gefa-akl-kl-07-.jpg",
                   "clean_gefa_f6dc3gemi_ambar_kapak_lastigi-kose-gefa-akl-kl-18.jpg", "c01a8hatch-cover-rubber-corner-packing-2.jpg"),
}
URUN = os.path.join(G.ROOT, "assets", "img", "urun")
MANTAR = ("Edit this studio product photograph. Remove the translucent amber-orange polyurethane plate "
          "(the rightmost, see-through sheet) completely, together with its reflection. Keep the other three "
          "sheets exactly as they are (tan cork sheet, black fabric-textured sheet, rust-orange sheet) and move "
          "the fanned group so it sits centred horizontally and vertically in the frame with balanced empty "
          "backdrop on both sides. Keep the identical dark graphite seamless backdrop, lighting, camera angle, "
          "colour grade and resolution. Do not add anything. " + G.RECIPE)

def job(slug):
    if slug == "mantar-levha":
        return G.gen(slug, MANTAR, refs=[os.path.join(URUN, "mantar-levha.webp")], raw=True)
    p = next(x for x in catalog.P if x["slug"] == slug)
    refs = [r for r in REFS.get(slug, []) if os.path.exists(r)]
    obj = p["gorsel"] + (". " + FORM if refs else "")
    return G.gen(slug, obj, refs=refs)

if __name__ == "__main__":
    for slug, st, sz in cf.ThreadPoolExecutor(3).map(job, sys.argv[1:]):
        print(f"{slug:34} {st} {sz//1024 if sz else ''}", flush=True)
