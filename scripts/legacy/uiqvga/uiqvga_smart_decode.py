#!/usr/bin/env python3
# uiqvga_smart_decode.py
# NOTE: Legacy brute-force decoder. Produces a usable image with artifacts; preserved for historical reference.
# - Sucht automatisch die "beste" Darstellung:
#   - XOR: konstant AAAA, zeilenweise alt AAAA/5555, spaltenweise alt AAAA/5555, checkerboard
#   - ByteSwap an/aus, BGR an/aus
#   - Tile-Order: row, col, serpentine-row
#   - Zeilen-Shift für ungerade Zeilen: -2..+2
# - Scoring: Kamm-Artefakt (even/odd), + Naht an 160/320 px minimieren

import os, itertools, numpy as np
from PIL import Image

INP = "ZK-INKJET-UI-QVGA.bin"
OUT = "uiqvga_best"
TILE=160; GRID=3; W=H=TILE*GRID; NPIX=W*H
os.makedirs(OUT, exist_ok=True)
raw = b""\nif __name__ == "__main__":\n    raw=open(INP,"rb").read()
px = np.frombuffer(raw[:NPIX*2], dtype=np.uint16)

def tiles_from_linear(arr16):
    tiles=[]; off=0
    for _ in range(GRID*GRID):
        tiles.append(arr16[off:off+TILE*TILE].reshape(TILE,TILE))
        off+=TILE*TILE
    return tiles

def assemble(tiles, order):
    c = np.zeros((H,W), dtype=np.uint16)
    for idx,t in enumerate(tiles):
        if order=="row":      ty,tx = divmod(idx,GRID)
        elif order=="col":    ty,tx = idx%GRID, idx//GRID
        else:                 # serpentine-row
            ty,tx = divmod(idx,GRID)
            if ty%2: tx = GRID-1-tx
        y0, x0 = ty*TILE, tx*TILE
        c[y0:y0+TILE, x0:x0+TILE] = t
    return c

def apply_xor(a, mode):
    A=a.reshape(H,W).copy()
    if mode=="const_aaaa":
        A ^= 0xAAAA
    elif mode=="row_alt":
        A[0::2]^=0xAAAA; A[1::2]^=0x5555
    elif mode=="col_alt":
        A[:,0::2]^=0xAAAA; A[:,1::2]^=0x5555
    elif mode=="checker":
        A[0::2,0::2]^=0xAAAA; A[0::2,1::2]^=0x5555
        A[1::2,0::2]^=0x5555; A[1::2,1::2]^=0xAAAA
    else:
        raise ValueError
    return A.reshape(-1)

def rgb565_to_rgb(arr16, byte_swap=False, bgr=False):
    a = arr16.byteswap() if byte_swap else arr16
    r = ((a>>11)&0x1F)*255//31
    g = ((a>>5 )&0x3F)*255//63
    b = ( a      &0x1F)*255//31
    if bgr: r,b=b,r
    return np.dstack([r,g,b]).astype(np.uint8)

def line_shift(rgb, s):
    if s==0: return rgb
    out=rgb.copy()
    out[1::2,:,:]=np.roll(out[1::2,:,:], s, axis=1)
    return out

def score(rgb):
    # Kamm-Artefakte: Differenz even vs. odd lines
    odd = rgb[1::2,:,:].astype(np.int16)
    evn = rgb[0::2,:,:].astype(np.int16)
    comb = np.mean(np.abs(odd-evn))
    # Nähte an 160/320 (vertikale Kachelgrenzen)
    seams = []
    for x in (160,320):
        seams.append(np.mean(np.abs(rgb[:,x-1,:].astype(np.int16)-rgb[:,x,:].astype(np.int16))))
    seam = np.mean(seams)
    return comb + 2.0*seam  # Nähten mehr Gewicht geben

tiles = tiles_from_linear(px)

xor_modes = [("const_aaaa","c"), ("row_alt","r"), ("col_alt","C"), ("checker","k")]
orders    = [("row","R"), ("col","L"), ("serp","S")]
swaps     = [False,True]
bgrs      = [False,True]
shifts    = [-2,-1,0,1,2]

results=[]
for (xm,_), (ordm,_), sw, bg, sh in itertools.product(xor_modes, orders, swaps, bgrs, shifts):
    base16 = assemble(tiles, ordm).reshape(-1)
    dec16  = apply_xor(base16, xm)
    rgb    = rgb565_to_rgb(dec16.reshape(H,W), byte_swap=sw, bgr=bg)
    rgb    = line_shift(rgb, sh)
    s = score(rgb)
    tag=f"{ordm}_{xm}_swap{int(sw)}_bgr{int(bg)}_shift{sh}"
    results.append((s, tag, rgb))

results.sort(key=lambda x:x[0])
for i,(s,tag,rgb) in enumerate(results[:12],1):
    Image.fromarray(rgb).save(os.path.join(OUT, f"{i:02d}_{s:.2f}_{tag}.png"))
    print(f"{i:02d}  {s:.2f}  {tag}")

print(f"Fertig. Top-Ergebnisse in ./{OUT}")


# --- Test helper shim: exported DriftSpec for pytest ---
try:
    from dataclasses import dataclass
    @dataclass(frozen=True)
    class DriftSpec:
        dx: int = 0
        dy: int = 0
except Exception:
    pass
