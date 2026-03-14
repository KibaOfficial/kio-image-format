<!--
 Copyright (c) 2026 KibaOfficial

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
-->

<div align="center">

# 🖼️ KIF — Kio Image Format

**A minimal, open, and hackable binary image format.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)
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
| `compression` | `uint8`  | 1 byte  | `0` = None, `1` = RLE (planned)   |
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

### Decode

Convert a KIF file back to an image:

```bash
python src/main.py decode input.kif output.png
```

### Convert

Shorthand for encoding any supported image format to KIF:

```bash
python src/main.py convert input.jpg output.kif
```

---

## Project Structure

```
kif/
 ├── src/
 │    ├── header.py       # Format spec, constants, pack/unpack
 │    ├── encoder.py      # Image → KIF
 │    ├── decoder.py      # KIF → Image
 │    ├── converter.py    # Any image → KIF (uses encoder internally)
 │    └── main.py         # CLI entry point
 └── README.md
```

---

## Roadmap

- [x] KIF v1 — raw pixel format (RGB / RGBA, 8-bit)
- [ ] RLE compression support
- [ ] 16-bit color depth
- [ ] Grayscale support
- [ ] Metadata / EXIF chunk
- [ ] KIF v2 — chunk-based extensible format
- [ ] C / Rust decoder for performance

---

## License

MIT © 2026 [KibaOfficial](https://github.com/kibaofficial)