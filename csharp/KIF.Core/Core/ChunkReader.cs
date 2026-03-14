// Copyright (c) 2026 KibaOfficial
//
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

using System.IO.Hashing;

namespace KIF.Core;

/// <summary>
/// Reads a single KIF v2 chunk from a stream and validates CRC32.
/// </summary>
public static class ChunkReader
{
    /// <summary>
    /// Read one chunk — returns (type, data).
    /// Throws if CRC mismatch or unexpected EOF.
    /// </summary>
    public static (byte[] Type, byte[] Data) Read(Stream stream)
    {
        // type (4 bytes)
        var type = new byte[4];
        if (stream.Read(type, 0, 4) < 4)
            throw new EndOfStreamException("Unexpected EOF reading chunk type");

        // length (4 bytes, big-endian)
        var lengthBytes = new byte[4];
        if (stream.Read(lengthBytes, 0, 4) < 4)
            throw new EndOfStreamException("Unexpected EOF reading chunk length");

        uint length = (uint)((lengthBytes[0] << 24) | (lengthBytes[1] << 16) |
                             (lengthBytes[2] <<  8) |  lengthBytes[3]);

        // data
        var data = new byte[length];
        if (length > 0 && stream.Read(data, 0, (int)length) < (int)length)
            throw new EndOfStreamException($"Unexpected EOF reading chunk data ({System.Text.Encoding.ASCII.GetString(type)})");

        // crc32 (4 bytes, big-endian)
        var crcBytes = new byte[4];
        if (stream.Read(crcBytes, 0, 4) < 4)
            throw new EndOfStreamException("Unexpected EOF reading chunk CRC");

        uint storedCrc = (uint)((crcBytes[0] << 24) | (crcBytes[1] << 16) |
                                (crcBytes[2] <<  8) |  crcBytes[3]);

        // validate
        var crc = new Crc32();
        crc.Append(type);
        crc.Append(data);
        uint expectedCrc = BitConverter.ToUInt32(crc.GetCurrentHash());

        if (storedCrc != expectedCrc)
            throw new InvalidDataException(
                $"CRC mismatch in chunk {System.Text.Encoding.ASCII.GetString(type)}: " +
                $"expected 0x{expectedCrc:X8}, got 0x{storedCrc:X8}");

        return (type, data);
    }

    /// <summary>
    /// Read all chunks until END chunk — returns dict keyed by type string.
    /// </summary>
    public static Dictionary<string, byte[]> ReadAll(Stream stream)
    {
        var chunks = new Dictionary<string, byte[]>();
        while (true)
        {
            var (type, data) = Read(stream);
            var key = System.Text.Encoding.ASCII.GetString(type);
            chunks[key] = data;
            if (ChunkType.IsEnd(type)) break;
        }
        return chunks;
    }
}