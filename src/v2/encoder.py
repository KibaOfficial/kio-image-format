# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import struct
from PIL import Image
from core.header import KIF_SIGNATURE, Channels, Compression
from chunk import write_chunk, CHUNK_HEAD, CHUNK_DATA, CHUNK_END, CHUNK_META
from core.rle import rle_encode


# ============================================================
# HEAD CHUNK DATA
# ============================================================

def pack_head(width: int, height: int, channels: int, bit_depth: int, compression: int) -> bytes:
    """Pack HEAD chunk data — 12 bytes, same layout as v1 header"""
    return struct.pack(">IIBBBB", width, height, channels, bit_depth, compression, 0)


# ============================================================
# META CHUNK DATA
# ============================================================

def pack_meta(metadata: dict) -> bytes:
    """Pack META chunk — key=value pairs, UTF-8 encoded, null separated"""
    pairs = []
    for k, v in metadata.items():
        pairs.append(f"{k}={v}")
    return "\x00".join(pairs).encode("utf-8")


# ============================================================
# ENCODER
# ============================================================

def encode(
    input_path: str,
    output_path: str,
    compression: int = Compression.NONE,
    grayscale: bool = False,
    metadata: dict = None,
):
    # load image
    img = Image.open(input_path)

    # convert mode
    if grayscale:
        img = img.convert("L")
        channels = Channels.GRAYSCALE
    elif img.mode == "RGBA":
        channels = Channels.RGBA
    else:
        img = img.convert("RGB")
        channels = Channels.RGB

    width, height = img.size
    bit_depth = 8
    pixel_data = img.tobytes()

    # apply compression
    if compression == Compression.RLE:
        pixel_data = rle_encode(pixel_data, channels)
        compression_label = "RLE"
    else:
        compression_label = "none"

    channel_label = {
        Channels.GRAYSCALE: "Grayscale",
        Channels.RGB:       "RGB",
        Channels.RGBA:      "RGBA",
    }.get(channels, "Unknown")

    # write KIF v2 file
    with open(output_path, "wb") as f:
        # signature (same as v1)
        f.write(KIF_SIGNATURE)

        # HEAD chunk
        write_chunk(f, CHUNK_HEAD, pack_head(width, height, channels, bit_depth, compression))

        # META chunk (optional)
        if metadata:
            write_chunk(f, CHUNK_META, pack_meta(metadata))

        # DATA chunk
        write_chunk(f, CHUNK_DATA, pixel_data)

        # END chunk
        write_chunk(f, CHUNK_END, b"")

    print(f"[KIF v2] encoded: {input_path} -> {output_path}")
    print(f"         size:        {width}x{height}")
    print(f"         channels:    {channel_label}")
    print(f"         compression: {compression_label}")
    print(f"         bytes:       {len(pixel_data)}")