# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from PIL import Image
from header import KIF_SIGNATURE, Channels, Compression, pack_header


def encode(input_path: str, output_path: str):
    # load image
    img = Image.open(input_path)

    # convert to RGB or RGBA depending on source image
    if img.mode == "RGBA":
        channels = Channels.RGBA
    else:
        img = img.convert("RGB")
        channels = Channels.RGB

    width, height = img.size
    bit_depth = 8
    compression = Compression.NONE

    # get raw pixel bytes
    pixel_data = img.tobytes()

    # write KIF file
    with open(output_path, "wb") as f:
        f.write(KIF_SIGNATURE)
        f.write(pack_header(width, height, channels, bit_depth, compression))
        f.write(pixel_data)

    print(f"[KIF] encoded: {input_path} -> {output_path}")
    print(f"      size:    {width}x{height}")
    print(f"      channels:{channels}")
    print(f"      bytes:   {len(pixel_data)}")