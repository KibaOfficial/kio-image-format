# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import argparse
from encoder import encode
from decoder import decode
from converter import convert
from info import info
from compare import compare
from stats import stats
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
    encode_parser.add_argument(
        "--grayscale", "-g",
        action="store_true",
        help="convert image to grayscale before encoding"
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
    convert_parser.add_argument(
        "--grayscale", "-g",
        action="store_true",
        help="convert image to grayscale before encoding"
    )

    # info command
    info_parser = subparsers.add_parser("info", help="display KIF file metadata")
    info_parser.add_argument("input", help="input KIF path (e.g. image.kif)")

    # compare command
    compare_parser = subparsers.add_parser("compare", help="compare two images pixel by pixel")
    compare_parser.add_argument("a", help="first image path")
    compare_parser.add_argument("b", help="second image path")

    # stats command
    stats_parser = subparsers.add_parser("stats", help="show RLE stats and compression analysis")
    stats_parser.add_argument("input", help="input KIF path (e.g. image.kif)")

    args = parser.parse_args()

    if args.command == "encode":
        c = Compression.RLE if args.compression == "rle" else Compression.NONE
        encode(args.input, args.output, c, args.grayscale)
    elif args.command == "decode":
        decode(args.input, args.output)
    elif args.command == "convert":
        c = Compression.RLE if args.compression == "rle" else Compression.NONE
        convert(args.input, args.output, c, args.grayscale)
    elif args.command == "info":
        info(args.input)
    elif args.command == "compare":
        compare(args.a, args.b)
    elif args.command == "stats":
        stats(args.input)


if __name__ == "__main__":
    main()