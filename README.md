<!--
 Copyright (c) 2026 KibaOfficial

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
-->

<div align="center">

# 🖼️ KIF — Kio Image Format

**A minimal, open, and hackable binary image format.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.4.0-green.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-yellow.svg)

</div>

---

## What is KIF?

KIF (Kio Image Format) is a custom binary image format built from scratch.
It stores raw pixel data with a fixed signature and a compact 12-byte header —
no bloat, no magic, just pixels.

It was designed as a learning project to understand how image formats like PNG and JPEG
actually work at the binary level: signatures, headers, pixel encoding, and file structure.

---

## File Structure

Every `.kif` file follows this exact layout:

```
[Signature]   8 bytes
[Header]     12 bytes
[ImageData]  variable
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
git clone https://github.com/kibaofficial/kif.git
cd kif
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install pillow
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

### Info

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

Generates all 4 variants (rgb_raw, rgb_rle, gray_raw, gray_rle), runs info + stats on each,
compares RGB decoded output against the original, and prints a size summary:

```
  Variant                 File Size
  -------------------- ------------
  rgb_raw                    2.48 MB
  rgb_rle                    1.62 MB
  gray_raw                   0.83 MB
  gray_rle                   0.73 MB
```

| Flag              | Description                                      |
|-------------------|--------------------------------------------------|
| `-c none`         | No compression — raw pixel data (default)        |
| `-c rle`          | Run-Length Encoding — best for flat colors/logos |

> **Note:** RLE works best on images with large uniform areas (logos, UI, pixel art).
> For photos with lots of color variation it may not reduce file size significantly.

---

## Project Structure

```
kif/
 ├── src/
 │    ├── header.py       # Format spec, constants, pack/unpack
 │    ├── encoder.py      # Image → KIF
 │    ├── decoder.py      # KIF → Image
 │    ├── converter.py    # Any image → KIF (uses encoder internally)
 │    ├── rle.py          # RLE compression / decompression
 │    ├── info.py         # KIF metadata display
 │    ├── compare.py      # Pixel-by-pixel image comparison
 │    ├── stats.py        # RLE analysis and compression stats
 │    ├── test.py         # Full test suite for all variants
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
- [ ] Benchmarks (encode/decode speed vs PNG)
- [ ] 16-bit color depth
- [ ] Metadata / EXIF chunk
- [ ] KIF v2 — chunk-based extensible format
- [ ] C / Rust decoder for performance

---

## License

MIT © 2026 [KibaOfficial](https://github.com/kibaofficial)