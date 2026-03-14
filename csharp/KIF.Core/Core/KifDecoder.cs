// Copyright (c) 2026 KibaOfficial
//
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;

namespace KIF.Core;

/// <summary>
/// Decodes KIF v2 files to images.
/// </summary>
public static class KifDecoder
{
    public static void Decode(string inputPath, string outputPath)
    {
        using var stream = File.OpenRead(inputPath);

        // validate signature
        var sig = new byte[8];
        stream.ReadExactly(sig);
        if (!KifSignature.IsValid(sig))
            throw new InvalidDataException($"Invalid KIF signature: {Convert.ToHexString(sig)}");

        // read all chunks
        var chunks = ChunkReader.ReadAll(stream);

        if (!chunks.TryGetValue("HEAD", out var headData))
            throw new InvalidDataException("Missing HEAD chunk");
        if (!chunks.TryGetValue("DATA", out var pixelData))
            throw new InvalidDataException("Missing DATA chunk");

        var header = KifHeader.FromBytes(headData);

        // optional metadata
        if (chunks.TryGetValue("META", out var metaData))
        {
            var meta = System.Text.Encoding.UTF8.GetString(metaData)
                .Split('\0')
                .Where(p => p.Contains('='))
                .ToDictionary(p => p.Split('=')[0], p => p.Split('=')[1]);

            Console.WriteLine($"[KIF] metadata:");
            foreach (var kv in meta)
                Console.WriteLine($"      {kv.Key}: {kv.Value}");
        }

        // decompress
        if (header.Compression == KifCompression.Rle)
            pixelData = RleCodec.Decode(pixelData, (int)header.Channels);

        // validate size
        if (pixelData.Length != header.RawDataSize)
            throw new InvalidDataException(
                $"Pixel data size mismatch: expected {header.RawDataSize}, got {pixelData.Length}");

        Console.WriteLine($"[KIF] decoding: {inputPath}");
        Console.WriteLine($"      size:     {header.Width}x{header.Height}");
        Console.WriteLine($"      channels: {header.Channels}");
        Console.WriteLine($"      bitdepth: {header.BitDepth}");
        Console.WriteLine($"      compression: {header.Compression}");

        // reconstruct image
        int width  = (int)header.Width;
        int height = (int)header.Height;
        int idx    = 0;

        switch (header.Channels)
        {
            case KifChannels.Rgb:
            {
                using var image = new Image<Rgb24>(width, height);
                image.ProcessPixelRows(accessor =>
                {
                    for (int y = 0; y < height; y++)
                    {
                        var row = accessor.GetRowSpan(y);
                        for (int x = 0; x < width; x++)
                            row[x] = new Rgb24(pixelData[idx++], pixelData[idx++], pixelData[idx++]);
                    }
                });
                image.Save(outputPath);
                break;
            }
            case KifChannels.Rgba:
            {
                using var image = new Image<Rgba32>(width, height);
                image.ProcessPixelRows(accessor =>
                {
                    for (int y = 0; y < height; y++)
                    {
                        var row = accessor.GetRowSpan(y);
                        for (int x = 0; x < width; x++)
                            row[x] = new Rgba32(pixelData[idx++], pixelData[idx++], pixelData[idx++], pixelData[idx++]);
                    }
                });
                image.Save(outputPath);
                break;
            }
            case KifChannels.Grayscale:
            {
                using var image = new Image<L8>(width, height);
                image.ProcessPixelRows(accessor =>
                {
                    for (int y = 0; y < height; y++)
                    {
                        var row = accessor.GetRowSpan(y);
                        for (int x = 0; x < width; x++)
                            row[x] = new L8(pixelData[idx++]);
                    }
                });
                image.Save(outputPath);
                break;
            }
            default:
                throw new InvalidDataException($"Unsupported channel count: {header.Channels}");
        }

        Console.WriteLine($"      saved to: {outputPath}");
    }
}