# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import struct
import customtkinter as ctk
from PIL import Image
from header import KIF_SIGNATURE, Channels, Compression
from rle import rle_decode


# ============================================================
# CONFIG
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

MAX_IMG_WIDTH  = 800
MAX_IMG_HEIGHT = 600


# ============================================================
# LOAD KIF
# ============================================================

def load_kif(path: str):
    with open(path, "rb") as f:
        sig = f.read(8)
        if sig != KIF_SIGNATURE:
            raise ValueError(f"Invalid KIF signature: {sig.hex()}")

        header = f.read(12)
        width, height, channels, bit_depth, compression, _ = struct.unpack(">IIBBBB", header)
        pixel_data = f.read()

    if compression == Compression.RLE:
        pixel_data = rle_decode(pixel_data, channels)

    # validate pixel data size
    expected_size = width * height * channels * (bit_depth // 8)
    if len(pixel_data) != expected_size:
        raise ValueError(
            f"Invalid pixel data size: expected {expected_size} bytes, got {len(pixel_data)} bytes"
        )

    mode_map = {
        Channels.GRAYSCALE: "L",
        Channels.RGB:       "RGB",
        Channels.RGBA:      "RGBA",
    }
    mode = mode_map.get(channels)
    if not mode:
        raise ValueError(f"Unsupported channel count: {channels}")

    img = Image.frombytes(mode, (width, height), pixel_data)

    channel_label = {
        Channels.GRAYSCALE: "Grayscale",
        Channels.RGB:       "RGB",
        Channels.RGBA:      "RGBA",
    }.get(channels, "Unknown")

    compression_label = {
        Compression.NONE: "None",
        Compression.RLE:  "RLE",
    }.get(compression, "Unknown")

    file_size = os.path.getsize(path)
    raw_size  = width * height * channels * (bit_depth // 8)  # future-proof for 16-bit

    meta = {
        "filename":    os.path.basename(path),
        "width":       width,
        "height":      height,
        "channels":    channel_label,
        "bit_depth":   bit_depth,
        "compression": compression_label,
        "file_size":   file_size,
        "raw_size":    raw_size,
    }

    return img, meta


# ============================================================
# VIEWER APP
# ============================================================

class KIFViewer(ctk.CTk):
    def __init__(self, path: str):
        super().__init__()

        self.resizable(False, False)

        img, meta = load_kif(path)

        # window title with filename
        self.title(f"KIF Viewer — {meta['filename']}")

        # scale image to fit window
        scale = min(MAX_IMG_WIDTH / img.width, MAX_IMG_HEIGHT / img.height, 1.0)
        display_w = int(img.width  * scale)
        display_h = int(img.height * scale)
        img_resized = img.resize((display_w, display_h), Image.LANCZOS)

        # convert for CTk
        self._ctk_img = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(display_w, display_h))

        # ── layout ──────────────────────────────────────────

        # image panel
        self._img_label = ctk.CTkLabel(self, image=self._ctk_img, text="")
        self._img_label.pack(padx=0, pady=0)

        # info bar
        info_frame = ctk.CTkFrame(self, corner_radius=0)
        info_frame.pack(fill="x", padx=0, pady=0)

        def fmt_size(b):
            if b >= 1_000_000:
                return f"{b / 1_000_000:.2f} MB"
            elif b >= 1_000:
                return f"{b / 1_000:.2f} KB"
            return f"{b} B"

        ratio = (1 - meta["file_size"] / meta["raw_size"]) * 100 if meta["raw_size"] > 0 else 0
        saved = f"  •  Saved {ratio:.1f}%" if meta["compression"] != "None" else ""

        info_text = (
            f"{meta['filename']}  •  "
            f"{meta['width']}×{meta['height']}  •  "
            f"{meta['channels']}  •  "
            f"{meta['bit_depth']}bit  •  "
            f"Compression: {meta['compression']}  •  "
            f"File: {fmt_size(meta['file_size'])}"
            f"{saved}"
        )

        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(family="Courier", size=12),
            anchor="w",
        )
        info_label.pack(padx=12, pady=8, fill="x")

        # center window
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        ww = self.winfo_width()
        wh = self.winfo_height()
        self.geometry(f"+{(sw - ww) // 2}+{(sh - wh) // 2}")


# ============================================================
# ENTRY
# ============================================================

def view(path: str):
    app = KIFViewer(path)
    app.mainloop()