# ZK‑INKJET Firmware‑Analyse – Gesamtstand (Stand 09.10.2025)

> [⤴ Zurück zur Archivübersicht](../README.md)

## Kontext und Ziel

Im Rahmen der Untersuchung des handheld‑Tintenstrahldruckers „ZK‑INKJET“  wurden mehrere Roh‑Binärdateien (Boot‑Loader, Applikationscontainer,  UI‑Grafiken und Ressourcendateien) sowie ein ursprünglich  abgeschnittenes ext4‑Image analysiert. Ziel war es, den Aufbau der  Firmware zu verstehen, Ressourcen (Schriftarten, Bilder) zu extrahieren  und die proprietären Formate zu dokumentieren.

## Dateistruktur und Bootvorgang

- **SD‑Karte als Bootmedium**: Die Firmware liegt auf einer entnehmbaren SD‑Karte, die keine  klassische Partitionstabelle besitzt. Am Anfang befindet sich ein  Stage‑1‑Bootloader (Signatur „ZBWp1WBZ“), gefolgt von einem größeren  Stage‑2‑Loader. Ohne SD‑Karte startet das Gerät nicht. Erst ab Offset  711 MB erscheint ein FAT‑ähnliches Dateisystem, das im Menü als „MINI“  geführt wird.
- **Abgeschnittenes ext4‑Rootfs**: Im Image wurden Reste eines ext4‑Root‑Dateisystems gefunden. Es hatte  eine logische Größe von ca. 7,4 GB, während die physische Karte nur  3,75 GB bot. Das Filesystem ließ sich nicht reparieren; daher wurden nur vereinzelte Datenstücke mittels File‑Carving extrahiert  (ELF‑Bibliotheken, Android‑APKs). Dieses Alt‑Rootfs stammt vermutlich  von einem Vorgängergerät und ist für die aktuelle Firmware nicht  relevant.
- **ZK‑INKJET‑NANO‑BOOT.bin (≈ 12,7 kB)**: Der Binärblob weist eine niedrige Entropie (~5,8 Bit/B) auf, enthält  kaum ASCII‑Strings und keine bekannten Dateisignaturen. Er besteht fast  ausschließlich aus ARM‑Instruktionen. Es handelt sich vermutlich um den  Stage‑2‑Bootloader, der die nachfolgenden Module in den RAM lädt.  Hinweise auf die Offset‑Adressen deuten darauf hin, dass er das Modul  „APP“ und die GUI‑Ressourcen ins RAM kopiert.

## Applikationsmodul (ZK‑INKJET‑NANO‑APP.bin)

- **Größe und Struktur**: Die Datei ist ca. 2,6 MB groß und enthält eine Mischung aus Binärdaten  und lesbaren Strings. Eine Suche nach bekannten Formaten (SquashFS, ZIP, ELF) blieb erfolglos; stattdessen fanden sich zahlreiche Pfadangaben  und Ressourcennamen wie 0:/simhei.ttf, 0:/arial.ttf oder  3:/inkjet-ui-%04d%02d%02d %02d%02d%02d.bmp. Daraus lässt sich schließen, dass APP.bin einen proprietären Container darstellt.
- **Carving‑Ergebnisse**: Mittels Signatur‑Scanning und Carving wurden fragmentarische Ressourcen extrahiert:
   OpenType‑/TrueType‑Fonts (Montserrat-Regular.otf, OpenSans-Regular.ttf  etc.) konnten identifiziert, aber nur teilweise rekonstruiert werden.  Eine Datei ZK‑INKJET-GUI-RES.zkml stellte sich als vollwertige  TrueType‑Font (Leelawadee UI) heraus.
   Bitmap‑Dateien (BMP) wurden in großer Anzahl gefunden, jedoch waren  viele stark fragmentiert. Durch Auslesen des BMP‑Headers (Feld bfSize)  konnten einige Bilder korrekt ausgeschnitten werden.
