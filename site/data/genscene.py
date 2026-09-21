# -*- coding: utf-8 -*-
"""Kategori ve uygulama sahnesi görselleri — ürün çekimlerinden farklı, ortam fotoğrafı."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genimg as G, concurrent.futures as cf

G.OUT = os.path.join(G.ROOT, "assets", "img", "sahne")
os.makedirs(G.OUT, exist_ok=True)
G.RECIPE = (
 "Editorial industrial photograph, documentary style, shot on a 35mm lens at f/2.8. "
 "Real working environment with honest wear: scuffed paint, oil traces, weld seams, worn steel. "
 "Cool blue-grey colour grade with deep shadows and one warm practical light source. "
 "Moody low-key exposure, natural window or worklamp light, subtle atmospheric haze. "
 "No readable text, no signage, no logos, no brand names, no watermarks, no faces looking at camera."
)

S = [
 # kategori sahneleri
 ("kat-contalar","Close view of a large bolted pipe flange joint in a ship engine room, two steel flange faces drawn together by heavy studs and nuts, a pale green fibre gasket just visible in the seam, insulated pipework receding behind"),
 ("kat-mekanik-salmastralar","A large centrifugal pump with its casing opened during overhaul, the polished shaft end and seal chamber exposed, wrenches resting on the steel deck plate beside it"),
 ("kat-yumusak-salmastralar","A valve stuffing box being repacked, the gland follower loosened and a coil of braided packing rope lying on the warm valve body, steam pipework behind"),
 ("kat-oringler","An open hydraulic manifold block on a workbench, precision bores and O-ring grooves visible, a scattering of rubber O-rings on the steel bench top"),
 ("kat-keceler","A gearbox output shaft during maintenance, the bearing housing open and the shaft seal seat exposed, oil film on machined steel"),
 ("kat-ambar-kapak","The raised hatch cover of a bulk carrier seen from the deck, the long rubber sealing profile running along the coaming rim, sea horizon and cranes beyond"),
 ("kat-levhalar","A gasket cutting bench in a workshop, a large sheet of green fibre gasket material laid flat with a cut ring lifted from it, hollow punches and a mallet on the bench"),
 ("kat-kaplinler","A motor-pump coupling guard removed to reveal the jaw coupling between an electric motor and a pump, alignment gauge resting on the shaft"),
 ("kat-flanslar","A stack and row of steel pipe flanges of different diameters in a supply warehouse, raw machined faces catching cold light, racking behind"),
 ("kat-takozlar","The mounting foot of a marine generator set bolted down onto anti-vibration mounts, thick steel bedplate and deck, engine block above"),
 ("kat-setler","An open ship's spare parts locker with labelled compartment boxes and sealing kits on steel shelving, engine room lighting"),
 ("kat-el-aletleri","A maintenance workbench in a ship engine room with a bearing puller clamped on a shaft end, hand tools laid out on the steel surface"),
 # uygulama şeritleri
 ("uyg-tersane","A ship in dry dock at a Turkish shipyard seen from below at dusk, the vast hull and bilge keel above, scaffolding and yard cranes, cold blue light"),
 ("uyg-makine-dairesi","The interior of a ship engine room, the main engine block rising through the frame, walkway gratings, colour-coded pipework and valves, warm worklight"),
 ("uyg-pompa","A row of industrial centrifugal pumps on a plant floor, motors coupled to pump casings, suction and discharge pipework with flanged joints"),
 ("uyg-esanjor","A plate heat exchanger in a machinery space, its stack of stainless plates clamped between tie bars, insulated pipes entering the ports"),
 # kurumsal
 ("kurumsal-depo","Deep shelving racks in a sealing products warehouse, rolls of rubber sheet standing on end, boxes of gaskets and coils of packing rope, cool overhead light down a long aisle"),
 ("kurumsal-tezgah","A workshop bench where an industrial gasket is being cut from a sheet, hands in work gloves guiding a cutting knife around a template, curled offcuts on the bench"),
]
HERO = ("hero-frame","Extreme macro view of two heavy machined steel flange faces almost touching, a dark green-grey gasket ring compressed in the narrow seam between them, a single cold highlight running along the polished edge, deep black background, cinematic industrial still, shallow depth of field")

if __name__ == "__main__":
    jobs = [(s, p, "4:3") for s, p in S] + [(HERO[0], HERO[1], "16:9")]
    only = set(sys.argv[1:])
    if only: jobs = [j for j in jobs if j[0] in only]
    print(len(jobs), "sahne kuyrukta")
    done = 0
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for slug, st, sz in ex.map(lambda a: G.gen(a[0], a[1], a[2]), jobs):
            done += 1
            print(f"[{done}/{len(jobs)}] {slug:24} {st} {sz//1024 if sz else ''}", flush=True)
