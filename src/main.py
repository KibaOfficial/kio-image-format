# Copyright (c) 2026 KibaOfficial
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import argparse
from encoder import encode
from decoder import decode
from converter import convert


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

    # decode command
    decode_parser = subparsers.add_parser("decode", help="decode a KIF file to image")
    decode_parser.add_argument("input",  help="input KIF path (e.g. image.kif)")
    decode_parser.add_argument("output", help="output image path (e.g. image.png)")

    # convert command
    convert_parser = subparsers.add_parser("convert", help="convert any image to KIF")
    convert_parser.add_argument("input",  help="input image path (e.g. image.jpg)")
    convert_parser.add_argument("output", help="output KIF path (e.g. image.kif)")

    args = parser.parse_args()

    if args.command == "encode":
        encode(args.input, args.output)
    elif args.command == "decode":
        decode(args.input, args.output)
    elif args.command == "convert":
        convert(args.input, args.output)


if __name__ == "__main__":
    main()