#!/usr/bin/env python3
# uiqvga_decode_sweep.py
# Testet: XOR (konstant/alternierend), Byte-Swap, BGR, Tile-Order, Zeilen-Shift.

import os, itertools, numpy as np
from PIL import Image

INP = "ZK-INKJET-UI-QVGA.bin"
OUT = "uiqvga_sweep"
TILE = 160
GRID = 3
W = H = TILE*GRID           # 480x480
NPIX = W*H

os.makedirs(OUT, exist_ok=True)
raw = open(INP, "rb").read()
if len(raw) < NPIX*2:
    raise SystemExit(f"Datei zu klein ({len(raw)}B), erwartet {NPIX*2}B")

# 9 Tiles a 160x160, je 16bit
px = np.frombuffer(raw[:NPIX*2], dtype=np.uint16)

def rgb565_to_rgb(arr16, byte_swap=False, bgr=False):
    a = arr16.byteswap() if byte_swap else arr16
    r = ((a >> 11) & 0x1F) * 255 // 31
    g = ((a >>  5) & 0x3F) * 255 // 63
    b = ( a        & 0x1F) * 255 // 31
    if bgr: r, b = b, r
    return np.dstack([r,g,b]).astype(np.uint8)

def tiles_from_linear(arr16):
    tiles=[]
    off=0
    for _ in range(GRID*GRID):
        tiles.append(arr16[off:off+TILE*TILE].reshape(TILE,TILE))
        off+=TILE*TILE
    return tiles

def assemble(tiles, order="row"):
    canvas = np.zeros((H, W), dtype=np.uint16)
    for idx,t in enumerate(tiles):
        if order=="row":      # 0..8: (0,0)(0,1)(0,2)(1,0)...
            ty, tx = divmod(idx, GRID)
        else:                 # "col": (0,0)(1,0)(2,0)(0,1)...
            ty, tx = idx%GRID, idx//GRID
        y0, x0 = ty*TILE, tx*TILE
        canvas[y0:y0+TILE, x0:x0+TILE] = t
    return canvas

def apply_xor(arr16, mode):
    if mode=="const_aaaa":
        return arr16 ^ 0xAAAA
    if mode=="alt_aaaa_5555":
        # je Zeile XOR-Key wechseln
        a = arr16.reshape(H,W).copy()
        a[1::2,:] ^= 0x5555
        a[0::2,:] ^= 0xAAAA
        return a.reshape(-1)
    raise ValueError(mode)

def line_phase_shift(rgb, shift):  # shift in Pixel, nur für ungerade Zeilen
    if shift==0: return rgb
    out = rgb.copy()
    # zyklischer Shift der Spalten für ungerade Zeilen
    out[1::2,:,:] = np.roll(out[1::2,:,:], shift=shift, axis=1)
    return out

xor_modes   = ["const_aaaa", "alt_aaaa_5555"]
swap_modes  = [False, True]
bgr_modes   = [False, True]
orders      = ["row", "col"]
line_shifts = [0, +2, -2]   # ggf. bei Bedarf +2/-2 ergänzen

tiles = tiles_from_linear(px)

combos = list(itertools.product(xor_modes, swap_modes, bgr_modes, orders, line_shifts))
for (xm, sw, bg, ordm, lsh) in combos:
    base16 = assemble(tiles, ordm).reshape(-1)
    dec16  = apply_xor(base16, xm).reshape(H,W)
    rgb    = rgb565_to_rgb(dec16, byte_swap=sw, bgr=bg)
    rgb    = line_phase_shift(rgb, lsh)

    tag = f"{ordm}_{xm}_swap{int(sw)}_bgr{int(bg)}_shift{lsh}"
    Image.fromarray(rgb).save(os.path.join(OUT, f"UIQ_{tag}.png"))

print(f"Fertig. {len(combos)} Varianten in ./{OUT}")
