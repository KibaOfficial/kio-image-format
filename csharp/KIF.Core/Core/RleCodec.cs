// Copyright (c) 2026 KibaOfficial
//
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

namespace KIF.Core;

/// <summary>
/// Run-Length Encoding codec for KIF pixel data.
/// Format: [count byte][pixel bytes] repeated.
/// Max run length: 255.
/// </summary>
public static class RleCodec
{
    /// <summary>Encode raw pixel data with RLE.</summary>
    public static byte[] Encode(byte[] data, int channels)
    {
        var result = new List<byte>();
        int i = 0;
        int total = data.Length;

        while (i < total)
        {
            // read current pixel
            var pixel = data.AsSpan(i, channels);
            int count = 1;

            // count consecutive identical pixels (max 255)
            while (count < 255 &&
                   i + count * channels + channels <= total &&
                   data.AsSpan(i + count * channels, channels).SequenceEqual(pixel))
            {
                count++;
            }

            result.Add((byte)count);
            result.AddRange(pixel.ToArray());

            i += count * channels;
        }

        return [.. result];
    }

    /// <summary>Decode RLE-compressed pixel data.</summary>
    public static byte[] Decode(byte[] data, int channels)
    {
        var result = new List<byte>();
        int i = 0;

        while (i < data.Length)
        {
            byte count = data[i++];
            var pixel = data.AsSpan(i, channels);

            for (int j = 0; j < count; j++)
                result.AddRange(pixel.ToArray());

            i += channels;
        }

        return [.. result];
    }
}