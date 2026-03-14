# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from PIL import Image


def compare(path_a: str, path_b: str):
    img_a = Image.open(path_a).convert("RGB")
    img_b = Image.open(path_b).convert("RGB")

    if img_a.size != img_b.size:
        print(f"[KIF] compare failed: size mismatch")
        print(f"  {path_a}: {img_a.size}")
        print(f"  {path_b}: {img_b.size}")
        return

    pixels_a = list(img_a.getdata())
    pixels_b = list(img_b.getdata())

    total = len(pixels_a)
    differences = sum(1 for a, b in zip(pixels_a, pixels_b) if a != b)

    status = "identical ✓" if differences == 0 else "DIFFERENT ✗"

    print(f"KIF Compare")
    print(f"-----------")
    print(f"  A:               {path_a}")
    print(f"  B:               {path_b}")
    print(f"")
    print(f"  Pixels compared: {total:,}")
    print(f"  Differences:     {differences:,}")
    print(f"  Status:          {status}")