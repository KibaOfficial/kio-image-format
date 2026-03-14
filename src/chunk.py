# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import struct
import zlib


# ============================================================
# CHUNK TYPES
# ============================================================

CHUNK_HEAD = b"HEAD"
CHUNK_DATA = b"DATA"
CHUNK_META = b"META"
CHUNK_END  = b"END "


# ============================================================
# WRITE / READ
# ============================================================

def write_chunk(f, chunk_type: bytes, data: bytes):
    """Write a single chunk: [type][length][data][crc32]"""
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    f.write(chunk_type)
    f.write(struct.pack(">I", len(data)))
    f.write(data)
    f.write(struct.pack(">I", crc))


def read_chunk(f):
    """Read a single chunk, validate CRC, return (type, data)"""
    chunk_type = f.read(4)
    if len(chunk_type) < 4:
        raise EOFError("Unexpected end of file while reading chunk type")

    length_bytes = f.read(4)
    if len(length_bytes) < 4:
        raise EOFError("Unexpected end of file while reading chunk length")

    length = struct.unpack(">I", length_bytes)[0]
    data   = f.read(length)
    crc_bytes = f.read(4)

    if len(data) < length:
        raise EOFError(f"Unexpected end of file reading chunk data ({chunk_type})")

    # validate CRC
    expected_crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    actual_crc   = struct.unpack(">I", crc_bytes)[0]
    if expected_crc != actual_crc:
        raise ValueError(
            f"CRC mismatch in chunk {chunk_type}: "
            f"expected {expected_crc:#010x}, got {actual_crc:#010x}"
        )

    return chunk_type, data


def read_all_chunks(f):
    """Read all chunks from file until END chunk, return dict"""
    chunks = {}
    while True:
        chunk_type, data = read_chunk(f)
        chunks[chunk_type] = data
        if chunk_type == CHUNK_END:
            break
    return chunks