- **JPEG/PNG**: vereinzelt wurden JPEG‑Header gefunden; die zugehörigen Daten waren  jedoch häufig unvollständig, sodass keine validen Bilder entstanden.
- **Dateireferenzen**: Ein strings‑Dump von APP.bin liefert eine Liste erwarteter Dateien.  Unter anderem werden folgende Fonts referenziert: arial.ttf,  DroidSansFallback.ttf, DZPMYD.ttf, FZFSJW.ttf, FZKTJW.ttf,  Montserrat-Regular.otf, OpenSans-Regular.ttf, simfang.ttf, simhei.ttf,  simkai.ttf und times.ttf. Außerdem werden die beiden Ressourcendateien  ZK‑INKJET-RES-HW.zkml und ZK‑INKJET-GUI-RES.zkml erwähnt.
   Fazit: Das Applikationsmodul dient als Ressourcencontainer, der während  des Betriebs vom Bootloader in den RAM geladen wird. Es enthält keine  standardisierte Dateisystemstruktur und erfordert dedizierte Parser, um  die eingebetteten Ressourcen zu extrahieren.

## UI‑Grafikmodul (ZK‑INKJET‑UI‑QVGA.bin)

- **Dieses Modul (≈ 450 kB) enthält die Hintergrundgrafiken des Druckers. Die  Daten sind als 16‑Bit‑Worte kodiert und zusätzlich verschleiert. Die  Analyse ergab folgende Punkte**:
- **Kachelaufbau**: Die Rohdaten bestehen aus neun Tiles à 160×160 Pixel, die in einer  3×3‑Matrix zusammengesetzt werden. Der resultierende Frame hat  480×480 Pixel.
- **Farbraum und Verschleierung**: Jedes Pixel ist im Format BGR565 gespeichert und vorab mit dem XOR‑Wert 0xAAAA verschleiert. Werden die 16‑Bit‑Worte mit 0xAAAA verknüpft und  in BGR565 umgewandelt, erscheinen die Farben plausibel.
- **Zeilen‑ und Spaltenverschiebung**: Trotz korrekter Farbdarstellung bleiben horizontale Versätze in den  Schrift‑ und Symbolgrafiken. Experimente zeigten, dass die ungeraden  Zeilen horizontal verschoben sind (Basis‑Shift s0), und dass diese  Verschiebung pro Zeile zusätzlich um einen Drift‑Wert k anwachsen kann.  Darüber hinaus benötigen die drei Kachelspalten separate Offsets  (d0,d1,d2), um die Nähte an den Spaltengrenzen zu minimieren.
- **Näherungsverfahren**: Über ein Hyper‑Search‑Skript wurden verschiedene Parameterkombinationen (s0, k, L, d0,d1,d2) getestet. Die beste gefundene Kombination liefert  eine nahezu korrekte Bilddarstellung (Hintergrund durchgängig, Schrift  gut lesbar), allerdings verbleiben geringe Restverschiebungen. Das  deutet darauf hin, dass zusätzlich eine bitweise Permutation oder ein  Serpentin‑Scan in der Hardware aktiv ist.
   Die genaue Methode zur Rekonstruktion (Pipeline, Parameterbereiche) wird im separaten Dokument ZK‑INKJET UI/Graphics – Arbeitsstand &  Methode (06.10.2025) beschrieben und kann dort nachgeschlagen werden.

## Ressourcendateien (ZK‑INKJET‑RES‑HW.zkml und ZK‑INKJET‑GUI‑RES.zkml)

ZK‑INKJET‑GUI‑RES.zkml wurde als TrueType‑Font identifiziert. Nach Umbenennung zu .ttf kann  die Datei mit Standard‑Tools (z. B. fc-scan) analysiert werden; sie  enthält die Schrift „Leelawadee UI“.
 ZK‑INKJET‑RES‑HW.zkml weist keine offensichtlichen Signaturen auf. Die  Entropie (~5 Bit/B) spricht gegen Verschlüsselung. Vermutlich handelt es sich um einen weiteren Ressourcencontainer (z. B. Hardware‑Icons oder  Maschinendaten). Eine detaillierte Analyse steht noch aus.

## Analyse der Boot‑Prozedur und Update‑Mechanismus

