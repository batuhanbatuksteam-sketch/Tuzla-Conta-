# -*- coding: utf-8 -*-
"""Eylül 2026 revizyonu: kategori ve kullanım sahneleri.
Eski sahneler karanlık, yağlı tersane/makine dairesi havasındaydı. Müşteri talebi:
nizami, temiz, fabrika yüzeyi, stüdyo ışığı. Yapaylığa kaçmaması için istemde gerçek
çekim parametreleri, malzeme dokusu ve fiziksel tutarlılık açıkça tarif ediliyor."""
import os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genimg as G

G.OUT = os.path.join(G.ROOT, "assets", "img", "sahne")

# ürün odaklı kategori kareleri
PRODUCT = (
 "Premium commercial photograph for a modern industrial rubber and sealing manufacturer's brochure, in the style of "
 "leading European sealing brands. Clean, orderly, modern factory setting: the products are neatly arranged in tidy, "
 "evenly spaced rows or neat stacks on a clean matte light-grey powder-coated steel work surface; behind them a spotless "
 "modern production hall falls softly out of focus — light grey walls, polished light-grey epoxy floor, tidy machines, "
 "cool LED high-bay lighting. Studio-quality lighting on the products: a large soft key light, gentle fill and a subtle "
 "rim light; neutral cool-white balance, true-to-life colours, medium-key exposure. Full-frame camera, 50mm lens at f/4, "
 "products tack sharp, background in smooth bokeh. Realistic materials with genuine fine detail: satin rubber with subtle "
 "mould parting lines, machined metal with fine tool marks. Factory-new clean parts: no dirt, no rust, no oil, no grime, "
 "no clutter, no worn surfaces. Physically plausible scale, contact shadows and reflections. All machines and equipment "
 "are unbranded with plain painted panels: absolutely no lettering, brand names, stickers, screens with text or numbers "
 "anywhere in the frame. No people, no hands, no text, "
 "no labels, no signage, no logos, no watermarks. Not CGI, not a 3D render, no plastic look, no oversaturation, no HDR halos.")

# mekân odaklı kullanım kareleri
PLACE = (
 "Architectural industrial photograph for a modern manufacturer's brochure. A spotless, bright, orderly modern plant "
 "interior: clean painted equipment, colour-coded pipework, polished light-grey epoxy floor, even cool LED lighting mixed "
 "with soft daylight from high windows, everything tidy and well maintained. Full-frame camera, 24-35mm lens at f/5.6, "
 "straight verticals, natural perspective, true-to-life colours, medium-key exposure with gentle contrast. Factory-new "
 "clean surfaces: no dirt, no rust, no oil stains, no grime, no clutter. All equipment is unbranded: absolutely no lettering, "
 "brand names, stickers or numbers anywhere. No people, no text, no readable signage, no logos, "
 "no watermarks. Not CGI, not a 3D render, no oversaturation, no HDR halos.")

