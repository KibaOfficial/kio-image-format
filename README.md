<!--
 Copyright (c) 2026 KibaOfficial

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
-->

<div align="center">

# 🖼️ KIF — Kio Image Format

**A minimal, open, and hackable binary image format.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-2.1.0-green.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-yellow.svg)
![CSharp](https://img.shields.io/badge/C%23-.NET%2010-purple.svg)

</div>

---

## What is KIF?

KIF (Kio Image Format) is a custom binary image format built from scratch as a learning project to understand how image formats like PNG and JPEG actually work at the binary level: signatures, headers, chunk systems, pixel encoding, and compression.

The format comes in two versions:

- **KIF v1** — fixed 12-byte header, raw pixel data, simple and fast
- **KIF v2** — chunk-based extensible format with CRC32 validation and optional metadata

Both share the same 8-byte file signature and support RGB, RGBA, Grayscale, and RLE compression.

> **Status:** The Python implementation (v1/v2) is feature-complete and no longer actively developed. Active development continues in C# targeting a redesigned KIF v3.

---

## File Structure

### Signature

Every `.kif` file starts with the same 8-byte signature:

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

### KIF v1 Layout

```
[Signature]   8 bytes
[Header]     12 bytes
[ImageData]  variable
```

All multi-byte integers are stored in **big-endian** byte order.

| Field         | Type     | Size    | Description                             |
|---------------|----------|---------|-----------------------------------------|
| `width`       | `uint32` | 4 bytes | Image width in pixels                   |
| `height`      | `uint32` | 4 bytes | Image height in pixels                  |
| `channels`    | `uint8`  | 1 byte  | `1` = Grayscale, `3` = RGB, `4` = RGBA |
| `bit_depth`   | `uint8`  | 1 byte  | Bits per channel (currently: `8`)       |
| `compression` | `uint8`  | 1 byte  | `0` = None, `1` = RLE                  |
| `reserved`    | `uint8`  | 1 byte  | Must be `0` in KIF v1                  |

### KIF v2 Layout

KIF v2 uses a chunk-based layout — extensible and CRC-validated:

```
[Signature]   8 bytes
[HEAD chunk]  type + length + data + crc32
[META chunk]  optional — key=value metadata
[DATA chunk]  type + length + pixel data + crc32
[END  chunk]  type + length + crc32
```

Each chunk:
```
[type]    4 bytes  ASCII (e.g. "HEAD", "DATA")
[length]  4 bytes  uint32 big-endian
[data]    variable
[crc32]   4 bytes  CRC32 over type + data
```

---

## Download

Pre-built binaries (Python-based, v1/v2) are available on the [Releases page](https://github.com/KibaOfficial/kio-image-format/releases/latest).

| File                    | Platform        | Description                          |
|-------------------------|-----------------|--------------------------------------|
| `kif-2.1.0-setup.exe`  | Windows x64     | Installer — adds KIF to PATH         |
| `kif.exe`               | Windows x64     | Portable — no install needed         |
| `kif-linux-x86_64`      | Linux x64       | Portable — no install needed         |

> No Python required — all binaries are self-contained.

---

## Python Implementation (v1/v2) — archived

> ⚠️ The Python implementation is **feature-complete and no longer actively developed**. It serves as the reference implementation for KIF v1 and v2.

### Installation from source

```bash
git clone https://github.com/kibaofficial/kio-image-format.git
cd kio-image-format
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install pillow customtkinter
```

### Commands

All commands are run via `python/main.py`.

```bash
# encode
python python/main.py encode input.png output.kif
python python/main.py encode input.png output.kif -c rle -g

# encode v2 (with optional metadata)
python python/main.py encode-v2 input.png output.kif
python python/main.py encode-v2 input.png output.kif --meta author=kiba tool=KIF

# decode
python python/main.py decode input.kif output.png
python python/main.py decode-v2 input.kif output.png

# tools
python python/main.py info     image.kif
python python/main.py compare  imageA.png imageB.png
python python/main.py stats    image.kif
python python/main.py view     image.kif
python python/main.py test
python python/main.py benchmark
```

### Benchmark results (Python exe, 736×1121 JPEG, 5 runs averaged)

```
  Variant                  Encode     Decode       Size
  -------------------- ---------- ---------- ----------
  KIF v2 raw RGB           11.9ms     46.7ms     2.48MB
  KIF v2 RLE RGB          303.0ms    141.4ms     1.62MB
  PNG baseline             39.6ms     11.1ms     0.44MB
```

---

## C# Implementation (v2/v3) — active development

The C# implementation targets KIF v2 and will be the foundation for the upcoming KIF v3 redesign.
It supports v2 only — no v1 legacy.

### Build

```bash
cd csharp
dotnet build KIF.slnx
```

### Commands

```bash
dotnet run --project csharp/KIF.CLI -- encode input.png output.kif
dotnet run --project csharp/KIF.CLI -- encode input.png output.kif -c rle -g
dotnet run --project csharp/KIF.CLI -- encode input.png output.kif --meta author=kiba tool=KIF
dotnet run --project csharp/KIF.CLI -- decode input.kif output.png
dotnet run --project csharp/KIF.CLI -- info   input.kif
dotnet run --project csharp/KIF.CLI -- compare imageA.png imageB.png
dotnet run --project csharp/KIF.CLI -- stats   input.kif
dotnet run --project csharp/KIF.CLI -- test
dotnet run --project csharp/KIF.CLI -- benchmark
```

### Benchmark results (C# published binary, 736×1121 JPEG, 5 runs averaged)

> Note: end-to-end benchmarks (JPEG load + encode + decode + PNG save), not isolated codec benchmarks.

```
  Variant                  Encode     Decode       Size
  -------------------- ---------- ---------- ----------
  KIF v2 raw RGB           89.7ms    123.4ms     2.48MB
  KIF v2 RLE RGB           60.7ms    107.0ms     1.57MB
  KIF v2 raw Gray          20.1ms     51.5ms     0.83MB
  KIF v2 RLE Gray          25.8ms     58.6ms     0.73MB
```

### Cross-language interoperability

KIF v2 files are fully interoperable between Python and C#:

```
Python encode-v2 → C# decode       ✓  identical pixels
C# encode        → Python decode-v2 ✓  identical pixels
```

---

## Project Structure

```
kio-image-format/
 ├── python/                    # Python reference implementation (archived)
 │    ├── core/
 │    │    ├── header.py        # Format spec, constants, pack/unpack
 │    │    ├── chunk.py         # Chunk engine with CRC32
 │    │    └── rle.py           # RLE compression / decompression
 │    ├── v1/
 │    │    ├── encoder.py       # Image → KIF v1
 │    │    └── decoder.py       # KIF v1 → Image
 │    ├── v2/
 │    │    ├── encoder.py       # Image → KIF v2
 │    │    └── decoder.py       # KIF v2 → Image
 │    ├── tools/
 │    │    ├── converter.py     # Any image → KIF
 │    │    ├── info.py          # Metadata display (auto-detects v1/v2)
 │    │    ├── compare.py       # Pixel-by-pixel comparison
 │    │    ├── stats.py         # RLE analysis
 │    │    ├── test.py          # Full test suite
 │    │    ├── benchmark.py     # Benchmark vs PNG
 │    │    └── viewer.py        # CustomTkinter GUI viewer
 │    └── main.py               # CLI entry point
 │
 ├── csharp/                    # C# implementation (active)
 │    ├── KIF.Core/
 │    │    └── Core/
 │    │         ├── KifSignature.cs
 │    │         ├── KifHeader.cs
 │    │         ├── ChunkType.cs
 │    │         ├── ChunkReader.cs
 │    │         ├── ChunkWriter.cs
 │    │         ├── RleCodec.cs
 │    │         ├── KifEncoder.cs
 │    │         └── KifDecoder.cs
 │    ├── KIF.CLI/
 │    │    └── Program.cs       # CLI entry point
 │    └── KIF.slnx
 │
 ├── installer/
 │    └── kif_installer.iss     # Inno Setup installer script
 ├── kif.spec                   # PyInstaller build spec
 └── README.md
```

---

## Roadmap

### Python (v1 / v2) — complete ✅

- [x] KIF v1 — raw pixel format (RGB / RGBA, 8-bit)
- [x] RLE compression support
- [x] Info, Compare, Stats, Test, Benchmark commands
- [x] GUI Viewer (CustomTkinter, dark mode, v1/v2 auto-detect)
- [x] KIF v2 — chunk-based format with CRC32 + metadata
- [x] Windows installer + Linux binary

### C# (v2 / v3) — active 🔧

- [x] KIF v2 encoder / decoder
- [x] CRC32 chunk validation
- [x] Metadata support
- [x] CLI (encode, decode, info, compare, stats, test, benchmark)
- [x] Cross-language interoperability with Python
- [ ] KIF v3 spec — redesigned from lessons learned
- [ ] NuGet package (`KibaOfficial.KIF`)
- [ ] GitHub Actions (auto build + release)
- [ ] 16-bit color depth
- [ ] Deflate compression
- [ ] Color profiles
- [ ] Animation support

---

## License

MIT © 2026 [KibaOfficial](https://github.com/kibaofficial)