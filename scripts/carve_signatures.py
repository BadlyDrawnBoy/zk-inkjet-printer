import os, struct
INP = "ZK-INKJET-NANO-APP.bin"
OUT = "carved"
sigs = {
    b"\xFF\xD8\xFF": ("jpg", b"\xFF\xD9"),              # JPEG SOI..EOI
    b"\x89PNG\r\n\x1a\n": ("png", b"IEND"),            # PNG, Ende via IEND (+4 CRC)
    b"BM": ("bmp", None),                              # BMP (Größe im Header)
    b"\x7FELF": ("elf", None),                         # ELF
    b"\x00\x01\x00\x00": ("ttf", None),                # TrueType
    b"OTTO": ("otf", None),                            # OpenType (CFF/OTF)
}
os.makedirs(OUT, exist_ok=True)
data = open(INP, "rb").read()
n = len(data)
hits = []
for magic,(ext,endtag) in sigs.items():
    i = 0
    while True:
        j = data.find(magic, i)
        if j < 0: break
        hits.append((j, magic, ext, endtag))
        i = j+1
hits.sort()
def cut(end_idx): return max(0, min(end_idx, n))
idx = 0
manifest = []
for k,(off,magic,ext,endtag) in enumerate(hits,1):
    start = off
    stop = None
    # Versuch 1: Heuristik über nächstes Treffer-Offset
    next_offsets = [o for (o,_,_,_) in hits if o>off]
    if next_offsets: stop = next_offsets[0]
    # Versuch 2: Endmarken (JPEG/PNG)
    if endtag:
        if ext=="jpg":
            e = data.find(endtag, start+2)
            if e!=-1: stop = e+2
        elif ext=="png":
            e = data.find(endtag, start+8)
            if e!=-1: 
                # IEND + 4-Byte CRC
                stop = e + 4 + 4
    # Versuch 3: 4-Byte-Längenfeld direkt vor Start (LE)
    if stop is None and start>=4:
        L = struct.unpack("<I", data[start-4:start])[0]
        if 64 <= L <= (n-start):
            stop = start + L
    # Fallback: 512 KB Fenster
    if stop is None:
        stop = start + 512*1024
    chunk = data[start:cut(stop)]
    outp = os.path.join(OUT, f"{k:04d}_{ext}_0x{start:X}.bin")
    with open(outp,"wb") as f: f.write(chunk)
    manifest.append((outp, start, len(chunk), ext))
# Kurzer Report
for path,off,size,ext in manifest:
    print(f"{path}, offset={off}, size={size}, type={ext}")
print(f"Done. Files in ./{OUT}  (Treffer: {len(manifest)})")
