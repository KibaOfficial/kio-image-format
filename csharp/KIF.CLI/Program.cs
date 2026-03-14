// Copyright (c) 2026 KibaOfficial
//
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

using System.Diagnostics;
using KIF.Core;

if (args.Length == 0) { PrintHelp(); return; }

switch (args[0])
{
    case "encode":    RunEncode(args[1..]); break;
    case "decode":    RunDecode(args[1..]); break;
    case "info":      RunInfo(args[1..]); break;
    case "compare":   RunCompare(args[1..]); break;
    case "stats":     RunStats(args[1..]); break;
    case "test":      RunTest(); break;
    case "benchmark": RunBenchmark(); break;
    default:
        Console.WriteLine($"[KIF] unknown command: {args[0]}");
        PrintHelp();
        break;
}

// ============================================================
// ENCODE
// ============================================================

static void RunEncode(string[] args)
{
    if (args.Length < 2)
    {
        Console.WriteLine("Usage: kif encode <input> <output> [--compression rle] [--grayscale] [--meta key=value ...]");
        return;
    }

    string input  = args[0];
    string output = args[1];
    var compression = KifCompression.None;
    bool grayscale  = false;
    var metadata    = new Dictionary<string, string>();

    for (int i = 2; i < args.Length; i++)
    {
        switch (args[i])
        {
            case "--compression" or "-c" when i + 1 < args.Length:
                compression = args[++i] == "rle" ? KifCompression.Rle : KifCompression.None;
                break;
            case "--grayscale" or "-g":
                grayscale = true;
                break;
            case "--meta" or "-m":
                while (i + 1 < args.Length && args[i + 1].Contains('='))
                {
                    var parts = args[++i].Split('=', 2);
                    metadata[parts[0]] = parts[1];
                }
                break;
        }
    }

    KifEncoder.Encode(input, output, compression, grayscale, metadata.Count > 0 ? metadata : null);
}

// ============================================================
// DECODE
// ============================================================

static void RunDecode(string[] args)
{
    if (args.Length < 2)
    {
        Console.WriteLine("Usage: kif decode <input> <output>");
        return;
    }
    KifDecoder.Decode(args[0], args[1]);
}

// ============================================================
// INFO
// ============================================================

static void RunInfo(string[] args)
{
    if (args.Length < 1) { Console.WriteLine("Usage: kif info <input>"); return; }

    string path = args[0];
    using var stream = File.OpenRead(path);

    var sig = new byte[8];
    stream.ReadExactly(sig);
    if (!KifSignature.IsValid(sig)) { Console.WriteLine("[KIF] invalid signature"); return; }

    var chunks = ChunkReader.ReadAll(stream);
    if (!chunks.TryGetValue("HEAD", out var headData)) { Console.WriteLine("[KIF] missing HEAD chunk"); return; }

    var header    = KifHeader.FromBytes(headData);
    long fileSize = new FileInfo(path).Length;
    long rawSize  = header.RawDataSize;
    long dataSize = chunks.TryGetValue("DATA", out var data) ? data.Length : 0;
    double ratio  = header.Compression != KifCompression.None
        ? (1.0 - (double)dataSize / rawSize) * 100 : 0;

    Console.WriteLine("KIF Image (v2)");
    Console.WriteLine("--------------");
    Console.WriteLine($"  File:        {path}");
    Console.WriteLine($"  Width:       {header.Width}px");
    Console.WriteLine($"  Height:      {header.Height}px");
    Console.WriteLine($"  Channels:    {header.Channels}");
    Console.WriteLine($"  Bit Depth:   {header.BitDepth}");
    Console.WriteLine($"  Compression: {header.Compression}");

    if (chunks.TryGetValue("META", out var metaBytes))
    {
        Console.WriteLine("  Metadata:");
        foreach (var pair in System.Text.Encoding.UTF8.GetString(metaBytes).Split('\0'))
            if (pair.Contains('=')) Console.WriteLine($"    {pair}");
    }

    Console.WriteLine();
    Console.WriteLine($"  Raw Size:    {FmtSize(rawSize)}");
    Console.WriteLine($"  File Size:   {FmtSize(fileSize)}");
    if (header.Compression != KifCompression.None)
        Console.WriteLine($"  Saved:       {ratio:F1}%");
}

