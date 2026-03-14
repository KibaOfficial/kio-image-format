# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


def rle_encode(data: bytes, channels: int) -> bytes:
    result = bytearray()
    total = len(data)
    i = 0

    while i < total:
        # read current pixel (one full pixel = channels bytes)
        pixel = data[i:i + channels]
        count = 1

        # count how many times this pixel repeats
        while (
            count < 255 and
            i + count * channels + channels <= total and
            data[i + count * channels:i + count * channels + channels] == pixel
        ):
            count += 1

        # write: [count][pixel bytes]
        result.append(count)
        result.extend(pixel)

        i += count * channels

    return bytes(result)


def rle_decode(data: bytes, channels: int) -> bytes:
    result = bytearray()
    i = 0
    total = len(data)

    while i < total:
        count = data[i]
        i += 1

        pixel = data[i:i + channels]
        i += channels

        # repeat pixel count times
        result.extend(pixel * count)

    return bytes(result)