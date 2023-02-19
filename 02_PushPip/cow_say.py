from argparse import ArgumentParser
from cowsay import cowsay
import sys


def cow_modes():
    modes = {'b': 'Borg',
             'd': 'dead',
             'g': 'greedy',
             'p': 'paranoia',
             's': 'stoned',
             't': 'tired',
             'w': 'wired',
             'y': 'youthful'
    }
    return modes


def emulate_cow(args):
    if args.mode is not None:
        args.mode = ''.join(args.mode)
    args.message = ' '.join(args.message)
    print(
        cowsay(
            message=args.message,
            cow=args.f,
            preset=args.mode,
            eyes=args.e[:2],
            tongue=args.T[:2],
            width=args.W,
            wrap_text=args.n
        )
    )



if __name__ == '__main__':
    parser = ArgumentParser(prog='Cowsay', description='Emulation of cowsay command')

    parser.add_argument('message', type=str, default=' ', action='store', nargs='*', help="message for cow to say")

    parser.add_argument('-e', type=str, default='oo', action='store', metavar='eye_string', help="select the appearance of the cow's eyes")
    parser.add_argument('-f', type=str, default='default', metavar='cowfile', help='cow picture file')
    parser.add_argument('-n', action='store_false', help='do not word-wrap message')
    parser.add_argument('-T', type=str, action='store', default='  ', metavar='tongue_string', help="select the appearance of the cow's tongue")
    parser.add_argument('-W', type=int, action='store', default=40, metavar='column', help='column where the message should be wrapped')

    for mode, descr in cow_modes().items():
        parser.add_argument(f'-{mode}', action='append_const', dest='mode', const=mode, help='mode: ' + descr)

    args = parser.parse_args()

    emulate_cow(args)