- **Startadresse**: In den bisherigen Disassemblierungsversuchen mit Gemini wurde ein  Einsprungpunkt im Bootcode gefunden, der nicht am Dateianfang, sondern  weiter hinten (0x0000 3xxx) lag. Dieser Bereich scheint für das Laden  der BNR/BIN‑Dateien zuständig zu sein. Es könnte sich um einen Teil des  Firmware‑Update‑Mechanismus handeln, der die Module aus dem  FAT‑Dateisystem in den RAM kopiert.
- **Mehrkern‑Architektur**: Untersuchungen der extrahierten ELF‑Fragmente deuten auf eine  SoC‑Architektur mit einem ARM‑Kern und einem 8051‑Kern hin. Der  8051‑Teil dürfte die exakte Ansteuerung des HP‑45‑Druckkopfs übernehmen, während der ARM‑Kern das Linux‑/Android‑System und die UI bearbeitet.
- **Nächste Schritte**: Um den Lade‑/Update‑Mechanismus vollständig zu verstehen, ist eine  tiefergehende statische Codeanalyse des Boot‑ und Applikationsmoduls  (z. B. mit Ghidra oder Rizin) erforderlich. Gesucht wird insbesondere  eine Routine, die die XOR‑Entschlüsselung und eventuelle Bit‑Permutation der Grafikdaten durchführt. Die Konstante 0xAAAA kann als Suchbegriff  dienen, um in den Binärdateien entsprechende Stellen zu finden.

## Fazit und Ausblick

Die bisherigen Untersuchungen zeigen, dass die Firmware des  ZK‑INKJET‑Druckers auf einer proprietären Containerstruktur basiert.  Grafiken werden in BGR565 gespeichert, per XOR verschleiert und  möglicherweise durch weitere Hardware‑Tricks (Zeilenshift,  Serpentin‑Scan) verzerrt. Das Applikationsmodul enthält Schriften und  Bitmaps, die nur durch File‑Carving extrahiert werden können. Eine  vollständige Dekodierung der UI‑Ressourcen erfordert entweder das  Reverse‑Engineering der entsprechenden Firmware‑Routine oder eine  systematische Suche nach den korrekten Phasen‑Parametern.

- **Für die nächste Phase empfiehlt sich**:
   Statische Codeanalyse der BOOT.bin‑ und APP.bin‑Dateien mit einem  Disassembler, um die Lade‑ und Dekodierfunktionen zu identifizieren.
   Erweiterung des Carvers um Bit‑Permutation und Serpentin‑Scans, um die Restverschiebungen in den Grafiken zu eliminieren.
   Untersuchung der RES‑HW.zkml auf mögliche weitere Ressourcenformate.
   Gesamtdokumentation aller Tests und Parameter, damit künftige Analysen auf diesem Wissen aufbauen können.
   Mit dieser Zusammenfassung sind die bisherigen Erkenntnisse dokumentiert und können später als Ausgangspunkt für weitere Experimente dienen.

# ZK‑INKJET UI/Graphics – Arbeitsstand & Methode (06.10.2025)

## Kontext

Ziel: Grafiken aus den ZK‑INKJET‑Firmwaredateien rekonstruieren (insb. `ZK‑INKJET-UI-QVGA.bin`). Das Rohmaterial wirkt „gescrambled“; wir haben eine Näherung  erarbeitet, die Farben korrekt macht und das Kachelraster richtig  zusammensetzt, aber noch horizontale Versätze in der Schrift zeigt.

## Dateien & Artefakte (relevant)

- `ZK-INKJET-UI-QVGA.bin` → 480×480 Pixel, 16 bpp; logisch in **9 Tiles à 160×160** organisiert.
- `ZK-INKJET-GUI-RES.zkml` → echte TTF (Leelawadee UI).
- `ZK-INKJET-NANO-APP.bin` → proprietärer Container; Carving liefert Fragmente (BMP/OTF/JPEG), keine ELF; XOR hier **nicht** pauschal sinnvoll.
- `ZK-INKJET-NANO-BOOT.bin` → Bootcode; für Grafikdekodierung vermutlich nur indirekt relevant.

## Bisherige Erkenntnisse (Findings)

