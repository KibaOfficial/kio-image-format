# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import sys
from v1.encoder import encode
from v2.encoder import encode_v2
from v1.decoder import decode
from v2.decoder import decode_v2
from tools.info import info
from tools.stats import stats
from tools.compare import compare
from core.header import Compression

# ============================================================
# CONFIG
# ============================================================

INPUT_IMAGE = "img/test.jpeg"
OUT_DIR     = "out"

VARIANTS_V1 = [
    { "name": "rgb_raw",  "compression": Compression.NONE, "grayscale": False },
    { "name": "rgb_rle",  "compression": Compression.RLE,  "grayscale": False },
    { "name": "gray_raw", "compression": Compression.NONE, "grayscale": True  },
    { "name": "gray_rle", "compression": Compression.RLE,  "grayscale": True  },
]

VARIANTS_V2 = [
    { "name": "v2_rgb_raw",  "compression": Compression.NONE, "grayscale": False, "meta": None },
    { "name": "v2_rgb_rle",  "compression": Compression.RLE,  "grayscale": False, "meta": None },
    { "name": "v2_gray_raw", "compression": Compression.NONE, "grayscale": True,  "meta": None },
    { "name": "v2_gray_rle", "compression": Compression.RLE,  "grayscale": True,  "meta": None },
    { "name": "v2_rgb_meta", "compression": Compression.NONE, "grayscale": False, "meta": {"author": "kiba", "tool": "KIF", "version": "2"} },
]

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


# ============================================================
# RUN VARIANTS
# ============================================================

def run_v1(variant: dict):
    name        = variant["name"]
    compression = variant["compression"]
    grayscale   = variant["grayscale"]

    kif_path     = os.path.join(OUT_DIR, f"test_{name}.kif")
    decoded_path = os.path.join(OUT_DIR, f"test_{name}_decoded.png")

    divider(f"[v1] {name.upper()}")

    print(f"\n[1/4] Encoding...")
    encode(INPUT_IMAGE, kif_path, compression, grayscale)

    print(f"\n[2/4] Decoding...")
    decode(kif_path, decoded_path)

    print(f"\n[3/4] Info:")
    info(kif_path)

    print(f"\n[4/4] Stats:")
    stats(kif_path)

    if not grayscale:
        print(f"\n[+] Compare original vs decoded:")
        compare(INPUT_IMAGE, decoded_path)

    return kif_path


def run_v2(variant: dict):
    name        = variant["name"]
    compression = variant["compression"]
    grayscale   = variant["grayscale"]
    meta        = variant["meta"]

    kif_path     = os.path.join(OUT_DIR, f"test_{name}.kif")
    decoded_path = os.path.join(OUT_DIR, f"test_{name}_decoded.png")

    divider(f"[v2] {name.upper()}")

    print(f"\n[1/3] Encoding...")
    encode_v2(INPUT_IMAGE, kif_path, compression, grayscale, meta)

    print(f"\n[2/3] Decoding...")
    decode_v2(kif_path, decoded_path)

    print(f"\n[3/3] Info:")
    info(kif_path)

    if not grayscale:
        print(f"\n[+] Compare original vs decoded:")
        compare(INPUT_IMAGE, decoded_path)

    return kif_path


# ============================================================
# MAIN
# ============================================================

def main():
    if not os.path.exists(INPUT_IMAGE):
        print(f"[ERROR] Input image not found: {INPUT_IMAGE}")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"KIF Test Suite")
    print(f"==============")
    print(f"Input:       {INPUT_IMAGE}")
    print(f"v1 variants: {len(VARIANTS_V1)}")
    print(f"v2 variants: {len(VARIANTS_V2)}")

    results = []

    for variant in VARIANTS_V1:
        kif_path = run_v1(variant)
        results.append({ "name": f"[v1] {variant['name']}", "size": os.path.getsize(kif_path) })

    for variant in VARIANTS_V2:
        kif_path = run_v2(variant)
        results.append({ "name": f"[v2] {variant['name']}", "size": os.path.getsize(kif_path) })

    # summary
    divider("SUMMARY")
    print(f"\n  {'Variant':<25} {'File Size':>12}")
    print(f"  {'-'*25} {'-'*12}")
    for r in results:
        mb = r["size"] / 1_000_000
        print(f"  {r['name']:<25} {mb:>10.2f} MB")

    print(f"\n✓ All variants generated in '{OUT_DIR}/'")


if __name__ == "__main__":
    main()