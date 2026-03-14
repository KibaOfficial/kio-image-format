# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import struct
from header import KIF_SIGNATURE, Channels, Compression


def info(input_path: str):
    with open(input_path, "rb") as f:
        # validate signature
        sig = f.read(8)
        if sig != KIF_SIGNATURE:
            raise ValueError(f"[KIF] invalid signature: {sig.hex()}")

        # read header (12 bytes)
        header = f.read(12)
        width, height, channels, bit_depth, compression, _ = struct.unpack(">IIBBBB", header)

    # map channels to label
    channel_label = {
        Channels.GRAYSCALE: "Grayscale",
        Channels.RGB:       "RGB",
        Channels.RGBA:      "RGBA",
    }.get(channels, f"Unknown ({channels})")

    # map compression to label
    compression_label = {
        Compression.NONE: "None",
        Compression.RLE:  "RLE",
    }.get(compression, f"Unknown ({compression})")

    # calculate sizes
    raw_bytes = width * height * channels * (bit_depth // 8)
    file_bytes = os.path.getsize(input_path)
    overhead = 8 + 12  # signature + header

    pixel_data_bytes = file_bytes - overhead
    ratio = (1 - pixel_data_bytes / raw_bytes) * 100 if raw_bytes > 0 else 0

    def fmt_size(b):
        if b >= 1_000_000:
            return f"{b / 1_000_000:.2f} MB"
        elif b >= 1_000:
            return f"{b / 1_000:.2f} KB"
        return f"{b} B"

    print(f"KIF Image")
    print(f"---------")
    print(f"  File:          {input_path}")
    print(f"  Width:         {width}px")
    print(f"  Height:        {height}px")
    print(f"  Channels:      {channel_label}")
    print(f"  Bit Depth:     {bit_depth}")
    print(f"  Compression:   {compression_label}")
    print(f"")
    print(f"  Raw Size:      {fmt_size(raw_bytes)}")
    print(f"  File Size:     {fmt_size(file_bytes)}")
    if compression != Compression.NONE:
        print(f"  Saved:         {ratio:.1f}%")