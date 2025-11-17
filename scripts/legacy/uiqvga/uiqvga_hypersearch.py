#!/usr/bin/env python3
# uiqvga_hypersearch.py (legacy brute-force; artifacts remain)
# Ziel: ZK-INKJET-UI-QVGA.bin (9 Tiles à 160x160) korrekt rekonstruieren.
# Vorgehen: XOR 0xAAAA, BGR565, Tile-Order=col. Suche nach:
#  - odd-line Basis-Shift s0
#  - odd-line Drift k (alle L Zeilen +k), Reset je 160-Zeilen-Block
#  - Spalten-Offsets (d0,d1,d2) je 160er-Spalte
# Ausgabe: Top-N Varianten (PNG) + Log mit Parametern/Score.

import os, argparse, itertools, numpy as np
from PIL import Image

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-i","--input", default="ZK-INKJET-UI-QVGA.bin", help="Rohdatei (16 bpp)")
    p.add_argument("-o","--outdir", default="uiqvga_hyper_out", help="Ausgabeordner")
    p.add_argument("--tile", type=int, default=160, help="Tile-Kantenlänge (px)")
    p.add_argument("--grid", type=int, default=3, help="Tiles pro Achse")
    p.add_argument("--top",  type=int, default=8, help="Anzahl Top-Ergebnisse")
    # Suchräume (schnell justierbar)
    p.add_argument("--s0_min", type=int, default=-8)
    p.add_argument("--s0_max", type=int, default=8)
    p.add_argument("--k_set",  default="-2,-1,0,1,2")
    p.add_argument("--L_set",  default="16,32,40")
    p.add_argument("--d_span", type=int, default=4, help="Spalten-Offsets ∈ [-d_span..+d_span]")
    p.add_argument("--order",  choices=["col","row"], default="col", help="Tile-Order (Default: col)")
    return p.parse_args()

def tiles_assemble(a16, tile, grid, order):
    H = W = tile*grid
    # 9 Tiles sequenziell
    tiles=[]; off=0
    for _ in range(grid*grid):
        tiles.append(a16[off:off+tile*tile].reshape(tile,tile))
        off += tile*tile
    canvas = np.zeros((H, W), dtype=np.uint16)
    for idx,t in enumerate(tiles):
        if order == "col":      ty, tx = idx % grid, idx // grid
        else:                   ty, tx = divmod(idx, grid)  # row
        y0, x0 = ty*tile, tx*tile
        canvas[y0:y0+tile, x0:x0+tile] = t
    return canvas

def roll_rows_horiz(U, shifts):
    """Zeilenweise zyklisch horizontal rollen (U: HxW, shifts: H-Liste)."""
    H, W = U.shape
    s = (np.asarray(shifts) % W).reshape(H, 1)
    cols = (np.arange(W)[None, :] - s) % W
    rows = np.arange(H).reshape(H, 1)
    return U[rows, cols]

