#!/usr/bin/env python3
# detile_ui_qvga.py – 3x3 Tiles à 160x160 (gesamt 480x480), 16 bpp RGB565

import argparse, os, sys
import numpy as np
from PIL import Image

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-i","--input", default="ZK-INKJET-UI-QVGA.bin", help="Raw 16bpp-Datei")
    p.add_argument("--tile",  type=int, default=160, help="Tile-Kantenlänge (px)")
    p.add_argument("--grid",  type=int, default=3,   help="Kachelraster pro Achse")
    p.add_argument("-o","--out", default="uiqvga_out", help="Ausgabeordner")
    return p.parse_args()

def to_rgb(arr_u16, byte_swap=False, bgr=False):
    a = arr_u16
    if byte_swap:
        a = a.byteswap()  # 16-bit Byteorder tauschen
    r = ((a >> 11) & 0x1F) * 255 // 31
    g = ((a >>  5) & 0x3F) * 255 // 63
    b = ( a        & 0x1F) * 255 // 31
    if bgr:
        r, b = b, r
    return np.dstack([r, g, b]).astype(np.uint8)

def assemble(order, tiles, T, G, H, W):
    canvas = np.zeros((H, W), dtype=np.uint16)
    for idx, tile in enumerate(tiles):
        if order == "row":         # zeilenweise
            ty, tx = divmod(idx, G)
        else:                      # spaltenweise
            ty, tx = idx % G, idx // G
        y0, x0 = ty*T, tx*T
        canvas[y0:y0+T, x0:x0+T] = tile
    return canvas

def main():
    args = parse_args()
    T, G = args.tile, args.grid
    W = H = T * G
    os.makedirs(args.out, exist_ok=True)

    raw = open(args.input, "rb").read()
    need = W * H * 2
    if len(raw) < need:
        print(f"[Warnung] Datei kleiner als erwartet ({len(raw)} < {need}). Versuche dennoch Render.", file=sys.stderr)
    px = np.frombuffer(raw[:need], dtype=np.uint16)

    # 9 Tiles à T*T
    expected_tile_pixels = T*T
    tiles = []
    for i in range(G*G):
        s = i*expected_tile_pixels
        e = s+expected_tile_pixels
        if e > px.size:
            print(f"[Fehler] Unerwartete Pixelanzahl, Abbruch.", file=sys.stderr); sys.exit(1)
        tiles.append(px[s:e].reshape(T, T))

    modes = [
        ("rgb_le",         dict(byte_swap=False, bgr=False)),
        ("rgb_byteswap",   dict(byte_swap=True,  bgr=False)),
        ("bgr_le",         dict(byte_swap=False, bgr=True )),
        ("bgr_byteswap",   dict(byte_swap=True,  bgr=True )),
    ]
    orders = ["row", "col"]

    for ordname in orders:
        base16 = assemble(ordname, tiles, T, G, H, W)
        for mname, opts in modes:
            rgb = to_rgb(base16, **opts)
            out_full = os.path.join(args.out, f"UI_QVGA_{ordname}_{mname}_{W}x{H}.png")
            Image.fromarray(rgb, "RGB").save(out_full)

            # erste Kachel separat
            t0rgb = to_rgb(tiles[0], **opts)
            Image.fromarray(t0rgb, "RGB").save(
                os.path.join(args.out, f"UI_QVGA_tile0_{ordname}_{mname}.png")
            )
            print(f"[OK] {out_full}")

    print("[Fertig] 8 Varianten erzeugt. Eine sollte farblich/typografisch korrekt wirken.")

if __name__ == "__main__":
    main()
