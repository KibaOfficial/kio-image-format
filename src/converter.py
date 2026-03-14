# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from encoder import encode
from header import Compression


def convert(input_path: str, output_path: str, compression: int = Compression.NONE):
    print(f"[KIF] converting: {input_path} -> {output_path}")
    encode(input_path, output_path, compression)