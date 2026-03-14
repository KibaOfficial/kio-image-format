# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import sys
import time
from PIL import Image
from encoder import encode
from encoder_v2 import encode_v2
from decoder import decode
from decoder_v2 import decode_v2
from header import Compression

# ============================================================
# CONFIG
# ============================================================

INPUT_IMAGE = "img/test.jpeg"
OUT_DIR     = os.path.join("out", "benchmark")
RUNS        = 5

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


def benchmark_encode_v1(input_path, output_path, compression, grayscale):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        with SuppressOutput():
            encode(input_path, output_path, compression, grayscale)
        times.append(time.perf_counter() - start)
    return avg_ms(times), os.path.getsize(output_path)


def benchmark_decode_v1(input_path, output_path):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        with SuppressOutput():
            decode(input_path, output_path)
        times.append(time.perf_counter() - start)
    return avg_ms(times)


def benchmark_encode_v2(input_path, output_path, compression, grayscale):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        with SuppressOutput():
            encode_v2(input_path, output_path, compression, grayscale)
        times.append(time.perf_counter() - start)
    return avg_ms(times), os.path.getsize(output_path)


def benchmark_decode_v2(input_path, output_path):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        with SuppressOutput():
            decode_v2(input_path, output_path)
        times.append(time.perf_counter() - start)
    return avg_ms(times)


def benchmark_png_encode(input_path, output_path):
    img = Image.open(input_path).convert("RGB")
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        img.save(output_path, format="PNG")
        times.append(time.perf_counter() - start)
    return avg_ms(times), os.path.getsize(output_path)


def benchmark_png_decode(input_path):
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

    variants = [
        ("KIF v1 raw RGB",   lambda o: benchmark_encode_v1(INPUT_IMAGE, o, Compression.NONE, False), "bench_v1_rgb_raw.kif",  lambda i, o: benchmark_decode_v1(i, o), "bench_v1_rgb_raw_dec.png"),
        ("KIF v1 RLE RGB",   lambda o: benchmark_encode_v1(INPUT_IMAGE, o, Compression.RLE,  False), "bench_v1_rgb_rle.kif",  lambda i, o: benchmark_decode_v1(i, o), "bench_v1_rgb_rle_dec.png"),
        ("KIF v2 raw RGB",   lambda o: benchmark_encode_v2(INPUT_IMAGE, o, Compression.NONE, False), "bench_v2_rgb_raw.kif",  lambda i, o: benchmark_decode_v2(i, o), "bench_v2_rgb_raw_dec.png"),
        ("KIF v2 RLE RGB",   lambda o: benchmark_encode_v2(INPUT_IMAGE, o, Compression.RLE,  False), "bench_v2_rgb_rle.kif",  lambda i, o: benchmark_decode_v2(i, o), "bench_v2_rgb_rle_dec.png"),
    ]

    for name, enc_fn, kif_name, dec_fn, dec_name in variants:
        divider(name)
        kif_path = os.path.join(OUT_DIR, kif_name)
        dec_path = os.path.join(OUT_DIR, dec_name)
        enc_ms, enc_size = enc_fn(kif_path)
        dec_ms = dec_fn(kif_path, dec_path)
        print(f"  Encode: {enc_ms:.1f} ms   Decode: {dec_ms:.1f} ms   Size: {enc_size / 1_000_000:.2f} MB")
        results.append((name, enc_ms, dec_ms, enc_size))

    # PNG baseline
    divider("PNG (baseline)")
    png_path = os.path.join(OUT_DIR, "bench_baseline.png")
    enc_ms, enc_size = benchmark_png_encode(INPUT_IMAGE, png_path)
    dec_ms = benchmark_png_decode(png_path)
    print(f"  Encode: {enc_ms:.1f} ms   Decode: {dec_ms:.1f} ms   Size: {enc_size / 1_000_000:.2f} MB")
    results.append(("PNG baseline", enc_ms, dec_ms, enc_size))

    divider("SUMMARY")
    print(f"\n  {'Variant':<20} {'Encode':>10} {'Decode':>10} {'Size':>10}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*10}")
    for name, enc, dec, size in results:
        print(f"  {name:<20} {enc:>8.1f}ms {dec:>8.1f}ms {size / 1_000_000:>8.2f}MB")

    print(f"\n✓ Benchmark complete ({RUNS} runs averaged)")


if __name__ == "__main__":
    main()