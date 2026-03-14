<!--
 Copyright (c) 2026 KibaOfficial

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
-->

<div align="center">

# 🖼️ KIF — Kio Image Format

**A minimal, open, and hackable binary image format.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-2.0.0-green.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-yellow.svg)

</div>

---

## What is KIF?

KIF (Kio Image Format) is a custom binary image format built from scratch.
It comes in two versions:

- **KIF v1** — fixed 12-byte header, raw pixel data, simple and fast
- **KIF v2** — chunk-based extensible format with CRC32 validation, optional metadata, and future-proof design

Both share the same 8-byte file signature and support RGB, RGBA, Grayscale, and RLE compression.

It was designed as a learning project to understand how image formats like PNG and JPEG
actually work at the binary level: signatures, headers, chunk systems, pixel encoding, and compression.

---

## File Structure

Every `.kif` file follows this exact layout:

```
[Signature]   8 bytes
[Header]     12 bytes   ← KIF v1
[ImageData]  variable
```

### KIF v2 File Structure

KIF v2 uses a chunk-based layout — extensible and CRC-validated:

```
[Signature]   8 bytes
[HEAD chunk]  type + length + data + crc32
[META chunk]  optional — key=value metadata
[DATA chunk]  type + length + pixel data + crc32
[END  chunk]  type + length + crc32
```

Each chunk follows this layout:
```
[type]    4 bytes  ASCII (e.g. "HEAD", "DATA")
[length]  4 bytes  uint32 big-endian
[data]    variable
[crc32]   4 bytes  CRC32 over type + data
```

### Signature

```
89 4B 49 46 0D 0A 1A 0A
```

| Byte | Value | Description              |
|------|-------|--------------------------|
| 0    | `89`  | Binary file indicator    |
| 1    | `4B`  | ASCII `K`                |
| 2    | `49`  | ASCII `I`                |
| 3    | `46`  | ASCII `F`                |
| 4    | `0D`  | CR — Carriage Return     |
| 5    | `0A`  | LF — Line Feed           |
| 6    | `1A`  | SUB — DOS EOF marker     |
| 7    | `0A`  | LF — Unix line ending    |

The signature is designed to detect text/binary corruption and line-ending conversions —
the same approach used by PNG.

### Header

All multi-byte integers are stored in **big-endian** byte order.

| Field         | Type     | Size    | Description                        |
|---------------|----------|---------|------------------------------------|
| `width`       | `uint32` | 4 bytes | Image width in pixels              |
| `height`      | `uint32` | 4 bytes | Image height in pixels             |
| `channels`    | `uint8`  | 1 byte  | `1` = Grayscale, `3` = RGB, `4` = RGBA |
| `bit_depth`   | `uint8`  | 1 byte  | Bits per channel (currently: `8`) |
| `compression` | `uint8`  | 1 byte  | `0` = None, `1` = RLE             |
| `reserved`    | `uint8`  | 1 byte  | Must be `0` in KIF v1             |

### Image Data

Pixels are stored row by row, **top to bottom, left to right**.

```
RGB:  R G B R G B R G B ...
RGBA: R G B A R G B A ...
```

Uncompressed data size:
```
width × height × channels × (bit_depth / 8)
```

---

## Installation

```bash
git clone https://github.com/kibaofficial/kio-image-format.git
cd kio-image-format
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install pillow customtkinter
```

---

## Usage

All commands are run via `src/main.py`.

### Encode

Convert any image to KIF:

```bash
python src/main.py encode input.png output.kif
```

With RLE compression:

```bash
python src/main.py encode input.png output.kif --compression rle
# or shorthand:
python src/main.py encode input.png output.kif -c rle
```

As grayscale:

```bash
python src/main.py encode input.png output.kif --grayscale
# or shorthand:
python src/main.py encode input.png output.kif -g
```

Combine both:

```bash
python src/main.py encode input.png output.kif -c rle -g
```

### Decode

Convert a KIF file back to an image:

```bash
python src/main.py decode input.kif output.png
```

### Convert

Shorthand for encoding any supported image format to KIF:

```bash
python src/main.py convert input.jpg output.kif
python src/main.py convert input.jpg output.kif -c rle
```

### Encode v2

Encode to KIF v2 (chunk-based, CRC validated, optional metadata):

```bash
python src/main.py encode-v2 input.png output.kif
python src/main.py encode-v2 input.png output.kif -c rle -g
python src/main.py encode-v2 input.png output.kif --meta author=kiba tool=KIF version=2
```

### Decode v2

```bash
python src/main.py decode-v2 input.kif output.png
```

Output with metadata:
```
[KIF v2] decoding: image.kif
         size:        736x1121
         channels:    3
         bitdepth:    8
         compression: none
         metadata:
           author: kiba
           tool: KIF
           version: 2
         saved to: output.png
```

> `info` auto-detects v1 vs v2 — no flags needed.

Display metadata of a KIF file without decoding it:

```bash
python src/main.py info image.kif
```

Output:
```
KIF Image
---------
  File:          image.kif
  Width:         736px
  Height:        1121px
  Channels:      RGB
  Bit Depth:     8
  Compression:   RLE

  Raw Size:      2.48 MB
  File Size:     1.62 MB
  Saved:         34.7%
```

