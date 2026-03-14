// Copyright (c) 2026 KibaOfficial
//
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

namespace KIF.Core;

/// <summary>
/// Channel count values used in the KIF header.
/// </summary>
public enum KifChannels : byte
{
    Grayscale = 1,
    Rgb       = 3,
    Rgba      = 4
}

/// <summary>
/// Compression method values used in the KIF header.
/// </summary>
public enum KifCompression : byte
{
    None = 0,
    Rle  = 1
}

/// <summary>
/// KIF image header — 12 bytes, stored in big-endian byte order.
/// Used as the data payload of the HEAD chunk in KIF v2.
/// </summary>
public record KifHeader(
    uint           Width,
    uint           Height,
    KifChannels    Channels,
    byte           BitDepth,
    KifCompression Compression
)
{
    /// <summary>Size of the header in bytes.</summary>
    public const int Size = 12;

    /// <summary>Serialize to bytes (big-endian).</summary>
    public byte[] ToBytes()
    {
        var bytes = new byte[Size];
        // width and height — big-endian uint32
        bytes[0] = (byte)(Width  >> 24);
        bytes[1] = (byte)(Width  >> 16);
        bytes[2] = (byte)(Width  >>  8);
        bytes[3] = (byte)(Width       );
        bytes[4] = (byte)(Height >> 24);
        bytes[5] = (byte)(Height >> 16);
        bytes[6] = (byte)(Height >>  8);
        bytes[7] = (byte)(Height      );
        bytes[8]  = (byte)Channels;
        bytes[9]  = BitDepth;
        bytes[10] = (byte)Compression;
        bytes[11] = 0; // reserved
        return bytes;
    }

    /// <summary>Deserialize from bytes (big-endian).</summary>
    public static KifHeader FromBytes(byte[] bytes)
    {
        if (bytes.Length < Size)
            throw new ArgumentException($"Header too short: {bytes.Length} bytes");

        uint width  = (uint)((bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]);
        uint height = (uint)((bytes[4] << 24) | (bytes[5] << 16) | (bytes[6] << 8) | bytes[7]);

        return new KifHeader(
            Width:       width,
            Height:      height,
            Channels:    (KifChannels)bytes[8],
            BitDepth:    bytes[9],
            Compression: (KifCompression)bytes[10]
        );
    }

    /// <summary>Raw pixel data size in bytes.</summary>
    public int RawDataSize => (int)(Width * Height * (byte)Channels * (BitDepth / 8));
}