1. **Kachelstruktur**: UI‑QVGA enthält **3×3 Tiles** (`160×160`) in Serie. Die sichtbare UI entsteht durch Zusammenfügen zu 480×480.
2. **Farben**: Pixel liegen als **BGR565** (5‑6‑5) vor, jedoch vorab mit **XOR 0xAAAA** über jedes 16‑Bit‑Wort verschleiert.
3. **Tile‑Order**: Beste Ergebnisse mit **column‑major** (Index → `ty = idx % 3`, `tx = idx // 3`).
4. **Zeilen‑Phasenfehler**: Nach XOR+Farbraum bleiben **horizontale Versätze** in Schrift/Sprites. Ursache: ein **line‑basierter Phasen‑Shift** der **ungeraden Bildzeilen** (vermutlich Controller/Scanline‑Effekt).
5. **Feinversatz pro Kachelspalte**: Zusätzliche zyklische Shifts je 160‑Pixel‑Spalte glätten Kachel‑Nähte und stabilisieren Text.
6. **Was (noch) nicht passt**: Schriftzüge (z. B. „System Starting“, „Thanks for using… Goodbye“) sind teilweise um 1–2 px je Zeile/Spalte versetzt → es fehlt eine exakte  Phasenregel (Drift oder ein weiteres Bit‑/Nibble‑Mapping).
7. **Nicht hilfreich**: Globales XOR mit anderen Masken (0x5555/0xFFFF), Byte‑Swap, reine  RGB565, Graustufen, 5‑5‑5‑1 / 4‑4‑4‑4 – liefern unplausible  Farben/Muster.
8. **APP/BOOT XOR**: Auf Code‑/Containerdateien wirkt 0xAAAA **nicht** sinnvoll; die XOR‑Maskierung scheint **grafikspezifisch** zu sein.

## Aktuelle Rekonstruktions‑Methode (Näherung)

**Ziel**: Farben korrekt, Kachelraster korrekt, geringe Text‑Versätze (noch kein „Lock‑in“).

### Pipeline (Schritte)

1. **Rohdaten laden** → als `uint16` (Host‑Endian), Länge 480×480.
2. **Tiles bilden** → 9 Blöcke à 160×160 nacheinander aus dem Stream extrahieren.
3. **Kacheln zusammenfügen** → **column‑major** in ein 480×480‑Raster setzen.
4. **XOR‑Descramble** → jedes 16‑Bit‑Wort mit `0xAAAA` verknüpfen.
5. **Odd‑Line‑Shift** → alle **ungeraden Zeilen** zyklisch **horizontal** um `s0` Pixel verschieben (aktuell `s0 ≈ +1…+2`). Optional **Drift**: zusätzlich alle `L` Zeilen `+k` addieren; Reset je 160‑Zeilen‑Block.
6. **Spalten‑Offsets** → jede 160‑Pixel‑Spalte separat zyklisch verschieben: `(d0, d1, d2)` (aktuell beständig nahe **(−2, −1, 0)**).
7. **BGR565 → RGB8** konvertieren (R5/G6/B5 auf 8 Bit skalieren).
8. **Qualitätsprüfung** → visuell (Kachel‑Nähte bei x=160/320, Lesbarkeit der Schrift) und heuristische Kosten (Nahtdifferenzen + Even/Odd‑„Kamm“).

### Aktuell beste Parameter (Stand heute)

- **XOR**: `0xAAAA`
- **Farbraum**: **BGR565** (kein Byte‑Swap)
- **Tile‑Order**: **column‑major**
- **Odd‑Line Basis‑Shift** `s0`: **+1** bis **+2** (Pixel)
- **Drift** `k` (je `L` Zeilen, Reset je 160): häufig **0**; einzelne Treffer mit `k=+1`, `L=32`
- **Spalten‑Offsets (d0, d1, d2)**: typischerweise **(−2, −1, 0)** (Feintuning ±1 nötig)

> **Interpretation:** Hintergrund (Kurven) wird durchgehend korrekt; die Schrift zeigt  Rest‑Versatz. Das deutet auf eine zusätzliche Phasenregel (z. B. lineare Drift je 160er‑Block, Serpentinen‑Scan oder Bit/Nibble‑Permutation)  hin, die noch nicht modelliert ist.

## Reproduzierbarkeit (ohne Code‑Listing)

