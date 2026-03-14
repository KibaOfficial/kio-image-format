# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import struct
from PIL import Image
from header import KIF_SIGNATURE, Channels, Compression
from rle import rle_encode


def stats(input_path: str):
    with open(input_path, "rb") as f:
        # validate signature
        sig = f.read(8)
        if sig != KIF_SIGNATURE:
            raise ValueError(f"[KIF] invalid signature: {sig.hex()}")

        # read header
        header = f.read(12)
        width, height, channels, bit_depth, compression, _ = struct.unpack(">IIBBBB", header)

        pixel_data = f.read()

    # if RLE compressed, work with raw for stats
    if compression == Compression.RLE:
        from rle import rle_decode
        raw_pixels = rle_decode(pixel_data, channels)
    else:
        raw_pixels = pixel_data

    total_pixels = width * height

    # unique colors
    chunk_size = channels
    pixel_set = set()
    for i in range(0, len(raw_pixels), chunk_size):
        pixel_set.add(raw_pixels[i:i + chunk_size])
    unique_colors = len(pixel_set)

    # RLE run analysis (simulate on raw data)
    rle_data = rle_encode(raw_pixels, channels)

    # parse runs from rle data
    runs = []
    i = 0
    while i < len(rle_data):
        count = rle_data[i]
        runs.append(count)
        i += 1 + channels

    total_runs = len(runs)
    avg_run = sum(runs) / total_runs if total_runs > 0 else 0
    longest_run = max(runs) if runs else 0
    shortest_run = min(runs) if runs else 0
    single_pixel_runs = sum(1 for r in runs if r == 1)

    # compression ratio simulation
    raw_size = total_pixels * channels
    rle_size = len(rle_data)
    ratio = (1 - rle_size / raw_size) * 100

    print(f"KIF Stats")
    print(f"---------")
    print(f"  File:              {input_path}")
    print(f"  Size:              {width}x{height}")
    print(f"  Pixels:            {total_pixels:,}")
    print(f"  Unique colors:     {unique_colors:,}")
    print(f"")
    print(f"  RLE Analysis:")
    print(f"  Total runs:        {total_runs:,}")
    print(f"  Average run:       {avg_run:.1f} pixels")
    print(f"  Longest run:       {longest_run} pixels")
    print(f"  Shortest run:      {shortest_run} pixels")
    print(f"  Single px runs:    {single_pixel_runs:,} ({single_pixel_runs / total_runs * 100:.1f}%)")
    print(f"")
    print(f"  RLE Efficiency:")
    print(f"  Raw size:          {raw_size / 1_000_000:.2f} MB")
    print(f"  RLE size:          {rle_size / 1_000_000:.2f} MB")
    print(f"  Saved:             {ratio:.1f}%")
    if ratio < 0:
        print(f"  ⚠ RLE makes this file larger — low repetition image")