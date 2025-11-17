#!/usr/bin/env python3
# NOTE: Legacy brute-force seam scorer; outputs still show artifacts.
import os, itertools, numpy as np
from PIL import Image

INP = "ZK-INKJET-UI-QVGA.bin"
OUT = "uiqvga_autotune_out"
TILE=160; GRID=3; W=H=TILE*GRID; NPIX=W*H
os.makedirs(OUT, exist_ok=True)

raw = open(INP,"rb").read()
if len(raw) < NPIX*2:
    raise SystemExit("Datei zu klein")
pix = np.frombuffer(raw[:NPIX*2], dtype=np.uint16)

# Grund-Dekodierung: XOR 0xAAAA, BGR565, Order=col
def assemble_col(arr16):
    tiles=[]; off=0
    for _ in range(GRID*GRID):
        tiles.append(arr16[off:off+TILE*TILE].reshape(TILE,TILE))
        off+=TILE*TILE
    canvas = np.zeros((H,W), dtype=np.uint16)
    for idx,t in enumerate(tiles):
        ty, tx =  divmod(idx, GRID) # idx%GRID, idx//GRID   col-major
        y0, x0 = ty*TILE, tx*TILE
        canvas[y0:y0+TILE, x0:x0+TILE] = t
    return canvas

def rgb565_bgr(a16):
    r = ( a16        &0x1F)*255//31
    g = ((a16>>5 )&0x3F)*255//63
    b = ((a16>>11)&0x1F)*255//31
    return np.dstack([r,g,b]).astype(np.uint8)

base16 = assemble_col(pix) ^ 0xAAAA  # XOR hier global

# Kostenfunktion: Nähte bei x=160/320 + „Kamm“ (even vs odd)
def cost(img):
    im = img.astype(np.int16)
    seams = []
    for x in (160,320):
        seams.append(np.mean(np.abs(im[:,x-1,:]-im[:,x,:])))
    seam = np.mean(seams)
    comb = np.mean(np.abs(im[0::2,:,:]-im[1::2,:,:]))
    return seam*2.0 + comb*0.5

best = (1e9, None, None, None)

# Suchraum
line_shifts = [-2,-1,0,1,2]
col_shifts  = range(-3,4)  # -3..+3
for s in line_shifts:
    # odd-line shift
    rolled = np.roll(base16, shift=s, axis=1)  # erst global, wir korrigieren Spalten separat
    # pro Spalte zyklisch rollen
    for d0, d1, d2 in itertools.product(col_shifts, repeat=3):
        a = rolled.copy()
        a[:, 0:160] = np.roll(a[:, 0:160], d0, axis=1)
        a[:,160:320] = np.roll(a[:,160:320], d1, axis=1)
        a[:,320:480] = np.roll(a[:,320:480], d2, axis=1)
        rgb = rgb565_bgr(a)
        c = cost(rgb)
        if c < best[0]:
            best = (c, s, (d0,d1,d2), rgb)

# Ergebnis ausgeben
score, s, (d0,d1,d2), rgb = best
out = os.path.join(OUT, f"best_score{score:.2f}_oddShift{s}_cols{d0}_{d1}_{d2}.png")
Image.fromarray(rgb).save(out)
print("BEST:", out)
