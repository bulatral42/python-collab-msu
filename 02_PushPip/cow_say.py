from argparse import ArgumentParser
from cowsay import cowsay
import sys


def emulate_cow(args):
    print(
        cowsay(
            message=args.message,
            cow=args.f,
            preset=None,
            eyes=args.e,
            tongue=args.T,
            width=args.W,
            wrap_text=args.n
        )
    )



if __name__ == '__main__':
    parser = ArgumentParser(prog='Cowsay', description='Emulation of cowsay command')

    parser.add_argument('message', type=str, default='', action='store', help="message for cow to say")

    parser.add_argument('-e', type=str, default='oo', action='store', metavar='eye_string', help="select the appearance of the cow's eyes")
    parser.add_argument('-f', type=str, default='default', metavar='cowfile', help='cow picture file')
    parser.add_argument('-n', action='store_false', help='do not word-wrap message')
    parser.add_argument('-T', type=str, action='store', default='  ', metavar='tongue_string', help="select the appearance of the cow's tongue")
    parser.add_argument('-W', type=int, action='store', default=40, metavar='column', help='column where the message should be wrapped')

    args = parser.parse_args()
    emulate_cow(args)

