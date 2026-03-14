# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import sys
import time
from PIL import Image
from encoder import encode
from decoder import decode
from header import Compression

# ============================================================
# CONFIG
# ============================================================

INPUT_IMAGE = "img/test.jpeg"
OUT_DIR     = os.path.join("out", "benchmark")
RUNS        = 5  # average over N runs for accuracy

# ============================================================
# SUPPRESS OUTPUT
# ============================================================

class SuppressOutput:
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        return self

    def __exit__(self, *args):
        sys.stdout.close()
        sys.stdout = self._stdout

# ============================================================
# HELPERS
# ============================================================

def divider(title: str = ""):
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")
    else:
        print(f"\n{'-' * 60}")


def avg_ms(times: list) -> float:
    return (sum(times) / len(times)) * 1000


def benchmark_encode(input_path: str, output_path: str, compression: int, grayscale: bool):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        with SuppressOutput():
            encode(input_path, output_path, compression, grayscale)
        times.append(time.perf_counter() - start)
    size = os.path.getsize(output_path)
    return avg_ms(times), size


def benchmark_decode(input_path: str, output_path: str):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        with SuppressOutput():
            decode(input_path, output_path)
        times.append(time.perf_counter() - start)
    return avg_ms(times)


def benchmark_png_encode(input_path: str, output_path: str):
    img = Image.open(input_path).convert("RGB")
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        img.save(output_path, format="PNG")
        times.append(time.perf_counter() - start)
    size = os.path.getsize(output_path)
    return avg_ms(times), size


def benchmark_png_decode(input_path: str):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        img = Image.open(input_path)
        img.load()
        times.append(time.perf_counter() - start)
    return avg_ms(times)


# ============================================================
# MAIN
# ============================================================

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"KIF Benchmark")
    print(f"=============")
    print(f"Input:  {INPUT_IMAGE}")
    print(f"Runs:   {RUNS}x per variant (averaged)")

    results = []

    # --------------------------------------------------------
    # KIF raw RGB
    # --------------------------------------------------------
    divider("KIF raw RGB")
    kif_raw = os.path.join(OUT_DIR, "bench_rgb_raw.kif")
    dec_raw = os.path.join(OUT_DIR, "bench_rgb_raw_decoded.png")
    enc_ms, enc_size = benchmark_encode(INPUT_IMAGE, kif_raw, Compression.NONE, False)
    dec_ms = benchmark_decode(kif_raw, dec_raw)
    print(f"  Encode: {enc_ms:.1f} ms   Decode: {dec_ms:.1f} ms   Size: {enc_size / 1_000_000:.2f} MB")
    results.append(("KIF raw RGB",  enc_ms, dec_ms, enc_size))

    # --------------------------------------------------------
    # KIF RLE RGB
    # --------------------------------------------------------
    divider("KIF RLE RGB")
    kif_rle = os.path.join(OUT_DIR, "bench_rgb_rle.kif")
    dec_rle = os.path.join(OUT_DIR, "bench_rgb_rle_decoded.png")
    enc_ms, enc_size = benchmark_encode(INPUT_IMAGE, kif_rle, Compression.RLE, False)
    dec_ms = benchmark_decode(kif_rle, dec_rle)
    print(f"  Encode: {enc_ms:.1f} ms   Decode: {dec_ms:.1f} ms   Size: {enc_size / 1_000_000:.2f} MB")
    results.append(("KIF RLE RGB",  enc_ms, dec_ms, enc_size))

    # --------------------------------------------------------
    # KIF raw Grayscale
    # --------------------------------------------------------
    divider("KIF raw Grayscale")
    kif_gray = os.path.join(OUT_DIR, "bench_gray_raw.kif")
    dec_gray = os.path.join(OUT_DIR, "bench_gray_raw_decoded.png")
    enc_ms, enc_size = benchmark_encode(INPUT_IMAGE, kif_gray, Compression.NONE, True)
    dec_ms = benchmark_decode(kif_gray, dec_gray)
    print(f"  Encode: {enc_ms:.1f} ms   Decode: {dec_ms:.1f} ms   Size: {enc_size / 1_000_000:.2f} MB")
    results.append(("KIF gray raw", enc_ms, dec_ms, enc_size))

    # --------------------------------------------------------
    # KIF RLE Grayscale
    # --------------------------------------------------------
    divider("KIF RLE Grayscale")
    kif_gray_rle = os.path.join(OUT_DIR, "bench_gray_rle.kif")
    dec_gray_rle = os.path.join(OUT_DIR, "bench_gray_rle_decoded.png")
    enc_ms, enc_size = benchmark_encode(INPUT_IMAGE, kif_gray_rle, Compression.RLE, True)
    dec_ms = benchmark_decode(kif_gray_rle, dec_gray_rle)
    print(f"  Encode: {enc_ms:.1f} ms   Decode: {dec_ms:.1f} ms   Size: {enc_size / 1_000_000:.2f} MB")
    results.append(("KIF gray RLE", enc_ms, dec_ms, enc_size))

    # --------------------------------------------------------
    # PNG (baseline)
    # --------------------------------------------------------
    divider("PNG (baseline)")
    png_path = os.path.join(OUT_DIR, "bench_baseline.png")
    enc_ms, enc_size = benchmark_png_encode(INPUT_IMAGE, png_path)
    dec_ms = benchmark_png_decode(png_path)
    print(f"  Encode: {enc_ms:.1f} ms   Decode: {dec_ms:.1f} ms   Size: {enc_size / 1_000_000:.2f} MB")
    results.append(("PNG baseline", enc_ms, dec_ms, enc_size))

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------
    divider("SUMMARY")
    print(f"\n  {'Variant':<20} {'Encode':>10} {'Decode':>10} {'Size':>10}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*10}")
    for name, enc, dec, size in results:
        print(f"  {name:<20} {enc:>8.1f}ms {dec:>8.1f}ms {size / 1_000_000:>8.2f}MB")

    print(f"\n✓ Benchmark complete ({RUNS} runs averaged)")


if __name__ == "__main__":
    main()