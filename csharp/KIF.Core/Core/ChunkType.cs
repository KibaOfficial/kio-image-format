// Copyright (c) 2026 KibaOfficial
//
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

namespace KIF.Core;

/// <summary>
/// KIF v2 chunk type identifiers — 4 ASCII bytes each.
/// </summary>
public static class ChunkType
{
    public static readonly byte[] Head = "HEAD"u8.ToArray();
    public static readonly byte[] Data = "DATA"u8.ToArray();
    public static readonly byte[] Meta = "META"u8.ToArray();
    public static readonly byte[] End  = "END "u8.ToArray();

    public static bool IsHead(byte[] type) => type.SequenceEqual(Head);
    public static bool IsData(byte[] type) => type.SequenceEqual(Data);
    public static bool IsMeta(byte[] type) => type.SequenceEqual(Meta);
    public static bool IsEnd(byte[]  type) => type.SequenceEqual(End);
}