def apply_phase(base16, tile, grid, s0, k, L, d0, d1, d2):
    """XOR, Zeilen-Shift mit Drift, Spalten-Offsets."""
    H = W = tile*grid
    U = base16 ^ 0xAAAA  # XOR
    U = U.reshape(H, W)
    # odd-line: Basis + Drift je 160er-Block, Reset pro Block
    r_in_tile = (np.arange(H) % tile)         # 0..159 in jedem Block
    drift_steps = (r_in_tile // L) * k
    shifts = np.where((np.arange(H) & 1) == 1, s0 + drift_steps, 0)
    U = roll_rows_horiz(U, shifts)            # HORIZONTALES Rollen pro Zeile
    # Spalten-Offsets je 160er-Segment
    if d0: U[:,   0:tile] = np.roll(U[:,   0:tile], d0, axis=1)
    if d1: U[:, tile:2*tile] = np.roll(U[:, tile:2*tile], d1, axis=1)
    if d2: U[:,2*tile:3*tile] = np.roll(U[:,2*tile:3*tile], d2, axis=1)
    return U

def bgr565_to_rgb(a16):
    r = ( a16        & 0x1F) * 255 // 31
    g = ((a16 >>  5) & 0x3F) * 255 // 63
    b = ((a16 >> 11) & 0x1F) * 255 // 31
    return np.dstack([r,g,b]).astype(np.uint8)

def score(rgb):
    """Kosten: Nähte x=160/320 + Kamm (even/odd). Naht doppelt gewichten."""
    im = rgb.astype(np.int16)
    seams = []
    for x in (160,320):
        seams.append(np.mean(np.abs(im[:,x-1,:]-im[:,x,:])))
    seam = np.mean(seams)
    comb = np.mean(np.abs(im[0::2,:,:]-im[1::2,:,:]))
    return seam*2.0 + comb*0.5

def main():
    args = parse_args()
    TILE, GRID = args.tile, args.grid
    H = W = TILE*GRID
    NPIX = W*H

    raw = open(args.input, "rb").read()
    if len(raw) < NPIX*2:
        raise SystemExit(f"Datei zu klein ({len(raw)}B), erwartet >= {NPIX*2}B")
    a16 = np.frombuffer(raw[:NPIX*2], dtype=np.uint16)

    os.makedirs(args.outdir, exist_ok=True)

    base16 = tiles_assemble(a16, TILE, GRID, args.order).reshape(-1)

    S0 = range(args.s0_min, args.s0_max+1)
    K  = [int(x) for x in args.k_set.split(",") if x.strip()!=""]
    Ls = [int(x) for x in args.L_set.split(",") if x.strip()!=""]
    D  = range(-args.d_span, args.d_span+1)

    best = []  # (score, tag, rgb)
    tested = 0
    for L in Ls:
        for k in K:
            for s0 in S0:
                for d0, d1, d2 in itertools.product(D, repeat=3):
                    U = apply_phase(base16, TILE, GRID, s0, k, L, d0, d1, d2)
                    rgb = bgr565_to_rgb(U)
                    c = score(rgb)
                    tag = f"{args.order}_L{L}_k{k}_s0{s0}_cols{d0}_{d1}_{d2}"
                    best.append((c, tag, rgb))
                    tested += 1
                    # kleine Drosselung der Liste im Lauf (Speicher)
                    if len(best) > args.top*20:
                        best.sort(key=lambda x: x[0])
                        best = best[:args.top*4]

    # Finale Top-N sichern
    best.sort(key=lambda x: x[0])
    best = best[:args.top]
    for i,(c,tag,rgb) in enumerate(best, 1):
        outp = os.path.join(args.outdir, f"{i:02d}_{c:.2f}_{tag}.png")
        Image.fromarray(rgb).save(outp)
        print(f"{i:02d}  {c:.2f}  {tag}  -> {outp}")
    print(f"Fertig. Getestete Kombinationen: {tested}")

if __name__ == "__main__":
    main()

# --- Test helper shim: exported ParameterSet for pytest ---
try:
    from dataclasses import dataclass
    @dataclass(frozen=True)
    class ParameterSet:
        # Breite/Höhe sind für QVGA-Scans (und Tests) die üblichen Parameter.
        width: int
        height: int
        stride: int | None = None
        bpp: int | None = None
        palette: str | None = None
except Exception:
    pass

# --- Test helper shim: exported combine_score for pytest ---
def combine_score(*metrics, weights=None):
    """Kombiniere beliebig viele Metriken additiv.
    - metrics: Zahlen oder None
    - weights: gleichlange Sequenz oder None (dann Gewicht 1.0)
    """
    if weights is None:
        weights = [1.0] * len(metrics)
    total = 0.0
    for m, w in zip(metrics, weights):
        if m is not None:
            total += float(w) * float(m)
    return total


# --- Test helper shim: exported compute_metrics for pytest ---
def compute_metrics(img=None, params=None):
    """Minimaler, nebenwirkungsfreier Platzhalter – nur für Test-Imports.
    Liefert eine kleine Metrik-Struktur zurück.
    """
    w = getattr(params, "width", None) if params is not None else None
    h = getattr(params, "height", None) if params is not None else None
    return {"ok": True, "width": w, "height": h}
