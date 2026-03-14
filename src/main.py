# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import argparse
from encoder import encode
from decoder import decode
from converter import convert
from header import Compression


def main():
    parser = argparse.ArgumentParser(
        prog="kif",
        description="KIF - Kio Image Format CLI"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # encode command
    encode_parser = subparsers.add_parser("encode", help="encode an image to KIF")
    encode_parser.add_argument("input",  help="input image path (e.g. image.png)")
    encode_parser.add_argument("output", help="output KIF path (e.g. image.kif)")
    encode_parser.add_argument(
        "--compression", "-c",
        choices=["none", "rle"],
        default="none",
        help="compression method (default: none)"
    )

    # decode command
    decode_parser = subparsers.add_parser("decode", help="decode a KIF file to image")
    decode_parser.add_argument("input",  help="input KIF path (e.g. image.kif)")
    decode_parser.add_argument("output", help="output image path (e.g. image.png)")

    # convert command
    convert_parser = subparsers.add_parser("convert", help="convert any image to KIF")
    convert_parser.add_argument("input",  help="input image path (e.g. image.jpg)")
    convert_parser.add_argument("output", help="output KIF path (e.g. image.kif)")
    convert_parser.add_argument(
        "--compression", "-c",
        choices=["none", "rle"],
        default="none",
        help="compression method (default: none)"
    )

    args = parser.parse_args()

    if args.command == "encode":
        c = Compression.RLE if args.compression == "rle" else Compression.NONE
        encode(args.input, args.output, c)
    elif args.command == "decode":
        decode(args.input, args.output)
    elif args.command == "convert":
        c = Compression.RLE if args.compression == "rle" else Compression.NONE
        convert(args.input, args.output, c)


if __name__ == "__main__":
    main()