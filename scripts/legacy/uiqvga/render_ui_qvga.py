#!/usr/bin/env python3
# Legacy helper: quick render attempt for UI-QVGA blob (brute-force; artifacts remain).
from PIL import Image
import numpy as np

raw = open("ZK-INKJET-UI-QVGA.bin","rb").read()
w=h=480
arr = np.frombuffer(raw, dtype=np.uint16).reshape(h,w)
# RGB565 little-endian → zu 8-bit RGB expandieren
r = ((arr >> 11) & 0x1F) * 255 // 31
g = ((arr >> 5)  & 0x3F) * 255 // 63
b = (arr & 0x1F)          * 255 // 31
rgb = np.dstack([r,g,b]).astype('uint8')
Image.fromarray(rgb, 'RGB').save("UI_QVGA_480x480.png")
print("OK: UI_QVGA_480x480.png")