// ============================================================
// COMPARE
// ============================================================

static void RunCompare(string[] args)
{
    if (args.Length < 2) { Console.WriteLine("Usage: kif compare <imageA> <imageB>"); return; }

    using var imgA = SixLabors.ImageSharp.Image.Load<SixLabors.ImageSharp.PixelFormats.Rgb24>(args[0]);
    using var imgB = SixLabors.ImageSharp.Image.Load<SixLabors.ImageSharp.PixelFormats.Rgb24>(args[1]);

    if (imgA.Width != imgB.Width || imgA.Height != imgB.Height)
    {
        Console.WriteLine("[KIF] compare failed: size mismatch");
        Console.WriteLine($"  A: {imgA.Width}x{imgA.Height}");
        Console.WriteLine($"  B: {imgB.Width}x{imgB.Height}");
        return;
    }

    int total = imgA.Width * imgA.Height;
    int differences = 0;

    imgA.ProcessPixelRows(imgB, (accessorA, accessorB) =>
    {
        for (int y = 0; y < accessorA.Height; y++)
        {
            var rowA = accessorA.GetRowSpan(y);
            var rowB = accessorB.GetRowSpan(y);
            for (int x = 0; x < rowA.Length; x++)
                if (rowA[x] != rowB[x]) differences++;
        }
    });

    string status = differences == 0 ? "identical ✓" : "DIFFERENT ✗";

    Console.WriteLine("KIF Compare");
    Console.WriteLine("-----------");
    Console.WriteLine($"  A:               {args[0]}");
    Console.WriteLine($"  B:               {args[1]}");
    Console.WriteLine();
    Console.WriteLine($"  Pixels compared: {total:N0}");
    Console.WriteLine($"  Differences:     {differences:N0}");
    Console.WriteLine($"  Status:          {status}");
}

// ============================================================
// STATS
// ============================================================

static void RunStats(string[] args)
{
    if (args.Length < 1) { Console.WriteLine("Usage: kif stats <input>"); return; }

    string path = args[0];
    using var stream = File.OpenRead(path);

    var sig = new byte[8];
    stream.ReadExactly(sig);
    if (!KifSignature.IsValid(sig)) { Console.WriteLine("[KIF] invalid signature"); return; }

    var chunks = ChunkReader.ReadAll(stream);
    if (!chunks.TryGetValue("HEAD", out var headData)) return;
    if (!chunks.TryGetValue("DATA", out var pixelData)) return;

    var header = KifHeader.FromBytes(headData);

    // decompress for stats
    byte[] raw = header.Compression == KifCompression.Rle
        ? RleCodec.Decode(pixelData, (int)header.Channels)
        : pixelData;

    int channels   = (int)header.Channels;
    int total      = (int)(header.Width * header.Height);

    // unique colors
    var unique = new HashSet<string>();
    for (int i = 0; i < raw.Length; i += channels)
        unique.Add(string.Join(",", raw[i..(i + channels)]));

    // RLE analysis
    byte[] rleData = RleCodec.Encode(raw, channels);
    var runs = new List<int>();
    for (int i = 0; i < rleData.Length; i += 1 + channels)
        runs.Add(rleData[i]);

    int totalRuns    = runs.Count;
    double avgRun    = runs.Average();
    int longestRun   = runs.Max();
    int shortestRun  = runs.Min();
    int singleRuns   = runs.Count(r => r == 1);

    long rawSize = raw.Length;
    long rleSize = rleData.Length;
    double ratio = (1.0 - (double)rleSize / rawSize) * 100;

    Console.WriteLine("KIF Stats");
    Console.WriteLine("---------");
    Console.WriteLine($"  File:              {path}");
    Console.WriteLine($"  Size:              {header.Width}x{header.Height}");
    Console.WriteLine($"  Pixels:            {total:N0}");
    Console.WriteLine($"  Unique colors:     {unique.Count:N0}");
    Console.WriteLine();
    Console.WriteLine("  RLE Analysis:");
    Console.WriteLine($"  Total runs:        {totalRuns:N0}");
    Console.WriteLine($"  Average run:       {avgRun:F1} pixels");
    Console.WriteLine($"  Longest run:       {longestRun} pixels");
    Console.WriteLine($"  Shortest run:      {shortestRun} pixels");
    Console.WriteLine($"  Single px runs:    {singleRuns:N0} ({(double)singleRuns / totalRuns * 100:F1}%)");
    Console.WriteLine();
    Console.WriteLine("  RLE Efficiency:");
    Console.WriteLine($"  Raw size:          {FmtSize(rawSize)}");
    Console.WriteLine($"  RLE size:          {FmtSize(rleSize)}");
    Console.WriteLine($"  Saved:             {ratio:F1}%");
}

