// Copyright (c) 2026 KibaOfficial
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

namespace KIF.Core;

/// <summary>
/// KIF file signature — 8 bytes at the start of every .kif file.
/// Identical across v1 and v2.
/// </summary>

public static class KifSignature
{
    /// <summary>
    /// The KIF file signature bytes.
    /// 89 4B 49 46 0D 0A 1A 0A
    /// </summary>
	public static readonly byte[] Bytes =
	[
		0x89, // binary file indicator
		0x4B, // 'K'
		0x49, // 'I'
		0x46, // 'F'
		0x0D, // CR  (Carriage Return)
		0x0A, // LF  (Line Feed)
		0x1A, // SUB (DOS EOF marker)
		0x0A  // LF  (Unix line ending)
	];

	/// <summary>
    /// Validates that the given bytes match the KIF signature.
    /// </summary>
	public static bool IsValid(byte[] bytes) =>
		bytes.Length == 8 && bytes.SequenceEqual(Bytes);
}