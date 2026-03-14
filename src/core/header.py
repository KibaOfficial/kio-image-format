# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import struct

# 89       = binary file indicator
# 4B 49 46 = "KIF" in ASCII
# 0D 0A    = CRLF line ending
# 1A       = EOF character (to detect text/binary corruption)
# 0A       = LF line ending (to detect line-ending conversions)
KIF_SIGNATURE = bytes([0x89, 0x4B, 0x49, 0x46, 0x0D, 0x0A, 0x1A, 0x0A])

class Channels:
    GRAYSCALE = 1
    RGB = 3
    RGBA = 4

class Compression:
    NONE = 0
    RLE = 1

def pack_header(width, height, channels, bit_depth, compression):
    return struct.pack(">IIBBBB", width, height, channels, bit_depth, compression, 0)