// ============================================================
// TEST
// ============================================================

static void RunTest()
{
    const string INPUT  = "img/test.jpeg";
    const string OUTDIR = "out";
    Directory.CreateDirectory(OUTDIR);

    var variants = new[]
    {
        (Name: "rgb_raw",      Compression: KifCompression.None, Grayscale: false, Meta: false),
        (Name: "rgb_rle",      Compression: KifCompression.Rle,  Grayscale: false, Meta: false),
        (Name: "gray_raw",     Compression: KifCompression.None, Grayscale: true,  Meta: false),
        (Name: "gray_rle",     Compression: KifCompression.Rle,  Grayscale: true,  Meta: false),
        (Name: "rgb_meta",     Compression: KifCompression.None, Grayscale: false, Meta: true),
    };

    Console.WriteLine("KIF Test Suite (C#)");
    Console.WriteLine("===================");
    Console.WriteLine($"Input:    {INPUT}");
    Console.WriteLine($"Variants: {variants.Length}");

    var results = new List<(string Name, long Size)>();

    foreach (var v in variants)
    {
        string kif     = Path.Combine(OUTDIR, $"cs_test_{v.Name}.kif");
        string decoded = Path.Combine(OUTDIR, $"cs_test_{v.Name}_decoded.png");

        Console.WriteLine($"\n{new string('=', 60)}");
        Console.WriteLine($"  {v.Name.ToUpper()}");
        Console.WriteLine(new string('=', 60));

        var meta = v.Meta ? new Dictionary<string, string> { ["author"] = "kiba", ["tool"] = "KIF", ["version"] = "3" } : null;

        Console.WriteLine("\n[1/3] Encoding...");
        KifEncoder.Encode(INPUT, kif, v.Compression, v.Grayscale, meta);

        Console.WriteLine("\n[2/3] Decoding...");
        KifDecoder.Decode(kif, decoded);

        Console.WriteLine("\n[3/3] Info:");
        RunInfo([kif]);

        results.Add((v.Name, new FileInfo(kif).Length));
    }

    Console.WriteLine("\n============================================================");
    Console.WriteLine("  SUMMARY");
    Console.WriteLine("============================================================");
    Console.WriteLine($"\n  {"Variant",-25} {"File Size",12}");
    Console.WriteLine($"  {new string('-', 25)} {new string('-', 12)}");
    foreach (var (name, size) in results)
        Console.WriteLine($"  {name,-25} {size / 1_000_000.0,10:F2} MB");

    Console.WriteLine($"\n✓ All variants generated in '{OUTDIR}/'");
}

// ============================================================
// BENCHMARK
// ============================================================

