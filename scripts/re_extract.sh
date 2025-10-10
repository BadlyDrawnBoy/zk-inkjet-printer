#!/bin/bash
set -euo pipefail

IMG="sdcard.work.img"
BYTE_OFFSET=711048704      # dein bekannter FAT-Start (Bytes)
SECTOR_SIZE=512

# 1) berechne Sektor-Offset
SECTOR_OFFSET=$((BYTE_OFFSET / SECTOR_SIZE))
echo "Byte-Offset: $BYTE_OFFSET"
echo "Sector-Offset: $SECTOR_OFFSET (sectors of $SECTOR_SIZE bytes)"

# 2) fls (list) rekursiv, Ausgabe in file
echo "[*] fls -r -o $SECTOR_OFFSET $IMG -> fat_listing.txt"
fls -r -o "$SECTOR_OFFSET" "$IMG" > fat_listing.txt || { echo "fls failed"; exit 1; }

# 3) zeige die Liste kurz
echo "------ fls output (erste 40 Zeilen) ------"
head -n 40 fat_listing.txt
echo "------------------------------------------"

# 4) Extrahiere alle regulären Dateien (inode-Zeilen beginnen mit r/rw) - nur falls gewünscht
#    Du kannst hier filtern oder manuell Inode-IDs aus fat_listing.txt wählen.
mkdir -p extracted_fat
echo "[*] Extrahiere reguläre Dateien mit icat (automatisch alle inodes der Liste)"
awk '/^[0-9]+r/ {print $1} /^[0-9]+rwx/ {print $1} /^[0-9]+-r/ {print $1}' fat_listing.txt | sort -u | while read -r inode; do
  out="extracted_fat/${inode}.bin"
  echo "icat -o $SECTOR_OFFSET $IMG $inode > $out"
  icat -o "$SECTOR_OFFSET" "$IMG" "$inode" > "$out" || echo "icat failed for inode $inode"
done

# 5) Inspect known binwalk-found offsets in APP.bin (falls vorhanden)
APP="ZK-INKJET-NANO-APP.bin"
if [ -f "$APP" ]; then
  echo "[*] Inspektions-Offsets aus binwalk (hex dump around each)"
  # die Offsets, die binwalk bei dir ausgab:
  OFFSETS=(976226 989627 1059702 1065459 1442060)
  for o in "${OFFSETS[@]}"; do
    echo "----- Offset $o (0x$(printf '%X' $o)) -----"
    # zeige 256 Bytes ab Offset
    dd if="$APP" bs=1 skip=$o count=256 2>/dev/null | hexdump -C
  done
else
  echo "[!] $APP nicht gefunden — überspringe APP-Inspektion"
fi

echo "[*] Fertig. Prüfe extracted_fat/ und fat_listing.txt"
