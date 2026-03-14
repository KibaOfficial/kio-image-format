# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import struct
from core.header import KIF_SIGNATURE, Channels, Compression
from chunk import CHUNK_HEAD, CHUNK_DATA, CHUNK_META, read_all_chunks


# ============================================================
# HELPERS
# ============================================================

def fmt_size(b):
    if b >= 1_000_000:
        return f"{b / 1_000_000:.2f} MB"
    elif b >= 1_000:
        return f"{b / 1_000:.2f} KB"
    return f"{b} B"


def channel_label(c):
    return { Channels.GRAYSCALE: "Grayscale", Channels.RGB: "RGB", Channels.RGBA: "RGBA" }.get(c, f"Unknown ({c})")


def compression_label(c):
    return { Compression.NONE: "None", Compression.RLE: "RLE" }.get(c, f"Unknown ({c})")


# ============================================================
# INFO V1
# ============================================================

def info_v1(input_path: str, f):
    header = f.read(12)
    width, height, channels, bit_depth, compression, _ = struct.unpack(">IIBBBB", header)

    raw_bytes  = width * height * channels * (bit_depth // 8)
    file_bytes = os.path.getsize(input_path)
    pixel_data_bytes = file_bytes - 20  # sig + header
    ratio = (1 - pixel_data_bytes / raw_bytes) * 100 if raw_bytes > 0 else 0

    print(f"KIF Image (v1)")
    print(f"--------------")
    print(f"  File:          {input_path}")
    print(f"  Width:         {width}px")
    print(f"  Height:        {height}px")
    print(f"  Channels:      {channel_label(channels)}")
    print(f"  Bit Depth:     {bit_depth}")
    print(f"  Compression:   {compression_label(compression)}")
    print(f"")
    print(f"  Raw Size:      {fmt_size(raw_bytes)}")
    print(f"  File Size:     {fmt_size(file_bytes)}")
    if compression != Compression.NONE:
        print(f"  Saved:         {ratio:.1f}%")


# ============================================================
# INFO V2
# ============================================================

def info_v2(input_path: str, f):
    chunks = read_all_chunks(f)

    if CHUNK_HEAD not in chunks:
        raise ValueError("[KIF v2] missing HEAD chunk")

    head = chunks[CHUNK_HEAD]
    width, height, channels, bit_depth, compression, _ = struct.unpack(">IIBBBB", head)

    raw_bytes  = width * height * channels * (bit_depth // 8)
    file_bytes = os.path.getsize(input_path)
    pixel_data_bytes = len(chunks.get(CHUNK_DATA, b""))
    ratio = (1 - pixel_data_bytes / raw_bytes) * 100 if raw_bytes > 0 else 0

    # optional meta
    meta = {}
    if CHUNK_META in chunks:
        for pair in chunks[CHUNK_META].decode("utf-8").split("\x00"):
            if "=" in pair:
                k, _, v = pair.partition("=")
                meta[k.strip()] = v.strip()

    print(f"KIF Image (v2)")
    print(f"--------------")
    print(f"  File:          {input_path}")
    print(f"  Width:         {width}px")
    print(f"  Height:        {height}px")
    print(f"  Channels:      {channel_label(channels)}")
    print(f"  Bit Depth:     {bit_depth}")
    print(f"  Compression:   {compression_label(compression)}")
    if meta:
        print(f"  Metadata:")
        for k, v in meta.items():
            print(f"    {k}: {v}")
    print(f"")
    print(f"  Raw Size:      {fmt_size(raw_bytes)}")
    print(f"  File Size:     {fmt_size(file_bytes)}")
    if compression != Compression.NONE:
        print(f"  Saved:         {ratio:.1f}%")


# ============================================================
# INFO (auto-detect v1/v2)
# ============================================================

def info(input_path: str):
    with open(input_path, "rb") as f:
        sig = f.read(8)
        if sig != KIF_SIGNATURE:
            raise ValueError(f"[KIF] invalid signature: {sig.hex()}")

        # peek at next 4 bytes to detect version
        peek = f.read(4)

        if peek == CHUNK_HEAD:
            # v2 — chunk based, put back the 4 bytes by seeking
            f.seek(8)
            info_v2(input_path, f)
        else:
            # v1 — fixed header, peek was first 4 bytes of header
            remaining = f.read(8)
            header = peek + remaining
            width, height, channels, bit_depth, compression, _ = struct.unpack(">IIBBBB", header)

            raw_bytes  = width * height * channels * (bit_depth // 8)
            file_bytes = os.path.getsize(input_path)
            pixel_data_bytes = file_bytes - 20
            ratio = (1 - pixel_data_bytes / raw_bytes) * 100 if raw_bytes > 0 else 0

            print(f"KIF Image (v1)")
            print(f"--------------")
            print(f"  File:          {input_path}")
            print(f"  Width:         {width}px")
            print(f"  Height:        {height}px")
            print(f"  Channels:      {channel_label(channels)}")
            print(f"  Bit Depth:     {bit_depth}")
            print(f"  Compression:   {compression_label(compression)}")
            print(f"")
            print(f"  Raw Size:      {fmt_size(raw_bytes)}")
            print(f"  File Size:     {fmt_size(file_bytes)}")
            if compression != Compression.NONE:
                print(f"  Saved:         {ratio:.1f}%")