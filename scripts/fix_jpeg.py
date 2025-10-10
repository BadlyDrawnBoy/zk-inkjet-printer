#!/usr/bin/env python3
import os, re

APP = "ZK-INKJET-NANO-APP.bin"
data = open(APP, "rb").read()
for name in sorted(os.listdir("carved")):
    if "_jpg_" not in name or not name.endswith(".bin"): continue
    m = re.search(r"_0x([0-9A-Fa-f]+)\.bin$", name)
    if not m: continue
    off = int(m.group(1), 16)
    if data[off:off+3] != b"\xFF\xD8\xFF": 
        continue
    eoi = data.find(b"\xFF\xD9", off+2)
    if eoi < 0: 
        print("skip (no EOI):", name); continue
    out = os.path.join("carved", name.replace(".bin", "_fixed.jpg"))
    open(out,"wb").write(data[off:eoi+2])
    print("OK:", out, "bytes:", eoi+2-off)