### Compare

Compare two images pixel by pixel — useful for verifying encode/decode integrity:

```bash
python src/main.py compare original.jpeg decoded.png
```

Output:
```
KIF Compare
-----------
  A:               original.jpeg
  B:               decoded.png

  Pixels compared: 825,056
  Differences:     0
  Status:          identical ✓
```

### Stats

Show RLE analysis and compression efficiency of a KIF file:

```bash
python src/main.py stats image.kif
```

Output:
```
KIF Stats
---------
  File:              image.kif
  Size:              736x1121
  Pixels:            825,056
  Unique colors:     24,011

  RLE Analysis:
  Total runs:        404,319
  Average run:       2.0 pixels
  Longest run:       90 pixels
  Shortest run:      1 pixels
  Single px runs:    273,865 (67.7%)

  RLE Efficiency:
  Raw size:          2.48 MB
  RLE size:          1.62 MB
  Saved:             34.7%
```

### Test Suite

Run all encoding/decoding variants and print a full summary:

```bash
python src/test.py
```

Generates all v1 and v2 variants, runs info + stats on each, compares decoded output against the original, and prints a size summary:

```
  Variant                      File Size
  ------------------------- ------------
  [v1] rgb_raw                    2.48 MB
  [v1] rgb_rle                    1.62 MB
  [v1] gray_raw                   0.83 MB
  [v1] gray_rle                   0.73 MB
  [v2] v2_rgb_raw                 2.48 MB
  [v2] v2_rgb_rle                 1.62 MB
  [v2] v2_gray_raw                0.83 MB
  [v2] v2_gray_rle                0.73 MB
  [v2] v2_rgb_meta                2.48 MB
```

| Flag              | Description                                      |
|-------------------|--------------------------------------------------|
| `-c none`         | No compression — raw pixel data (default)        |
| `-c rle`          | Run-Length Encoding — best for flat colors/logos |

> **Note:** RLE works best on images with large uniform areas (logos, UI, pixel art).
> For photos with lots of color variation it may not reduce file size significantly.

### Benchmark

Compare encode/decode speed and file size across all KIF variants vs PNG:

```bash
python src/benchmark.py
```

Results on a 736×1121 JPEG (averaged over 5 runs):

```
  Variant                  Encode     Decode       Size
  -------------------- ---------- ---------- ----------
  KIF v1 raw RGB           12.8ms     55.7ms     2.48MB
  KIF v1 RLE RGB          392.3ms    162.3ms     1.62MB
  KIF v2 raw RGB           10.5ms     43.5ms     2.48MB
  KIF v2 RLE RGB          289.2ms    139.6ms     1.62MB
  PNG baseline             39.6ms     11.2ms     0.44MB
```

> KIF v2 is faster than v1 in all categories — the chunk overhead is minimal and CRC32 runs via zlib (C implementation).
> RLE is slower in Python due to per-pixel looping. A C/Rust implementation would be significantly faster.

### View

Open a KIF file in the built-in GUI viewer:

```bash
python src/main.py view image.kif
```

- Dark mode GUI powered by CustomTkinter
- Auto-scales image to fit the window
- Info bar shows: filename, resolution, channels, bit depth, compression, file size, and compression savings
- Window title displays the filename

> Requires `customtkinter`: `pip install customtkinter`

---

## Project Structure

```
kif/
 ├── src/
 │    ├── header.py       # Format spec, constants, pack/unpack (v1)
 │    ├── chunk.py        # Chunk engine with CRC32 (v2)
 │    ├── encoder.py      # Image → KIF v1
 │    ├── encoder_v2.py   # Image → KIF v2 (chunk-based)
 │    ├── decoder.py      # KIF v1 → Image
 │    ├── decoder_v2.py   # KIF v2 → Image
 │    ├── converter.py    # Any image → KIF (uses encoder internally)
 │    ├── rle.py          # RLE compression / decompression
 │    ├── info.py         # KIF metadata display (auto-detects v1/v2)
 │    ├── compare.py      # Pixel-by-pixel image comparison
 │    ├── stats.py        # RLE analysis and compression stats
 │    ├── test.py         # Full test suite for all variants (v1 + v2)
 │    ├── benchmark.py    # Encode/decode speed benchmark vs PNG
 │    ├── viewer.py       # CustomTkinter GUI viewer
 │    └── main.py         # CLI entry point
 └── README.md
```

---

## Roadmap

- [x] KIF v1 — raw pixel format (RGB / RGBA, 8-bit)
- [x] RLE compression support
- [x] Info command (display KIF metadata without decoding)
- [x] Pixel compare tool (regression testing)
- [x] Grayscale support
- [x] Stats command (RLE analysis and compression efficiency)
- [x] Test suite (all variants, auto compare, summary)
- [x] Benchmarks (encode/decode speed vs PNG)
- [x] GUI Viewer (CustomTkinter, dark mode, info bar)
- [x] KIF v2 — chunk-based extensible format with CRC32 + metadata
- [ ] KIF v2 viewer support
- [ ] 16-bit color depth
- [ ] C / Rust decoder for performance

---

## License

MIT © 2026 [KibaOfficial](https://github.com/kibaofficial)