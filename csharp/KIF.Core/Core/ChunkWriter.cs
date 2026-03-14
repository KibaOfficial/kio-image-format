// Copyright (c) 2026 KibaOfficial
//
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

using System.IO.Hashing;

namespace KIF.Core;

/// <summary>
/// Writes KIF v2 chunks to a stream.
/// Chunk layout: [type 4] [length 4] [data n] [crc32 4]
/// All integers big-endian.
/// </summary>
public static class ChunkWriter
{
    public static void Write(Stream stream, byte[] type, byte[] data)
    {
        // crc32 over type + data
        var crc = new Crc32();
        crc.Append(type);
        crc.Append(data);
        uint checksum = BitConverter.ToUInt32(crc.GetCurrentHash());

        // type
        stream.Write(type);

        // length (big-endian)
        uint length = (uint)data.Length;
        stream.WriteByte((byte)(length >> 24));
        stream.WriteByte((byte)(length >> 16));
        stream.WriteByte((byte)(length >>  8));
        stream.WriteByte((byte)(length      ));

        // data
        stream.Write(data);

        // crc32 (big-endian)
        stream.WriteByte((byte)(checksum >> 24));
        stream.WriteByte((byte)(checksum >> 16));
        stream.WriteByte((byte)(checksum >>  8));
        stream.WriteByte((byte)(checksum      ));
    }
}