#!/usr/bin/env python3
import os, struct, re

APP = "ZK-INKJET-NANO-APP.bin"
data = open(APP, "rb").read()

def fix_one(path):
    m = re.search(r"_0x([0-9A-Fa-f]+)\.bin$", path)
    if not m: return None
    off = int(m.group(1), 16)
    head = data[off:off+12]
    if head[:4] not in (b"OTTO", b"\x00\x01\x00\x00"): return None  # OTF/TTF
    sfntVersion = head[:4]
    numTables = struct.unpack(">H", head[4:6])[0]
    # Table records: 16 Bytes je Tabelle ab Offset 12
    end = 12 + 16*numTables
    if off+end > len(data): return None
    max_end = end
    for i in range(numTables):
        rec = data[off+12+16*i : off+12+16*(i+1)]
        # tag(4) checkSum(4) offset(4) length(4) big-endian
        _,_,to,tl = struct.unpack(">4sIII", rec)
        if to+tl > max_end: max_end = to+tl
    blob = data[off:off+max_end]
    out = path.replace(".bin", "_fixed.otf" if sfntVersion==b"OTTO" else "_fixed.ttf")
    open(out, "wb").write(blob)
    return out, max_end

for f in sorted([p for p in os.listdir("carved") if p.endswith(".bin") and "_otf_" in p or "_ttf_" in p]):
    res = fix_one(os.path.join("carved", f))
    if res: print("OK:", res)