static void RunBenchmark()
{
    const string INPUT  = "img/test.jpeg";
    const string OUTDIR = "out/benchmark";
    const int    RUNS   = 5;
    Directory.CreateDirectory(OUTDIR);

    Console.WriteLine("KIF Benchmark (C#)");
    Console.WriteLine("==================");
    Console.WriteLine($"Input: {INPUT}");
    Console.WriteLine($"Runs:  {RUNS}x per variant (averaged)");

    var results = new List<(string Name, double Enc, double Dec, long Size)>();

    void Bench(string name, string kif, string dec,
               Action encode, Action decode)
    {
        Console.WriteLine($"\n{new string('=', 60)}");
        Console.WriteLine($"  {name}");
        Console.WriteLine(new string('=', 60));

        var encTimes = new List<double>();
        var decTimes = new List<double>();

        for (int i = 0; i < RUNS; i++)
        {
            var sw = Stopwatch.StartNew();
            encode();
            encTimes.Add(sw.Elapsed.TotalMilliseconds);
        }

        for (int i = 0; i < RUNS; i++)
        {
            var sw = Stopwatch.StartNew();
            decode();
            decTimes.Add(sw.Elapsed.TotalMilliseconds);
        }

        double enc = encTimes.Average();
        double decAvg = decTimes.Average();
        long size = new FileInfo(kif).Length;

        Console.WriteLine($"  Encode: {enc:F1} ms   Decode: {decAvg:F1} ms   Size: {size / 1_000_000.0:F2} MB");
        results.Add((name, enc, decAvg, size));
    }

    Bench("KIF v2 raw RGB",
        Path.Combine(OUTDIR, "bench_rgb_raw.kif"),
        Path.Combine(OUTDIR, "bench_rgb_raw_dec.png"),
        () => KifEncoder.Encode(INPUT, Path.Combine(OUTDIR, "bench_rgb_raw.kif")),
        () => KifDecoder.Decode(Path.Combine(OUTDIR, "bench_rgb_raw.kif"), Path.Combine(OUTDIR, "bench_rgb_raw_dec.png")));

    Bench("KIF v2 RLE RGB",
        Path.Combine(OUTDIR, "bench_rgb_rle.kif"),
        Path.Combine(OUTDIR, "bench_rgb_rle_dec.png"),
        () => KifEncoder.Encode(INPUT, Path.Combine(OUTDIR, "bench_rgb_rle.kif"), KifCompression.Rle),
        () => KifDecoder.Decode(Path.Combine(OUTDIR, "bench_rgb_rle.kif"), Path.Combine(OUTDIR, "bench_rgb_rle_dec.png")));

    Bench("KIF v2 raw Gray",
        Path.Combine(OUTDIR, "bench_gray_raw.kif"),
        Path.Combine(OUTDIR, "bench_gray_raw_dec.png"),
        () => KifEncoder.Encode(INPUT, Path.Combine(OUTDIR, "bench_gray_raw.kif"), grayscale: true),
        () => KifDecoder.Decode(Path.Combine(OUTDIR, "bench_gray_raw.kif"), Path.Combine(OUTDIR, "bench_gray_raw_dec.png")));

    Bench("KIF v2 RLE Gray",
        Path.Combine(OUTDIR, "bench_gray_rle.kif"),
        Path.Combine(OUTDIR, "bench_gray_rle_dec.png"),
        () => KifEncoder.Encode(INPUT, Path.Combine(OUTDIR, "bench_gray_rle.kif"), KifCompression.Rle, grayscale: true),
        () => KifDecoder.Decode(Path.Combine(OUTDIR, "bench_gray_rle.kif"), Path.Combine(OUTDIR, "bench_gray_rle_dec.png")));

    Console.WriteLine("\n============================================================");
    Console.WriteLine("  SUMMARY");
    Console.WriteLine("============================================================");
    Console.WriteLine($"\n  {"Variant",-20} {"Encode",10} {"Decode",10} {"Size",10}");
    Console.WriteLine($"  {new string('-', 20)} {new string('-', 10)} {new string('-', 10)} {new string('-', 10)}");
    foreach (var (name, enc, dec, size) in results)
        Console.WriteLine($"  {name,-20} {enc,8:F1}ms {dec,8:F1}ms {size / 1_000_000.0,8:F2}MB");

    Console.WriteLine($"\n✓ Benchmark complete ({RUNS} runs averaged)");
}

// ============================================================
// HELPERS
// ============================================================

static string FmtSize(long b) =>
    b >= 1_000_000 ? $"{b / 1_000_000.0:F2} MB"
  : b >= 1_000     ? $"{b / 1_000.0:F2} KB"
  : $"{b} B";

static void PrintHelp()
{
    Console.WriteLine("KIF - Kio Image Format CLI v3 (C#)");
    Console.WriteLine();
    Console.WriteLine("Commands:");
    Console.WriteLine("  encode    <input> <output> [--compression rle] [--grayscale] [--meta key=value ...]");
    Console.WriteLine("  decode    <input> <output>");
    Console.WriteLine("  info      <input>");
    Console.WriteLine("  compare   <imageA> <imageB>");
    Console.WriteLine("  stats     <input>");
    Console.WriteLine("  test");
    Console.WriteLine("  benchmark");
}