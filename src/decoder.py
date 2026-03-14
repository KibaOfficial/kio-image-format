# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from PIL import Image
from header import KIF_SIGNATURE, Channels, Compression
from rle import rle_decode
import struct


def decode(input_path: str, output_path: str):
    with open(input_path, "rb") as f:
        # validate signature
        sig = f.read(8)
        if sig != KIF_SIGNATURE:
            raise ValueError(f"[KIF] invalid signature: {sig.hex()}")

        # read header (12 bytes)
        header = f.read(12)
        width, height, channels, bit_depth, compression, _ = struct.unpack(">IIBBBB", header)

        print(f"[KIF] decoding: {input_path}")
        print(f"      size:     {width}x{height}")
        print(f"      channels: {channels}")
        print(f"      bitdepth: {bit_depth}")
        print(f"      compression: {'RLE' if compression == Compression.RLE else 'none'}")

        # read pixel data
        pixel_data = f.read()

    # decompress if needed
    if compression == Compression.RLE:
        pixel_data = rle_decode(pixel_data, channels)

    # determine PIL mode
    if channels == Channels.RGBA:
        mode = "RGBA"
    elif channels == Channels.RGB:
        mode = "RGB"
    else:
        raise ValueError(f"[KIF] unsupported channel count: {channels}")

    # reconstruct image
    img = Image.frombytes(mode, (width, height), pixel_data)
    img.save(output_path)

    print(f"      saved to: {output_path}")