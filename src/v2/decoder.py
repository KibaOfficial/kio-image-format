# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import struct
from PIL import Image
from header import KIF_SIGNATURE, Channels, Compression
from chunk import read_all_chunks, CHUNK_HEAD, CHUNK_DATA, CHUNK_META, CHUNK_END
from rle import rle_decode


# ============================================================
# UNPACK HEAD CHUNK
# ============================================================

def unpack_head(data: bytes):
    width, height, channels, bit_depth, compression, _ = struct.unpack(">IIBBBB", data)
    return width, height, channels, bit_depth, compression


# ============================================================
# UNPACK META CHUNK
# ============================================================

def unpack_meta(data: bytes) -> dict:
    meta = {}
    for pair in data.decode("utf-8").split("\x00"):
        if "=" in pair:
            k, _, v = pair.partition("=")
            meta[k.strip()] = v.strip()
    return meta


# ============================================================
# DECODER
# ============================================================

def decode_v2(input_path: str, output_path: str):
    with open(input_path, "rb") as f:
        # validate signature
        sig = f.read(8)
        if sig != KIF_SIGNATURE:
            raise ValueError(f"[KIF v2] invalid signature: {sig.hex()}")

        # read all chunks
        chunks = read_all_chunks(f)

    # HEAD is required
    if CHUNK_HEAD not in chunks:
        raise ValueError("[KIF v2] missing HEAD chunk")
    if CHUNK_DATA not in chunks:
        raise ValueError("[KIF v2] missing DATA chunk")

    width, height, channels, bit_depth, compression = unpack_head(chunks[CHUNK_HEAD])
    pixel_data = chunks[CHUNK_DATA]

    # optional META
    meta = {}
    if CHUNK_META in chunks:
        meta = unpack_meta(chunks[CHUNK_META])

    print(f"[KIF v2] decoding: {input_path}")
    print(f"         size:        {width}x{height}")
    print(f"         channels:    {channels}")
    print(f"         bitdepth:    {bit_depth}")
    print(f"         compression: {'RLE' if compression == Compression.RLE else 'none'}")
    if meta:
        print(f"         metadata:")
        for k, v in meta.items():
            print(f"           {k}: {v}")

    # decompress if needed
    if compression == Compression.RLE:
        pixel_data = rle_decode(pixel_data, channels)

    # validate size
    expected = width * height * channels * (bit_depth // 8)
    if len(pixel_data) != expected:
        raise ValueError(
            f"[KIF v2] pixel data size mismatch: expected {expected}, got {len(pixel_data)}"
        )

    # determine PIL mode
    mode_map = {
        Channels.GRAYSCALE: "L",
        Channels.RGB:       "RGB",
        Channels.RGBA:      "RGBA",
    }
    mode = mode_map.get(channels)
    if not mode:
        raise ValueError(f"[KIF v2] unsupported channel count: {channels}")

    img = Image.frombytes(mode, (width, height), pixel_data)
    img.save(output_path)

    print(f"         saved to:    {output_path}")