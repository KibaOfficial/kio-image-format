# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from v1.encoder import encode
from core.header import Compression


def convert(input_path: str, output_path: str, compression: int = Compression.NONE, grayscale: bool = False):
    print(f"[KIF] converting: {input_path} -> {output_path}")
    encode(input_path, output_path, compression, grayscale)