S = {
 # --- kategori (ana sayfa sahnesi, 12+2)
 "kat-ambar-kapak": (PRODUCT, "Several short sections of black EPDM ship hatch cover rubber profiles stand upright in a neat row with their cut ends facing the camera, showing their cross-sections: a cat face profile with three hollow chambers, a lip seal with an oval hollow, a triple-ridge profile, a flex seal with an oval core; beside them two moulded L-shaped corner pieces and a neat coil of long profile, in a clean rubber extrusion plant"),
 "kat-mekanik-salmastralar": (PRODUCT, "A neat row of polished stainless steel mechanical shaft seals of increasing size with visible springs and black carbon faces, each paired with its mirror-polished seat ring, lined up on the work surface of a clean pump assembly plant"),
 "kat-contalar": (PRODUCT, "Neat stacks of new flange gaskets: pale green compressed fibre gaskets with bolt holes, spiral wound gaskets with yellow outer rings, white PTFE gaskets and black rubber gaskets, arranged in tidy groups next to a modern CNC gasket cutting table with a large green gasket sheet on it"),
 "kat-levhalar": (PRODUCT, "Neatly rolled and stacked technical sheet materials: rolls of black rubber sheet standing on end, a stack of pale green fibre gasket sheets, white PTFE sheets and a red silicone sheet, with one sheet laid flat showing a cleanly cut gasket ring lifted from it"),
 "kat-yumusak-salmastralar": (PRODUCT, "Neat coils of braided gland packing rope in white PTFE, black graphite, off-white glass fibre and tan oil-impregnated fibre, each coil wound tidily with a cut end showing its square cross-section, arranged in a row"),
 "kat-oringler": (PRODUCT, "Rubber O-rings of many sizes sorted in neat concentric groups and straight rows by material: black NBR, brown Viton, green and red silicone, lying flat on the clean surface, with an open compartmented O-ring case behind them"),
 "kat-keceler": (PRODUCT, "Rotary shaft oil seals of several diameters arranged in a tidy diagonal row, black rubber lips with springs and metal-cased outer diameters, a couple standing on edge to show the lip profile, beside a clean machined steel shaft"),
 "kat-kaplinler": (PRODUCT, "Jaw couplings with machined aluminium hubs and red, yellow and black star-shaped elastomer spiders neatly arranged in pairs, with a clean new electric motor and pump set on a painted base frame softly out of focus behind"),
 "kat-takozlar": (PRODUCT, "Anti-vibration rubber mounts neatly arranged in a grid: cylindrical black rubber mounts bonded to zinc-plated steel plates with threaded studs, square rubber pads and rubber buffers of different sizes"),
 "kat-flanslar": (PRODUCT, "Clean new steel pipe flanges of different diameters in tidy stacks and a neat row standing on edge: slip-on flanges, a weld neck flange, a blind flange and galvanised threaded flanges, machined faces with fine concentric grooves, in a clean modern warehouse"),
 "kat-setler": (PRODUCT, "Three open service kit cases on the work surface, each with neatly labelled-looking compartments without readable text: copper and aluminium sealing washers sorted by size, brown Viton O-rings sorted by size and black NBR O-rings sorted by size"),
 "kat-el-aletleri": (PRODUCT, "Two-arm forged steel gear pullers of three sizes with central forcing screws laid out in a neat row on the work surface next to a clean wall-mounted tool board, a bearing on a machined shaft beside them"),
 "kat-ozel-kaucuk": (PRODUCT, "A tray of freshly moulded custom black rubber parts in tidy rows — bellows boots, flanged bushings, stepped plugs, rubber-to-metal bonded mounts and a few red silicone parts — next to a modern hydraulic rubber moulding press with an open heated steel mould softly out of focus"),
 "kat-ozel-conta": (PRODUCT, "Custom-made gaskets neatly arranged in groups: a large rectangular vulcanised black rubber frame gasket, red silicone door gaskets, white PTFE rings with bolt holes and green fibre gaskets of unusual shapes, next to a modern flatbed CNC oscillating-knife cutting machine"),
 # --- kullanım alanları (fabrika ağırlıklı)
 "uyg-fabrika": (PLACE, "A modern automated production hall with long clean process lines, painted steel machine frames, stainless piping and flanged connections running along the lines"),
 "uyg-gida": (PLACE, "A hygienic food and beverage processing plant: rows of polished stainless steel tanks, sanitary pipework with clamp connections and valves, white walls and a clean light floor"),
 "uyg-pompa": (PLACE, "A clean modern pump room: a row of freshly painted blue centrifugal pumps coupled to electric motors on concrete plinths, suction and discharge pipework with bolted flange joints and valves"),
 "uyg-esanjor": (PLACE, "A clean energy and process plant room: a large stainless plate heat exchanger with its plate pack clamped between tie bars, insulated pipework and flanged connections entering its ports"),
 # --- kurumsal
 "kurumsal-depo": (PLACE, "A clean modern sealing products warehouse: long tidy aisles of grey metal shelving with neatly stacked plain grey boxes, rolls of rubber sheet standing upright in a dedicated rack and coils of profile rubber on reels, bright even light"),
 "kaucuk-silikon": (PRODUCT, "An elegant arrangement of custom rubber and silicone products: black moulded rubber parts, black extruded profiles showing their cross-sections, red and translucent silicone tubes and profiles, a white silicone gasket and brown Viton rings, grouped harmoniously on the work surface with a modern rubber moulding press softly out of focus behind"),
}
WIDE = {"kurumsal-hakkimizda": (
 "Minimal, modern, calm architectural photograph for the about page of an industrial rubber and sealing company. "
 "A long, clean light-grey concrete-and-steel surface runs across the frame in a bright minimalist space with soft "
 "diffused daylight from large windows; on it, with generous negative space, a curated row of a few products: a polished "
 "mechanical shaft seal, a pale green fibre flange gasket standing on edge, a short black cat face rubber profile section, "
 "a black O-ring and a red silicone profile. Soft natural shadows, neutral cool-white palette, gentle contrast. "
 "Full-frame camera, 50mm lens at f/5.6. Realistic materials, factory-new. No people, no text, no logos, no watermarks. "
 "Not CGI, not a 3D render.")}

def job(k):
    if k in WIDE:
        return G.gen(k, WIDE[k], ratio="21:9", raw=True)
    rec, obj = S[k]
    return G.gen(k, f"{obj}. {rec}", ratio="4:3", raw=True)

if __name__ == "__main__":
    keys = sys.argv[1:] or list(S) + list(WIDE)
    for k, st, sz in cf.ThreadPoolExecutor(3).map(job, keys):
        print(f"{k:28} {st} {sz//1024 if sz else ''}", flush=True)
