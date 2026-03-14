// Copyright (c) 2026 KibaOfficial
//
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;

namespace KIF.Core;

/// <summary>
/// Encodes images to KIF v2 format.
/// </summary>
public static class KifEncoder
{
    /// <summary>
    /// Encode an image file to KIF v2.
    /// </summary>
    public static void Encode(
        string inputPath,
        string outputPath,
        KifCompression compression = KifCompression.None,
        bool grayscale = false,
        Dictionary<string, string>? metadata = null)
    {
        using var image = Image.Load<Rgba32>(inputPath);

        KifChannels channels;
        byte[] pixelData;

        if (grayscale)
        {
            channels = KifChannels.Grayscale;
            pixelData = new byte[image.Width * image.Height];
            int idx = 0;
            image.ProcessPixelRows(accessor =>
            {
                for (int y = 0; y < accessor.Height; y++)
                {
                    var row = accessor.GetRowSpan(y);
                    for (int x = 0; x < row.Length; x++)
                    {
                        var p = row[x];
                        pixelData[idx++] = (byte)(0.299 * p.R + 0.587 * p.G + 0.114 * p.B);
                    }
                }
            });
        }
        else if (image.Metadata.DecodedImageFormat?.Name == "PNG" &&
                 HasAlpha(image))
        {
            channels = KifChannels.Rgba;
            pixelData = new byte[image.Width * image.Height * 4];
            int idx = 0;
            image.ProcessPixelRows(accessor =>
            {
                for (int y = 0; y < accessor.Height; y++)
                {
                    var row = accessor.GetRowSpan(y);
                    for (int x = 0; x < row.Length; x++)
                    {
                        var p = row[x];
                        pixelData[idx++] = p.R;
                        pixelData[idx++] = p.G;
                        pixelData[idx++] = p.B;
                        pixelData[idx++] = p.A;
                    }
                }
            });
        }
        else
        {
            channels = KifChannels.Rgb;
            pixelData = new byte[image.Width * image.Height * 3];
            int idx = 0;
            image.ProcessPixelRows(accessor =>
            {
                for (int y = 0; y < accessor.Height; y++)
                {
                    var row = accessor.GetRowSpan(y);
                    for (int x = 0; x < row.Length; x++)
                    {
                        var p = row[x];
                        pixelData[idx++] = p.R;
                        pixelData[idx++] = p.G;
                        pixelData[idx++] = p.B;
                    }
                }
            });
        }

        // apply compression
        if (compression == KifCompression.Rle)
            pixelData = RleCodec.Encode(pixelData, (int)channels);

        var header = new KifHeader(
            Width:       (uint)image.Width,
            Height:      (uint)image.Height,
            Channels:    channels,
            BitDepth:    8,
            Compression: compression
        );

        using var stream = File.OpenWrite(outputPath);

        // signature
        stream.Write(KifSignature.Bytes);

        // HEAD chunk
        ChunkWriter.Write(stream, ChunkType.Head, header.ToBytes());

        // META chunk (optional)
        if (metadata is { Count: > 0 })
        {
            var metaStr = string.Join("\0", metadata.Select(kv => $"{kv.Key}={kv.Value}"));
            ChunkWriter.Write(stream, ChunkType.Meta, System.Text.Encoding.UTF8.GetBytes(metaStr));
        }

        // DATA chunk
        ChunkWriter.Write(stream, ChunkType.Data, pixelData);

        // END chunk
        ChunkWriter.Write(stream, ChunkType.End, []);

        Console.WriteLine($"[KIF] encoded: {inputPath} -> {outputPath}");
        Console.WriteLine($"      size:    {image.Width}x{image.Height}");
        Console.WriteLine($"      channels:{channels}");
        Console.WriteLine($"      bytes:   {pixelData.Length}");
    }

    private static bool HasAlpha(Image<Rgba32> image)
    {
        bool hasAlpha = false;
        image.ProcessPixelRows(accessor =>
        {
            for (int y = 0; y < accessor.Height && !hasAlpha; y++)
            {
                var row = accessor.GetRowSpan(y);
                for (int x = 0; x < row.Length; x++)
                {
                    if (row[x].A < 255) { hasAlpha = true; break; }
                }
            }
        });
        return hasAlpha;
    }
}