from argparse import ArgumentParser
from cowsay import cowsay, list_cows
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
    if args.l:
        print('List of available cow files:', ' '.join(list_cows()), sep='\n')
        return

    # generate mode
    if args.mode is not None:
        args.mode = ''.join(args.mode)
    # generate message or wait for input
    if len(args.message) == 0:
        message = []
        for line in sys.stdin:
            message.append(line.strip())
        args.message = message
    args.message = ' '.join(args.message)
    use_cowfile = '/' in args.f

    if not use_cowfile and not args.f in list_cows():
        print(f'cowsay: Could not find {args.f} cowfile!')
        return

    print(
        cowsay(
            message=args.message,
            cow=args.f,
            preset=args.mode,
            eyes=args.e[:2],
            tongue=args.T[:2],
            width=args.W,
            wrap_text=args.n,
            cowfile=args.f if use_cowfile else None
        )
    )



if __name__ == '__main__':
    parser = ArgumentParser(prog='Cowsay', description='Emulation of cowsay command')

    parser.add_argument('message', type=str, default='', action='store', nargs='*', help="message for cow to say")

    parser.add_argument('-e', type=str, default='oo', action='store', metavar='eye_string', help="select the appearance of the cow's eyes")
    parser.add_argument('-f', type=str, default='default', metavar='cowfile', help='cow picture file')
    parser.add_argument('-n', action='store_false', help='do not word-wrap message')
    parser.add_argument('-T', type=str, action='store', default='  ', metavar='tongue_string', help="select the appearance of the cow's tongue")
    parser.add_argument('-W', type=int, action='store', default=40, metavar='column', help='column where the message should be wrapped')

    parser.add_argument('-l', action='store_true', help='list all cowfiles')

    for mode, descr in cow_modes().items():
        parser.add_argument(f'-{mode}', action='append_const', dest='mode', const=mode, help='mode: ' + descr)

    args = parser.parse_args()

    emulate_cow(args)

