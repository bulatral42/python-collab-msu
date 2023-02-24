from collections import defaultdict
import random
from argparse import ArgumentParser
from urllib.request import urlretrieve
import os
from cowsay import cowsay, get_random_cow, read_dot_cow
from io import StringIO


def bullscows(guess: str, secret: str) -> (int, int):
    bulls, cows = 0, 0
    for a, b in zip(guess, secret):
        if a == b:
            bulls += 1

    g_dict = defaultdict(int)
    s_dict = defaultdict(int)
    for a in guess:
        g_dict[a] += 1
    for a in secret:
        s_dict[a] += 1
    for a, n in s_dict.items():
        cows += min(n, g_dict[a])
    cows -= bulls

    return bulls, cows


def gameplay(ask: callable, inform: callable, words: list[str]) -> int:
    secret = random.choice(words)
    n_attempts = 0
    while True:
        guess = ask("Введите слово: ", words)
        n_attempts += 1
        bulls, cows = bullscows(guess, secret)
        inform("Быки {}, Коровы {}", bulls, cows)
        if guess == secret:
            break
    return n_attempts

def ask(prompt: str, valid: list[str] = None) -> str:
    # cow = get_random_cow()
    cow = read_dot_cow(StringIO("""
    $the_cow = <<EOC;
        $thoughts
            $thoughts
              P^P
             (+ +)
            ( >*< )
              [Y]
         ( ......... )
          ( _______ )
              L  L
    EOC
    """))
    word = input(cowsay(prompt, cowfile=cow))
    if valid:
        while not word in valid:
            word = input(cowsay(prompt, cowfile=cow))
    return word

def inform(format_string: str, bulls: int, cows: int) -> None:
    cow = get_random_cow()
    print(cowsay(format_string.format(bulls, cows), cow=cow))


if __name__ == "__main__":
    parser = ArgumentParser(prog='bulls-cows', description="A word guessing game called 'bulls and cows'")
    parser.add_argument('dictionary', type=str, action='store', help='filename or URL of words that can be used')
    parser.add_argument('length', type=int, action='store', nargs='?', default=5, help='length of used words')

    args = parser.parse_args()

    if os.path.exists(args.dictionary):
        fname = args.dictionary
    else:
        fname, _ = urlretrieve(args.dictionary)

    words = []
    with open(fname, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) == args.length:
                words.append(line)

    if len(words) == 0:
        print('В словаре нет слов заданной длины :(')
    else:
        n_attempts = gameplay(ask, inform, words)
        print(f"Успех... Вы угадали слово...\nКоличество использованных попыток: всего лишь {n_attempts}")
