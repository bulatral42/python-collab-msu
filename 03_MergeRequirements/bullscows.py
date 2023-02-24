from collections import defaultdict
import random



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
    word = input(prompt)
    if not valid:
        while not word in valid:
            word = input(prompt)
    return word

def inform(format_string: str, bulls: int, cows: int) -> None:
    print(format_string.format(bulls, cows))



if __name__ == "__main__":
    words = ['bull', 'cow', 'milk', 'grass', 'water']
    n_attempts = gameplay(ask, inform, words)
    print(f"Успех... Вы угадали слово за всего лишь {n_attempts} попыток")
