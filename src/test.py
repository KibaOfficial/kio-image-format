# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import sys
from encoder import encode
from decoder import decode
from info import info
from stats import stats
from compare import compare
from header import Compression

# ============================================================
# CONFIG
# ============================================================

INPUT_IMAGE = "img/test.jpeg"
OUT_DIR     = "out"

VARIANTS = [
    { "name": "rgb_raw",      "compression": Compression.NONE, "grayscale": False },
    { "name": "rgb_rle",      "compression": Compression.RLE,  "grayscale": False },
    { "name": "gray_raw",     "compression": Compression.NONE, "grayscale": True  },
    { "name": "gray_rle",     "compression": Compression.RLE,  "grayscale": True  },
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


def run_variant(variant: dict):
    name        = variant["name"]
    compression = variant["compression"]
    grayscale   = variant["grayscale"]

    kif_path     = os.path.join(OUT_DIR, f"test_{name}.kif")
    decoded_path = os.path.join(OUT_DIR, f"test_{name}_decoded.png")

    divider(f"Variant: {name.upper()}")

    # encode
    print(f"\n[1/4] Encoding...")
    encode(INPUT_IMAGE, kif_path, compression, grayscale)

    # decode
    print(f"\n[2/4] Decoding...")
    decode(kif_path, decoded_path)

    # info
    print(f"\n[3/4] Info:")
    info(kif_path)

    # stats
    print(f"\n[4/4] Stats:")
    stats(kif_path)

    # compare (only RGB variants — grayscale loses color info so pixel compare vs jpeg won't be identical)
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
    print(f"Input:    {INPUT_IMAGE}")
    print(f"Variants: {len(VARIANTS)}")

    results = []
    for variant in VARIANTS:
        kif_path = run_variant(variant)
        size = os.path.getsize(kif_path)
        results.append({ "name": variant["name"], "size": size })

    # summary
    divider("SUMMARY")
    print(f"\n  {'Variant':<20} {'File Size':>12}")
    print(f"  {'-'*20} {'-'*12}")
    for r in results:
        mb = r["size"] / 1_000_000
        print(f"  {r['name']:<20} {mb:>10.2f} MB")

    print(f"\n✓ All variants generated in '{OUT_DIR}/'")


if __name__ == "__main__":
    main()