- **Voraussetzungen**: Python 3, NumPy, Pillow.
- **Werkzeuge**: wir nutzen ein Suchskript, das per CLI die Parameterbereiche durchläuft und die Top‑N Ergebnisse als PNG speichert.
- **Empfohlene Startbereiche** (für schnelle Läufe):
  - `s0 ∈ [−4 … +4]`
  - `k ∈ {−1, 0, +1}` bei `L ∈ {32}` (danach `L` variieren)
  - `d0, d1, d2 ∈ [−3 … +3]`
- **Bewertung**: Minimierung der Nahtkosten an x=160/320 (|links−rechts|), mit Zusatzgewicht gegenüber Even/Odd‑Differenzen.
- **Aufruf‑Hinweis**: Listenargumente **mit Gleichheitszeichen** übergeben (z. B. `--k_set=-1,0,1`) – sonst interpretiert der Parser negative Werte als neue Optionen.

## Offene Hypothesen

- **Drift‑Modell**: Linear‑/Treppen‑Drift je 160er‑Block (Parameter `k`, `L`) – bisher nicht stabil verifiziert.
- **Serpentin‑Layout**: Zeilenweise Richtungswechsel (LTR/RTL) oder blockweise Serpentin – muss ggf. ergänzt werden.
- **Nibble‑Permutation**: Vertauschung innerhalb der Bytes (High/Low‑Nibble) vor/nach XOR möglich.
- **Weitere XOR‑Patterns**: Checkerboard (zeilen‑/spaltenweise alternierend) – erste Tests zeigten keine klaren Vorteile.

## Nächste Schritte (konkret)

1. **Suchraum eng → weit**: Mit kleinen Ranges starten; nur erweitern, wenn Score sichtbar fällt und die Schrift stabiler wird.
2. **Serpentin‑Option ergänzen**: Pro Zeile die Leserichtung invertieren (jede 2. Zeile) und neu bewerten.
3. **Nibble‑Swap testen**: Low/High/Both vor dem XOR einbauen und die Top‑Scans vergleichen.
4. **Code‑Analyse**: In `APP.bin/BOOT.bin` nach Routinen suchen, die auf `0xAAAA`/`0x5555` testen oder 16‑Bit‑Pixel verarbeiten (Disassembler; Strings/Immediates). Das liefert wahrscheinlich die echte Phasenregel.
5. **Weitere UI‑Blobs**: `ZK-INKJET-UI.bin` o. ä. mit derselben Pipeline prüfen – evtl. leichteres Testmotiv (Icons) statt Vollbild.

## Troubleshooting

- **„Skript hängt“**: Meist sind die Bereiche zu groß. Ranges verkleinern (s0, d‑Span, k/L) und Top‑N stark begrenzen.
- **Falsche Argument‑Parsing**: Kommalisten mit `=` übergeben (`--k_set=-2,-1,0,1,2`), sonst werden negative Zahlen als neue Flags gelesen.
- **Leistung**: Ergebnisse im Lauf konsequent auf die besten ~4×Top‑N heruntertrimmen – Speicher & Zeit sparen.

## Kurz‑Glossar

- **BGR565**: 16‑Bit‑Farbformat (5 Bit Blau, 6 Bit Grün, 5 Bit Rot) – hier tatsächlich **B→G→R**.
- **XOR 0xAAAA**: Einfache bitweise Verschleierung über jedes 16‑Bit‑Pixelwort.
- **column‑major**: Kachelreihenfolge spaltenweise (Index 0..8 → erst Ty, dann Tx: `ty = idx % 3`, `tx = idx // 3`).
- **Odd‑Line‑Shift** `s0`/`k`/`L`: Horizontale Phasenverschiebung nur für ungerade Bildzeilen; optional Drift `k` in Stufen alle `L` Zeilen; Reset pro 160‑Zeilen‑Block.
- **(d0, d1, d2)**: Zyklische Feinoffsets je Kachelspalte (x∈[0:160], [160:320], [320:480]).

------

**Stand:** 06.10.2025 • **Autor:** Nina (Sparring) • **Status:** Farben & Kacheln korrekt; Schrift noch mit Restversatz. Methode reproduzierbar; Feintuning/Regel noch ausstehend.
