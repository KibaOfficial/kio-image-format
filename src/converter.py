# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from encoder import encode


def convert(input_path: str, output_path: str):
    print(f"[KIF] converting: {input_path} -> {output_path}")
    encode(input_path, output_path)